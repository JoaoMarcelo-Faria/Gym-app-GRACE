from datetime import datetime
from backend.controllers.workout_controller import WorkoutController
from backend.models.workout import WorkoutModel
from backend.models.exercise import ExerciseModel
from backend.database import db
import streamlit as st
from streamlit_option_menu import option_menu
from utils.workout_forms import create_workout_form, edit_workout_form

## Checa se o usuário está autenticado
if not st.session_state["autenticado"] or "autenticado" not in st.session_state:
    st.error("Usuário não autenticado. Cancelando a execução")
    st.stop()



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
         icons=[":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:"]
    )

    st.divider()        # Formatar a pagina

    ## Buscar o treino do dia selecionado
    workout_controller = WorkoutController(db)
    selected_workout = workout_controller.get_workouts_by_date(weekdays_menu, user_id)

    ## Exibir o Treino e Ações (Card)
    with st.container(border=True):
        if selected_workout is None:
            # Caso não haja treino no dia
            st.subheader(f"Nenhum treino para {weekdays_menu}")

            if st.session_state.get("current_action") == "create" and st.session_state.get("action_day") == weekdays_menu:
                create_workout_form(weekdays_menu, workout_controller, user_id)
                
                # Botão opcional para cancelar a criação e fechar o form
                if st.button("❌ Cancelar", use_container_width=True):
                    del st.session_state["temp_exercises"]
                    if "current_action" in st.session_state: del st.session_state["current_action"]
                    st.rerun()
            else:
                st.write("O que você gostaria de fazer?")
                # Botão de Criar Novo
                if st.button("Criar Novo Treino", type="primary", use_container_width=True):
                    # Guarda no session_state qual dia o usuário quer criar
                    st.session_state["action_day"] = weekdays_menu
                    st.session_state["current_action"] = "create"
                    st.rerun()
                    
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
            if st.session_state.get("current_action") == "edit" and st.session_state.get("action_day") == weekdays_menu:
                edit_workout_form(workout_controller, user_id)

                # Botão opcional para cancelar a criação e fechar o form
                if st.button("❌ Cancelar", use_container_width=True):
                    del st.session_state["temp_exercises"]
                    if "current_action" in st.session_state: del st.session_state["current_action"]
                    st.rerun()
            
            else:
                ## Botões de Ação para Treino Existente (Editar e Deletar)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✏️ Editar Treino", use_container_width=True):
                        st.session_state["workout_to_edit"] = selected_workout
                        st.session_state["current_action"] = "edit"
                        st.session_state["action_day"] = weekdays_menu
                        st.rerun()
                
                with col2:
                    # O botão de deletar executa a ação imediatamente e recarrega a tela
                    if st.button("🗑️ Deletar Treino", use_container_width=True):
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