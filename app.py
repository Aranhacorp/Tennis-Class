import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

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

# 4. DESIGN E ESTILO (CSS SEM ERROS DE SINTAXE)
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
        background-color: rgba(255, 255, 255, 0.95) !important; 
        padding: 30px; border-radius: 20px; 
        max-width: 800px; margin: auto; text-align: center; 
        color: #333 !important;
    }
    .valor-destaque {
        font-size: 30px; color: #1e5e20; font-weight: bold;
        background-color: #e8f5e9; padding: 15px; border-radius: 12px;
        margin: 15px 0; border: 2px solid #1e5e20;
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
    st.markdown("<h2 style='color: white; text-align: center;'>MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            st.rerun()

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 6. PÁGINA HOME: AGENDAMENTO
if st.session_state.pagina == "Home":
    if not st.session_state.pagamento_ativo:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        with st.form("agendamento"):
            aluno = st.text_input("Nome do Aluno")
            precos = {
                "Aula Individual (R$ 250)": 250,
                "Pacote 4 Aulas (R$ 940)": 940,
                "Pacote 8 Aulas (R$ 1800)": 1800
            }
            servico_sel = st.selectbox("Serviço", list(precos.keys()))
            academia = st.selectbox("Academia", ["Play Tennis Ibirapuera", "Top One tennis", "Fontes & Barbeta", "Arena BTG"])
            
            # 📅 PADRÃO BRASILEIRO NO SELETOR
            data_sel = st.date_input("Data da Aula", format="DD/MM/YYYY") 
            
            hora_sel = st.selectbox("Horário", [f"{h:02d}:00" for h in range(7, 22)])
            
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO"):
                if aluno:
                    st.session_state.reserva_temp = {
                        "Data": data_sel.strftime("%d/%m/%Y"), # 📅 GRAVAÇÃO EM PT-BR
                        "Horario": hora_sel,
                        "Aluno": aluno,
                        "Servico": servico_sel,
                        "Status": "Pendente",
                        "Academia": academia,
                        "Valor": precos[servico_sel]
                    }
                    st.session_state.pagamento_ativo = True
                    st.rerun()
                else:
                    st.error("Por favor, preencha o nome do aluno.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # TELA DE PAGAMENTO (VALOR VISÍVEL E SEM QR CODE)
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("### 💳 Pagamento via PIX")
        
        # EXIBIÇÃO DO VALOR DA COMPRA
        valor_total = f"R$ {st.session_state.reserva_temp['Valor']:.2f}"
        st.markdown(f'<div class="valor-destaque">VALOR TOTAL: {valor_total}</div>', unsafe_allow_html=True)
        
        st.write("Chave PIX: **aranha.corp@gmail.com.br**")
        st.write("Favorecido: **André Aranha**")
        
        st.file_uploader("Anexe o comprovante", type=['png', 'jpg', 'pdf'])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Voltar", use_container_width=True):
                st.session_state.pagamento_ativo = False
                st.rerun()
        with col2:
            if st.button("CONFIRMAR AGENDAMENTO", type="primary", use_container_width=True):
                try:
                    # Gravação na Planilha TennisClass_DB
                    df_atual = conn.read(worksheet="Página1")
                    dados_salvar = st.session_state.reserva_temp.copy()
                    dados_salvar.pop("Valor") # Remove o valor para manter colunas da DB
                    
                    novo_df = pd.concat([df_atual, pd.DataFrame([dados_salvar])], ignore_index=True)
                    conn.update(worksheet="Página1", data=novo_df)
                    
                    st.balloons()
                    st.success(f"Reserva para o dia {st.session_state.reserva_temp['Data']} confirmada!")
                    st.session_state.pagamento_ativo = False
                except Exception as e:
                    st.error(f"Erro ao salvar na planilha: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

# 7. DEMAIS PÁGINAS (CONTATO, SERVIÇOS)
elif st.session_state.pagina == "Contato":
    st.markdown('<div class="custom-card"><h2>Contato</h2><p>Email: aranha.corp@gmail.com.br</p></div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Serviços":
    st.markdown('<div class="custom-card"><h2>Nossos Serviços</h2><p>Aulas de tênis para todos os níveis.</p></div>', unsafe_allow_html=True)
