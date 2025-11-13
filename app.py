# app.py

import streamlit as st

st.set_page_config(
    page_title="Lotofácil Analyzer Pro",
    page_icon="🎰",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("🎰 Lotofácil Analyzer Pro")
st.markdown("Bem-vindo ao analisador avançado da Lotofácil!")

st.markdown("""
### 📋 Funcionalidades

Este aplicativo foi dividido em seções para facilitar sua análise:

1.  **🎲 Gerar Jogos**: Use dados históricos da Lotofácil (via API) para aplicar diferentes estratégias estatísticas, refinar parâmetros e gerar jogos para os próximos concursos.
2.  **📊 Backtest**: Teste a eficácia de qualquer estratégia em concursos passados. Veja quantos acertos cada método teria tido e analise seu retorno financeiro simulado.
3.  **📈 Análise Estatística**: Explore os dados com gráficos de Business Intelligence, como mapas de calor, análise de tendências e de pares.
4.  **🎰 Verificador de Jogos**: Compare rapidamente seus bilhetes com os resultados oficiais.
5.  **🎲 Simulação Monte Carlo**: Simule milhares de cenários futuros para entender o risco e o potencial de uma estratégia.

### 🚀 Como Começar

Navegue pelas páginas usando o menu à esquerda.
""")

st.info("Dica: Use a página de 'Análise Estatística' para encontrar padrões e, em seguida, valide suas hipóteses no 'Backtest' antes de gerar jogos.")