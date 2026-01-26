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

# 4. DESIGN E ESTILO (CORREÇÃO DE ASPAS E SINTAXE)
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
    .valor-compra {
        font-size: 28px; color: #1e5e20; font-weight: bold;
        background-color: #e8f5e9; padding: 15px; border-radius: 10px;
        margin: 15px 0; border: 1px solid #c8e6c9;
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
        if st.button(item, use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            st.rerun()

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 6. LÓGICA DE PÁGINAS
if st.session_state.pagina == "Home":
    if not st.session_state.pagamento_ativo:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        with st.form("agendamento"):
            nome = st.text_input("Nome do Aluno")
            opcoes = {
                "Aula Individual (R$ 250)": 250,
                "Pacote 4 Aulas (R$ 940)": 940,
                "Pacote 8 Aulas (R$ 1800)": 1800
            }
            servico = st.selectbox("Escolha o Plano", list(opcoes.keys()))
            data = st.date_input("Data da Aula")
            hora = st.selectbox("Horário", [f"{h:02d}:00" for h in range(7, 22)])
            
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO"):
                if nome:
                    st.session_state.reserva_temp = {
                        "Data": data.strftime("%d/%m/%Y"),
                        "Horario": hora,
                        "Aluno": nome,
                        "Servico": servico,
                        "Status": "Pendente",
                        "Valor": opcoes[servico]
                    }
                    st.session_state.pagamento_ativo = True
                    st.rerun()
                else:
                    st.error("Por favor, preencha o nome do aluno.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # TELA DE PAGAMENTO (VALOR DA COMPRA E SEM QR CODE)
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("### Finalizar Agendamento")
        
        # Apresenta o valor da compra
        valor = st.session_state.reserva_temp['Valor']
        st.markdown(f'<div class="valor-compra">Total do Pedido: R$ {valor:.2f}</div>', unsafe_allow_html=True)
        
        st.write("**Pagamento via PIX**")
        st.code("aranha.corp@gmail.com.br", language=None)
        st.write("Favorecido: André Aranha")
        
        st.file_uploader("Anexe o comprovante (Opcional)", type=['png', 'jpg', 'pdf'])
        
        if st.button("CONFIRMAR AGENDAMENTO", type="primary", use_container_width=True):
            try:
                # Atualização da Planilha TennisClass_DB
                df_existente = conn.read(worksheet="Página1")
                # Removemos o valor para manter o padrão das colunas da planilha
                dados = st.session_state.reserva_temp.copy()
                dados.pop("Valor")
                
                novo_df = pd.concat([df_existente, pd.DataFrame([dados])], ignore_index=True)
                conn.update(worksheet="Página1", data=novo_df)
                
                st.balloons()
                st.success("Tudo pronto! Sua reserva foi enviada.")
                st.session_state.pagamento_ativo = False
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
        
        if st.button("Voltar"):
            st.session_state.pagamento_ativo = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Serviços":
    st.markdown('<div class="custom-card"><h3>Nossos Serviços</h3><p>Aulas Individuais, em Dupla e Kids.</p></div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Contato":
    st.markdown('<div class="custom-card"><h3>Contato</h3><p>Email: aranha.corp@gmail.com.br</p></div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Cadastro":
    st.markdown('<div class="custom-card"><h3>Cadastro</h3><p>Selecione seu perfil no formulário abaixo.</p></div>', unsafe_allow_html=True)
