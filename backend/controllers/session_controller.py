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