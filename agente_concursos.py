import os
import requests

# Pega as chaves das Secrets
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_teste():
    print(f"Tentando enviar mensagem para o ID: {TELEGRAM_CHAT_ID}")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": "✅ Teste de Conexão: O robô está configurado corretamente!"
    }
    
    response = requests.post(url, json=payload)
    print(f"Resposta do Telegram: {response.status_code}")
    print(f"Conteúdo: {response.text}")

if __name__ == "__main__":
    enviar_teste()
