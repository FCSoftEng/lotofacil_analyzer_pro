# INÍCIO DO ARQUIVO pages/1_🏆_Resultados.py

import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import fetch_latest_contest, fetch_all_results, get_all_numbers

st.set_page_config(page_title="Últimos Resultados", page_icon="🏆", layout="wide")

st.title("🏆 Central de Resultados da Lotofácil")

# --- SEÇÃO PRINCIPAL: ÚLTIMO CONCURSO ---
latest_result = fetch_latest_contest()

if not latest_result.empty:
    st.markdown("---")
    st.header(f"🎯 Concurso Mais Recente: {latest_result['Concurso']} ({latest_result['Data'].strftime('%d/%m/%Y')})")
    
    # Exibe as dezenas em cards grandes e destacados
    st.markdown("### Dezenas Sorteadas:")
    dezenas_cols = st.columns(15)
    sorted_dezenas = sorted([latest_result[f'Bola{i}'] for i in range(1, 16)])
    for i, col in enumerate(dezenas_cols):
        with col:
            st.markdown(
                f'<div style="background-color:#262730;padding:10px;border-radius:5px;text-align:center;font-size:20px;font-weight:bold;">{sorted_dezenas[i]}</div>',
                unsafe_allow_html=True
            )

    st.markdown("---")

    # --- SEÇÃO DE ANÁLISE RÁPIDA ---
    with st.expander("📊 Análise Detalhada do Último Concurso", expanded=True):
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Soma Total", sum(sorted_dezenas))
        with col2:
            st.metric("Maior Dezena", max(sorted_dezenas))
        with col3:
            st.metric("Menor Dezena", min(sorted_dezenas))
        with col4:
            pares = len([n for n in sorted_dezenas if n % 2 == 0])
            st.metric("Quant. Pares", pares)
        with col5:
            impares = 15 - pares
            st.metric("Quant. Ímpares", impares)

    # --- SEÇÃO DE HISTÓRICO COM FILTROS ---
    st.header("📜 Histórico de Resultados")
    
    df_all = fetch_all_results()
    if not df_all.empty:
        # Filtros na barra lateral para a tabela de histórico
        with st.sidebar.expander("Filtros do Histórico"):
            # Filtro por número do concurso
            search_concurso = st.number_input("Buscar por número do concurso:", min_value=1, value=0, placeholder="Digite o número")
            
            # Filtro por intervalo de datas
            min_date = df_all['Data'].min().to_pydatetime()
            max_date = df_all['Data'].max().to_pydatetime()
            start_date_filter = st.date_input("Data de Início:", value=min_date, min_value=min_date, max_value=max_date)
            end_date_filter = st.date_input("Data de Fim:", value=max_date, min_value=min_date, max_value=max_date)

        # Aplicar filtros ao DataFrame
        df_filtered = df_all.copy()
        if search_concurso > 0:
            df_filtered = df_filtered[df_filtered['Concurso'] == search_concurso]
        
        # Converter as datas do filtro para o mesmo tipo do DataFrame
        start_date_ts = pd.to_datetime(start_date_filter)
        end_date_ts = pd.to_datetime(end_date_filter)
        df_filtered = df_filtered[(df_filtered['Data'] >= start_date_ts) & (df_filtered['Data'] <= end_date_ts)]

        st.write(f"Exibindo {len(df_filtered)} concurso(s) encontrado(s) com os filtros aplicados.")
        
        if not df_filtered.empty:
            display_cols = ['Concurso', 'Data'] + [f'Bola{i}' for i in range(1, 16)]
            display_df = df_filtered[display_cols].sort_values(by='Concurso', ascending=False)
            
            # Botão de download
            csv = display_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar Resultados Filtrados (CSV)",
                data=csv,
                file_name='resultados_lotofacil_filtrados.csv',
                mime='text/csv',
            )
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.warning("Nenhum concurso encontrado com os filtros selecionados.")

# FIM DO ARQUIVO pages/1_🏆_Resultados.py