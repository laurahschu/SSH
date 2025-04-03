import sqlite3
import pandas as pd

DB_NAME = 'data.db'

def extract_user(message):
    # Supondo que o nome do usuário seja a primeira palavra da mensagem
    return message.split()[0]

def analyze_logs():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM logs", conn)
    conn.close()

    # Converter timestamp para datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Extrair usuário a partir da mensagem
    df['user'] = df['message'].apply(extract_user)
    
    # Agrupar por usuário
    grouped = df.groupby('user')

    print("=== Análise de Logs por Usuário ===")
    for user, group in grouped:
        # Filtrando logs específicos para cada usuário
        entradas = group[group['message'].str.contains("entrou", case=False, na=False)]
        saidas = group[group['message'].str.contains("saiu", case=False, na=False)]
        nao_autorizadas = group[group['message'].str.contains("NÃO AUTORIZADA", case=False, na=False)]
        
        # Calculando o tempo total para o usuário (em minutos)
        if not group.empty:
            tempo_total = (group['timestamp'].max() - group['timestamp'].min()).total_seconds() / 60.0
        else:
            tempo_total = 0
        
        print(f"\nUsuário: {user}")
        print(f"  Total de entradas: {len(entradas)}")
        print(f"  Total de saídas: {len(saidas)}")
        print(f"  Tentativas não autorizadas: {len(nao_autorizadas)}")
        print(f"  Tempo total em minutos: {tempo_total:.2f}")

if __name__ == "__main__":
    analyze_logs()
