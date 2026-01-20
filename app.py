import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import segno
from io import BytesIO

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CSS PERSONALIZADO (DARK GLASS DESIGN)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .header-title {
        color: white;
        font-size: 50px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.8) !important;
        backdrop-filter: blur(15px);
        margin: 20px 0 20px 20px !important;
        border-radius: 20px !important;
        min-width: 225px !important; 
        max-width: 225px !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .custom-card {
        background-color: rgba(0, 0, 0, 0.7) !important;
        backdrop-filter: blur(10px);
        padding: 40px;
        border-radius: 25px;
        color: white !important;
        max-width: 800px;
        margin: auto;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
    }
    .stButton > button {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 12px !important;
        width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. CONEXÃO E NAVEGAÇÃO
if 'menu_selecionado' not in st.session_state:
    st.session_state.menu_selecionado = "Home"

with st.sidebar:
    st.markdown("<h3 style='text-align: center; color: white;'>🎾 MENU</h3>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}"):
            st.session_state.menu_selecionado = item
            st.rerun()

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 4. LÓGICA DE AGENDAMENTO COM BLOQUEIO
if st.session_state.menu_selecionado == "Home":
    st.markdown("<h2 style='text-align: center; color: white;'>Agendamento Profissional</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df_base = conn.read() # Lê a planilha TennisClass_DB

            with st.form("agendamento"):
                aluno = st.text_input("Nome do Aluno")
                precos = {
                    "Aula Individual (R$ 250/hora)": 250,
                    "Aula em Dupla (R$ 200/pessoa)": 200,
                    "Aluguel de Quadra (R$ 250/hora)": 250
                }
                servico = st.selectbox("Serviço", list(precos.keys()))
                n_horas = st.number_input("Número de Horas", min_value=1, max_value=5, value=1)
                data = st.date_input("Data", format="DD/MM/YYYY")
                horario = st.selectbox("Horário", [f"{h:02d}:00" for h in range(8, 22)])
                academia = st.selectbox("Academia", ["Play Tennis Ibirapuera", "Fontes e Barbeta", "TOP One", "Arena BTG"])

                if st.form_submit_button("CONFIRMAR RESERVA"):
                    if not aluno:
                        st.error("Por favor, insira o nome do aluno.")
                    else:
                        data_str = data.strftime("%Y-%m-%d") # Formato de busca na planilha
                        
                        # LÓGICA DE BLOQUEIO: Verifica se já existe reserva para essa Data e Horário
                        conflito = df_base[(df_base['Data'].astype(str) == data_str) & 
                                          (df_base['Horario'].astype(str) == horario)]
                        
                        if not conflito.empty:
                            st.error(f"❌ O horário {horario} do dia {data.strftime('%d/%m/%Y')} já está ocupado.")
                        else:
                            # Cálculo e Gravação
                            valor_total = precos[servico] * n_horas
                            nova_reserva = pd.DataFrame([{
                                "Data": data_str,
                                "Horario": horario,
                                "Aluno": aluno,
                                "Servico": servico,
                                "Horas": n_horas,
                                "Valor": valor_total,
                                "Status": "Pendente",
                                "Academia": academia
                            }])
                            
                            df_final = pd.concat([df_base, nova_reserva], ignore_index=True)
                            conn.update(data=df_final)
                            
                            st.balloons() #
                            st.session_state.confirmado = True
                            st.rerun()

            if st.session_state.get('confirmado'):
                st.success("Reserva realizada com sucesso!") #
                qr = segno.make("25019727830")
                img_buffer = BytesIO()
                qr.save(img_buffer, kind='png', scale=5)
                st.image(img_buffer.getvalue(), width=200)
                st.code("250.197.278-30")
                
        except Exception as e:
            st.warning("Erro ao conectar com a planilha. Verifique as configurações do GSheets.")
        st.markdown('</div>', unsafe_allow_html=True)

# Aba Contato (Seguindo o design solicitado)
elif st.session_state.menu_selecionado == "Contato":
    st.markdown("""
        <div class="custom-card">
            <h1>André Aranha</h1>
            <p style="font-size: 20px;">📧 aranha.corp@gmail.com.br</p>
            <p style="font-size: 20px;">📞 11 - 97142 5028</p>
            <br>
            <a href="https://wa.me/5511971425028" target="_blank" 
               style="background:#25d366; color:white; padding:15px 30px; border-radius:10px; text-decoration:none
