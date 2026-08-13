import streamlit as st
from backend.database import db
from backend.controllers.users_controller import UserController
from backend.controllers.workout_controller import WorkoutController
from datetime import datetime
# Configuração opcional para deixar a página mais amigável
st.set_page_config(page_title="Home", page_icon="🏠")

def load_home_page(user_id: str):
    ## Mensagem de Boas-Vindas
    st.title("Olá João, pronto para o treino de hoje?")
    st.write("Aqui está o seu plano de treino:")

    ## Descobre o dia da semana atual
    weekdays = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    today_index = datetime.today().weekday()
    today_name = weekdays[today_index]

    ## Busca o treino no banco de dados
    workout_controller = WorkoutController(db)
    today_workout = workout_controller.get_workouts_by_date(today_name, user_id)

    ## card do treino
    with st.container(border=True):
        if today_workout is None:
            # Cenário: Dia de Descanso
            st.subheader("🎉 Dia de descanso!")
            st.write(f"Você não tem nenhum treino cadastrado para **{today_name}**.")
        else:
            # Cenário: Tem treino hoje
            st.subheader(f"💪 {today_workout.get('Name')}")
            st.caption(f"Dia da semana: {today_name}")
            st.divider() # Linha divisória dentro do card
            
            # Lista os exercícios dentro do card
            exercises = today_workout.get('Order', [])
            if not exercises:
                st.write("Nenhum exercício cadastrado neste treino.")
            else:
                for ex in exercises:
                    st.markdown(f"🏋️ **{ex.get('Name')}**")
                    # Placeholder para o RF05: Quando você terminar o session_controller, 
                    # os dados da última sessão entrarão aqui embaixo:
                    # st.caption("Última sessão: -- kg | -- reps") 

    st.write("") # Dá um pequeno espaçamento na tela
    
    ## BOTÕES DE NAVEGAÇÃO
    col1, col2 = st.columns(2)
    with col1:
        st.page_link("pages/analytics_view.py", label="📊 Ver Gráficos", use_container_width=True)
    with col2:
        st.page_link("pages/workouts_view.py", label="⚙️ Editar/Criar Treinos", use_container_width=True)


def main():
    # Recupera o ID do usuário (Tenta pegar da sessão, se não achar, puxa do secrets)
    user_id = st.session_state.get("User_id")
    if not user_id:
        try:
            user_id = st.secrets["MASTER_USER_ID"]
            st.session_state["User_id"] = user_id
        except KeyError:
            st.error("Erro: Usuário não autenticado e MASTER_USER_ID não encontrado no secrets.toml.")
            st.stop()

    ## Inicializar o usuário único do sistema
    master_user = UserController(db).get_user_by_id(st.secrets["MASTER_USER_ID"])
    st.session_state["User"] = master_user.to_dict()
    load_home_page(user_id)

if __name__ == "__main__":
    main()