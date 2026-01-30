import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide", page_icon="🎾")

# 2. CONEXÃO COM BANCO DE DADOS
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. ESTADOS DA SESSÃO
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state: st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state: st.session_state.reserva_temp = {}
if 'inicio_timer' not in st.session_state: st.session_state.inicio_timer = None
if 'admin_autenticado' not in st.session_state: st.session_state.admin_autenticado = False

# 4. CSS GLOBAL (Corrigido para evitar erros de aspas das imagens anteriores)
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .header-title { color: white; font-size: 50px; font-weight: bold; text-align: center; margin-bottom: 20px; text-shadow: 2px 2px 4px black; }
    .custom-card { background-color: rgba(255, 255, 255, 0.95); padding: 30px; border-radius: 20px; color: #333; position: relative; }
    .whatsapp-float { position: fixed; width: 60px; height: 60px; bottom: 40px; right: 40px; background-color: #25d366; color: #FFF; border-radius: 50px; text-align: center; font-size: 35px; box-shadow: 2px 2px 3px #999; z-index: 9999; display: flex; align-items: center; justify-content: center; text-decoration: none; }
</style>
<a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="35"></a>
""", unsafe_allow_html=True)

# 5. MENU LATERAL
with st.sidebar:
    st.markdown("<h2 style='color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Preços", "Cadastro", "Dashboard", "Contato"]:
        if st.button(item, use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            st.rerun()

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 6. LÓGICA DE PÁGINAS
if st.session_state.pagina == "Home":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    if not st.session_state.pagamento_ativo:
        with st.form("reserva_form"):
            st.subheader("📅 Agendar Aula")
            aluno = st.text_input("Nome do Aluno")
            email = st.text_input("E-mail")
            servico = st.selectbox("Serviço", ["Aula particular R$ 250/hora", "Aula em grupo R$ 200/hora", "Treinamento competitivo R$ 1.400/mes"])
            unidade = st.selectbox("Unidade", ["PLAY TENNIS Ibirapuera", "TOP One Tennis", "MELL Tennis", "ARENA BTG Morumbi"])
            c1, c2 = st.columns(2)
            with c1: dt = st.date_input("Data", format="DD/MM/YYYY")
            with c2: hr = st.selectbox("Horário", [f"{h:02d}:00" for h in range(7, 23)])
            
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO", use_container_width=True):
                if aluno and email:
                    st.session_state.reserva_temp = {
                        "Data": dt.strftime("%d/%m/%Y"), "Horário": hr, "Aluno": aluno, 
                        "Serviço": servico, "Unidade": unidade, "E-mail": email, "Status": "Pendente"
                    }
                    st.session_state.pagamento_ativo = True
                    st.rerun()
    else:
        st.subheader("💳 Pagamento via PIX")
        st.image("https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=aranha.corp@gmail.com")
        
        if st.button("CONFIRMAR PAGAMENTO", type="primary"):
            try:
                # CORREÇÃO AQUI: ttl=0 força o app a ler TODOS os registros antigos antes de adicionar o novo
                df_antigo = conn.read(worksheet="Página1", ttl=0)
                
                # Criar o DataFrame do novo registro
                novo_registro = pd.DataFrame([st.session_state.reserva_temp])
                
                # Concatenar (empilhar) o novo registro abaixo dos antigos
                df_final = pd.concat([df_antigo, novo_registro], ignore_index=True)
                
                # Atualizar a planilha inteira com o histórico completo
                conn.update(worksheet="Página1", data=df_final)
                
                st.success("✅ Agendamento salvo com sucesso no histórico!")
                st.session_state.pagamento_ativo = False
                time.sleep(2)
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Dashboard":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("📊 Histórico de Reservas")
    # ttl=0 para garantir que você veja os registros novos e antigos sem delay
    df_exibicao = conn.read(worksheet="Página1", ttl=0)
    st.dataframe(df_exibicao, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
