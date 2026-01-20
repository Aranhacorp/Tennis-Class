import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import segno
from io import BytesIO

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CSS PARA DESIGN "DARK GLASS"
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
        max-width: 850px; margin: auto; color: white !important; text-align: center;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.8) !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. NAVEGAÇÃO
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"

with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.rerun()

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 4. LÓGICA DAS PÁGINAS
menu = st.session_state.pagina

if menu == "Home":
    st.markdown("<h2 style='text-align: center; color: white;'>Agendamento Profissional</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df_base = conn.read()

            with st.form("agendamento"):
                aluno = st.text_input("Nome do Aluno")
                precos = {"Aula Individual": 250, "Aula em Dupla": 200, "Aluguel": 250}
                servico = st.selectbox("Serviço", list(precos.keys()))
                n_horas = st.number_input("Número de Horas", min_value=1, max_value=5, value=1)
                data = st.date_input("Data", format="DD/MM/YYYY")
                horario = st.selectbox("Horário", [f"{h:02d}:00" for h in range(8, 22)])
                academia = st.selectbox("Academia", ["Play Tennis Ibirapuera", "Fontes e Barbeta", "TOP One", "Arena BTG"])

                if st.form_submit_button("CONFIRMAR RESERVA"):
                    if not aluno:
                        st.error("Informe o nome do aluno.")
                    else:
                        data_str = data.strftime("%Y-%m-%d")
                        
                        # BLOQUEIO DE HORÁRIO
                        conflito = df_base[(df_base['Data'].astype(str) == data_str) & 
                                          (df_base['Horario'].astype(str) == horario)]
                        
                        if not conflito.empty:
                            st.error(f"❌ Horário {horario} já ocupado em {data.strftime('%d/%m/%Y')}.")
                        else:
                            valor_total = precos[servico] * n_horas
                            nova_reserva = pd.DataFrame([{
                                "Data": data_str, "Horario": horario, "Aluno": aluno, 
                                "Servico": servico, "Horas": n_horas, "Valor": valor_total, 
                                "Status": "Pendente", "Academia": academia
                            }])
                            df_final = pd.concat([df_base, nova_reserva], ignore_index=True)
                            conn.update(data=df_final)
                            st.balloons()
                            st.session_state.confirmado = True
                            st.rerun()

            if st.session_state.get('confirmado'):
                st.success("Reserva realizada com sucesso!")
                qr = segno.make("25019727830")
                img_buffer = BytesIO()
                qr.save(img_buffer, kind='png', scale=5)
                st.image(img_buffer.getvalue(), width=200)

        except Exception:
            st.warning("Aguardando conexão com TennisClass_DB...")
        st.markdown('</div>', unsafe_allow_html=True)

# --- CORREÇÃO DA ABA CADASTRO ---
elif menu == "Cadastro":
    st.markdown("<h3 style='text-align: center; color: white;'>Cadastro de Professor</h3>", unsafe_allow_html=True)
    
    # O link abaixo é o link de VISUALIZAÇÃO do formulário (botão 'Enviar' -> ícone de link)
    form_url = "https
