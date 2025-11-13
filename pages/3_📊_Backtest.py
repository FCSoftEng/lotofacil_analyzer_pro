# pages/3_📊_Backtest.py

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import (
    fetch_data_from_api, estrategia_frequencia, estrategia_atraso,
    estrategia_finais, estrategia_primos, estrategia_fibonacci,
    estrategia_linhas_colunas, estrategia_alpha_envolve,
    generate_games
)

st.set_page_config(page_title="Backtest", page_icon="📊", layout="wide")

st.title("📊 Backtest de Estratégias")
st.markdown("Teste o desempenho de combinações de estratégias em concursos passados.")

st.sidebar.header("⚙️ Configurações de Backtest")
start_concurso_bt = st.sidebar.number_input("Concurso Inicial", min_value=1, value=2000, key="bt_start")
end_concurso_bt = st.sidebar.number_input("Concurso Final", min_value=1, value=2200, key="bt_end")
df_bt = fetch_data_from_api(start_concurso_bt, end_concurso_bt)

if not df_bt.empty:
    st.sidebar.success(f"Carregados {len(df_bt)} concursos para o backtest!")
    
    strategy_map = {
        "Frequência": estrategia_frequencia, "Atraso": estrategia_atraso,
        "Finais (Último Dígito)": estrategia_finais, "Números Primos": estrategia_primos,
        "Sequência de Fibonacci": estrategia_fibonacci, "Linhas do Cartão": lambda df: estrategia_linhas_colunas(df, mode='row'),
        "Colunas do Cartão": lambda df: estrategia_linhas_colunas(df, mode='col'), "Alpha Envolve (Híbrido)": estrategia_alpha_envolve
    }
    
    selected_strategy_names_bt = st.sidebar.multiselect("Escolha as estratégias para o backtest:", list(strategy_map.keys()), default=["Frequência"])
    
    params_bt = {}
    with st.sidebar.expander("🔧 Refinar Parâmetros do Backtest"):
        if "Frequência" in selected_strategy_names_bt:
            params_bt['top_n_freq'] = st.slider("Top N Frequência:", 10, 25, 20, key="bt_freq")
        if "Atraso" in selected_strategy_names_bt:
            params_bt['top_n_atraso'] = st.slider("Top N Atraso:", 5, 25, 15, key="bt_atraso")
        if "Alpha Envolve (Híbrido)" in selected_strategy_names_bt:
            params_bt['alpha_freq_n'] = st.slider("Alpha Envolve (N Frequência):", 5, 20, 15, key="bt_alpha_freq")
            params_bt['alpha_atraso_n'] = st.slider("Alpha Envolve (N Atraso):", 5, 20, 10, key="bt_alpha_atraso")

    num_games_per_draw = st.sidebar.number_input("Jogos por Concurso:", min_value=1, max_value=100, value=10)
    max_draws_for_test = len(df_bt) - 1
    num_draws_to_test = st.sidebar.slider("Quantos concursos analisar:", 10, max_draws_for_test, min(100, max_draws_for_test))
    run_backtest_btn = st.sidebar.button("Executar Backtest", key="run_bt")

    def run_backtest(df, strategy_names, params, num_games_per_draw, num_draws_to_test):
        if len(df) < num_draws_to_test + 1:
            st.error(f"Não há dados suficientes. Necessário pelo menos {num_draws_to_test + 1} concursos.")
            return {}, 0, 0
        st.info(f"Executando backtest para os últimos {num_draws_to_test} concursos...")
        results = {f"{i} Pontos": 0 for i in range(11, 16)}
        total_cost, total_prize = 0, 0
        prizes = {11: 10, 12: 25, 13: 100, 14: 2000, 15: 2000000}
        
        for i in range(num_draws_to_test):
            historical_df = df.iloc[:-(num_draws_to_test - i)]
            target_draw = df.iloc[-(num_draws_to_test - i)]
            target_numbers = set(target_draw[[f'Bola{j}' for j in range(1, 16)]].values)
            
            combined_pool = set()
            for strategy_name in strategy_names:
                strategy_func = strategy_map[strategy_name]
                if strategy_name == "Frequência":
                    pool_from_strategy = set(strategy_func(historical_df.copy(), top_n=params.get('top_n_freq', 25)))
                elif strategy_name == "Atraso":
                    pool_from_strategy = set(strategy_func(historical_df.copy(), top_n=params.get('top_n_atraso', 25)))
                elif strategy_name == "Alpha Envolve (Híbrido)":
                    pool_from_strategy = set(strategy_func(historical_df.copy(), freq_n=params.get('alpha_freq_n', 15), atraso_n=params.get('alpha_atraso_n', 10)))
                else:
                    pool_from_strategy = set(strategy_func(historical_df.copy()))
                combined_pool.update(pool_from_strategy)
            pool = sorted(list(combined_pool))
            
            generated_games = generate_games(pool, num_games_per_draw)
            total_cost += len(generated_games) * 2.5
            for game in generated_games:
                hits = len(set(game) & target_numbers)
                if hits >= 11:
                    results[f"{hits} Pontos"] += 1
                    total_prize += prizes.get(hits, 0)
        return results, total_cost, total_prize

    if run_backtest_btn and selected_strategy_names_bt:
        st.header("📈 Resultados do Backtest")
        results, cost, prize = run_backtest(df_bt, selected_strategy_names_bt, params_bt, num_games_per_draw, num_draws_to_test)
        if results:
            col1, col2, col3 = st.columns(3)
            col1.metric("Custo Total (R$)", f"R$ {cost:.2f}")
            col2.metric("Prêmio Estimado (R$)", f"R$ {prize:.2f}")
            col3.metric("Resultado Líquido (R$)", f"R$ {prize - cost:.2f}", delta=f"R$ {prize - cost:.2f}")
            st.subheader("Distribuição de Acertos")
            if not any(results.values()):
                st.warning("Nenhuma premiação encontrada no período testado.")
            else:
                results_df = pd.DataFrame(list(results.items()), columns=['Faixa de Acerto', 'Vezes'])
                fig_results = px.bar(results_df, x='Faixa de Acerto', y='Vezes', title='Quantidade de Prêmios por Faixa')
                st.plotly_chart(fig_results, use_container_width=True)