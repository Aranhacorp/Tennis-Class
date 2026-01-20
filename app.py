import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import segno
from io import BytesIO

# 1. CONFIGURAÇÃO E DESIGN
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .header-title {
        color: white; font-size: 50px; font-weight: bold; text-align: center;
        margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .custom-card {
        background-color: rgba(0, 0, 0, 0.75) !important; backdrop-filter: blur(10px);
        padding: 30px; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.2);
        max-width: 850px; margin: auto; color: white !important;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.8) !important; backdrop-filter: blur(15px);
    }
    </style>
""", unsafe_allow_html=True)

# 2. NAVEGAÇÃO
if 'menu' not in st.session_state:
    st.session_state.menu = "Home"

with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}", use_container_width=True):
            st.session_state.menu = item
            st.rerun()

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 3. LÓGICA DAS ABAS
menu = st.session_state.menu

if menu == "Home":
    st.markdown("<h3 style='text-align: center; color: white;'>Agendamento Profissional</h3>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df_base = conn.read() # Conexão com TennisClass_DB

            with st.form("form_reserva"):
                aluno = st.text_input("Nome do Aluno")
                precos = {
                    "Aula Individual (R$ 250/hora)": 250,
                    "Aula em Dupla (R$ 200/pessoa)": 200,
                    "Aluguel de Quadra (R$ 250/hora)": 250
                }
                servico = st.selectbox("Escolha o Serviço", list(precos.keys()))
                n_horas = st.number_input("Número de Horas", min_value=1, max_value=5, value=1)
                data = st.date_input("Data Desejada", format="DD/MM/YYYY")
                horario = st.selectbox("Horário Disponível", [f"{h:02d}:00" for h in range(8, 22)])
                academia = st.selectbox("Academia", ["Play Tennis Ibirapuera", "Fontes e Barbeta", "TOP One", "Arena BTG"])

                if st.form_submit_button("CONFIRMAR RESERVA"):
                    if not aluno:
                        st.error("Por favor, informe o nome do aluno.")
                    else:
                        data_str = data.strftime("%Y-%m-%d")
                        # LÓGICA DE BLOQUEIO DE HORÁRIO
                        conflito = df_base[(df_base['Data'].astype(str) == data_str) & 
                                          (df_base['Horario'].astype(str) == horario)]
                        
                        if not conflito.empty:
                            st.error(f"❌ O horário {horario} em {data.strftime('%d/%m/%Y')} já está ocupado.")
                        else:
                            valor_total = precos[servico] * n_horas # Cálculo Valor x Horas
                            nova_reserva = pd.DataFrame([{
                                "Data": data_str, "Horario": horario, "Aluno": aluno, 
                                "Servico": servico, "Horas": n_horas, "Valor": valor_total, 
                                "Status": "Pendente", "Academia": academia
                            }])
                            df_final = pd.concat([df_base, nova_reserva], ignore_index=True)
                            conn.update(data=df_final)
                            st.balloons() #
                            st.session_state.sucesso = True
                            st.rerun()

            if st.session_state.get('sucesso'):
                st.success("Reserva realizada com sucesso!") #
                qr = segno.make("25019727830")
                img_buffer = BytesIO()
                qr.save(img_buffer, kind='png', scale=5)
                st.image(img_buffer.getvalue(), width=200, caption="PIX para Pagamento")
                st.code("Chave PIX: 250.197.278-30")
        except Exception:
            st.warning("Conectando à planilha...")
        st.markdown('</div>', unsafe_allow_html=True)

# ABA DE CADASTRO COM GOOGLE FORMS [SOLICITADO]
elif menu == "Cadastro":
    st.markdown("<h3 style='text-align: center; color: white;'>Cadastro de Professor</h3>", unsafe_allow_html=True)
    
    # URL do seu formulário
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfN-d-T_G2V_u_yN0_S_b8O_G2H_u_yN0_S_b/viewform?embedded=true"
    
    st.markdown(f"""
        <div style="display: flex; justify-content: center;">
            <iframe src="{form_url}" width="100%" height="1000" frameborder="0" marginheight="0" marginwidth="0" 
            style="background-color: white; border-radius: 15px; max-width: 800px;">
            Carregando...</iframe>
        </div>
    """, unsafe_allow_html=True)

elif menu == "Contato":
    st.markdown("""
        <div class="custom-card" style="text-align: center;">
            <h2>André Aranha</h2>
            <p>📧 aranha.corp@gmail.com.br</p>
            <p>📞 11 - 97142 5028</p>
            <br>
            <a href="https://wa.me/5511971425028" target="_blank" 
               style="background:#25d366; color:white; padding:12px 25px; border-radius:10px; text-decoration:none; font-weight:bold;">
               FALAR NO WHATSAPP
            </a>
        </div>
    """, unsafe_allow_html=True)
