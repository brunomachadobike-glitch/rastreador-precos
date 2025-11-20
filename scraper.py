import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import time

# --- CONFIGURAÇÃO ---
# Coloque aqui o LINK DIRETO do produto que você quer (não a página de busca)
# Exemplo: Link de um PS5 Slim oficial
URL_PRODUTO = "https://www.mercadolivre.com.br/sony-playstation-5-slim-digital-edition-1tb-cor-branco/p/MLB28766628"
ARQUIVO_DADOS = "historico_precos.csv"

def extrair_preco(soup):
    """Tenta encontrar o preço de 3 formas diferentes"""
    
    # TENTATIVA 1: Meta Tag (A mais estável, usada para SEO)
    try:
        meta_price = soup.find("meta", itemprop="price")
        if meta_price:
            return float(meta_price["content"])
    except:
        pass

    # TENTATIVA 2: Preço Principal (Classe visual padrão do ML)
    try:
        # Procura o container de preço grande na página do produto
        container = soup.find("div", {"class": "ui-pdp-price__second-line"})
        if container:
            fracao = container.find("span", {"class": "andes-money-amount__fraction"})
            if fracao:
                return float(fracao.text.replace('.', '').replace(',', '.'))
    except:
        pass

    # TENTATIVA 3: Script JSON (Dados estruturados escondidos)
    # Muitas vezes o preço está dentro de um script <script type="application/ld+json">
    # Mas vamos manter simples por enquanto.
    
    return None

def pegar_dados():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    print(f"Acessando: {URL_PRODUTO}")
    
    try:
        response = requests.get(URL_PRODUTO, headers=headers, timeout=20)
        
        if response.status_code != 200:
            return None, f"Erro HTTP: {response.status_code}"
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Pega o Título
        titulo_tag = soup.find("h1", {"class": "ui-pdp-title"})
        titulo = titulo_tag.text.strip() if titulo_tag else "Produto Sem Nome"
        
        # Tenta pegar o preço com a função inteligente
        preco = extrair_preco(soup)
        
        if preco:
            return {"produto": titulo, "preco": preco}, None
        else:
            # Debug: Salva um pedaço do HTML para sabermos o que houve (opcional)
            print("Debug: Não achei preço. Classes encontradas nas spans:", [s.get('class') for s in soup.find_all('span')[:5]])
            return None, "Preço não encontrado (Seletores falharam)"

    except Exception as e:
        return None, f"Erro Crítico: {e}"

def main():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    dados, erro = pegar_dados()
    
    registro = {
        "data": timestamp,
        "produto": "Desconhecido",
        "preco": 0.0,
        "status": "Erro"
    }
    
    if dados:
        registro["produto"] = dados["produto"]
        registro["preco"] = dados["preco"]
        registro["status"] = "Sucesso"
        print(f"✅ SUCESSO! Item: {dados['produto']} | Preço: R$ {dados['preco']}")
    else:
        registro["status"] = f"Falha: {erro}"
        print(f"❌ {erro}")

    # Salvar (Append)
    if os.path.exists(ARQUIVO_DADOS):
        df = pd.read_csv(ARQUIVO_DADOS)
    else:
        df = pd.DataFrame(columns=["data", "produto", "preco", "status"])
    
    # Correção para versões novas do Pandas
    df_novo = pd.DataFrame([registro])
    df = pd.concat([df, df_novo], ignore_index=True)
    
    df.to_csv(ARQUIVO_DADOS, index=False)
    print("💾 CSV Atualizado.")

if __name__ == "__main__":
    main()
