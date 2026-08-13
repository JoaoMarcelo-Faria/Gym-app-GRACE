import streamlit as st


print("Initializing Streamlit app...")
st.set_page_config(initial_sidebar_state="collapsed")


st.title("Olá! Você é o João?")
init_btn = st.button("Sim, sou eu!", width="stretch")
if init_btn:
    st.session_state["autenticado"] = True
    st.session_state["User_id"] = st.secrets["MASTER_USER_ID"]
    st.switch_page("pages/home.py")
