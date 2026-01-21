import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. DESIGN: CARD BRANCO, ASSINATURA E WHATSAPP
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
        backdrop-filter: blur(10px);
        padding: 40px; border-radius: 25px; 
        max-width: 850px; margin: auto; text-align: center; 
        color: #1E1E1E !important;
    }
    .assinatura-aranha {
        position: fixed; bottom: 25px; left: 25px;
        width: 180px; z-index: 9999;
        filter: drop-shadow(2px 2px 5px rgba(0,0,0,0.8));
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

# 3. NAVEGAÇÃO E ACADEMIAS NO MENU LATERAL
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"

with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.rerun()
    
    # SEÇÃO: ACADEMIAS RECOMENDADAS NO MENU LATERAL
    st.markdown("---")
    st.markdown("<h3 style='color: white;'>🏢 Academias Recomendadas</h3>", unsafe_allow_html=True)
    
    academias = {
        "Play Tennis Ibirapuera": {"Endereço": "R. Joinville, 401", "Tel": "(11) 5085-2100"},
        "Slice Tennis": {"Endereço": "Av. Caminho do Mar, 2097", "Tel": "(11) 4368-7171"},
        "Winner Tennis": {"Endereço": "R. Prof. Atílio Innocenti, 800", "Tel": "(11) 3044-1011"}
    }
    
    for nome, info in academias.items():
        with st.expander(nome):
            st.write(f"📍 {info['Endereço']}")
            st.write(f"📞 {info['Tel']}")

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)
menu = st.session_state.pagina

# --- PÁGINA HOME: AGENDAMENTO (HORÁRIO 11h-21h) ---
if menu == "Home":
    st.markdown("<h3 style='text-align: center; color: white;'>Agendamento Profissional</h3>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df_base = conn.read()
            with st.form("agendamento"):
                aluno = st.text_input("Nome do Aluno")
                
                # PACOTES NA ORDEM SOLICITADA
                pacotes_lista = {
                    "Aula Individual Pacote 4 Aulas (R$ 235/hora)": 235,
                    "Aula Individual Pacote 8 Aulas (R$ 225/hora)": 225,
                    "Aula Individual Única (R$ 250/hora)": 250,
                    "Aula Kids Pacote 4 Aulas (R$ 230/hora)": 230,
                    "Aula em Grupo até 3 pessoas (R$ 200/hora)": 200,
                    "Locação de Quadra (Valor a Consultar)": 0,
                    "Eventos (Valor a Consultar)": 0
                }
                
                pacote_sel = st.selectbox("Pacotes", list(pacotes_lista.keys()))
                n_horas = st.number_input("Horas/Sessões", min_value=1, value=1)
                data = st.date_input("Data")
                
                # HORÁRIOS: 11:00 às 21:00
                horario = st.selectbox("Horário", [f"{h:02d}:00" for h in range(11, 22)])
                
                if st.form_submit_button("CONFIRMAR RESERVA"):
                    if aluno:
                        v_unit = pacotes_lista[pacote_sel]
                        valor_final = (v_unit * n_horas) if v_unit > 0 else "A Consultar"
                        nova_reserva = pd.DataFrame([{"Data": str(data), "Horario": horario, "Aluno": aluno, "Pacote": pacote_sel, "Total": valor_final}])
                        df_final = pd.concat([df_base, nova_reserva], ignore_index=True)
                        conn.update(data=df_final)
                        st.balloons()
                        st.success("Reserva enviada!")
        except:
            st.info("Conectando ao banco de dados...")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA CADASTRO (CORREÇÃO DE SINTAXE) ---
elif menu == "Cadastro":
    st.markdown("<h2 style='text-align: center; color: white;'>Central de Cadastros</h2>", unsafe_allow_html=True)
    tipo_cad = st.radio("Selecione:", ["Aluno", "Professor", "Academia"], horizontal=True)
    links = {
        "Professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?embedded=true",
        "Aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?embedded=true",
        "Academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform?embedded=true"
    }
    # Sintaxe corrigida para evitar o erro da linha 149
    st.markdown(f'<iframe src="{links[tipo_cad]}" width="100%" height="800" frameborder="0" style="background:white; border-radius:20px;"></iframe>', unsafe_allow_html=True)

# --- PÁGINAS ADICIONAIS ---
elif menu == "Contato":
    st.markdown('<div class="custom-card"><h2>André Aranha</h2><p>📧 aranha.corp@gmail.com.br</p><p>📞 (11) 97142-5028</p></div>', unsafe_allow_html=True)
