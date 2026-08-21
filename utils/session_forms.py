from datetime import datetime
import zoneinfo
import streamlit as st

from backend.controllers.session_controller import SessionController
from backend.controllers.workout_controller import WorkoutController
from backend.models.session import ExerciseSessionModel, SessionModel




def create_session_form(session_controller: SessionController, user_id: str, date_workout: dict):
    st.subheader(f"Registrar sessão do treino {date_workout.get('Name')}")

    # Dá a liberdade do usuário passar a data mas limita até o dia de hoje
    timezone_br = zoneinfo.ZoneInfo("America/Sao_Paulo")
    today_br = datetime.now(timezone_br)
    session_date = st.date_input("Data da sessão:", value=today_br.date(), max_value=today_br.date())
    session_date_str = session_date.strftime("%Y-%m-%d")

    st.write("")        ## Espaçamento
    st.markdown("##### Preencha seu desempenho em cada exercício:")

    with st.form(key=f"form_session_{date_workout.get('id')}"):
        input_keys = []     # Lista para salvar os dados a serem salvos no bd

        for i, ex in enumerate(date_workout.get("Order", [])):
            st.markdown(f"**{i + 1}. {ex.get('Name')}**")

            col1, col2 = st.columns(2)

            with col1:
                weight_key = f"weight_{ex.get('id')}_{i}"
                st.number_input("Carga (kg)", min_value=0.0, step=0.5, key=weight_key)
            with col2:
                reps_key = f"reps_{ex.get('id')}_{i}"
                st.number_input("Repetições", min_value=0, step=1, key=reps_key)
            ## Salvar os inputs em weight_key e reps_key permite usar o st.session_state e não perder os dados com a atualização do usuário
            
            input_keys.append({
                "exercise_id": ex.get("id"),
                "weight_key": weight_key,
                "reps_key": reps_key
            })
            st.write("")        ## Espaçamento
        submit_btn = st.form_submit_button("Salvar Sessão", type="primary", width='stretch')

        if submit_btn:
            try:
                ## Monta a lista de exercícios para serem salvos
                exs_session_list = []
                for item in input_keys:
                    ex_session = ExerciseSessionModel(
                        Occurency_date=session_date_str,
                        Exercise_id=item["exercise_id"],
                        Reps=st.session_state[item["reps_key"]],
                        Weight=st.session_state[item["weight_key"]],
                        id="",
                        User_id=user_id
                    )
                    exs_session_list.append(ex_session)

                ## Monta a sessão para ser salva
                new_session = SessionModel(
                    Occurency_date=session_date_str,
                    Workout_id=date_workout.get("id"),
                    User_id=user_id,
                    Data_session=exs_session_list,
                    id=""
                )
                session_controller.create_session(new_session)
                st.success("Sessão salva com sucesso! 🎉")
                st.session_state["current_action"] = None
                st.rerun()

            except Exception as e:
                st.error(f"Erro ao salvar sessão: {e}")



