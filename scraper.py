from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os
import time
import random

ARQUIVO_DADOS = "historico_precos.csv"
ARQUIVO_LISTA = "lista.txt"

def pegar_preco_amazon(page, url):
    try:
        page.goto(url.strip(), timeout=60000)
        time.sleep(random.uniform(4, 7))
        
        titulo = page.title()
        preco_final = 0.0
        nome_produto = "Desconhecido"

        # Tenta pegar Título
        try:
            nome_produto = page.locator('#productTitle').inner_text().strip()
            # Limita o tamanho do nome para não quebrar o gráfico
            nome_produto = (nome_produto[:40] + '..') if len(nome_produto) > 40 else nome_produto
        except:
            nome_produto = titulo[:30]

        # Tenta pegar Preço
        try:
            elemento_preco = page.locator('.a-price-whole').first
            if elemento_preco.is_visible():
                texto = elemento_preco.inner_text()
                preco_final = float(texto.replace('.', '').replace(',', ''))
        except:
            pass
            
        return {"produto": nome_produto, "preco": preco_final, "url": url}

    except Exception as e:
        print(f"Erro na URL {url}: {e}")
        return None

def main():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    novos_registros = []
    
    # 1. LER A LISTA DE PRODUTOS DO ARQUIVO TXT
    if not os.path.exists(ARQUIVO_LISTA):
        print("Arquivo lista.txt não encontrado!")
        return

    with open(ARQUIVO_LISTA, 'r') as f:
        urls = [linha.strip() for linha in f.readlines() if linha.strip()]

    print(f"🚀 Iniciando ronda para {len(urls)} produtos...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        for url in urls:
            dados = pegar_preco_amazon(page, url)
            
            registro = {
                "data": timestamp,
                "produto": "Erro",
                "preco": 0.0,
                "link": url,
                "status": "Falha"
            }

            if dados and dados['preco'] > 0:
                registro["produto"] = dados["produto"]
                registro["preco"] = dados["preco"]
                registro["status"] = "Sucesso"
                print(f"✅ {dados['produto']} -> R$ {dados['preco']}")
            else:
                print(f"⚠️ Falha ao capturar: {url}")

            novos_registros.append(registro)
            time.sleep(random.uniform(5, 10)) # Pausa de segurança

        browser.close()

    # Salvar no CSV
    if os.path.exists(ARQUIVO_DADOS):
        df = pd.read_csv(ARQUIVO_DADOS)
    else:
        df = pd.DataFrame(columns=["data", "produto", "preco", "link", "status"])
    
    df_novos = pd.DataFrame(novos_registros)
    df_final = pd.concat([df, df_novos], ignore_index=True)
    df_final.to_csv(ARQUIVO_DADOS, index=False)

if __name__ == "__main__":
    main()
