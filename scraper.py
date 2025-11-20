import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import random
import time

# Vamos tentar pegar o PS5. 
# Se falhar, o script NÃO vai quebrar, ele vai registrar o erro.
URL_ALVO = "https://lista.mercadolivre.com.br/playstation-5"
ARQUIVO_DADOS = "historico_precos.csv"

def pegar_dados():
    # Headers para parecer um navegador real
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    try:
        response = requests.get(URL_ALVO, headers=headers, timeout=15)
        if response.status_code != 200:
            return None, f"Bloqueio ou Erro: {response.status_code}"
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Tenta achar o primeiro item da lista
        item = soup.find('li', {'class': 'ui-search-layout__item'})
        if item:
            # Tenta achar o preço
            preco_obj = item.find('span', {'class': 'andes-money-amount__fraction'})
            titulo_obj = item.find('h2')
            
            if preco_obj and titulo_obj:
                preco = float(preco_obj.text.replace('.', '').replace(',', '.'))
                titulo = titulo_obj.text.strip()
                return {"produto": titulo, "preco": preco}, None
                
        return None, "Layout mudou ou não encontrou elementos"
        
    except Exception as e:
        return None, f"Erro exceção: {str(e)}"

def main():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 1. Tenta coletar
    dados, erro = pegar_dados()
    
    registro = {
        "data": timestamp,
        "produto": "N/A",
        "preco": 0.0,
        "status": "Erro"
    }
    
    if dados:
        registro["produto"] = dados["produto"]
        registro["preco"] = dados["preco"]
        registro["status"] = "Sucesso"
        print(f"✅ Sucesso! Preço: {dados['preco']}")
    else:
        registro["status"] = f"Falha: {erro}"
        print(f"⚠️ Falha na coleta: {erro}")

    # 2. Carrega ou Cria o DataFrame
    if os.path.exists(ARQUIVO_DADOS):
        df = pd.read_csv(ARQUIVO_DADOS)
    else:
        df = pd.DataFrame(columns=["data", "produto", "preco", "status"])
    
    # 3. Salva (Isso garante que o arquivo sempre exista/atualize)
    # Convertendo o registro (dict) para DataFrame antes de concatenar
    novo_dado_df = pd.DataFrame([registro])
    df = pd.concat([df, novo_dado_df], ignore_index=True)
    
    df.to_csv(ARQUIVO_DADOS, index=False)
    print("💾 Arquivo CSV salvo com sucesso.")

if __name__ == "__main__":
    main()
