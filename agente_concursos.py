import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# 1. Configurar o Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def buscar_concursos():
    # URL da seção de TI da Folha Dirigida
    url = "https://folha.qconcursos.com/n/concursos/ti"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Encontra as manchetes de concursos
        noticias = soup.find_all('h2')[:3] # Pega as 3 últimas notícias
        
        resultados = []
        for n in noticias:
            titulo = n.text.strip()
            # Tenta pegar o link da notícia
            link = n.find_parent('a')['href'] if n.find_parent('a') else url
            if not link.startswith('http'):
                link = "https://folha.qconcursos.com" + link
            resultados.append({"titulo": titulo, "url": link})
        return resultados
    except Exception as e:
        print(f"Erro ao buscar: {e}")
        return []

def analisar(concurso):
    # O SEU PROMPT EXATO
    prompt = f"""
    Faça análise do conteúdo de cada disciplina e destaque todos os conteúdos que são mais relevantes para concurso desta área e de acordo com a banca e a quantidade de questões destinada a cada uma das disciplinas.
    
    INFORMAÇÕES DO CONCURSO ENCONTRADO:
    Título: {concurso['titulo']}
    Fonte: {concurso['url']}
    """
    
    response = model.generate_content(prompt)
    print(f"\n--- ANÁLISE PARA: {concurso['titulo']} ---")
    print(response.text)

if __name__ == "__main__":
    lista = buscar_concursos()
    for item in lista:
        analisar(item)
