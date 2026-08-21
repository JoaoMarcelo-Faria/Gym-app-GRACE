import streamlit as st
from backend.controllers.users_controller import UserController
from backend.database import db
from utils.register_forms import register_form
from utils.login_forms import login_form

def render_auth_screen():
    # 1. Gerenciamento de Estado Persistente
    if "login_attempts" not in st.session_state:
        st.session_state["login_attempts"] = 0

    if st.session_state["login_attempts"] >= 3:
        st.error("🔒 Limite de tentativas atingido. Por segurança, reinicie o aplicativo.")
        st.stop()

    st.title("💪 PGApp - Rastreio de Treinos")
    
    # 2. Criação das Abas de Navegação
    tab_login, tab_register = st.tabs(["Entrar", "Cadastrar Novo Usuário"])

    user_controller = UserController(db)

    # ==========================================
    # ABA DE LOGIN
    # ==========================================
    with tab_login:
        login_form(user_controller)

    # ==========================================
    # ABA DE CADASTRO
    # ==========================================
    with tab_register:
        register_form(user_controller)

if __name__ == "__main__":
    render_auth_screen()