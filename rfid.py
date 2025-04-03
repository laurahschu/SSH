# rfid.py
import RPi.GPIO as GPIO
import time
from mfrc522 import SimpleMFRC522
import requests
from datetime import datetime

class SistemaControleAcesso:

    def __init__(self):
        # Inicialização do leitor RFID
        self.leitorRfid = SimpleMFRC522()

        # Mapeia o estado dos colaboradores (dentro ou fora)
        self.estado_colaboradores = {}  # {tag: "inside"/"outside"}

    def send_log_to_api(self, message):
        """Envia log para a API Flask, que salva no DB e publica no PubNub."""
        try:
            url = "http://localhost:5000/logs"
            data = {"message": message}
            resp = requests.post(url, json=data)
            if resp.status_code == 201:
                print("Log enviado com sucesso:", message)
            else:
                print("Erro ao enviar log:", resp.status_code, resp.text)
        except Exception as e:
            print("Erro na conexão com API:", e)

    def process_tag(self, tag,url = "http://localhost:5000/collaborators"):
        """Verifica se a tag está autorizada e registra entrada/saída."""
        # Aqui, ao invés de ter um cadastro fixo, poderia consultar a API/DB para verificar.
        # Exemplo simplificado: se a tag for 123456, consideramos o colaborador "Fulano" autorizado.

        response = requests.get(url)

        # Verifica se a requisição foi bem-sucedida
        if response.status_code == 200:
            colaboradores = response.json()

            for colaborador in colaboradores:
                if tag == colaborador["tag"]:
                    nome = colaborador["name"]
                    autorizado = True
                else:
                    nome = "Desconhecido"
                    autorizado = False
                
            print(f"Nome: {nome}, Autorizado: {autorizado}")

        if not autorizado:
            self.send_log_to_api(f"NÃO AUTORIZADA para tag {tag} - {datetime.now()}")
            return

        # Verifica se o colaborador está entrando ou saindo
        estado_atual = self.estado_colaboradores.get(tag, "outside")
        if estado_atual == "outside":
            self.estado_colaboradores[tag] = "inside"
            self.send_log_to_api(f"{nome} (tag {tag}) entrou às {datetime.now()}")
            
        else:
            self.estado_colaboradores[tag] = "outside"
            self.send_log_to_api(f"{nome} (tag {tag}) saiu às {datetime.now()}")

    def iniciar(self):
        try:
            print("Sistema de Controle de Acesso Iniciado. Aguardando leituras...")
            while True:
                tag, _ = self.leitorRfid.read()
                self.process_tag(tag)
                time.sleep(1)
        except KeyboardInterrupt:
            print("Encerrando sistema RFID...")
        finally:
            GPIO.cleanup()

if __name__ == "__main__":
    sistema = SistemaControleAcesso()
    sistema.iniciar()
 