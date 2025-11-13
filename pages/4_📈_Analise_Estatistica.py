# INÍCIO DO ARQUIVO pages/4_📈_Analise_Estatistica.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys
import os
from itertools import combinations
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import fetch_data_from_api, get_all_numbers, analyze_positional_frequencies, analyze_sum_and_range, analyze_triplets, analyze_quads

st.set_page_config(page_title="Análise Estatística", page_icon="📈", layout="wide")

st.title("📈 Análise Estatística e Business Intelligence")
st.markdown("Explore os dados da Lotofácil com gráficos interativos e insights profundos.")

st.sidebar.header("⚙️ Configurações de Análise")
start_concurso = st.sidebar.number_input("Concurso Inicial", min_value=1, value=2200)
end_concurso = st.sidebar.number_input("Concurso Final", min_value=1, value=2500)
df = fetch_data_from_api(start_concurso, end_concurso)

if not df.empty:
    st.sidebar.success(f"Analisando {len(df)} concursos.")
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🗺️ Mapa de Calor", "📉 Tendências", "📊 Distribuições", "🤝 Análise de Pares", "🔢 Trincas", "🎲 Quads"])
    all_numbers = get_all_numbers(df)
    freq_series = pd.Series(all_numbers).value_counts().sort_index()

    with tab1:
        st.header("Mapa de Calor dos Números")
        heatmap_data = np.zeros((5, 5))
        for num in range(1, 26):
            row, col = (num - 1) // 5, (num - 1) % 5
            heatmap_data[row, col] = freq_series.get(num, 0)
        fig = px.imshow(heatmap_data, labels=dict(x="Coluna", y="Linha", color="Frequência"), x=[1, 2, 3, 4, 5], y=[5, 4, 3, 2, 1], text_auto=True, aspect="auto", color_continuous_scale='Viridis')
        fig.update_xaxes(side="top"); st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.header("Análise de Tendências de um Número")
        selected_num = st.selectbox("Escolha um número para analisar:", list(range(1, 26)))
        count_per_draw = df.apply(lambda row: 1 if selected_num in row.values else 0, axis=1)
        df_trend = pd.DataFrame({'Concurso': df['Concurso'], 'Apareceu': count_per_draw})
        df_trend['Media Movel (20 concursos)'] = df_trend['Apareceu'].rolling(window=20).mean()
        fig = px.line(df_trend, x='Concurso', y=['Apareceu', 'Media Movel (20 concursos)'], title=f'Tendência do Número {selected_num}', labels={'value': 'Ocorrência', 'variable': 'Legenda'})
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.header("Análises de Distribuição")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Distribuição dos Finais")
            finais = [num % 10 for num in all_numbers]
            freq_finais = pd.Series(finais).value_counts().sort_index()
            fig_finais = px.bar(x=freq_finais.index, y=freq_finais.values, labels={'x':'Final (0-9)', 'y':'Frequência'}, title='Frequência dos Últimos Dígitos')
            st.plotly_chart(fig_finais, use_container_width=True)
        with col2:
            st.subheader("Distribuição de Atrasos")
            delays = {num: 0 for num in range(1, 26)}
            for index, row in df.iterrows():
                current_draw = set(row[[f'Bola{i}' for i in range(1, 16)]].values)
                for num in range(1, 26):
                    if num not in current_draw: delays[num] += 1
                    else: delays[num] = 0
            delay_counts = pd.Series(list(delays.values())).value_counts().sort_index()
            fig_delays = px.bar(x=delay_counts.index, y=delay_counts.values, labels={'x':'Concursos de Atraso', 'y':'Quantidade de Números'}, title='Quantos números estão atrasados em X concursos?')
            st.plotly_chart(fig_delays, use_container_width=True)
        
        st.subheader("Análise de Soma e Faixa")
        sum_range_df = analyze_sum_and_range(df)
        col3, col4 = st.columns(2)
        with col3:
            fig_sum = px.histogram(sum_range_df, x="Soma", nbins=50, title="Distribuição da Soma das Dezenas")
            st.plotly_chart(fig_sum, use_container_width=True)
        with col4:
            fig_range = px.histogram(sum_range_df, x="Faixa", nbins=25, title="Distribuição da Faixa (Maior - Menor)")
            st.plotly_chart(fig_range, use_container_width=True)

    with tab4:
        st.header("Análise de Pares (Avançado)")
        pair_counts = {}
        for index, row in df.iterrows():
            draw_numbers = sorted(row[[f'Bola{i}' for i in range(1, 16)]].values)
            for pair in combinations(draw_numbers, 2):
                pair_counts[pair] = pair_counts.get(pair, 0) + 1
        df_pairs = pd.DataFrame(sorted(pair_counts.items(), key=lambda item: item[1], reverse=True), columns=['Par', 'Frequência']).head(20)
        df_pairs['Par'] = df_pairs['Par'].apply(lambda p: f"{p[0]} - {p[1]}")
        st.dataframe(df_pairs, use_container_width=True)
        fig_pairs = px.bar(df_pairs, x='Par', y='Frequência', title='Top 20 Pares Mais Frequentes')
        fig_pairs.update_xaxes(tickangle=45); st.plotly_chart(fig_pairs, use_container_width=True)
    
    with tab5:
        st.header("Análise de Trincas (Avançado)")
        top_triplets = analyze_triplets(df, top_n=20)
        df_triplets = pd.DataFrame(top_triplets, columns=['Trinca', 'Frequência'])
        df_triplets['Trinca'] = df_triplets['Trinca'].apply(lambda t: f"{t[0]}-{t[1]}-{t[2]}")
        st.dataframe(df_triplets, use_container_width=True)
        fig_triplets = px.bar(df_triplets, x='Trinca', y='Frequência', title='Top 20 Trincas Mais Frequentes')
        fig_triplets.update_xaxes(tickangle=45); st.plotly_chart(fig_triplets, use_container_width=True)

    with tab6:
        st.header("Análise de Quads (Avançado)")
        top_quads = analyze_quads(df, top_n=20)
        df_quads = pd.DataFrame(top_quads, columns=['Quadra', 'Frequência'])
        df_quads['Quadra'] = df_quads['Quadra'].apply(lambda q: f"{q[0]}-{q[1]}-{q[2]}-{q[3]}")
        st.dataframe(df_quads, use_container_width=True)
        fig_quads = px.bar(df_quads, x='Quadra', y='Frequência', title='Top 20 Quadras Mais Frequentes')
        fig_quads.update_xaxes(tickangle=45); st.plotly_chart(fig_quads, use_container_width=True)

# FIM DO ARQUIVO pages/4_📈_Analise_Estatistica.py