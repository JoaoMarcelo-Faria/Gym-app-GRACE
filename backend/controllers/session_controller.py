from backend.models.session import SessionModel, ExerciseSessionModel
from google.cloud import firestore

class ExerciseSessionController():
    def __init__(self, db_client: firestore.Client):
        self.db = db_client
        self.collection = self.db.collection("Exercise_Session")

    def create_exercise_session(self, data: ExerciseSessionModel):
        ## Realiza a verificação da existência de um exercício no banco
        exist_exercise_id = self.db.collection("Exercise").document(data.Exercise_id).get()
        if not exist_exercise_id.exists:
            raise ValueError("Não existe exercício cadastrado com esse id.")

        new_doc_ref = self.collection.document()
        data.id = new_doc_ref.id
        new_doc_ref.set(data.to_dict())

        return data


    ## Método para auxiliar na RF04 - gerar gráficos para um determinado exercício
    def get_exercise_sessions(self, exercise_id: str, user_id: str):
        sessions_stream = self.collection.where("Exercise_id", "==", exercise_id).where("User_id", "==", user_id).stream()
        sessions = [session.to_dict() for session in sessions_stream]

        if len(sessions) == 0:
            raise ValueError("Não foi possível obter as sessões deste exercício")
        

        return sessions

    def delete_exercise_session(self, session_id: str, user_id: str):
        exercise_session = self.collection.document(session_id).get()
        if not exercise_session.exists:
            raise ValueError("Não existe sessão com esse id")

        ## verificação de segurança
        data = exercise_session.to_dict()
        if data.get("User_id") != user_id:
            raise PermissionError("Esse usuário não é permitido a realizar essa ação")

        self.collection.document(session_id).delete()
        return True

    def update_exercise_session(self, new_session: ExerciseSessionModel, user_id: str, session_id: str):
        ## Validar as entradas
        # id da sessão no banco
        older_session = self.collection.document(session_id).get()
        if not older_session.exists:
            raise ValueError("Não existe sessão com esse id")

        # validação de segurança
        if older_session.to_dict().get("User_id") != user_id:
            raise PermissionError("Esse usuário não é permitido a realizar essa ação")

        ## Tudo está validado
        data = new_session.to_dict()
        self.collection.document(session_id).update(data)

        return new_session


class SessionController():
    def __init__(self, db_client: firestore.Client):
        self.db = db_client
        self.collection = self.db.collection("Session")
        self.exercise_session_controller = ExerciseSessionController(db_client)


    def create_session(self, data: SessionModel):
        ## Validar os dados de entrada
        # Existência do treino que tera uma sessão registrada
        exist_workout = self.db.collection("Workout").document(data.Workout_id).get()
        if not exist_workout.exists:
            raise ValueError("O treino solicitado não existe")

        # Existência do usuário
        exist_user = self.db.collection("User").document(data.User_id).get()
        if not exist_user.exists:
            raise ValueError("O usuário solicitado não existe")

        # Se já ocorreu a criação de uma sessão no dia
        session_already = self.collection\
            .where("Occurency_date", "==", data.Occurency_date)\
            .where("User_id", "==", data.User_id).limit(1).get()
        if len(session_already) != 0:
            raise ValueError("Não é possível adicionar outra sessão no mesmo dia")

        ## Criação das sessões dos exercícios
        exs_list = []
        for ex_session in data.Data_session:
            ex_session.Occurency_date = data.Occurency_date
            ex_session.User_id = data.User_id
            self.exercise_session_controller.create_exercise_session(ex_session)
            exs_list.append(ex_session)

        data.Data_session = exs_list

        new_doc_ref = self.collection.document()
        data.id = new_doc_ref.id
        new_doc_ref.set(data.to_dict())

        return data


    def get_last_session(self, workout_id: str, user_id: str):
        # Não há necessidade de validação de treino pois se não houver, o retorno será vazio e tratado no frontend
        data = self.collection.where("Workout_id", "==", workout_id).where("User_id", "==", user_id).order_by("Occurency_date", direction=firestore.Query.DESCENDING).limit(1).get()
        if len(data) == 0:
            return None

        return data[0].to_dict()

    def get_sessions_by_workout(self, workout_id: str, user_id: str):
        # Validar a existência de um treino 
        workout = self.db.collection("Workout").document(workout_id).get()
        if not workout.exists:
            raise ValueError("O treino solicitado não existe")

        # Busca todas as sessões de um treino específico para o usuário
        sessions = self.collection \
            .where("Workout_id", "==", workout_id) \
            .where("User_id", "==", user_id) \
            .order_by("Occurency_date", direction=firestore.Query.DESCENDING) \
            .stream()
        response = [session.to_dict() for session in sessions]
        if len(response) == 0:
            return None         # Se não houverem sessões cadastradas, não tem problema só não retorna nada

        return response

    def delete_session(self, session_id: str, user_id: str):
        ## Verificações
        # Existencia da sessão no banco
        session = self.collection.document(session_id).get()
        if not session.exists:
            raise ValueError("Não existe sessão com esse id")

        ## verificação de segurança
        data = session.to_dict()
        if data.get("User_id") != user_id:
            raise PermissionError("Esse usuário não é permitido a realizar essa ação")

        for ex in data.get("Data_session", []):
            ex_id = ex.get("id")
            if ex_id:
                self.exercise_session_controller.delete_exercise_session(ex_id, user_id)

        self.collection.document(session_id).delete()
        return True

    def update_session(self, new_session: SessionModel, user_id: str, session_id: str):
        older_session = self.collection.document(session_id).get()
        if not older_session.exists:
            raise ValueError("Não existe sessão de treino com esse id")

        if older_session.to_dict().get("User_id") != user_id:
            raise PermissionError("Esse usuário não é permitido realizar essa ação")

        new_exs_list = []
        for new_exercise in new_session.Data_session:
            self.exercise_session_controller.update_exercise_session(new_exercise, user_id, new_exercise.id)
            new_exs_list.append(new_exercise)
        new_session.Data_session = new_exs_list

        data = new_session.to_dict()
        self.collection.document(session_id).update(data)

        return new_session