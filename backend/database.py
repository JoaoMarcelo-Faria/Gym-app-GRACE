import firebase_admin
from firebase_admin import firestore, credentials
import streamlit as st

def get_db_connection():
    # Verifica se o app já foi inicializado
    if not firebase_admin._apps:
        print("Initializing database connection...")
        
        # Roteamento: Nuvem (Secrets) X Local (JSON)
        if "firebase" in st.secrets:
            # Transforma o AttrDict do Streamlit em um dicionário Python padrão
            key_dict = dict(st.secrets["firebase"])

            ## Auxilia na leitura da string da private key
            key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")
            
            cred = credentials.Certificate(key_dict)
            
        else:
            # Fallback para o desenvolvimento local
            cred = credentials.Certificate("backend/firebase_credentials.json")
        
        # Inicializa o aplicativo do Firebase com a credencial escolhida
        firebase_admin.initialize_app(cred)
        print("Database connection initialized!")
        
    #  Retorna o cliente do Firestore pronto para uso
    return firestore.client()

db = get_db_connection()