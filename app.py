import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CONEXÃO COM A PLANILHA (TennisClass_DB)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. ESTADOS DA SESSÃO
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state:
    st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state:
    st.session_state.reserva_temp = {}
if 'academia_foco' not in st.session_state:
    st.session_state.academia_foco = None

# 4. DESIGN E ESTILO
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .header-title {
        color: white; font-size: 50px; font-weight: bold; text-align: center;
        margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
    }
    .custom-card {
        background-color: rgba(255, 255, 255, 0.9) !important; 
        padding: 30px; border-radius: 20px; 
        max-width: 800px; margin: auto; text-align: center; 
        color: #333 !important; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .sidebar-detalhe {
        text-align: left !important; color: #f0f0f0;
        font-size: 13px; margin: -10px 0 15px 35px;
        line-height: 1.4; border-left: 2px solid #ff4b4b; padding-left: 10px;
    }
    .assinatura-aranha { position: fixed; bottom: 20px; left: 20px; width: 150px; z-index: 1000; }
    .whatsapp-float { position: fixed; bottom: 20px; right: 20px; width: 60px; z-index: 1000; }
</style>
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-aranha">
<a href="https://wa.me/5511971425028" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-float">
</a>
""", unsafe_allow_html=True)

# 5. MENU LATERAL
with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            st.session_state.academia_foco = None
            st.rerun()
    
    st.markdown("---")
    st.markdown("<h3 style='color: white; text-align: left;'>🏢 Academias</h3>", unsafe_allow_html=True)
    info_academias = {
        "Play Tennis Ibirapuera": "R. Joinville, 401 - Vila Mariana<br>📞 (11) 5081-3000",
        "Top One Tennis": "R. João Lourenço, 629 - Vila Nova Conceição<br>📞 (11) 3845-6688",
        "Fontes & Barbeta Tennis": "Av. Prof. Ascendino Reis, 724<br>📞 (11) 99911-3000",
        "Arena BTG": "Av. das Nações Unidas, 13797<br>📞 (11) 94555-2200"
    }
    for nome in info_academias.keys():
        if st.button(f"📍 {nome}", key=f"nav_{nome}", use_container_width=True):
            st.session_state.academia_foco = nome if st.session_state.academia_foco != nome else None
        if st.session_state.academia_foco == nome:
            st.markdown(f'<div class="sidebar-detalhe">{info_academias[nome]}</div>', unsafe_allow_html=True)

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 6. PÁGINAS
if st.session_state.pagina == "Home":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    if not st.session_state.pagamento_ativo:
        with st.form("form_reserva"):
            aluno = st.text_input("Nome do Aluno")
            servico = st.selectbox("Serviço", ["Aula Individual (R$ 250)", "Pacote 4 Aulas (R$ 940)", "Pacote 8 Aulas (R$ 1800)"])
            local = st.selectbox("Local", list(info_academias.keys()))
            data_aula = st.date_input("Data da Aula", format="DD/MM/YYYY")
            hora_aula = st.selectbox("Horário", [f"{h:02d}:00" for h in range(7, 22)])
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO"):
                st.session_state.pagamento_ativo = True
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Serviços":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("## 🎾 Nossos Serviços")
    st.write("- **Aulas Particulares e em Grupo**")
    st.write("- **Treinamento de Performance**")
    st.write("- **Locação de Quadras**")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Cadastro":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### 📝 Portal de Cadastros")
    tipo_cad = st.tabs(["Aluno", "Academia", "Professor"])
    
    with tipo_cad[0]: # CADASTRO ALUNO
        with st.form("cad_aluno"):
            st.text_input("Nome Completo")
            st.text_input("WhatsApp")
            st.select_slider("Nível de Jogo", options=["Iniciante", "Intermediário", "Avançado"])
            st.form_submit_button("Cadastrar Aluno")

    with tipo_cad[1]: # CADASTRO ACADEMIA
        with st.form("cad_academia"):
            st.text_input("Nome da Academia")
            st.text_input("Endereço Completo")
            st.number_input("Quantidade de Quadras", min_value=1)
            st.form_submit_button("Cadastrar Academia")

    with tipo_cad[2]: # CADASTRO PROFESSOR
        with st.form("cad_prof"):
            st.text_input("Nome do Professor")
            st.text_input("CREF / Certificação")
            st.multiselect("Especialidades", ["Infantil", "Adulto", "Competição"])
            st.form_submit_button("Cadastrar Professor")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Contato":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### 📞 Fale Conosco")
    st.write("📩 **aranha.corp@gmail.com.br**")
    st.write("📱 **(11) 97142-5028**")
    st.markdown('</div>', unsafe_allow_html=True)
