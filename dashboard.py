import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Caçador de Ofertas", layout="wide")

st.title("🎯 Central de Alertas - Black Friday")

# --- 1. Área de Cadastro Rápido (Visual apenas) ---
with st.expander("➕ Adicionar Novo Produto"):
    st.write("Para rastrear um novo item, adicione o link no arquivo `lista.txt` no GitHub.")
    novo_link = st.text_input("Link do produto (apenas para teste local):")
    if st.button("Simular Adição"):
        st.success("Link reconhecido! Adicione-o ao arquivo 'lista.txt' no GitHub para monitoramento contínuo.")

st.divider()

# --- 2. Carregar Dados ---
arquivo = "historico_precos.csv"

try:
    df = pd.read_csv(arquivo)
    df['data'] = pd.to_datetime(df['data'])
    
    # Filtra só os sucessos
    df_ok = df[df['status'] == 'Sucesso'].copy()
    
    if not df_ok.empty:
        # Pega a lista de produtos únicos monitorados
        produtos_unicos = df_ok['link'].unique()
        
        st.subheader("📢 Status dos Produtos")
        
        # Cria cartões para cada produto
        for link in produtos_unicos:
            # Pega todo o histórico desse produto
            hist_prod = df_ok[df_ok['link'] == link].sort_values(by='data')
            
            if not hist_prod.empty:
                nome_atual = hist_prod.iloc[-1]['produto']
                preco_atual = hist_prod.iloc[-1]['preco']
                
                # Análise de Queda de Preço
                preco_maximo = hist_prod['preco'].max()
                preco_minimo = hist_prod['preco'].min()
                primeiro_preco = hist_prod.iloc[0]['preco']
                
                # Container visual
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        st.markdown(f"### {nome_atual}")
                        st.caption(f"Link: {link}")
                    
                    with col2:
                        st.metric("Preço Agora", f"R$ {preco_atual:,.2f}")
                    
                    with col3:
                        # Compara com o preço MÁXIMO já visto (para ver desconto real)
                        desconto = ((preco_maximo - preco_atual) / preco_maximo) * 100
                        
                        if desconto > 0:
                            st.metric("Queda (vs Máx)", f"{desconto:.1f}%", delta=f"- R$ {preco_maximo - preco_atual:.2f}", delta_color="normal")
                        else:
                            st.metric("Estável", "-", delta_color="off")

                    with col4:
                        if preco_atual <= preco_minimo:
                             st.error("🔥 MENOR PREÇO!")
                        elif preco_atual < primeiro_preco:
                             st.success("✅ Abaixo do início")
                        else:
                             st.info("😐 Preço normal")
                    
                    # Gráfico Miniatura
                    grafico = px.line(hist_prod, x='data', y='preco', height=200)
                    st.plotly_chart(grafico, use_container_width=True)
                    st.divider()

    else:
        st.warning("Ainda não há dados de sucesso coletados.")

except FileNotFoundError:
    st.error("O arquivo de dados ainda não foi criado pelo robô.")
