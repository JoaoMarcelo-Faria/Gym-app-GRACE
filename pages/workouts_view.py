from datetime import datetime
import streamlit as st
from streamlit_option_menu import option_menu

from backend.controllers.workout_controller import WorkoutController
from backend.controllers.session_controller import SessionController
from backend.models.workout import WorkoutModel
from backend.models.exercise import ExerciseModel
from backend.database import db
from utils.workout_forms import create_workout_form, edit_workout_form
from utils.session_forms import create_session_form, edit_session_form



## Checa se o usuário está autenticado
if not st.session_state.get("autenticado"):
    st.error("Usuário não autenticado. Cancelando a execução")
    st.stop()

def update_global_states(action: str, day: str, workout: dict = None):
    if workout: st.session_state["workout_to_session"] = workout
    if action: st.session_state["current_action"] = action
    if day: st.session_state["action_day"] = day
    st.rerun()

def render_cancel_button():
    if st.button("❌ Cancelar Operação", width='stretch'):
        st.session_state.pop("current_action", None)
        st.session_state.pop("action_day", None)
        st.session_state.pop("temp_exercises", None)
        st.rerun()

def render_empty_days(day: str, workout_controller: WorkoutController, user_id: str, is_rest_day: bool):
    st.write("O que você gostaria de fazer?")
    if not is_rest_day:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Criar Novo Treino", type="primary", width='stretch'):
                update_global_states("create", day)
        with col2:
            if st.button("😴 Cadastrar Descanso", width='stretch'):
                workout_controller.create_rest_day(day, user_id)
                st.success("Dia de descanso cadastrado com sucesso!")
                st.rerun()
    else:
        if st.button("➕ Criar Novo Treino", type="primary", width='stretch'):
            update_global_states("create", day)


def load_workout_screen():
    # Recupera o ID do usuário (Tenta pegar da sessão, se não achar, puxa do secrets)
    user_id = st.session_state.get("User_id")
    if not user_id:
        try:
            user_id = st.secrets["MASTER_USER_ID"]
            st.session_state["User_id"] = user_id
        except KeyError:
            st.error("Erro: Usuário não autenticado e MASTER_USER_ID não encontrado no secrets.toml.")
            st.stop()

    st.title("⚙️ Gerenciar Treinos")
    st.subheader("Selecione um dia da semana para ver, editar ou criar treinos.")

    ## Mostrar o menu de opções de dias da semana
    today_index = datetime.today().weekday()
    weekdays_menu = option_menu(
         menu_title= "Selecione o dia da semana para ver o exercício",
         options=["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"],
         default_index=today_index,
         orientation="horizontal",
         menu_icon=":calendar:",
         styles={
             "container": {"paddding": "5px", "background-color": "#0a0a0f", "border": "1px solid #ff6b00"}
         },
         icons=[":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:"]
    )

    st.divider()        # Formatar a pagina

    ## controllers a serem usados
    workout_controller = WorkoutController(db)
    selected_workout = workout_controller.get_workouts_by_date(weekdays_menu, user_id)
    session_controller = SessionController(db)

    ## Exibir o Treino e Ações (Card)
    with st.container(border=True):
        current_action = st.session_state.get("current_action")
        action_day = st.session_state.get("action_day")

        ## Fluxo de criação de treino
        if st.session_state.get("current_action") == "create" and st.session_state.get("action_day") == weekdays_menu:
            create_workout_form(weekdays_menu, workout_controller, user_id)
            render_cancel_button()

        ## Fluxo de dia vazio ou de descanso
        elif selected_workout is None or selected_workout.get("Name") == "Descanso":
            if selected_workout is None:
                st.subheader(f"Nenhum treino para {weekdays_menu}")
                render_empty_days(weekdays_menu, workout_controller, user_id, False)
            else:
                st.subheader("🎉 Hoje é dia de descanso!")
                st.text("Certifique-se de beber bastante água e dormir por 8 horas.")
                render_empty_days(weekdays_menu, workout_controller, user_id, True)

        ## Fluxo dos formulários específicos
        elif current_action == "edit" and action_day == weekdays_menu:
            edit_workout_form(workout_controller, user_id)
            render_cancel_button()

        elif current_action == "create_session" and action_day == weekdays_menu:
            create_session_form(session_controller, user_id, selected_workout)
            render_cancel_button()

        elif current_action == "edit_session" and action_day == weekdays_menu:
            edit_session_form(selected_workout, session_controller, user_id)
            render_cancel_button()


        else:
            # Caso haja treino cadastrado
            st.subheader(f"💪 {selected_workout.get('Name')}")
            
            # Lista os exercícios
            exercises = selected_workout.get('Order', [])
            if exercises:
                for ex in exercises:
                    st.markdown(f"🏋️ **{ex.get('Name')}**")
            else:
                st.write("Sem exercícios cadastrados.")
            
            st.write("") # Espaçamento

            ## Botões de Ação para Treino Existente (Editar e Deletar)
            col1, col2 = st.columns(2)
            with col1:
                ## Botão de cadastrar uma sessão de treino
                if st.button("Cadastrar sessão de treino", width='stretch', type="primary"):
                    update_global_states("create_session", weekdays_menu, selected_workout)

                
                if st.button("✏️ Editar Treino", width='stretch'):
                    update_global_states("edit", weekdays_menu, selected_workout)
            
            with col2:
                if st.button("Editar sessões de treino", width='stretch'):
                    update_global_states("edit_session", weekdays_menu, selected_workout)

                # O botão de deletar executa a ação imediatamente e recarrega a tela
                if st.button("🗑️ Deletar Treino", width='stretch'):
                    workout_id = selected_workout.get('id')
                    if workout_id:
                        try:
                            # Chama o controller criado anteriormente (RF03)
                            workout_controller.delete_workout(workout_id, user_id)
                            st.success(f"Treino '{selected_workout.get('Name')}' deletado com sucesso!")
                            # Força a tela a recarregar para mostrar o dia vazio
                            st.rerun() 
                        except Exception as e:
                            st.error(f"Erro ao deletar: {e}")
                    else:
                        st.error("Não foi possível encontrar o ID do treino para deleção.")




    # Botão para voltar à Home de forma nativa
    st.write("")
    if st.button("🔙 Voltar para a Home", type="primary"):
        st.switch_page("pages/home.py")

if __name__ == "__main__":
    load_workout_screen()