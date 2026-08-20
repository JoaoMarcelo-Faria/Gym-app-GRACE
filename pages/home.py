import streamlit as st
from backend.database import db
from backend.controllers.users_controller import UserController
from backend.controllers.workout_controller import WorkoutController
from backend.controllers.session_controller import SessionController
from datetime import datetime
# Configuração opcional para deixar a página mais amigável
st.set_page_config(page_title="Home", page_icon="🏠")

def load_home_page(user_id: str):
    ## Mensagem de Boas-Vindas
    st.title("Olá João, pronto para o treino de hoje?")
    st.subheader("Aqui está o seu plano de treino:")

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
            st.subheader("Nenhum treino cadastrado")
            st.write(f"Você não tem nenhum treino cadastrado para **{today_name}**.")
            st.write("Clique no botão abaixo para cadastrar um treino para hoje.")
        
        elif today_workout.get("Name") == "Descanso":
            # Cenário: Dia de Descanso
            st.subheader("🎉 Dia de descanso!")
            st.write(f"Hoje não tem treino. Certifique-se de descansar, ingerir bastante água e dormir 8 horas.")
        
        else:
            # Cenário: Tem treino hoje
            st.subheader(f"💪 {today_workout.get('Name')}")
            st.text(f"Dia da semana: {today_name}")
            # st.divider() # Linha divisória dentro do card
            st.text("")

            # Buscar a última sessão desse treino
            session_controller = SessionController(db)
            last_session_data = session_controller.get_last_session(today_workout.get("id"), user_id)

            # Verificar se já foi feita uma sessão hoje
            already_done_today = False
            today_str = datetime.today().strftime("%Y-%m-%d")
            if last_session_data.get("Occurency_Date") == today_str:
                already_done_today = True
            # Exibição Condicional de Conclusão
            if already_done_today:
                st.success("✅ Treino de hoje concluído! Excelente trabalho.")
                st.divider()

            
            # Mapear os exercícios da ultima sessão
            history_map = {}
            last_date_str = ""
            if last_session_data:
                last_date_str = last_session_data.get('Occurency_date', '')
                for ex_sess in last_session_data.get("Data_session", []):
                    history_map[ex_sess.get("Exercise_id")] = ex_sess
            
            # Lista os exercícios dentro do card
            exercises = today_workout.get('Order', [])
            if not exercises:
                st.write("Nenhum exercício cadastrado neste treino.")
            else:
                for ex in exercises:
                    ex_id = ex.get("id")
                    st.markdown(f"🏋️ **{ex.get('Name')}**")
                    past_data = history_map.get(ex_id)
                    
                    if past_data:
                        # Uso correto de aspas simples nas chaves dentro da F-string
                        weight = past_data.get('Weight')
                        reps = past_data.get('Reps')
                        st.caption(f"Última sessão ({last_date_str}): {weight}kg | {reps} reps")
                    else:
                        st.caption("Última sessão: Sem registros anteriores") 

    st.write("") # Dá um pequeno espaçamento na tela
    
    ## BOTÕES DE NAVEGAÇÃO
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Ver Gráficos", use_container_width=True):
            st.switch_page("pages/analytics_view.py")
    with col2:
        if st.button("⚙️ Editar/Criar Treinos", use_container_width=True):
            st.switch_page("pages/workouts_view.py")


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