from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO ---
# Link direto do produto
URL_PRODUTO = "https://www.mercadolivre.com.br/sony-playstation-5-slim-digital-edition-1tb-cor-branco/p/MLB28766628"
ARQUIVO_DADOS = "historico_precos.csv"

def pegar_dados_com_navegador():
    print(f"🚀 Iniciando navegador para acessar: {URL_PRODUTO}")
    
    try:
        with sync_playwright() as p:
            # Abre um navegador Chrome invisível (Headless)
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Vai para a página e espera até 30 segundos para carregar
            page.goto(URL_PRODUTO, timeout=60000)
            
            # Espera um pouco para garantir que scripts de preço carregaram
            page.wait_for_timeout(5000) 
            
            # TENTATIVA 1: Meta Tag (Dados estruturados para Google)
            try:
                preco_meta = page.locator('meta[itemprop="price"]').get_attribute("content")
                nome_meta = page.locator('meta[name="twitter:title"]').get_attribute("content")
                
                if preco_meta:
                    return {
                        "produto": nome_meta if nome_meta else "Produto Detectado", 
                        "preco": float(preco_meta)
                    }, None
            except Exception as e:
                print(f"Meta tag falhou: {e}")

            # TENTATIVA 2: Seletor Visual Genérico (Procura cifrão e números grandes)
            # Isso tenta pegar qualquer preço visível grande na tela
            try:
                # Procura pelo preço principal (geralmente o maior texto numérico)
                elemento_preco = page.locator('.ui-pdp-price__second-line .andes-money-amount__fraction').first
                if elemento_preco.is_visible():
                    texto_preco = elemento_preco.inner_text()
                    preco_float = float(texto_preco.replace('.', '').replace(',', '.'))
                    return {"produto": "Produto via Visual", "preco": preco_float}, None
            except Exception as e:
                print(f"Visual falhou: {e}")

            # Fecha o navegador
            browser.close()
            
            return None, "Não foi possível achar o preço nem via Meta nem Visual."

    except Exception as e:
        return None, f"Erro no Navegador: {str(e)}"

def main():
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    dados, erro = pegar_dados_com_navegador()
    
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
        print(f"✅ SUCESSO! R$ {dados['preco']}")
    else:
        registro["status"] = f"Falha: {erro}"
        print(f"❌ {erro}")

    # Salvar
    if os.path.exists(ARQUIVO_DADOS):
        df = pd.read_csv(ARQUIVO_DADOS)
    else:
        df = pd.DataFrame(columns=["data", "produto", "preco", "status"])
    
    df_novo = pd.DataFrame([registro])
    df = pd.concat([df, df_novo], ignore_index=True)
    df.to_csv(ARQUIVO_DADOS, index=False)

if __name__ == "__main__":
    main()
