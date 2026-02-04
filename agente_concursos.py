import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# Configurações via Secrets do GitHub
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Inicializa Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    # Dividir mensagens longas para não exceder o limite do Telegram (4096 chars)
    if len(mensagem) > 4000:
        parts = [mensagem[i:i+4000] for i in range(0, len(mensagem), 4000)]
    else:
        parts = [mensagem]
    
    for part in parts:
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": part, "parse_mode": "Markdown"}
        requests.post(url, json=payload)

def buscar_concursos():
    # Usando a URL de notícias gerais de concursos para garantir que pegamos dados
    url = "https://folha.qconcursos.com/n/concursos"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Busca por títulos que contenham "TI", "Tecnologia", "Informática" ou "Analista"
        noticias = []
        for h2 in soup.find_all(['h2', 'h3']):
            texto = h2.get_text().strip()
            # Filtro para focar na sua área
            if any(termo in texto.upper() for termo in ["TI", "TECNOLOGIA", "INFORMÁTICA", "ANALISTA", "PROVAS"]):
                link_tag = h2.find_parent('a') or h2.find('a')
                link = link_tag['href'] if link_tag else url
                if not link.startswith('http'): link = "https://folha.qconcursos.com" + link
                noticias.append({"titulo": texto, "url": link})
        
        return noticias[:3] # Retorna as 3 mais relevantes
    except Exception as e:
        print(f"Erro na busca: {e}")
        return []

def processar_e_enviar():
    concursos = buscar_concursos()
    
    if not concursos:
        enviar_telegram("🔎 Hoje não encontrei notícias específicas de TI na Folha Dirigida. Vou monitorar novamente amanhã!")
        return

    for item in concursos:
        prompt = f"""
        Você é um especialista em concursos públicos de TI. 
        Analise a notícia/concurso abaixo e responda com foco em:
        1. Disciplinas prováveis.
        2. Conteúdos mais relevantes para a área de TI.
        3. Perfil da banca (se mencionada).
        4. Estimativa de relevância de tópicos por quantidade de questões.

        DADOS:
        Título: {item['titulo']}
        Link: {item['url']}
        
        Responda em um formato Markdown elegante para Telegram.
        """
        
        try:
            response = model.generate_content(prompt)
            analise = response.text
            
            mensagem = f"🚀 *ANÁLISE DE CONCURSO TI*\n\n" \
                       f"📌 *Evento:* {item['titulo']}\n" \
                       f"🔗 *Fonte:* [Acesse a notícia]({item['url']})\n\n" \
                       f"{analise}"
            
            enviar_telegram(mensagem)
        except Exception as e:
            print(f"Erro no Gemini: {e}")

if __name__ == "__main__":
    processar_e_enviar()
