from datetime import datetime
import zoneinfo

import streamlit as st

from backend.database import db
from backend.controllers.users_controller import UserController
from backend.controllers.workout_controller import WorkoutController
from backend.controllers.session_controller import SessionController


WEEKDAYS = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]



def load_home_page(user_id: str):
    ## Mensagem de Boas-Vindas
    st.title(f"Olá {st.session_state["logged_user"].get("Name")}, tudo pronto para o treino de hoje?")
    st.subheader("Aqui está o seu plano de treino:")

    ## Definir o fuso horário no Brasil
    timezone_br = zoneinfo.ZoneInfo("America/Sao_Paulo")
    today_br = datetime.now(timezone_br)
    
    ## Descobre o dia da semana atual
    today_index = today_br.weekday()            
    today_name = WEEKDAYS[today_index]

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
            today_str = today_br.strftime("%Y-%m-%d")
            if last_session_data and last_session_data.get("Occurency_date") == today_str:
                already_done_today = True
            # Exibição Condicional de Conclusão
            if already_done_today:
                st.success("✅ Treino de hoje concluído! Excelente trabalho.")
                st.divider()

            
            # Mapear os exercícios da ultima sessão
            history_map = {
                ex_sess.get("Exercise_id"): ex_sess 
                for ex_sess in last_session_data.get("Data_session", [])
            } if last_session_data else {}

            last_date_str = last_session_data.get('Occurency_date') if last_session_data else ""        ## fallback para caso não tenha últimas sessões
            
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
        if st.button("📊 Ver Gráficos", width='stretch'):
            st.switch_page("pages/analytics_view.py")
    with col2:
        if st.button("⚙️ Editar/Criar Treinos", width='stretch'):
            st.switch_page("pages/workouts_view.py")


def main():
    ## Checa se o usuário está autenticado
    if not st.session_state.get("autenticado"):
        st.error("Usuário não autenticado. Cancelando a execução.")
        st.stop()
    
    load_home_page(st.session_state.get("User_id"))

if __name__ == "__main__":
    main()