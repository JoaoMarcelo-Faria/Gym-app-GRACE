import streamlit as st

from backend.controllers.users_controller import UserController

def login_form(user_controller: UserController):
    st.title("Acesse sua conta")
    if "login_attempts" not in st.session_state:
            st.session_state["login_attempts"] = 0

    if st.session_state["login_attempts"] >= 3:
        st.error("Limite de tentativas atingido. Por segurança, reinicie o aplicativo.")
        st.stop()
    
    with st.form(key="login_form"):
        username = st.text_input("Informe seu nome de usuário")
        password = st.text_input("Informe sua senha", type='password')

        submit_btn = st.form_submit_button("Entrar", type="primary", use_container_width=True)
        if submit_btn:
            if not username or not password:
                st.warning("É necessário preencher todos os campos.")
            else:
                try:
                    logged_user = user_controller.login_user(username, password)      # Tenta realizar o login
                    if logged_user:
                        ## Salva o contexto do usuário
                        st.session_state["autenticado"] = True
                        st.session_state["User_id"] = logged_user.id
                        st.session_state["logged_user"] = logged_user.to_dict()

                        st.success("Login realizado com sucesso! Redirecionando...")
                        st.switch_page("pages/home.py")

                except Exception as e:
                    st.session_state["login_attempts"] += 1
                    tentativas_restantes = 3 - st.session_state["login_attempts"] 
                    st.error(str(e))
                    if tentativas_restantes > 0:
                        st.warning(f"Aviso: Você tem mais {tentativas_restantes} tentativa(s).")
                    else:
                        st.rerun() # Força o recarregamento para travar a tela