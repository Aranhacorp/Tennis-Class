import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide")

# 2. CONEXÃO COM A PLANILHA (TennisClass_DB)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. DESIGN E ESTILO (CSS) - CORREÇÃO DE ASPAS E PADRONIZAÇÃO CINZA
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
        box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    }
    .text-total {
        color: white !important; font-size: 32px; font-weight: bold; text-align: center; margin-bottom: 20px;
    }
    .assinatura-aranha { position: fixed; bottom: 25px; left: 25px; width: 180px; z-index: 9999; }
    .whatsapp-float { position: fixed; bottom: 70px; right: 25px; width: 60px; z-index: 9999; }
    </style>
    <img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-aranha">
    <a href="https://wa.me/5511971425028" target="_blank">
        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-float">
    </a>
""", unsafe_allow_html=True)

# 4. INICIALIZAÇÃO DO ESTADO (PREVINE ATTRIBUTERROR)
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state:
    st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state:
    st.session_state.reserva_temp = {}

# 5. MENU LATERAL
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            st.rerun()

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# --- PÁGINA HOME ---
if st.session_state.pagina == "Home":
    if not st.session_state.pagamento_ativo:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        with st.form("form_reserva"):
            aluno = st.text_input("Nome do Aluno")
            opcoes = {
                "Aula Individual (R$ 250)": 250,
                "Pacote 4 Aulas (R$ 940)": 940,
                "Pacote 8 Aulas (R$ 1800)": 1800,
                "Aula Kids (R$ 230)": 230,
                "Aula em Grupo (R$ 200)": 200
            }
            pacote_sel = st.selectbox("Selecione o Pacote", list(opcoes.keys()))
            data_input = st.date_input("Escolha a Data")
            horario = st.selectbox("Escolha o Horário", [f"{h:02d}:00" for h in range(11, 22)])
            
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO"):
                if aluno:
                    st.session_state.reserva_temp = {
                        "Data": data_input.strftime("%d/%m/%Y"),
                        "Horario": horario,
                        "Aluno": aluno,
                        "Servico": "Aula",
                        "Pacote": pacote_sel,
                        "Status": "Aguardando Pagamento",
                        "Total": opcoes[pacote_sel]
                    }
                    st.session_state.pagamento_ativo = True
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # TELA DE PAGAMENTO LIMPA (SEM QR CODE E SEM INSTRUÇÕES)
        res = st.session_state.reserva_temp
        st.markdown(f"<div class='text-total'>Total do Pacote: R$ {res['Total']:.2f}</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="contact-card">', unsafe_allow_html=True)
        st.markdown("### Pagamento via PIX")
        st.write("Chave E-mail:")
        st.code("aranha.corp@gmail.com.br", language=None) # Botão de cópia automático
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.file_uploader("Anexe o comprovante aqui", type=['png', 'jpg', 'pdf'])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Voltar", use_container_width=True):
                st.session_state.pagamento_ativo = False
                st.rerun()
        with col2:
            if st.button("CONFIRMAR AGENDAMENTO", type="primary", use_container_width=True):
                try:
                    # GRAVAÇÃO NA PLANILHA TennisClass_DB
                    df_atual = conn.read(worksheet="Página1")
                    # Removemos a chave 'Total' para não dar erro de coluna se ela não existir na planilha
                    dados_para_salvar = res.copy()
                    del dados_para_salvar['Total']
                    
                    novo_df = pd.DataFrame([dados_para_salvar])
                    df_final = pd.concat([df_atual, novo_df], ignore_index=True)
                    conn.update(worksheet="Página1", data=df_final)
                    
                    st.balloons()
                    st.success("Reserva enviada com sucesso!")
                    st.session_state.pagamento_ativo = False
                except Exception as e:
                    st.error(f"Erro ao salvar na planilha: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA CADASTRO ---
elif st.session_state.pagina == "Cadastro":
    st.markdown("<h2 style='text-align: center; color: white;'>Central de Cadastros</h2>", unsafe_allow_html=True)
    perfil = st.radio("Selecione o perfil:", ["Aluno", "Professor", "Academia"], horizontal=True)
    links = {
        "Professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?embedded=true",
        "Aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?embedded=true",
        "Academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform?embedded=true"
    }
    st.markdown(f'<iframe src="{links[perfil]}" width="100%" height="700" frameborder="0" style="background:white; border-radius:20px;"></iframe>', unsafe_allow_html=True)

# --- PÁGINA CONTATO ---
elif st.session_state.pagina == "Contato":
    st.markdown('<div class="contact-card">', unsafe_allow_html=True)
    st.markdown("## André Aranha")
    st.write("✉️ aranha.corp@gmail.com.br")
    st.write("📱 (11) 97142-5028")
    st.markdown('</div>', unsafe_allow_html=True)
