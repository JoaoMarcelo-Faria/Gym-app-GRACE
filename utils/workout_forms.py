from backend.controllers.workout_controller import WorkoutController
from backend.models.workout import WorkoutModel
from backend.models.exercise import ExerciseModel
import streamlit as st



def create_workout_form(weekday: str, workout_controller: WorkoutController, user_id: str):
    if "temp_exercises" not in st.session_state:        # cria uma lista temporaria dos exercicios
        st.session_state["temp_exercises"] = []

    if "input_key_create_counter" not in st.session_state:      # permite que o campo de input seja limpo a cada interação com o usuário
        st.session_state["input_key_create_counter"] = 0

    
    name = st.text_input("Informe o nome do treino:")
    st.divider()

    ## Mostrar os exercícios do treino
    st.subheader("Exercícios do treino")
    for i, ex_name in enumerate(st.session_state["temp_exercises"]):
        st.markdown(f"{i + 1}. 🏋️ {ex_name}")

    
    ## Inputs para adicionar um novo exercício
    col1, col2 = st.columns([2, 1])
    with col1:
        new_ex_name = st.text_input("Nome do novo exercício:", key=f"new_exercise_input_{st.session_state["input_key_create_counter"]}")
        new_ex_name = new_ex_name.strip().capitalize()
    with col2:
        # Dá um alinhamento visual para o botão ficar ao lado do input
        st.write("") 
        st.write("")
        if st.button("Adicionar à lista", use_container_width=True):
            if new_ex_name and new_ex_name not in st.session_state.get("temp_exercises"):
                # Salva o nome na lista temporária e recarrega a tela
                st.session_state["temp_exercises"].append(new_ex_name)
                st.session_state["input_key_create_counter"] += 1       # altera a chave do campo de input para ser limpa
                st.rerun()
            else:
                st.warning("Digite um nome para o exercício.")
    st.divider()
    ## Botão final para salvar o treino completo no banco
    if st.button("Finalizar e Salvar Treino", type="primary", use_container_width=True):
        if not name:
            st.error("O treino precisa de um nome!")
        elif len(st.session_state["temp_exercises"]) == 0:
            st.error("Adicione pelo menos um exercício ao treino!")
        else:
            # Converte a lista de strings para a lista de objetos ExerciseModel
            exercises_list = [
                ExerciseModel(id="", name=ex, user_id=user_id) 
                for ex in st.session_state["temp_exercises"]
            ]
            
            new_workout = WorkoutModel(
                Name=name,
                Weekday=weekday,
                id="",
                user_id=user_id,
                exs_order=exercises_list
            )
            
            try:
                # Tenta criar o treino
                workout_controller.create_workout(new_workout)
                st.success("Treino salvo com sucesso!")
                
                # Limpa a memória temporária e sai do modo de criação
                del st.session_state["temp_exercises"]
                del st.session_state["current_action"]
                del st.session_state["action_day"]
                st.rerun() # Atualiza a tela para mostrar o treino criado no Card
                
            except Exception as e:
                # Captura os erros que criamos nas regras de negócio (ex: Dia já possui treino)
                st.error(f"Erro ao salvar: {e}")


def edit_workout_form(workout_controller: WorkoutController, user_id: str):
    # Recupera o dicionário do treino que foi salvo no botão "Editar"
    workout_data = st.session_state.get("workout_to_session")
    if not workout_data:
        st.error("Erro: Nenhum treino selecionado para edição.")
        return

    if "input_key_edit_counter" not in st.session_state:      # permite que o campo de input seja limpo a cada interação com o usuário
        st.session_state["input_key_edit_counter"] = 0
    
    workout_id = workout_data.get("id")
    weekday = workout_data.get("Weekday")

    # Carrega os exercícios antigos para a lista temporária
    if "temp_exercises" not in st.session_state:
        # Pega a lista "Order" do banco e extrai apenas o "Name" de cada um
        st.session_state["temp_exercises"] = [ex.get("Name") for ex in workout_data.get("Order", [])]

    # Mudança de nome
    name = st.text_input("Nome do treino:", value=workout_data.get("Name"))
    
    st.write("")
    st.subheader("Exercícios do Treino")

    # LISTAGEM E REMOÇÃO
    # Usamos o enumerate para ter o índice (i).
    for i, ex_name in enumerate(st.session_state["temp_exercises"]):
        col_ex, col_del = st.columns([4, 1])
        with col_ex:
            st.markdown(f"{i + 1}. 🏋️ **{ex_name}**")
        with col_del:
            # A chave aqui precisa ser única para cada botão renderizado
            if st.button("❌ Remover", key=f"del_ex_{i}"):
                # Remove o item da lista e atualiza a tela
                st.session_state["temp_exercises"].pop(i)
                st.rerun()

    # ADIÇÃO DE NOVOS EXERCÍCIOS
    col1, col2 = st.columns([2, 1])
    with col1:
        new_ex_name = st.text_input("Nome do novo exercício:", key=f"edit_new_ex_input_{st.session_state["input_key_edit_counter"]}")
        new_ex_name = new_ex_name.strip().capitalize()
    with col2:
        st.write("") 
        st.write("")
        if st.button("Adicionar à lista", key="add_ex_edit_btn", use_container_width=True):
            if new_ex_name and new_ex_name not in st.session_state["temp_exercises"]:
                st.session_state["temp_exercises"].append(new_ex_name)
                st.session_state["input_key_edit_counter"] += 1
                st.rerun()
            else:
                st.warning("Digite um nome para o exercício.")

    st.divider()
    
    # SALVAR ALTERAÇÕES
    if st.button("Salvar Alterações", type="primary", use_container_width=True):
        if not name:
            # Mantem o mesmo nome se não enviar outro
            name = workout_data.get("Name")
        elif len(st.session_state["temp_exercises"]) == 0:
            st.error("O treino precisa ter pelo menos um exercício!")
        else:
            # Converte as strings de volta para o ExerciseModel
            exercises_list = [
                ExerciseModel(id="", name=ex, user_id=user_id) 
                for ex in st.session_state["temp_exercises"]
            ]
            
            # Monta o objeto atualizado passando o ID do treino existente
            updated_workout = WorkoutModel(
                Name=name,
                Weekday=weekday,
                id=workout_id,
                user_id=user_id,
                exs_order=exercises_list
            )
            
            try:
                # Dispara a requisição de update
                workout_controller.update_workout(workout_id, updated_workout, user_id)
                st.success("Treino atualizado com sucesso!")
                
                # Limpa TODA a sujeira da sessão e recarrega a tela principal
                del st.session_state["temp_exercises"]
                del st.session_state["current_action"]
                del st.session_state["workout_to_edit"]
                del st.session_state["action_day"]
                st.rerun()
                
            except Exception as e:
                st.error(f"Erro ao atualizar: {e}")