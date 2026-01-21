import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. DESIGN E ESTILO
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
        background-color: rgba(255, 255, 255, 0.95) !important; 
        padding: 40px; border-radius: 25px; 
        max-width: 850px; margin: auto; text-align: center; 
        color: #1E1E1E !important;
    }
    .assinatura-aranha {
        position: fixed; bottom: 25px; left: 25px;
        width: 180px; z-index: 9999;
    }
    .whatsapp-float {
        position: fixed; bottom: 70px; right: 25px;
        width: 60px; z-index: 9999;
    }
    </style>
    <img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-aranha">
    <a href="https://wa.me/5511971425028" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-float">
    </a>
""", unsafe_allow_html=True)

# 3. MENU LATERAL E ACADEMIAS
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"

with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.rerun()
    
    st.markdown("---")
    st.markdown("<h3 style='color: white;'>🏢 Academias Recomendadas</h3>", unsafe_allow_html=True)
    academias = {
        "Play Tennis Ibirapuera": {"End": "Rua Estado de Israel, 860", "Tel": "11-97752-0488"},
        "Top One tennis": {"End": "Avenida Indianapolis, 647", "Tel": "11-93236-3828"},
        "Fontes & Barbeta Tennis": {"End": "Rua Oscar Gomes Cardim, 535", "Tel": "11-94695-3738"},
        "Arena BTG": {"End": "Rua Major Sylvio de Magalhães Padilha, 16741", "Tel": "11-98854-3860"}
    }
    for nome, info in academias.items():
        with st.expander(nome):
            st.write(f"📍 {info['End']}")
            st.write(f"📞 {info['Tel']}")

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# --- PÁGINA HOME: AGENDAMENTO ---
if st.session_state.pagina == "Home":
    st.markdown("<h3 style='text-align: center; color: white;'>Agendamento Profissional</h3>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df_base = conn.read()
            with st.form("agendamento"):
                aluno = st.text_input("Nome do Aluno")
                pacotes = {
                    "Aula Individual Pacote 4 Aulas (R$ 235/hora)": 235,
                    "Aula Individual Pacote 8 Aulas (R$ 225/hora)": 225,
                    "Aula Individual Única (R$ 250/hora)": 250,
                    "Aula Kids Pacote 4 Aulas (R$ 230/hora)": 230,
                    "Aula em Grupo até 3 pessoas (R$ 200/hora)": 200,
                    "Locação de Quadra (Valor a Consultar)": 0,
                    "Eventos (Valor a Consultar)": 0
                }
                pacote_sel = st.selectbox("Pacotes", list(pacotes.keys()))
                n_horas = st.number_input("Horas/Sessões", min_value=1, value=1)
                
                # AJUSTE DA DATA PARA PADRÃO BRASILEIRO
                data_obj = st.date_input("Data", format="DD/MM/YYYY")
                data_br = data_obj.strftime("%d/%m/%Y")
                
                # HORÁRIO: 11:00 às 21:00
                horario = st.selectbox("Horário", [f"{h:02d}:00" for h in range(11, 22)])
                
                if st.form_submit_button("CONFIRMAR RESERVA"):
                    if aluno:
                        v_unit = pacotes[pacote_sel]
                        total = (v_unit * n_horas) if v_unit > 0 else "A Consultar"
                        nova_reserva = pd.DataFrame([{"Data": data_br, "Horario": horario, "Aluno": aluno, "Pacote": pacote_sel, "Total": total}])
                        df_final = pd.concat([df_base, nova_reserva], ignore_index=True)
                        conn.update(data=df_final)
                        st.balloons()
                        st.success(f"Reserva confirmada para {data_br}!")
        except:
            st.info("Conectando ao banco de dados...")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA CADASTRO (LINKS E DATA CORRIGIDOS) ---
elif st.session_state.pagina == "Cadastro":
    st.markdown("<h2 style='text-align: center; color: white;'>Central de Cadastros</h2>", unsafe_allow_html=True)
    tipo_cad = st.radio("Selecione o perfil:", ["Aluno", "Professor", "Academia"], horizontal=True)
    
    links = {
        "Professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?embedded=true",
        "Aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?embedded=true",
        "Academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform?embedded=true"
    }
    st.markdown(f'<iframe src="{links[tipo_cad]}" width="100%" height="800" frameborder="0" style="background:white; border-radius:20px;"></iframe>', unsafe_allow_html=True)

# --- PÁGINA CONTATO ---
elif st.session_state.pagina == "Contato":
    st.markdown('<div class="custom-card"><h2>André Aranha</h2><p>📧 aranha.corp@gmail.com.br</p><p>📞 (11) 97142-5028</p></div>', unsafe_allow_html=True)
