# INÍCIO DO ARQUIVO utils.py

import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import json
import time
from itertools import combinations

# --- CONSTANTES ---
NUM_DEZENAS = 25
DEZENAS_POR_JOGO = 15
API_URL = "https://loteriascaixa-api.herokuapp.com/api"

# --- FUNÇÕES DE API E CARREGAMENTO DE DADOS (OTIMIZADAS) ---
@st.cache_data(ttl=3600) # Cache por 1 hora
def fetch_all_results():
    """Busca TODOS os resultados da API de uma vez e os cacheia."""
    try:
        with st.spinner("Buscando todos os resultados da Lotofácil..."):
            response = requests.get(f"{API_URL}/lotofacil")
            response.raise_for_status()
            data = response.json()
            
            all_results = []
            for result in data:
                sorted_dezenas = sorted(result['dezenas'])
                row = {
                    'Concurso': int(result['concurso']),
                    'Data': pd.to_datetime(result['data'], format='%d/%m/%Y'),
                }
                for i in range(15):
                    row[f'Bola{i+1}'] = int(sorted_dezenas[i])
                all_results.append(row)
        
            if not all_results:
                st.warning("Nenhum concurso encontrado.")
                return pd.DataFrame()

            df = pd.DataFrame(all_results)
            df.sort_values(by='Concurso', inplace=True)
            return df
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar com a API: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Ocorreu um erro ao processar os dados: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600) # Cache por 10 minutos
def fetch_latest_contest():
    """Busca APENAS o concurso mais recente de forma rápida."""
    df_all = fetch_all_results()
    if not df_all.empty:
        return df_all.iloc[-1]
    return pd.DataFrame()

def fetch_data_from_api(start_concurso, end_concurso):
    """Filtra o DataFrame completo para o intervalo desejado."""
    df_all = fetch_all_results()
    if df_all.empty:
        return pd.DataFrame()
    mask = (df_all['Concurso'] >= start_concurso) & (df_all['Concurso'] <= end_concurso)
    return df_all.loc[mask].copy()

# --- FUNÇÕES AUXILIARES ---
def get_all_numbers(df):
    """Retorna uma lista com todas as dezenas sorteadas em um DataFrame."""
    if df.empty:
        return []
    all_numbers = []
    for i in range(1, 16):
        all_numbers.extend(df[f'Bola{i}'].tolist())
    return sorted(all_numbers)

# --- ESTRATÉGIAS / PROTOCOLOS DE ANÁLISE ---
def estrategia_frequencia(df, top_n=25):
    all_numbers = get_all_numbers(df)
    if not all_numbers: return []
    freq = pd.Series(all_numbers).value_counts().nlargest(top_n)
    return sorted(freq.index.tolist())

def estrategia_atraso(df, top_n=25):
    if df.empty:
        return list(range(1, NUM_DEZENAS + 1))
    delays = {num: 0 for num in range(1, NUM_DEZENAS + 1)}
    for index, row in df.iterrows():
        current_draw = set(row[[f'Bola{i}' for i in range(1, 16)]].values)
        for num in range(1, NUM_DEZENAS + 1):
            if num not in current_draw:
                delays[num] += 1
            else:
                delays[num] = 0
    sorted_by_delay = sorted(delays.items(), key=lambda item: item[1], reverse=True)
    return [num for num, delay in sorted_by_delay[:top_n]]

def estrategia_finais(df, top_n_finais=5):
    all_numbers = get_all_numbers(df)
    if not all_numbers: return []
    finais = [num % 10 for num in all_numbers]
    freq_finais = pd.Series(finais).value_counts().nlargest(top_n_finais)
    selected_finais = freq_finais.index.tolist()
    pool = [num for num in range(1, NUM_DEZENAS + 1) if num % 10 in selected_finais]
    return sorted(pool)

def estrategia_primos(df):
    primos = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    outros = estrategia_frequencia(df, top_n=25 - len(primos))
    return sorted(list(set(primos + outros)))

def estrategia_fibonacci(df):
    fib = [1, 2, 3, 5, 8, 13, 21]
    outros = estrategia_frequencia(df, top_n=25 - len(fib))
    return sorted(list(set(fib + outros)))

