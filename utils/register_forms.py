import re
import streamlit as st

from backend.controllers.users_controller import UserController

def validate_password(password: str):
    if len(password) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres."
    
    if not re.search(r"[A-Z]", password):
        return False, "A senha deve conter pelo menos uma letra maiúscula."
    
    if not re.search(r"[a-z]", password):
        return False, "A senha deve conter pelo menos uma letra minúscula."
    
    if not re.search(r"\d", password):
        return False, "A senha deve conter pelo menos um número."
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "A senha deve conter pelo menos um caractere especial (ex: ! @ # $ %)."
        
    return True, ""

def register_form(user_controller: UserController):
    st.title("Crie uma conta")

    with st.form(key="register_form"):
        new_name = st.text_input("Seu Nome Completo")
        new_username = st.text_input("Escolha um nome de usuário")
        new_password = st.text_input("Escolha uma senha", type="password")
        confirm_password = st.text_input("Confirme a senha", type="password")
        
        submit_register = st.form_submit_button("Cadastrar", type="primary", use_container_width=True)

        if submit_register:
            pswrd_ok, error_msg = validate_password(new_password)            
            if not new_name or not new_username or not new_password:
                st.warning("Preencha todos os campos.")

            elif new_password != confirm_password:
                st.error("As senhas não coincidem!")

            elif not pswrd_ok:
                st.warning(error_msg)
            
            else:
                try:
                    # Chama o controller para criar e fazer o hash
                    new_user = user_controller.register_user(new_name, new_username, new_password)
                    st.success("Conta criada com sucesso! Faça seu login.")
                    st.rerun()

                except Exception as e:
                    st.error(str(e))