# app.py (adicionando CRUD de colaboradores)
from flask import Flask, request, jsonify
import sqlite3
from pubsub import AsyncConn

app = Flask(__name__)

pubnub = AsyncConn("flask_app", "meu_canal")
DB_NAME = 'data.db'

def connect_db():
    return sqlite3.connect(DB_NAME)

def create_tables():
    with connect_db() as conn:
        cursor = conn.cursor()
        # Tabela de colaboradores
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS collaborators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password TEXT NOT NULL,          
            tag INTEGER UNIQUE,
            authorized INTEGER DEFAULT 0
        )
        """)
        # Tabela de logs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()

create_tables()

# Endpoints para logs (já existentes)
@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, message, timestamp FROM logs ORDER BY id DESC")
            rows = cursor.fetchall()
        logs = [{"id": row[0], "message": row[1], "timestamp": row[2]} for row in rows]
        return jsonify(logs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/logs', methods=['POST'])
def add_log():
    try:
        data = request.json
        message = data.get("message")
        if not message:
            return jsonify({"error": "No message provided"}), 400
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO logs (message) VALUES (?)", (message,))
            conn.commit()
        pubnub.publish({"text": message})
        return jsonify({"message": "Log criado com sucesso"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# CRUD para colaboradores
@app.route('/collaborators', methods=['GET'])
def list_collaborators():
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, password, tag, authorized FROM collaborators")
            rows = cursor.fetchall()
        collaborators = [
            {"id": row[0], "name": row[1],"password": row[2] , "tag": row[3], "authorized": bool(row[4])} for row in rows
        ]
        return jsonify(collaborators), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/collaborators', methods=['POST'])
def create_collaborator():
    try:
        data = request.json
        name = data.get("name")
        tag = data.get("tag")
        authorized = data.get("authorized", False)
        password = data.get("password")
        
        if not name or not tag:
            return jsonify({"error": "Name and tag are required"}), 400
        
        if password != "admin":
            return jsonify({"error": "invalid password"}), 400

        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO collaborators (name, tag, authorized, password) VALUES (?, ?, ?, ?)",
                (name, tag, int(authorized), password)
            )
            conn.commit()
        
        return jsonify({"message": "Colaborador criado com sucesso"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/collaborators/<int:id>', methods=['PUT'])
def update_collaborator(id):
    try:
        data = request.json
        name = data.get("name")
        tag = data.get("tag")
        authorized = data.get("authorized")
        password = data.get("password")

        if password != "admin":
            return jsonify({"error": "invalid password"}), 400

        with connect_db() as conn:
            cursor = conn.cursor()
            # Atualiza os campos somente se forem passados
            cursor.execute("SELECT * FROM collaborators WHERE id = ?", (id,))
            collaborator = cursor.fetchone()
            if not collaborator:
                return jsonify({"error": "Colaborador não encontrado"}), 404
            
            name = name if name is not None else collaborator[1]
            tag = tag if tag is not None else collaborator[2]
            authorized = int(authorized) if authorized is not None else collaborator[3]
            
            cursor.execute(
                "UPDATE collaborators SET name = ?, tag = ?, authorized = ? WHERE id = ?, password = ?",
                (name, tag, authorized, password, id)
            )
            conn.commit()
        
        return jsonify({"message": "Colaborador atualizado com sucesso"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/collaborators/<int:id>', methods=['DELETE'])
def delete_collaborator(id):
    try:
        data = request.json
        password = data.get("password")

        if password != "admin":
            return jsonify({"error": "invalid password"}), 400
    
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM collaborators WHERE id = ?", (id,))
            conn.commit()
        return jsonify({"message": "Colaborador deletado com sucesso"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return "API de Gerenciamento de Acessos no ar!"

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)