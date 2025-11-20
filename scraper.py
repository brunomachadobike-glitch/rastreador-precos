from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os
import time
import random

# --- SUA LISTA DE COMPRAS (Adicione quantos quiser) ---
LISTA_DESEJOS = [
    "https://www.amazon.com.br/PlayStation-5-Slim-Edi%C3%A7%C3%A3o-Digital/dp/B0CL5KNB9M/",
    "https://www.amazon.com.br/Apple-iPhone-15-128-GB/dp/B0CHH5H7Z7/",
    # Cole mais links aqui (sempre entre aspas e com vírgula no final)
]

ARQUIVO_DADOS = "historico_precos.csv"

def pegar_preco_amazon(page, url):
    print(f"🔎 Acessando: {url}")
    
    try:
        page.goto(url, timeout=60000)
        # Espera aleatória para parecer humano
        time.sleep(random.uniform(3, 6))
        
        titulo = page.title()
        preco_final = 0.0
        nome_produto = "Desconhecido"

        # 1. Tenta pegar o Título do Produto
        try:
            nome_produto = page.locator('#productTitle').inner_text().strip()
        except:
            nome_produto = titulo[:30] # Pega o começo do título da página se falhar

        # 2. Tenta pegar o Preço (O seletor clássico da Amazon)
        # Procura por <span class="a-price-whole">
        try:
            elemento_preco = page.locator('.a-price-whole').first
            if elemento_preco.is_visible():
                texto = elemento_preco.inner_text()
                # Remove pontos de milhar e troca vírgula por ponto se necessário
                # Amazon BR usa formato 3.500,00 -> queremos 3500.00
                preco_final = float(texto.replace('.', '').replace(',', ''))
        except Exception as e:
            print(f"⚠️ Erro ao ler seletor de preço: {e}")

        return {
            "produto": nome_produto,
            "preco": preco_final,
            "url": url
        }

    except Exception as e:
        print(f"❌ Erro na página: {e}")
        return None

def main():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    novos_registros = []

    print("🚀 Iniciando ronda de preços...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Cria um contexto com tamanho de tela normal para evitar layouts mobile quebrados
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        for url in LISTA_DESEJOS:
            dados = pegar_preco_amazon(page, url)
            
            registro = {
                "data": timestamp,
                "produto": "Erro",
                "preco": 0.0,
                "status": "Falha",
                "link": url
            }

            if dados and dados['preco'] > 0:
                registro["produto"] = dados["produto"]
                registro["preco"] = dados["preco"]
                registro["status"] = "Sucesso"
                print(f"✅ {dados['produto']} -> R$ {dados['preco']}")
            else:
                print(f"⚠️ Não consegui preço para: {url}")

            novos_registros.append(registro)
            
            # PAUSA DE SEGURANÇA ENTRE PRODUTOS
            # Se você acessar 10 links em 1 segundo, a Amazon te bloqueia.
            tempo_espera = random.uniform(5, 10)
            print(f"⏳ Esperando {tempo_espera:.1f}s antes do próximo...")
            time.sleep(tempo_espera)

        browser.close()

    # Salvar tudo no CSV
    if os.path.exists(ARQUIVO_DADOS):
        df = pd.read_csv(ARQUIVO_DADOS)
    else:
        df = pd.DataFrame(columns=["data", "produto", "preco", "status", "link"])
    
    df_novos = pd.DataFrame(novos_registros)
    df_final = pd.concat([df, df_novos], ignore_index=True)
    
    df_final.to_csv(ARQUIVO_DADOS, index=False)
    print("💾 CSV Atualizado com sucesso!")

if __name__ == "__main__":
    main()
