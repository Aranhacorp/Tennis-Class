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

# 4. DESIGN E ESTILO (CSS INTEGRADO)
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
    .valor-total {
        font-size: 30px; color: #1e5e20; font-weight: bold;
        background-color: #e8f5e9; padding: 15px; border-radius: 12px;
        margin: 15px 0; border: 2px solid #1e5e20;
    }
    /* ALINHAMENTO À ESQUERDA PARA ACADEMIAS NA SIDEBAR */
    .sidebar-info {
        text-align: left !important;
        color: white;
        font-size: 13px;
        margin-bottom: 15px;
        line-height: 1.4;
    }
    .assinatura-aranha { position: fixed; bottom: 20px; left: 20px; width: 150px; z-index: 1000; }
    .whatsapp-float { position: fixed; bottom: 20px; right: 20px; width: 60px; z-index: 1000; }
</style>
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-aranha">
<a href="https://wa.me/5511971425028" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-float">
</a>
""", unsafe_allow_html=True)

# 5. MENU LATERAL E ACADEMIAS (ALINHADO À ESQUERDA)
with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("<h3 style='color: white; text-align: left;'>🏢 Academias Recomendadas</h3>", unsafe_allow_html=True)
    
    # Lista detalhada conforme solicitado
    st.markdown("""
    <div class="sidebar-info">
        <strong>📍 Play Tennis Ibirapuera</strong><br>
        R. Joinville, 401 - Vila Mariana<br>
        📞 (11) 5081-3000
    </div>
    <div class="sidebar-info">
        <strong>📍 Top One Tennis</strong><br>
        R. João Lourenço, 629 - Vila Nova Conceição<br>
        📞 (11) 3845-6688
    </div>
    <div class="sidebar-info">
        <strong>📍 Fontes & Barbeta Tennis</strong><br>
        Av. Professor Ascendino Reis, 724<br>
        📞 (11) 99911-3000
    </div>
    <div class="sidebar-info">
        <strong>📍 Arena BTG</strong><br>
        Av. das Nações Unidas, 13797<br>
        📞 (11) 94555-2200
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 6. PÁGINA HOME: AGENDAMENTO
if st.session_state.pagina == "Home":
    if not st.session_state.pagamento_ativo:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        with st.form("form_reserva"):
            aluno = st.text_input("Nome do Aluno")
            precos = {
                "Aula Individual (R$ 250)": 250,
                "Pacote 4 Aulas (R$ 940)": 940,
                "Pacote 8 Aulas (R$ 1800)": 1800,
                "Aula Kids (R$ 230)": 230
            }
            servico = st.selectbox("Selecione o Serviço", list(precos.keys()))
            local = st.selectbox("Escolha o Local", ["Play Tennis Ibirapuera", "Top One Tennis", "Fontes & Barbeta", "Arena BTG"])
            
            # 📅 PADRÃO BRASILEIRO NO SELETOR
            data_aula = st.date_input("Data da Aula", format="DD/MM/YYYY")
            hora_aula = st.selectbox("Horário", [f"{h:02d}:00" for h in range(7, 22)])
            
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO"):
                if aluno:
                    st.session_state.reserva_temp = {
                        "Data": data_aula.strftime("%d/%m/%Y"), # 📅 GRAVAÇÃO EM PT-BR
                        "Horario": hora_aula,
                        "Aluno": aluno,
                        "Servico": servico,
                        "Status": "Pendente",
                        "Academia": local,
                        "Valor": precos[servico]
                    }
                    st.session_state.pagamento_ativo = True
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # TELA DE PAGAMENTO (VALOR VISÍVEL)
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("### 💳 Pagamento via PIX")
        v_final = f"R$ {st.session_state.reserva_temp['Valor']:.2f}"
        st.markdown(f'<div class="valor-total">VALOR TOTAL: {v_final}</div>', unsafe_allow_html=True)
        st.write("Chave PIX: **aranha.corp@gmail.com.br**")
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
                    dados = st.session_state.reserva_temp.copy()
                    dados.pop("Valor")
                    df_novo = pd.concat([df_atual, pd.DataFrame([dados])], ignore_index=True)
                    conn.update(worksheet="Página1", data=df_novo)
                    st.balloons()
                    st.success("Sua reserva foi salva na planilha!")
                    st.session_state.pagamento_ativo = False
                except Exception as e:
                    st.error(f"Erro ao atualizar planilha: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

# 7. SERVIÇOS
elif st.session_state.pagina == "Serviços":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("## 🎾 Nossos Serviços")
    st.write("- **Aula Particular:** Focada no seu desenvolvimento técnico.")
    st.write("- **Aula em Grupo:** Socialização e dinâmica de jogo.")
    st.write("- **Tennis Kids:** Metodologia lúdica para crianças.")
    st.markdown('</div>', unsafe_allow_html=True)

# 8. CADASTRO
elif st.session_state.pagina == "Cadastro":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### 📝 Cadastro")
    st.write("Preencha seus dados para entrar na nossa lista de atletas.")
    st.markdown('</div>', unsafe_allow_html=True)

# 9. CONTATO
elif st.session_state.pagina == "Contato":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown("### Contato")
    st.write("**E-mail:** aranha.corp@gmail.com.br")
    st.write("**WhatsApp:** (11) 97142-5028")
    st.markdown('</div>', unsafe_allow_html=True)
