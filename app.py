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
if 'academia_foco' not in st.session_state:
    st.session_state.academia_foco = None

# 4. DESIGN E ESTILO (CSS CORRIGIDO)
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
    .btn-cadastro {
        display: block; width: 100%; background-color: #1e5e20; color: white !important;
        padding: 15px; margin: 10px 0; border-radius: 10px; text-decoration: none; font-weight: bold;
    }
    .assinatura-aranha { position: fixed; bottom: 20px; left: 20px; width: 150px; z-index: 1000; }
</style>
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-aranha">
""", unsafe_allow_html=True)

# 5. MENU LATERAL E ACADEMIAS
with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            st.session_state.academia_foco = None
            st.rerun()
    
    st.markdown("---")
    st.markdown("<h3 style='color: white;'>🏢 Academias</h3>", unsafe_allow_html=True)
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

# 6. PÁGINA HOME: RESERVA (FORMATO BRASILEIRO)
if st.session_state.pagina == "Home":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    with st.form("reserva"):
        st.text_input("Nome do Aluno")
        st.selectbox("Serviço", ["Aula Individual (R$ 250)", "Pacote 4 Aulas", "Pacote 8 Aulas"])
        st.date_input("Data da Aula", format="DD/MM/YYYY")
        st.selectbox("Horário", [f"{h:02d}:00" for h in range(7, 22)])
        st.form_submit_button("AVANÇAR PARA PAGAMENTO")
    st.markdown('</div>', unsafe_allow_html=True)

# 7. SERVIÇOS
elif st.session_state.pagina == "Serviços":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("## 🎾 Nossos Serviços")
    st.write("Aulas particulares, em grupo e clínicas especializadas.")
    st.markdown('</div>', unsafe_allow_html=True)

# 8. CADASTRO (DIRECIONANDO PARA GOOGLE DOCS)
elif st.session_state.pagina == "Cadastro":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### 📝 Selecione o seu Cadastro")
    st.write("Você será redirecionado para o formulário oficial do Google.")
    
    st.markdown('<a href="https://docs.google.com/forms/d/e/1FAIpQLSdyHq5Wf1uCjL9fQG-Alp6N7qYqY/viewform" class="btn-cadastro">👤 Cadastro de Aluno de Tênis</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://docs.google.com/forms/d/e/1FAIpQLSfp5uE9Y_rXyXyXyXyXyXyXyXyX/viewform" class="btn-cadastro">🏢 Cadastro de Academia de Tênis</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://docs.google.com/forms/d/e/1FAIpQLSffh7vW9Z_rYvYvYvYvYvYvYvYv/viewform" class="btn-cadastro">🎾 Cadastro de Professor de Tênis</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 9. CONTATO (BALÃO CINZA TRANSPARENTE)
elif st.session_state.pagina == "Contato":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### 📞 Fale Conosco")
    st.write("📩 aranha.corp@gmail.com.br")
    st.write("📱 (11) 97142-5028")
    st.markdown('</div>', unsafe_allow_html=True)
