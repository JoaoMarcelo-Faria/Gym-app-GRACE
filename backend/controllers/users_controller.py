from google.cloud import firestore
from backend.models import users

class UserController:
    def __init__(self, db_client: firestore.Client):
        self.db = db_client
        self.collection = self.db.collection('User')

    def create_user(self, user: users.User):
        # Firestore gera uma referência com um ID aleatório
        new_doc_ref = self.collection.document()
        # Atribui o ID gerado ao objeto User
        user.id = new_doc_ref.id    # Não há necessidade de verificar o ID, pois o Firestore garante que seja único

        new_doc_ref.set(user.to_dict())

        return user
    

    def get_user(self, user_id: str) -> users.User:
        user_ref = self.collection.document(user_id)
        user_doc = user_ref.get()

        if user_doc.exists:
            return users.User.from_dict()
        else:
            return None