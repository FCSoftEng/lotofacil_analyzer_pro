# pages/6_🎰_Verificador_Jogos.py

import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import fetch_data_from_api

st.set_page_config(page_title="Verificador de Jogos", page_icon="🎰", layout="wide")

st.title("🎰 Verificador de Jogos")
st.markdown("Insira os números do seu bilhete e compare com o resultado de qualquer concurso.")

df_all = fetch_data_from_api(1, 3000)

if not df_all.empty:
    st.subheader("Seu Jogo")
    user_input = st.text_area("Digite seus 15 números (separados por vírgula, espaço ou quebra de linha):", "01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15")
    st.subheader("Concurso para Comparação")
    concursos_map = df_all.set_index('Concurso')['Data'].dt.strftime('%d/%m/%Y').to_dict()
    selected_concurso = st.selectbox("Escolha o concurso:", sorted(concursos_map.keys(), reverse=True), format_func=lambda x: f"Concurso {x} ({concursos_map[x]})")

    if st.button("Verificar Jogo"):
        try:
            user_numbers_str = user_input.replace('\n', ',').replace(' ', ',')
            user_numbers = {int(num.strip()) for num in user_numbers_str.split(',') if num.strip().isdigit()}
            if len(user_numbers) != 15:
                st.error("Por favor, insira exatamente 15 números válidos.")
            else:
                result_row = df_all[df_all['Concurso'] == selected_concurso].iloc[0]
                drawn_numbers = set(result_row[[f'Bola{i}' for i in range(1, 16)]].values)
                hits = sorted(list(user_numbers & drawn_numbers))
                num_hits = len(hits)
                st.markdown("---")
                st.subheader("📊 Resultado da Verificação")
                col1, col2, col3 = st.columns(3)
                col1.metric("Seus Números", len(user_numbers))
                col2.metric("Números Sorteados", len(drawn_numbers))
                col3.metric("Seus Acertos", num_hits)
                st.markdown(f"**Você acertou {num_hits} ponto(s)!**")
                if num_hits > 10:
                    st.success(f"Parabéns! Os números acertados foram: {', '.join(map(str, hits))}")
                else:
                    st.info(f"Os números acertados foram: {', '.join(map(str, hits))}")
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar seu jogo: {e}")