import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# Configurações via Secrets do GitHub
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    # O Telegram aceita Markdown para deixar o texto bonito (negrito, etc)
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def buscar_e_analisar():
    url_base = "https://folha.qconcursos.com/n/concursos/ti"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url_base, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    noticias = soup.find_all('h2')[:2] # Pega as 2 mais recentes
    
    if not noticias:
        print("Nenhuma notícia encontrada.")
        return

    for n in noticias:
        titulo = n.text.strip()
        link = n.find_parent('a')['href'] if n.find_parent('a') else url_base
        if not link.startswith('http'): link = "https://folha.qconcursos.com" + link
        
        prompt = f"Faça análise do conteúdo de cada disciplina e destaque todos os conteúdos que são mais relevantes para concurso desta área e de acordo com a banca e a quantidade de questões destinada a cada uma das disciplinas. Baseie-se neste concurso: {titulo} Link: {link}"
        
        analise = model.generate_content(prompt).text
        
        # Formatando a mensagem para o Telegram
        mensagem_final = f"🚀 *NOVO CONCURSO TI DETECTADO*\n\n" \
                         f"📌 *Edital:* {titulo}\n" \
                         f"🔗 *Link:* [Clique aqui]({link})\n\n" \
                         f"🤖 *ANÁLISE DO GEMINI:*\n{analise}"
        
        enviar_telegram(mensagem_final)

if __name__ == "__main__":
    buscar_e_analisar()
