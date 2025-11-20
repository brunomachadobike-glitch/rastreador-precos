from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os

# --- MUDANÇA DE ESTRATÉGIA ---
# Vamos testar com Amazon que bloqueia menos IPs dos EUA
# Se quiser tentar ML de novo, troque a URL, mas veja o print depois.
URL_PRODUTO = "https://www.amazon.com.br/PlayStation-5-Slim-Edi%C3%A7%C3%A3o-Digital/dp/B0CL5KNB9M/"
ARQUIVO_DADOS = "historico_precos.csv"

def pegar_dados_com_raio_x():
    print(f"📸 Preparando para tirar foto de: {URL_PRODUTO}")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800} # Tamanho de tela de laptop
            )
            page = context.new_page()
            
            # Tenta acessar
            page.goto(URL_PRODUTO, timeout=60000)
            page.wait_for_timeout(5000) # Espera 5 segs
            
            # --- O RAIO-X ---
            titulo_pagina = page.title()
            print(f"🔎 Título da Página encontrada: {titulo_pagina}")
            
            # Tira um Print da tela (Fundamental para descobrirmos o erro)
            page.screenshot(path="debug_screenshot.png")
            print("📸 Screenshot salvo como 'debug_screenshot.png'")
            
            # LÓGICA DE PREÇO (Adaptada para Amazon e ML)
            preco_final = 0.0
            nome_final = ""
            
            # Tenta achar preço Amazon (Classe a-price-whole)
            try:
                elemento_amazon = page.locator('.a-price-whole').first
                if elemento_amazon.is_visible():
                    texto = elemento_amazon.inner_text()
                    preco_final = float(texto.replace('.', '').replace(',', ''))
                    nome_final = page.locator('#productTitle').inner_text().strip()
            except:
                pass
            
            # Tenta achar preço ML (caso você troque a URL de volta)
            if preco_final == 0:
                try:
                    elemento_ml = page.locator('meta[itemprop="price"]').get_attribute("content")
                    if elemento_ml:
                        preco_final = float(elemento_ml)
                        nome_final = "Produto ML"
                except:
                    pass

            browser.close()
            
            if preco_final > 0:
                return {"produto": nome_final, "preco": preco_final}, None
            else:
                return None, f"Preço não achado. Título da pág: {titulo_pagina}"

    except Exception as e:
        return None, f"Erro Crítico: {str(e)}"

def main():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    dados, erro = pegar_dados_com_raio_x()
    
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
        print(f"✅ SUCESSO! {dados['produto']} - R$ {dados['preco']}")
    else:
        registro["status"] = f"Falha: {erro}"
        print(f"❌ {erro}")

    # Salva CSV
    if os.path.exists(ARQUIVO_DADOS):
        df = pd.read_csv(ARQUIVO_DADOS)
    else:
        df = pd.DataFrame(columns=["data", "produto", "preco", "status"])
    
    df_novo = pd.DataFrame([registro])
    df = pd.concat([df, df_novo], ignore_index=True)
    df.to_csv(ARQUIVO_DADOS, index=False)

if __name__ == "__main__":
    main()