def edit_session_form(workout_data: dict, session_controller: SessionController, user_id: str):
    if user_id != workout_data.get("User_id"):
        st.error("Esse usuário não tem permissão para realizar essa ação")
        st.stop()
    
    st.subheader(f"✏️ Editar Treino: {workout_data.get('Name')}")
    
    # 1. Busca todas as sessões já cadastradas
    try:
        past_sessions = session_controller.get_sessions_by_workout(workout_data.get("id"), user_id)
    except Exception as e:
        st.error(f"Erro ao buscar histórico: {e}")
        return

    # Se a lista estiver vazia, encerra o fluxo e avisa o usuário
    if not past_sessions:
        st.info("Você ainda não possui sessões cadastradas para este treino.")
        return

    # 2. Cria um dicionário para busca O(1) e alimenta o Selectbox
    # Chave = Data (string), Valor = Dicionário da Sessão inteira
    session_map = {sess.get("Occurency_date"): sess for sess in past_sessions}
    
    selected_date = st.selectbox(
        "Selecione a data da sessão que deseja editar:", 
        options=list(session_map.keys())
    )

    if selected_date:
        # Recupera os dados da sessão selecionada no dropdown
        session_to_edit = session_map[selected_date]
        session_id = session_to_edit.get("id")
        
        # Mapeia os exercícios dessa sessão pelo ID do exercício para facilitar a injeção nos inputs
        ex_sessions_map = {
            ex.get("Exercise_id"): ex 
            for ex in session_to_edit.get("Data_session", [])
        }

        st.divider()
        # Dá a opção de apagar essa sessão de treino
        if st.button("🗑️ Deletar Sessão", width='stretch'):
            try:
                session_controller.delete_session(session_id, user_id)
                st.success(f"Sessão deletada com sucesso!")
                # Força a tela a recarregar para mostrar o dia vazio
                st.session_state.pop("current_action", None)
                st.rerun() 
            except Exception as e:
                st.error(f"Erro ao deletar: {e}")

        
        # 3. Inicia o Formulário
        with st.form(key=f"edit_form_{session_id}"):
            input_keys = []
            
            # Itera sobre os exercícios que compõem o treino
            for i, ex in enumerate(workout_data.get("Order", [])):
                ex_id = ex.get("id")
                st.markdown(f"**{i + 1}. {ex.get('Name')}**")
                
                # Busca os valores antigos. Se por acaso não achar (treino alterado), preenche 0
                prev_data = ex_sessions_map.get(ex_id, {})
                prev_weight = float(prev_data.get("Weight", 0.0))
                prev_reps = int(prev_data.get("Reps", 0))
                ex_session_id = prev_data.get("id", "") # ID do ExerciseSession no banco

                col1, col2 = st.columns(2)
                with col1:
                    weight_key = f"edit_weight_{ex_id}_{i}"
                    # O parâmetro 'value' é a mágica que preenche o dado antigo
                    st.number_input("Carga (kg)", min_value=0.0, step=0.5, value=prev_weight, key=weight_key)
                with col2:
                    reps_key = f"edit_reps_{ex_id}_{i}"
                    st.number_input("Repetições", min_value=0, step=1, value=prev_reps, key=reps_key)
                
                # Guardamos a referência e os IDs para o momento do Update
                input_keys.append({
                    "exercise_id": ex_id,
                    "ex_session_id": ex_session_id,
                    "weight_key": weight_key,
                    "reps_key": reps_key
                })
                st.write("")

            submit_btn = st.form_submit_button("💾 Salvar Alterações", type="primary", width='stretch')

            if submit_btn:
                try:
                    exs_session_list = []
                    for item in input_keys:
                        # Reconstrói os objetos de exercício alterados
                        ex_session = ExerciseSessionModel(
                            Occurency_date=selected_date,
                            Exercise_id=item["exercise_id"],
                            Reps=st.session_state[item["reps_key"]],
                            Weight=st.session_state[item["weight_key"]],
                            id=item["ex_session_id"], # Passa o ID antigo para que o update ocorra
                            User_id=user_id
                        )
                        exs_session_list.append(ex_session)

                    # Reconstrói a Sessão Pai
                    updated_session = SessionModel(
                        Occurency_date=selected_date,
                        Workout_id=workout_data.get("id"),
                        User_id=user_id,
                        id=session_id, # Passa o ID antigo da Sessão Pai
                        Data_session=exs_session_list
                    )

                    # Envia tudo para o controller sobrescrever
                    session_controller.update_session(updated_session, user_id, session_id)
                    
                    st.success(f"Sessão do dia {selected_date} atualizada com sucesso! 🎉")
                    
                    # Limpa a memória para voltar à tela principal e recarrega
                    if "current_action" in st.session_state: st.session_state.pop("current_action", None)
                    st.rerun()

                except Exception as e:
                    st.error(f"Erro ao atualizar sessão: {e}")