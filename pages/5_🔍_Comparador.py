# INÍCIO DO ARQUIVO pages/5_🔍_Comparador.py

import streamlit as st
import pandas as pd
import plotly.express as px
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import (
    fetch_data_from_api, estrategia_frequencia, estrategia_atraso,
    estrategia_finais, estrategia_primos, estrategia_fibonacci,
    estrategia_linhas_colunas, estrategia_alpha_envolve,
    generate_games
)

st.set_page_config(page_title="Comparador de Estratégias", page_icon="🔍", layout="wide")

st.title("🔍 Comparador de Estratégias")
st.markdown("Compare o desempenho de duas estratégias lado a lado no mesmo período.")

# --- FUNÇÃO DE BACKTEST SIMPLIFICADA E ROBUSTA ---
def run_simple_backtest(df, strategy_func, num_games_per_draw, num_draws_to_test):
    if len(df) < num_draws_to_test + 1:
        return None, None, None # Retorna None se não houver dados suficientes
        
    prizes = {11: 10, 12: 25, 13: 100, 14: 2000, 15: 2000000}
    total_cost, total_prize = 0, 0
    
    for i in range(num_draws_to_test):
        historical_df = df.iloc[:-(num_draws_to_test - i)]
        target_draw = df.iloc[-(num_draws_to_test - i)]
        target_numbers = set(target_draw[[f'Bola{j}' for j in range(1, 16)]].values)
        
        pool = strategy_func(historical_df.copy())
        generated_games = generate_games(pool, num_games_per_draw)
        
        if not generated_games: # Se a estratégia não gerar jogos, pula
            continue
            
        total_cost += len(generated_games) * 2.5
        for game in generated_games:
            hits = len(set(game) & target_numbers)
            if hits >= 11:
                total_prize += prizes.get(hits, 0)
                
    return total_cost, total_prize, total_prize - total_cost

# --- CONTROLES NA SIDEBAR ---
st.sidebar.header("⚙️ Configurações da Comparação")

# Configurações gerais
st.sidebar.markdown("**Configurações Gerais**")
start_concurso = st.sidebar.number_input("Concurso Inicial", min_value=1, value=2000, key="comp_start")
end_concurso = st.sidebar.number_input("Concurso Final", min_value=1, value=2400, key="comp_end")
df_comp = fetch_data_from_api(start_concurso, end_concurso)
num_games_per_draw = st.sidebar.number_input("Jogos por Concurso:", min_value=1, max_value=100, value=10)
num_draws_to_test = st.sidebar.slider("Concursos para a Comparação:", 10, 200, 50)

# Configurações da Estratégia A
st.sidebar.markdown("---")
st.sidebar.markdown("🔵 **Estratégia A**")
strategy_map = {
    "Frequência": lambda df: estrategia_frequencia(df, top_n=st.session_state.get('top_n_a', 20)),
    "Atraso": lambda df: estrategia_atraso(df, top_n=st.session_state.get('top_n_a_atraso', 15)),
    "Alpha Envolve": lambda df: estrategia_alpha_envolve(df, freq_n=st.session_state.get('alpha_freq_n_a', 15), atraso_n=st.session_state.get('alpha_atraso_n_a', 10))
}
selected_strategy_a = st.sidebar.selectbox("Escolha a Estratégia A:", list(strategy_map.keys()))
if selected_strategy_a == "Frequência": st.session_state.top_n_a = st.sidebar.slider("Top N Frequência A:", 10, 25, 20)
if selected_strategy_a == "Atraso": st.session_state.top_n_a_atraso = st.sidebar.slider("Top N Atraso A:", 5, 25, 15)
if selected_strategy_a == "Alpha Envolve": st.session_state.alpha_freq_n_a = st.sidebar.slider("Alpha Freq N A:", 5, 20, 15); st.session_state.alpha_atraso_n_a = st.sidebar.slider("Alpha Atraso N A:", 5, 20, 10)
strategy_func_a = strategy_map[selected_strategy_a]

# Configurações da Estratégia B
st.sidebar.markdown("---")
st.sidebar.markdown("🔴 **Estratégia B**")
selected_strategy_b = st.sidebar.selectbox("Escolha a Estratégia B:", list(strategy_map.keys()))
if selected_strategy_b == "Frequência": st.session_state.top_n_b = st.sidebar.slider("Top N Frequência B:", 10, 25, 20)
if selected_strategy_b == "Atraso": st.session_state.top_n_b_atraso = st.sidebar.slider("Top N Atraso B:", 5, 25, 15)
if selected_strategy_b == "Alpha Envolve": st.session_state.alpha_freq_n_b = st.sidebar.slider("Alpha Freq N B:", 5, 20, 15); st.session_state.alpha_atraso_n_b = st.sidebar.slider("Alpha Atraso N B:", 5, 20, 10)
strategy_func_b = strategy_map[selected_strategy_b]

run_comparison_btn = st.sidebar.button("▶️ Executar Comparação")

# --- EXIBIÇÃO DOS RESULTADOS ---
if run_comparison_btn and not df_comp.empty:
    st.header("📈 Resultado da Comparação")
    
    with st.spinner("Executando backtest para a Estratégia A..."):
        cost_a, prize_a, profit_a = run_simple_backtest(df_comp, strategy_func_a, num_games_per_draw, num_draws_to_test)
    with st.spinner("Executando backtest para a Estratégia B..."):
        cost_b, prize_b, profit_b = run_simple_backtest(df_comp, strategy_func_b, num_games_per_draw, num_draws_to_test)

    # Verifica se ambos os backtests foram executados com sucesso
    if None not in (cost_a, profit_a, cost_b, profit_b):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"🔵 Estratégia A: {selected_strategy_a}")
            st.metric("Custo Total (R$)", f"R$ {cost_a:.2f}")
            st.metric("Prêmio Estimado (R$)", f"R$ {prize_a:.2f}")
            st.metric("Resultado Líquido (R$)", f"R$ {profit_a:.2f}", delta=f"R$ {profit_a:.2f}")

        with col2:
            st.subheader(f"🔴 Estratégia B: {selected_strategy_b}")
            st.metric("Custo Total (R$)", f"R$ {cost_b:.2f}")
            st.metric("Prêmio Estimado (R$)", f"R$ {prize_b:.2f}")
            st.metric("Resultado Líquido (R$)", f"R$ {profit_b:.2f}", delta=f"R$ {profit_b:.2f}")
        
        # Gráfico comparativo
        comparison_df = pd.DataFrame({
            'Estratégia': [f'Estratégia A ({selected_strategy_a})', f'Estratégia B ({selected_strategy_b})'],
            'Resultado Líquido (R$)': [profit_a, profit_b]
        })
        fig = px.bar(comparison_df, x='Estratégia', y='Resultado Líquido (R$)', title='Comparação de Resultado Líquido', barmode='group')
        fig.update_layout(yaxis_tickprefix='R$ ')
        st.plotly_chart(fig, use_container_width=True)

        # Veredito final
        st.markdown("---")
        if profit_a > profit_b:
            st.success("🔵 **A Estratégia A teve um desempenho superior neste período.**")
        elif profit_b > profit_a:
            st.success("🔴 **A Estratégia B teve um desempenho superior neste período.**")
        else:
            st.info("As estratégias tiveram um desempenho muito similar neste período.")
    else:
        st.error("Não foi possível executar um ou ambos os backtests. Verifique os parâmetros e tente novamente.")

# FIM DO ARQUIVO pages/5_🔍_Comparador.py