from google.cloud import firestore
from backend.models.users import UserModel
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

class UserController:
    def __init__(self, db_client: firestore.Client):
        self.db = db_client
        self.collection = self.db.collection('User')
        self.password_hasher = PasswordHash((Argon2Hasher(),))      # inicializa o gerenciador de senhas do argon2

    def register_user(self, name:str, username: str, password: str):
        ## Verificar se já tem um username no banco
        username_exists = self.collection.where("Username", "==", username).limit(1).get()
        if len(username_exists) != 0:
            raise ValueError("Este nome de usuário já está em uso")

        ## Gerar o hash da senha
        hashed_password = self.password_hasher.hash(password)

        ## Criar a referencia no banco e instanciar o model
        new_doc_ref = self.collection.document()
        new_user = UserModel(
            id=new_doc_ref.id,
            name=name,
            username=username,
            password_hash=hashed_password
        )
        new_doc_ref.set(new_user.to_dict())     # salva no banco
        return new_user

    def login_user(self, username:str, password: str):
        ## Buscar o documento pelo username
        user_doc = self.collection.where("Username", "==", username).limit(1).get()
        if len(user_doc) == 0:
            raise ValueError("Usuário ou senha incorretos")

        user = user_doc[0].to_dict()

        ## Verificar se a senha enviada bate com o hash salvo no banco
        is_pswrd_valid = self.password_hasher.verify(password, user.get("Password_hash"))
        if not is_pswrd_valid:
            raise ValueError("Usuário ou senha incorretos")

        return UserModel.from_dict(user)
    

    def get_user_by_id(self, user_id: str):
        user_ref = self.collection.document(user_id)
        user_doc = user_ref.get()

        if user_doc.exists:
            return UserModel.from_dict(user_doc.to_dict())
        else:
            return None