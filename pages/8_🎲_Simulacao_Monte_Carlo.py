# pages/9_🎲_Simulacao_Monte_Carlo.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import fetch_data_from_api

st.set_page_config(page_title="Simulação Monte Carlo", page_icon="🎲", layout="wide")

st.title("🎲 Simulação de Monte Carlo")
st.markdown("Simule milhares de cenários futuros para entender o risco e o potencial de uma estratégia.")

st.sidebar.header("⚙️ Configurações da Simulação")
st.sidebar.subheader("Base de Dados Históricos")
start_concurso_mc = st.sidebar.number_input("Concurso Inicial", min_value=1, value=2200)
end_concurso_mc = st.sidebar.number_input("Concurso Final", min_value=1, value=2300)
df_mc = fetch_data_from_api(start_concurso_mc, end_concurso_mc)

st.sidebar.subheader("Parâmetros da Simulação")
num_simulations = st.sidebar.number_input("Número de Simulações (Cenários):", min_value=100, max_value=10000, value=1000, step=100)
games_per_simulation = st.sidebar.number_input("Jogos por Simulação:", min_value=10, max_value=200, value=50)
prizes = {11: 10, 12: 25, 13: 100, 14: 2000, 15: 2000000}

if st.sidebar.button("Executar Simulação de Monte Carlo") and not df_mc.empty:
    st.info("Executando simulação... Isso pode levar um momento.")
    # Taxas de acerto ilustrativas. Em um modelo real, isso seria calculado a partir de um backtest prévio.
    hit_rates = {11: 0.02, 12: 0.008, 13: 0.001, 14: 0.00005, 15: 0.0000001}
    simulation_results = []
    cost_per_simulation = games_per_simulation * 2.5
    for _ in range(num_simulations):
        total_prize = 0
        for _ in range(games_per_simulation):
            roll = np.random.random()
            cumulative_prob = 0
            prize_won = 0
            for points, rate in hit_rates.items():
                cumulative_prob += rate
                if roll < cumulative_prob:
                    prize_won = prizes[points]
                    break
            total_prize += prize_won
        net_profit = total_prize - cost_per_simulation
        simulation_results.append(net_profit)
        
    st.header("📈 Resultados da Simulação")
    results_df = pd.DataFrame(simulation_results, columns=["Lucro/Prejuízo (R$)"])
    col1, col2, col3 = st.columns(3)
    col1.metric("Pior Cenário (5º percentil)", f"R$ {results_df.quantile(0.05).iloc[0]:.2f}")
    col2.metric("Cenário Mediano", f"R$ {results_df.median().iloc[0]:.2f}")
    col3.metric("Melhor Cenário (95º percentil)", f"R$ {results_df.quantile(0.95).iloc[0]:.2f}")
    prob_profit = (results_df > 0).sum() / len(results_df)
    st.metric(f"Probabilidade de Lucro em {games_per_simulation} jogos", f"{float(prob_profit):.2%}")
    st.subheader("Distribuição de Resultados")
    fig = px.histogram(results_df, nbins=50, title="Distribuição dos Lucros/Prejuízos Simulados")
    fig.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Ponto de Equilíbrio")
    st.plotly_chart(fig, use_container_width=True)