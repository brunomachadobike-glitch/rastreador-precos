import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

# Lista de produtos para monitorar (Adicione quantos quiser)
# DICA: Use links de busca específicos ou páginas de produtos
PRODUTOS = [
    {"nome": "Playstation 5", "url": "https://lista.mercadolivre.com.br/playstation-5"},
    {"nome": "iPhone 15", "url": "https://lista.mercadolivre.com.br/iphone-15"},
    # Adicione mais aqui...
]

def pegar_preco(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Tentativa de pegar o primeiro item da lista do ML
        item = soup.find('li', {'class': 'ui-search-layout__item'})
        if item:
            # Preço
            price_container = item.find('span', {'class': 'andes-money-amount__fraction'})
            if price_container:
                price = float(price_container.text.replace('.', '').replace(',', '.'))
                return price
    except Exception as e:
        print(f"Erro ao ler {url}: {e}")
    return None

def main():
# ... (dentro da def main(): )
    arquivo_csv = 'dados_precos.csv'
    
    # FORÇA A CRIAÇÃO DO ARQUIVO se ele não existir
    if not os.path.exists(arquivo_csv):
        df_inicial = pd.DataFrame(columns=['data', 'produto', 'preco'])
        df_inicial.to_csv(arquivo_csv, index=False)
        print("Arquivo inicial criado!")
    
    # ... (resto do código)
    
    # Carrega dados antigos se existirem
    if os.path.exists(arquivo_csv):
        df = pd.read_csv(arquivo_csv)
    else:
        df = pd.DataFrame(columns=['data', 'produto', 'preco'])

    novos_dados = []
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print(f"Iniciando coleta: {timestamp}")

    for item in PRODUTOS:
        preco_atual = pegar_preco(item['url'])
        if preco_atual:
            print(f"Preço {item['nome']}: R$ {preco_atual}")
            novos_dados.append({
                'data': timestamp,
                'produto': item['nome'],
                'preco': preco_atual
            })
        else:
            print(f"Não consegui pegar preço de {item['nome']}")

    # Salva tudo
    if novos_dados:
        df_novo = pd.DataFrame(novos_dados)
        df_final = pd.concat([df, df_novo], ignore_index=True)
        df_final.to_csv(arquivo_csv, index=False)
        print("Arquivo CSV atualizado com sucesso.")

if __name__ == "__main__":
    main()
