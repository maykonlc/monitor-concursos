import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# Configurações via Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def buscar_pci_concursos():
    """Busca concursos de TI no PCI Concursos (Nacional)"""
    url = "https://www.pciconcursos.com.br/pesquisa/?q=TI"
    headers = {"User-Agent": "Mozilla/5.0"}
    noticias = []
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # O PCI lista resultados em divs com a classe 'ca' ou dentro de #data_lista
        items = soup.find_all('div', class_='ca')
        for item in items[:3]:
            link_tag = item.find('a')
            if link_tag:
                titulo = link_tag.text.strip()
                link = link_tag['href']
                noticias.append({"titulo": titulo, "url": link, "fonte": "PCI Concursos"})
    except Exception as e:
        print(f"Erro PCI: {e}")
    return noticias

def buscar_folha_dirigida():
    """Busca na Folha Dirigida"""
    url = "https://folha.qconcursos.com/n/concursos/ti"
    headers = {"User-Agent": "Mozilla/5.0"}
    noticias = []
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Tenta pegar os títulos H2 ou H3
        titulos = soup.find_all(['h2', 'h3'])
        for t in titulos[:3]:
            link_tag = t.find_parent('a') or t.find('a')
            if link_tag:
                link = link_tag['href']
                if not link.startswith('http'): link = "https://folha.qconcursos.com" + link
                noticias.append({"titulo": t.text.strip(), "url": link, "fonte": "Folha Dirigida"})
    except Exception as e:
        print(f"Erro Folha: {e}")
    return noticias

def processar():
    enviar_telegram("🤖 *Iniciando busca diária de concursos de TI...*")
    
    # Busca nos dois sites
    lista_concursos = buscar_pci_concursos() + buscar_folha_dirigida()
    
    if not lista_concursos:
        enviar_telegram("⚠️ Rodei a busca, mas nenhum edital novo de TI foi detectado nos sites hoje.")
        return

    # Se achou, manda para o Gemini
    for item in lista_concursos:
        prompt = f"""
        Faça análise do conteúdo de cada disciplina e destaque todos os conteúdos que são mais relevantes para concurso desta área e de acordo com a banca e a quantidade de questões destinada a cada uma das disciplinas.
        DADOS: {item['titulo']} - Fonte: {item['url']}
        """
        
        try:
            response = model.generate_content(prompt)
            mensagem = f"🎯 *CONCURSO ENCONTRADO ({item['fonte']})*\n\n" \
                       f"📋 *Título:* {item['titulo']}\n" \
                       f"🔗 *Link:* [Acesse aqui]({item['url']})\n\n" \
                       f"💡 *ANÁLISE:* \n{response.text}"
            enviar_telegram(mensagem)
        except:
            enviar_telegram(f"❌ Erro ao analisar o concurso: {item['titulo']}")

if __name__ == "__main__":
    processar()