def estrategia_linhas_colunas(df, mode='row'):
    grid = {i: [] for i in range(1, 6)}
    for num in range(1, 26):
        row = (num - 1) // 5 + 1
        grid[row].append(num)
    
    all_numbers = get_all_numbers(df)
    if not all_numbers: return []
    freq_grid = {i: 0 for i in range(1, 6)}
    for num in all_numbers:
        row = (num - 1) // 5 + 1
        freq_grid[row] += 1
        
    if mode == 'row':
        most_frequent_row = max(freq_grid, key=freq_grid.get)
        return grid[most_frequent_row]
    else:
        col_grid = {i: [] for i in range(1, 6)}
        for num in range(1, 26):
            col = (num - 1) % 5 + 1
            col_grid[col].append(num)
        freq_col = {i: 0 for i in range(1, 6)}
        for num in all_numbers:
            col = (num - 1) % 5 + 1
            freq_col[col] += 1
        most_frequent_col = max(freq_col, key=freq_col.get)
        return col_grid[most_frequent_col]

def estrategia_alpha_envolve(df, freq_n=15, atraso_n=10):
    freq_nums = set(estrategia_frequencia(df, top_n=freq_n))
    atraso_nums = set(estrategia_atraso(df, top_n=atraso_n))
    final_pool = list(freq_nums.union(atraso_nums))
    return sorted(list(set(final_pool)))[:25]

# --- GERAÇÃO DE JOGOS ---
def generate_games(pool, num_games):
    if len(pool) < 15:
        st.error(f"O pool de números tem apenas {len(pool)} dezenas. Não é possível gerar um jogo de 15.")
        return []
    games = set()
    while len(games) < num_games:
        game = tuple(sorted(np.random.choice(pool, 15, replace=False)))
        games.add(game)
    return [list(game) for game in games]

# --- FUNÇÕES DE SALVAMENTO/CARREGAMENTO DE ESTRATÉGIAS ---
def save_strategy(name, strategy_config):
    if 'saved_strategies' not in st.session_state:
        st.session_state.saved_strategies = {}
    st.session_state.saved_strategies[name] = {
        'config': strategy_config,
        'saved_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def load_strategies():
    return st.session_state.get('saved_strategies', {})

def delete_strategy(name):
    if 'saved_strategies' in st.session_state and name in st.session_state.saved_strategies:
        del st.session_state.saved_strategies[name]

# --- FUNÇÕES DE ANÁLISE AVANÇADA ---
def analyze_positional_frequencies(df):
    pos_freq = {}
    for i in range(1, 16):
        freq = df[f'Bola{i}'].value_counts().sort_index()
        pos_freq[f'Posição {i}'] = {num: freq.get(num, 0) for num in range(1, 26)}
    return pd.DataFrame(pos_freq).fillna(0).astype(int)

def analyze_sum_and_range(df):
    df_analysis = df.copy()
    df_analysis['Soma'] = df_analysis[[f'Bola{i}' for i in range(1, 16)]].sum(axis=1)
    df_analysis['Faixa'] = df_analysis[[f'Bola{i}' for i in range(1, 16)]].max(axis=1) - df_analysis[[f'Bola{i}' for i in range(1, 16)]].min(axis=1)
    return df_analysis[['Soma', 'Faixa']]

def analyze_triplets(df, top_n=20):
    """Analisa as trincas mais frequentes (CUSTOSO)."""
    st.info("Analisando trincas... Isso pode levar um momento.")
    triplet_counts = {}
    for index, row in df.iterrows():
        draw_numbers = sorted(row[[f'Bola{i}' for i in range(1, 16)]].values)
        for triplet in combinations(draw_numbers, 3):
            triplet_counts[triplet] = triplet_counts.get(triplet, 0) + 1
    sorted_triplets = sorted(triplet_counts.items(), key=lambda item: item[1], reverse=True)
    return sorted_triplets[:top_n]

def analyze_quads(df, top_n=20):
    """Analisa as quadras mais frequentes (MUITO CUSTOSO)."""
    st.warning("Analisando quadras... Isso pode levar bastante tempo.")
    quad_counts = {}
    for index, row in df.iterrows():
        draw_numbers = sorted(row[[f'Bola{i}' for i in range(1, 16)]].values)
        for quad in combinations(draw_numbers, 4):
            quad_counts[quad] = quad_counts.get(quad, 0) + 1
    sorted_quads = sorted(quad_counts.items(), key=lambda item: item[1], reverse=True)
    return sorted_quads[:top_n]

# FIM DO ARQUIVO utils.py