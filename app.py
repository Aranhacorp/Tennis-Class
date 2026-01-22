import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO E CONEXÃO
st.set_page_config(page_title="TENNIS CLASS", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. INICIALIZAÇÃO DO ESTADO (PREVINE ERROS DE ATRIBUTO)
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state:
    st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state:
    st.session_state.reserva_temp = {}

# 3. ESTILO CSS COMPLETO (RESTAURA IDENTIDADE VISUAL E ACESSÓRIOS)
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
    .custom-card, .contact-card {
        background-color: rgba(30, 30, 30, 0.85) !important;
        padding: 40px; border-radius: 25px; 
        max-width: 850px; margin: auto; text-align: center; 
        color: white !important; border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .text-total { color: white !important; font-size: 32px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .assinatura-aranha { position: fixed; bottom: 25px; left: 25px; width: 180px; z-index: 9999; }
    .whatsapp-float { position: fixed; bottom: 70px; right: 25px; width: 60px; z-index: 9999; }
    </style>
    <img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-aranha">
    <a href="https://wa.me/5511971425028" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-float">
    </a>
""", unsafe_allow_html=True)

# 4. MENU LATERAL E ACADEMIAS RECOMENDADAS (RESTAURADOS)
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    if st.button("Home", use_container_width=True):
        st.session_state.pagina = "Home"
        st.session_state.pagamento_ativo = False
        st.rerun()
    if st.button("Serviços", use_container_width=True): st.session_state.pagina = "Serviços"
    if st.button("Produtos", use_container_width=True): st.session_state.pagina = "Produtos"
    if st.button("Cadastro", use_container_width=True): st.session_state.pagina = "Cadastro"
    if st.button("Contato", use_container_width=True): st.session_state.pagina = "Contato"
    
    st.markdown("<br><br>🏢 **Academias Recomendadas**", unsafe_allow_html=True)
    with st.expander("Play Tennis Ibirapuera"): st.write("Rua Joinville, 100")
    with st.expander("Top One tennis"): st.write("Av. Moema, 123")
    with st.expander("Fontes & Barbeta Tennis"): st.write("Rua Groenlândia, 456")
    with st.expander("Arena BTG"): st.write("Av. Faria Lima, 789")

# Título Principal (RESTAURADO)
st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 5. LÓGICA DAS PÁGINAS
if st.session_state.pagina == "Home":
    if not st.session_state.pagamento_ativo:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        with st.form("form_reserva"):
            aluno = st.text_input("Nome do Aluno")
            opcoes = {
                "Aula Individual Pacote 4 Aulas (R$ 235/h)": 940,
                "Aula Individual (R$ 250)": 250,
                "Aula Kids (R$ 230)": 230,
                "Aula em Grupo (R$ 200)": 200
            }
            pacote_sel = st.selectbox("Selecione o Pacote", list(opcoes.keys()))
            data_input = st.date_input("Escolha a Data")
            horario = st.selectbox("Horário", [f"{h:02d}:00" for h in range(11, 22)])
            
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO"):
                if aluno:
                    st.session_state.reserva_temp = {
                        "Data": data_input.strftime("%d/%m/%Y"),
                        "Horario": horario,
                        "Aluno": aluno,
                        "Servico": "Aula",
                        "Pacote": pacote_sel,
                        "Status": "Aguardando Pagamento",
                        "Academia": ""
                    }
                    st.session_state.total_valor = opcoes[pacote_sel]
                    st.session_state.pagamento_ativo = True
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # TELA DE PAGAMENTO LIMPA E CINZA
        st.markdown(f"<div class='text-total'>Total do Pacote: R$ {st.session_state.total_valor:.2f}</div>", unsafe_allow_html=True)
        st.markdown('<div class="contact-card">', unsafe_allow_html=True)
        st.markdown("### Pagamento via PIX")
        st.write("Chave E-mail:")
        st.code("aranha.corp@gmail.com.br", language=None)
        
        st.file_uploader("Anexe o comprovante", type=['png', 'jpg', 'pdf'])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Voltar", use_container_width=True):
                st.session_state.pagamento_ativo = False
                st.rerun()
        with col2:
            if st.button("CONFIRMAR E SALVAR", type="primary", use_container_width=True):
                try:
                    df_atual = conn.read(worksheet="Página1")
                    # Removemos 'Academia' se precisar ser preenchido manual depois, mas mantemos colunas da planilha
                    novo_df = pd.DataFrame([st.session_state.reserva_temp])
                    df_final = pd.concat([df_atual, novo_df], ignore_index=True)
                    conn.update(worksheet="Página1", data=df_final)
                    st.balloons()
                    st.success("Dados gravados na TennisClass_DB!")
                    st.session_state.pagamento_ativo = False
                except Exception as e:
                    st.error(f"Erro na planilha: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

# RESTANTE DAS PÁGINAS (Serviços, Produtos, Cadastro, Contato)
elif st.session_state.pagina == "Serviços":
    st.markdown('<div class="custom-card"><h2>Nossos Serviços</h2><p>Aulas individuais e em grupo.</p></div>', unsafe_allow_html=True)
elif st.session_state.pagina == "Produtos":
    st.markdown('<div class="custom-card"><h2>Nossos Produtos</h2><p>Equipamentos de alta performance.</p></div>', unsafe_allow_html=True)
elif st.session_state.pagina == "Cadastro":
    st.markdown("<h2 style='text-align: center; color: white;'>Cadastro</h2>", unsafe_allow_html=True)
    st.markdown('<iframe src="https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?embedded=true" width="100%" height="
