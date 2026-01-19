import streamlit as st
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1595435064219-49293a10173d?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

/* Deixa os textos mais visíveis com um fundo semitransparente nos cards */
.stForm {
    background-color: rgba(255, 255, 255, 0.85);
    padding: 20px;
    border-radius: 10px;
}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Tennis Class", layout="centered")

# CSS para fundo e estilo do cartão
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Sports-Class/main/fundo_tenis.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .main-card {
        background-color: rgba(0, 31, 63, 0.85);
        padding: 30px;
        border-radius: 20px;
        border: 2px solid #FF8C00;
        color: white;
    }
    h1 { color: #FF8C00; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1>TENNIS CLASS 🎾</h1>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    conn = st.connection("gsheets", type=GSheetsConnection)

    with st.form("agendamento"):
        aluno = st.text_input("Nome do Aluno")
        servico = st.selectbox("Serviço", ["Aula Individual", "Aula em Dupla", "Aluguel de Quadra"])
        data = st.date_input("Data")
        horario = st.selectbox("Horário", ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00"])

        if st.form_submit_button("RESERVAR AGORA"):
            nova_linha = pd.DataFrame([{"Data": str(data), "Horario": horario, "Aluno": aluno, "Servico": servico, "Status": "Pendente"}])
            dados_atuais = conn.read()
            df_final = pd.concat([dados_atuais, nova_linha], ignore_index=True)
            conn.update(data=df_final)
            st.success("Reserva enviada!")

    st.markdown('</div>', unsafe_allow_html=True)
