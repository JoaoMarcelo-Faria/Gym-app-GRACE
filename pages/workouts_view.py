import streamlit as st

## Checa se o usuário está autenticado
if not st.session_state["autenticado"] or "autenticado" not in st.session_state:
    st.error("Usuário não autenticado. Cancelando a execução")
    st.stop()

