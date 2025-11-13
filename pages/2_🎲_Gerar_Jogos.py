# pages/2_🎲_Gerar_Jogos.py

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
    generate_games, get_all_numbers, save_strategy, load_strategies
)

st.set_page_config(page_title="Gerar Jogos", page_icon="🎲", layout="wide")

st.title("🎲 Gerar Jogos Futuros")
st.markdown("Selecione um intervalo de concursos, combine estratégias, refine parâmetros e gere seus jogos.")

# --- CONTROLES NA SIDEBAR ---
st.sidebar.header("⚙️ Configurações de Geração")
start_concurso = st.sidebar.number_input("Concurso Inicial", min_value=1, value=2200)
end_concurso = st.sidebar.number_input("Concurso Final", min_value=1, value=2300)
df = fetch_data_from_api(start_concurso, end_concurso)

if not df.empty:
    st.sidebar.success(f"Carregados {len(df)} concursos com sucesso!")

    strategy_map = {
        "Frequência": estrategia_frequencia, "Atraso": estrategia_atraso,
        "Finais (Último Dígito)": estrategia_finais, "Números Primos": estrategia_primos,
        "Sequência de Fibonacci": estrategia_fibonacci, "Linhas do Cartão": lambda df: estrategia_linhas_colunas(df, mode='row'),
        "Colunas do Cartão": lambda df: estrategia_linhas_colunas(df, mode='col'), "Alpha Envolve (Híbrido)": estrategia_alpha_envolve
    }
    
    selected_strategy_names = st.sidebar.multiselect("Escolha uma ou mais estratégias:", list(strategy_map.keys()), default=["Frequência", "Atraso"])
    
    params = {}
    with st.sidebar.expander("🔧 Refinar Parâmetros das Estratégias"):
        if "Frequência" in selected_strategy_names:
            params['top_n_freq'] = st.slider("Top N Frequência:", 10, 25, 20)
        if "Atraso" in selected_strategy_names:
            params['top_n_atraso'] = st.slider("Top N Atraso:", 5, 25, 15)
        if "Finais (Último Dígito)" in selected_strategy_names:
            params['top_n_finais'] = st.slider("Top N Finais:", 1, 9, 5)
        if "Alpha Envolve (Híbrido)" in selected_strategy_names:
            params['alpha_freq_n'] = st.slider("Alpha Envolve (N Frequência):", 5, 20, 15)
            params['alpha_atraso_n'] = st.slider("Alpha Envolve (N Atraso):", 5, 20, 10)

    num_games = st.sidebar.number_input("Quantidade de Jogos para Gerar:", min_value=1, max_value=50, value=5)
    
    # --- SALVAR ESTRATÉGIAS ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("💾 Minhas Estratégias")
    saved_strategies = load_strategies()
    if saved_strategies:
        strategy_to_load = st.sidebar.selectbox("Carregar Estratégia:", ["Nenhuma"] + list(saved_strategies.keys()))
        if strategy_to_load != "Nenhuma":
            st.sidebar.json(saved_strategies[strategy_to_load])
    
    strategy_name_to_save = st.sidebar.text_input("Nome para Salvar:")
    if st.sidebar.button("💾 Salvar Configuração Atual") and strategy_name_to_save:
        current_config = {'strategies': selected_strategy_names, 'params': params}
        save_strategy(strategy_name_to_save, current_config)
        st.sidebar.success(f"Estratégia '{strategy_name_to_save}' salva!")
        st.rerun()
    
    # --- LÓGICA PRINCIPAL DA PÁGINA ---
    if selected_strategy_names:
        st.header(f"Análise com as Estratégias: {', '.join(selected_strategy_names)}")
        combined_pool = set()
        for strategy_name in selected_strategy_names:
            strategy_func = strategy_map[strategy_name]
            if strategy_name == "Frequência":
                pool_from_strategy = set(strategy_func(df.copy(), top_n=params.get('top_n_freq', 25)))
            elif strategy_name == "Atraso":
                pool_from_strategy = set(strategy_func(df.copy(), top_n=params.get('top_n_atraso', 25)))
            elif strategy_name == "Finais (Último Dígito)":
                pool_from_strategy = set(strategy_func(df.copy(), top_n_finais=params.get('top_n_finais', 5)))
            elif strategy_name == "Alpha Envolve (Híbrido)":
                pool_from_strategy = set(strategy_func(df.copy(), freq_n=params.get('alpha_freq_n', 15), atraso_n=params.get('alpha_atraso_n', 10)))
            else:
                pool_from_strategy = set(strategy_func(df.copy()))
            combined_pool.update(pool_from_strategy)
        pool = sorted(list(combined_pool))
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Pool Combinado de Dezenas")
            st.write(f"Total de {len(pool)} dezenas únicas selecionadas.")
            st.write(pool)
        with col2:
            st.subheader("Frequência Geral (no período)")
            all_numbers_filtered = get_all_numbers(df)
            if all_numbers_filtered:
                freq_series = pd.Series(all_numbers_filtered).value_counts().sort_index()
                fig_freq = px.bar(x=freq_series.index, y=freq_series.values, labels={'x':'Dezena', 'y':'Frequência'}, title='Frequência no Período')
                st.plotly_chart(fig_freq, use_container_width=True)
        
        st.header(f"Gerar {num_games} Jogos")
        if st.button("Gerar Jogos", key="generate_future"):
            generated_games = generate_games(pool, num_games)
            if generated_games:
                st.success(f"{len(generated_games)} jogos gerados com base na combinação de estratégias!")
                st.dataframe(pd.DataFrame(generated_games, columns=[f'Dezena {i+1}' for i in range(15)]))
    else:
        st.info("Por favor, selecione pelo menos uma estratégia para começar.")