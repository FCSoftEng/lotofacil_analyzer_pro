# pages/6_⚠️_Alertas.py

import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import fetch_latest_contest, fetch_all_results

st.set_page_config(page_title="Alertas Inteligentes", page_icon="⚠️", layout="wide")

st.title("⚠️ Alertas Inteligentes")
st.markdown("Crie alertas que serão disparados quando uma condição for atendida nos resultados mais recentes.")

# Inicializa alertas no session_state se não existirem
if 'alerts' not in st.session_state:
    st.session_state.alerts = []

# --- FORMULÁRIO PARA CRIAR ALERTA ---
with st.expander("➕ Criar Novo Alerta"):
    alert_name = st.text_input("Nome do Alerta (ex: Meu número da sorte)")
    alert_type = st.selectbox("Tipo de Condição", ["Número específico", "Atraso de um número"])
    
    if alert_type == "Número específico":
        alert_number = st.number_input("Número para monitorar:", 1, 25)
        condition = st.selectbox("Condição", ["Foi sorteado", "Não foi sorteado"])
    else: # Atraso
        alert_number = st.number_input("Número para monitorar o atraso:", 1, 25)
        min_delay = st.number_input("Atraso mínimo em concursos:", 1, 100)

    if st.button("Criar Alerta"):
        new_alert = {
            'name': alert_name,
            'type': alert_type,
            'number': alert_number,
            'condition': condition if alert_type == "Número específico" else min_delay
        }
        st.session_state.alerts.append(new_alert)
        st.success(f"Alerta '{alert_name}' criado!")
        st.rerun()

# --- VERIFICAÇÃO DE ALERTAS ---
st.subheader("🔍 Verificação de Alertas")
latest_result = fetch_latest_contest()

if not latest_result.empty:
    latest_draw_numbers = set([latest_result[f'Bola{i}'] for i in range(1, 16)])
    df_all = fetch_all_results()
    
    if st.session_state.alerts:
        for alert in st.session_state.alerts:
            triggered = False
            message = ""
            
            if alert['type'] == "Número específico":
                was_drawn = alert['number'] in latest_draw_numbers
                if (alert['condition'] == "Foi sorteado" and was_drawn) or \
                   (alert['condition'] == "Não foi sorteado" and not was_drawn):
                    triggered = True
                    message = f"O número {alert['number']} {alert['condition'].lower()} no concurso {latest_result['Concurso']}."
            else: # Atraso
                # Lógica para calcular atraso
                last_occurrence_idx = df_all[df_all.isin([alert['number']]).any(axis=1)].index
                if not last_occurrence_idx.empty:
                    delay = len(df_all) - last_occurrence_idx[-1] - 1
                    if delay >= alert['condition']:
                        triggered = True
                        message = f"O número {alert['number']} está atrasado em {delay} concursos (meta: {alert['condition']})."
                else: # Nunca foi sorteado
                    if len(df_all) >= alert['condition']:
                        triggered = True
                        message = f"O número {alert['number']} nunca foi sorteado e está atrasado em {len(df_all)} concursos (meta: {alert['condition']})."

            
            if triggered:
                st.error(f"🚨 **Alerta Disparado: {alert['name']}** - {message}")
            else:
                st.success(f"✅ **{alert['name']}** - Nenhuma condição atendida.")
    else:
        st.info("Nenhum alerta criado ainda.")
else:
    st.error("Não foi possível carregar o último resultado para verificar os alertas.")

# --- LISTA DE ALERTAS SALVOS ---
st.subheader("📋 Seus Alertas Ativos")
if st.session_state.alerts:
    st.dataframe(pd.DataFrame(st.session_state.alerts))
else:
    st.write("Você não possui alertas ativos.")