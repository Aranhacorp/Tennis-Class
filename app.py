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

# 4. CSS GLOBAL E COMPONENTES FIXOS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .header-title { color: white; font-size: 50px; font-weight: bold; text-align: center; margin-bottom: 20px; text-shadow: 2px 2px 4px black; }
    .custom-card { background-color: rgba(255, 255, 255, 0.95); padding: 30px; border-radius: 20px; color: #333; }
    .translucent-balloon { background-color: rgba(50, 50, 50, 0.85); padding: 25px; border-radius: 15px; color: white; backdrop-filter: blur(10px); margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1); }
    .whatsapp-float { position: fixed; width: 60px; height: 60px; bottom: 40px; right: 40px; background-color: #25d366; color: #FFF; border-radius: 50px; text-align: center; font-size: 35px; box-shadow: 2px 2px 3px #999; z-index: 9999; display: flex; align-items: center; justify-content: center; text-decoration: none; }
    .assinatura-footer { position: fixed; bottom: 15px; left: 20px; width: 130px; z-index: 9999; opacity: 0.8; }
    .sidebar-detalhe { font-size: 11px; color: #ccc; margin-bottom: 10px; line-height: 1.2; }
</style>
<a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="35"></a>
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-footer">
""", unsafe_allow_html=True)

# 5. MENU LATERAL E ACADEMIAS
with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Preços", "Cadastro", "Dashboard", "Contato"]:
        if st.button(item, key=f"nav_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            st.rerun()
    st.markdown("---")
    st.markdown("### 🏢 ACADEMIAS RECOMENDADAS")
    academias = {
        "PLAY TENNIS Ibirapuera": "R. Estado de Israel, 860 - SP\n📞 (11) 97752-0488",
        "TOP One Tennis": "Av. Indianópolis, 647 - SP\n📞 (11) 93236-3828",
        "MELL Tennis": "Rua Oscar Gomes Cardim, 535 - SP\n📞 (11) 97142-5028",
        "ARENA BTG Morumbi": "Av. Maj. Sylvio de Magalhães Padilha, 16741\n📞 (11) 98854-3860"
    }
    for nome, info in academias.items():
        st.markdown(f"📍 **{nome}**\n<div class='sidebar-detalhe'>{info}</div>", unsafe_allow_html=True)

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 6. PÁGINA HOME (Onde ocorre a gravação)
if st.session_state.pagina == "Home":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    if not st.session_state.pagamento_ativo:
        with st.form("reserva_form"):
            st.subheader("📅 Agendar Aula")
            aluno = st.text_input("Nome do Aluno")
            email_aluno = st.text_input("E-mail")
            # Mapeamento exato para as colunas da Planilha
            servicos = ["Aula Individual (R$ 250/h)", "Aula em Grupo R$ 200/hora", "Aula Kids (R$ 200/h)", "Treinamento competitivo: R$ 1.400 / mês"]
            servico_selecionado = st.selectbox("Serviço", servicos)
            academia_selecionada = st.selectbox("Unidade", list(academias.keys()))
            
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO", use_container_width=True):
                if aluno and email_aluno:
                    # Chaves ajustadas para as colunas C, D, G, H da planilha
                    st.session_state.reserva_temp = {
                        "Aluno": aluno, 
                        "Serviço": servico_selecionado, 
                        "Unidade": academia_selecionada,
                        "E-mail": email_aluno,
                        "Status": "Pendente"
                    }
                    st.session_state.pagamento_ativo = True
                    st.session_state.inicio_timer = time.time()
                    st.rerun()
    else:
        st.subheader("💳 Pagamento via PIX")
        st.image("https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=aranha.corp@gmail.com")
        st.code("aranha.corp@gmail.com", language="text")
        if st.button("CONFIRMAR PAGAMENTO", type="primary"):
            try:
                df = conn.read(worksheet="Página1")
                # Garante que as colunas existam no DataFrame antes do concat
                df_novo = pd.concat([df, pd.DataFrame([st.session_state.reserva_temp])], ignore_index=True)
                conn.update(worksheet="Página1", data=df_novo)
                st.success("✅ Reserva gravada com sucesso!")
                st.session_state.pagamento_ativo = False
                time.sleep(2); st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
        
        restante = 300 - (time.time() - st.session_state.inicio_timer)
        if restante <= 0: st.session_state.pagamento_ativo = False; st.rerun()
        m, s = divmod(int(restante), 60)
        st.warning(f"⏱️ Tempo restante: {m:02d}:{s:02d}")
        time.sleep(1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Outras páginas simplificadas para manter o foco na correção
elif st.session_state.pagina == "Dashboard":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    if st.session_state.admin_autenticado or st.text_input("Senha", type="password") == "aranha2026":
        st.session_state.admin_autenticado = True
        st.dataframe(conn.read(worksheet="Página1"), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
