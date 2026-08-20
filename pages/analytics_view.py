import streamlit as st
import pandas as pd
from backend.database import db
from backend.controllers.session_controller import ExerciseSessionController
from backend.controllers.workout_controller import WorkoutController, ExerciseController

## Checa se o usuário está autenticado
if not st.session_state.get("autenticado"):
    st.error("Usuário não autenticado. Cancelando a execução")
    st.stop()

def map_exercise_id_to_name(user_id: str):
    exercise_controller = ExerciseController(db)
    exercises_list = exercise_controller.get_exercises(user_id)
    unique_exercises = {}
    for exercise in exercises_list:
        ## os campos de exercises_list já estão em formato de dict
        unique_exercises[exercise.get("id")] = exercise.get("Name")
                
    return unique_exercises

def load_analytics_screen():
    user_id = st.session_state.get("User_id")
    if not user_id:
        st.error("Erro: Usuário não encontrado.")
        st.stop()

    st.title("📊 Análise de Rendimento")
    st.write("Acompanhe o seu progresso de carga e esforço ao longo do tempo.")
    st.divider()

    ## Busca os exercícios disponíveis para criar o seletor
    exercises_dict = map_exercise_id_to_name(user_id)

    if not exercises_dict:
        st.info("Você ainda não possui exercícios vinculados aos seus treinos.")
        st.stop()

    ## Cria o seletor de exercícios (RF - Exibição de gráficos)
    # Format_func exibe o Nome (valor do dict), mas a variável guarda o ID (chave)
    selected_ex_id = st.selectbox(
        "Selecione um exercício para analisar:",
        options=list(exercises_dict.keys()),
        format_func=lambda ex_id: exercises_dict[ex_id]
    )

    if selected_ex_id:
        ex_session_controller = ExerciseSessionController(db)
        
        try:
            ## Busca o histórico de sessões deste exercício
            sessions = ex_session_controller.get_exercise_sessions(selected_ex_id, user_id)
            
            # Se a lista voltar vazia ou não houver dados, o bloco 'except' será chamado 
        except Exception:
            # Captura a ausência de sessões e exibe a mensagem amigável solicitada
            st.info(f"Você ainda não registrou nenhuma sessão para o exercício **{exercises_dict[selected_ex_id]}**. Registre uma sessão no seu próximo treino para gerar o gráfico!")
            st.stop()
           
                
        # Preparação dos dados com Pandas
        df = pd.DataFrame(sessions)
        
        # Garante que a data está em formato datetime para ordenação cronológica correta (Eixo X)
        df["Occurency_date"] = pd.to_datetime(df["Occurency_date"])
        df = df.sort_values(by="Occurency_date")
        
        # Converte a data de volta para string formatada para ficar bonito no eixo X
        df["Data"] = df["Occurency_date"].dt.strftime("%d/%m/%Y")
        
        # Renomeia a coluna Effort para o Eixo Y
        df.rename(columns={"Effort": "Esforço"}, inplace=True)

        st.subheader(f"Evolução de Esforço: {exercises_dict[selected_ex_id]}")
        
        # 5. Renderiza o gráfico de barras
        # O Streamlit nativamente já inicia o Eixo Y no 0 quando detecta valores numéricos contínuos
        st.bar_chart(
            data=df,
            x="Data",
            y="Esforço",
            width='stretch',
            color="#FF4B4B" # Cor opcional para combinar com a identidade visual
        )
        
        # Tabela de dados brutos logo abaixo do gráfico (Opcional, mas agrega muito valor)
        with st.expander("Ver dados brutos"):
            st.dataframe(
                df[["Data", "Weight", "Reps", "Esforço"]].rename(
                    columns={"Weight": "Carga (kg)", "Reps": "Repetições"}
                ), 
                hide_index=True,
                width='stretch'
            )

    st.write("")
    if st.button("🔙 Voltar para a Home"):
        st.switch_page("pages/home.py")

if __name__ == "__main__":
    load_analytics_screen()