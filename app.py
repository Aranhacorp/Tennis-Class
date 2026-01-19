import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração da página
st.set_page_config(page_title="SPORTS CLASS", layout="centered")

# 2. CSS para o fundo com a imagem da quadra azul
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    .main-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        margin-top: 20px;
    }
    
    h1 {
        color: white;
        text-align: center;
        font-family: 'Arial Black', sans-serif;
        text-shadow: 2px 2px 4px #000000;
    }
    
    .stHeader {
        background-color: rgba(0,0,0,0);
    }
    </style>
    """, unsafe_allow_html=True)

# Título do App
st.markdown('<h1>SPORTS CLASS 🎾</h1>', unsafe_allow_html=True)

# Bloco de Agendamento
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("📝 Agende sua Aula")
    
    # Conexão com a planilha (certifique-se de que o Secrets está configurado no Streamlit)
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
    except Exception:
        st.error("Erro na conexão com a planilha. Verifique os Secrets.")

    with st.form("agendamento"):
        aluno = st.text_input("Nome do Aluno")
        servico = st.selectbox("Selecione o Serviço", ["Aula Individual", "Aula em Dupla", "Aluguel de Quadra"])
        data = st.date_input("Data Desejada")
        horario = st.selectbox("Horário", ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"])
        
        submit = st.form_submit_button("CONFIRMAR AGENDAMENTO")
        
        if submit:
            if aluno:
                try:
                    # Preparar os dados
                    nova_linha = pd.DataFrame([{
                        "Data": str(data),
                        "Horario": horario,
                        "Aluno": aluno,
                        "Servico": servico,
                        "Status": "Pendente"
                    }])
                    
                    # Ler dados atuais e adicionar novo
                    dados_existentes = conn.read()
                    df_final = pd.concat([dados_existentes, nova_linha], ignore_index=True)
                    conn.update(data=df_final)
                    
                    st.success(f"Excelente, {aluno}! Sua solicitação foi enviada.")
                    st.balloons()
                except Exception as e:
                    st.error("Erro ao salvar os dados. Verifique as permissões da planilha.")
            else:
                st.warning("Por favor, digite o nome do aluno.")
                
    st.markdown('</div>', unsafe_allow_html=True)
