import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# Configurações
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ARQUIVO_HISTORICO = "enviados.txt"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def carregar_enviados():
    if os.path.exists(ARQUIVO_HISTORICO):
        with open(ARQUIVO_HISTORICO, "r") as f:
            return set(f.read().splitlines())
    return set()

def salvar_enviado(link):
    with open(ARQUIVO_HISTORICO, "a") as f:
        f.write(link + "\n")

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def buscar_concursos():
    # PCI Concursos (Geralmente mais estável)
    url_pci = "https://www.pciconcursos.com.br/pesquisa/?q=TI"
    headers = {"User-Agent": "Mozilla/5.0"}
    novos = []
    
    try:
        response = requests.get(url_pci, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        enviados = carregar_enviados()

        items = soup.find_all('div', class_='ca')
        for item in items[:5]:
            link_tag = item.find('a')
            if link_tag:
                titulo = link_tag.text.strip()
                link = link_tag['href']
                
                # A MÁGICA ACONTECE AQUI:
                if link not in enviados:
                    novos.append({"titulo": titulo, "url": link})
                    salvar_enviado(link) # Marca como enviado
    except Exception as e:
        print(f"Erro: {e}")
    return novos

def rodar():
    concursos_novos = buscar_concursos()
    
    if not concursos_novos:
        print("Sem novidades reais hoje.")
        return

    for item in concursos_novos:
        prompt = f"Analise as disciplinas e conteúdos mais relevantes para TI deste concurso: {item['titulo']} no link {item['url']}. Destaque o que mais cai de acordo com a banca."
        
        response = model.generate_content(prompt)
        msg = f"🆕 *CONCURSO NOVO DETECTADO!*\n\n📌 {item['titulo']}\n🔗 [Link]({item['url']})\n\n💡 *ANÁLISE:* {response.text}"
        enviar_telegram(msg)

if __name__ == "__main__":
    rodar()
