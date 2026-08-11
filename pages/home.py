import streamlit as st
from backend.database import db
from backend.controllers.users_controller import UserController

## Checa se o usuário está autenticado
if not st.session_state["autenticado"] or "autenticado" not in st.session_state:
    st.error("Usuário não autenticado. Cancelando a execução")
    st.stop()


def load_home_page():
    st.title("Olá João, pronto para o treino de hoje?")
    st.write("Aqui está o seu plano de treino personalizado para hoje:")
    # Aqui você pode adicionar mais elementos da interface do usuário, como gráficos, tabelas, etc.

def main():
    ## Inicializar o usuário único do sistema
    master_user = UserController(db).get_user_by_id("0cQO5ayFUSKLycJcbQKU")
    st.session_state["User"] = master_user
    load_home_page()

if __name__ == "__main__":
    main()