import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import segno
from io import BytesIO

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. DESIGN (DARK GLASS) - CORREÇÃO DE ASPAS LATERAIS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .header-title {
        color: white; font-size: 55px; font-weight: bold; text-align: center;
        margin-bottom: 20px; text-shadow: 3px 3px 6px rgba(0,0,0,0.7);
    }
    .custom-card {
        background-color: rgba(0, 0, 0, 0.75) !important; backdrop-filter: blur(12px);
        padding: 40px; border-radius: 25px; border: 1px solid rgba(255, 255, 255, 0.2);
        max-width: 850px; margin: auto; text-align: center; color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. NAVEGAÇÃO
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"

with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    opcoes = ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]
    for item in opcoes:
        if st.button(item, key=f"btn_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.rerun()

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 4. LÓGICA DE PÁGINAS
menu = st.session_state.pagina

# --- PÁGINA HOME: AGENDAMENTO ---
if menu == "Home":
    st.markdown("<h2 style='text-align: center; color: white;'>Agendamento</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df_base = conn.read()
            with st.form("reserva_form"):
                aluno = st.text_input("Nome do Aluno")
                precos = {"Individual": 250, "Dupla": 200, "Aluguel": 250}
                servico = st.selectbox("Serviço", list(precos.keys()))
                n_horas = st.number_input("Horas", min_value=1, value=1)
                data = st.date_input("Data")
                horario = st.selectbox("Horário", [f"{h:02d}:00" for h in range(8, 22)])
                
                if st.form_submit_button("RESERVAR"):
                    data_str = data.strftime("%Y-%m-%d")
                    # Bloqueio de horário
                    conflito = df_base[(df_base['Data'].astype(str) == data_str) & (df_base['Horario'].astype(str) == horario)]
                    if not conflito.empty:
                        st.error("Horário já ocupado!")
                    elif aluno:
                        v_total = precos[servico] * n_horas
                        # Correção do erro '{' was never closed
                        nova_reserva = pd.DataFrame([{
                            "Data": data_str, "Horario": horario, "Aluno": aluno, 
                            "Valor": v_total, "Status": "Pendente"
                        }])
                        df_final = pd.concat([df_base, nova_reserva], ignore_index=True)
                        conn.update(data=df_final)
                        st.balloons()
                        st.success("Reservado!")
        except:
            st.warning("Conectando ao banco de dados...") # Correção de aspas
        st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA CADASTRO: TRIO DE FORMULÁRIOS ---
elif menu == "Cadastro":
    st.markdown("<h2 style='text-align: center; color: white;'>Central de Cadastros</h2>", unsafe_allow_html=True)
    
    # Seletor dinâmico
    tipo = st.radio("Quem você deseja cadastrar?", ["Aluno", "Professor", "Academia"], horizontal=True)
    
    # Dicionário de links com parâmetro 'embedded=true' para evitar erro de Drive
    links = {
        "Professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?embedded=true",
        "Aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?embedded=true",
        "Academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform?embedded=true"
    }
    
    url_final = links[tipo]
    
    st.markdown(f"""
        <div style="display: flex; justify-content: center;">
            <iframe src="{url_final}" width="100%" height="800" frameborder="0" marginheight="0" marginwidth="0" 
            style="background: white; border-radius: 20px; max-width: 850px;">
            Carregando formulário...</iframe>
        </div>
    """, unsafe_allow_html=True)

elif menu == "Contato":
    st.markdown('<div class="custom-card"><h3>André Aranha</h3><p>📞 11 97142 5028</p></div>', unsafe_allow_html=True)
