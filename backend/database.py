import firebase_admin
from firebase_admin import firestore, credentials

def get_db_connection():
    ## Inicializa a conexão com o banco de dados
    
    # Verifica se já foi inicializado
    if not firebase_admin._apps:
        cred = credentials.Certificate("./firebase_credentials.json")
        firebase_admin.initialize_app(cred)

    return firestore.client()

db = get_db_connection()    # Instância do banco de dados para ser usada