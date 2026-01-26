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

# 4. DESIGN E ESTILO (CSS MASTER)
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
        background-color: rgba(255, 255, 255, 0.98) !important; 
        padding: 40px; border-radius: 25px; 
        max-width: 850px; margin: auto; text-align: center; 
        color: #1E1E1E !important; box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    .contact-card {
        background-color: rgba(30, 30, 30, 0.85) !important;
        padding: 45px; border-radius: 30px;
        max-width: 650px; margin: 40px auto; text-align: center;
        color: white !important; border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    }
    .assinatura-aranha { position: fixed; bottom: 25px; left: 25px; width: 180px; z-index: 9999; }
    .whatsapp-float { position: fixed; bottom: 70px; right: 25px; width: 60px; z-index: 9999; }
</style>
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-aranha">
<a href="https://wa.me/5511971425028" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-float">
</a>
""", unsafe_allow_html=True)

# 5. MENU LATERAL
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: white;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"btn_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("<h3 style='color: white;'>🏢 Academias</h3>", unsafe_allow_html=True)
    academias_info = {
        "Play Tennis Ibirapuera": "Rua Estado de Israel, 860",
        "Top One tennis": "Avenida Indianapolis, 647",
        "Fontes & Barbeta Tennis": "Rua Oscar Gomes Cardim, 535",
        "Arena BTG": "Rua Major Sylvio de Magalhães Padilha, 16741"
    }
    for nome, end in academias_info.items():
        with st.expander(nome):
            st.write(f"📍 {end}")

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 6. LÓGICA DAS PÁGINAS
if st.session_state.pagina == "Home":
    if not st.session_state.pagamento_ativo:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        with st.form("form_reserva"):
            aluno = st.text_input("Nome do Aluno")
            servicos_lista = ["Aula Individual", "Aula em Dupla", "Aula em Grupo", "Aula Kids"]
            servico_sel = st.selectbox("Serviço", servicos_lista)
            pacote_sel = st.selectbox("Pacote", ["Único", "Pacote 4 Aulas", "Pacote 8 Aulas"])
            academia_sel = st.selectbox("Academia", list(academias_info.keys()))
            data_sel = st.date_input("Data")
            hora_sel = st.selectbox("Horário", [f"{h:02d}:00" for h in range(7, 22)])
            
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO"):
                if aluno:
                    st.session_state.reserva_temp = {
                        "Data": data_sel.strftime("%Y-%m-%d"),
                        "Horario": hora_sel,
                        "Aluno": aluno,
                        "Servico": servico_sel,
                        "Pacote": pacote_sel,
                        "Status": "Pendente",
                        "Academia": academia_sel
                    }
                    st.session_state.pagamento_ativo = True
                    st.rerun()
                else:
                    st.warning("Por favor, preencha o nome do aluno.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("### 💳 Pagamento via PIX")
        st.write("Chave: **aranha.corp@gmail.com.br**")
        st.file_uploader("Anexe o comprovante (Opcional)", type=['png', 'jpg', 'pdf'])
        
        if st.button("CONFIRMAR AGENDAMENTO", type="primary", use_container_width=True):
            try:
                # Lê a planilha atual
                df_atual = conn.read(worksheet="Página1")
                # Cria o novo registro
                novo_registro = pd.DataFrame([st.session_state.reserva_temp])
                # Concatena e atualiza
                df_final = pd.concat([df_atual, novo_registro], ignore_index=True)
                conn.update(worksheet="Página1", data=df_final)
                
                st.balloons()
                st.success("Tudo pronto! Sua reserva foi enviada e salva na planilha.")
                st.session_state.pagamento_ativo = False
            except Exception as e:
                st.error(f"Erro ao salvar na planilha: {e}")
        
        if st.button("Voltar"):
            st.session_state.pagamento_ativo = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Serviços":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("Nossos Serviços")
    col1, col2 = st.columns(2)
    with col1:
        st.write("🎾 **Aulas Individuais**")
        st.write("👥 **Aulas em Grupo**")
        st.write("👶 **Aulas Kids**")
    with col2:
        st.write("💪 **Treinamento Esportivo**")
        st.write("🏥 **Fisioterapia Esportiva**")
        st.write("📅 **Eventos e Clínicas**")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Cadastro":
    perfil = st.radio("Selecione o perfil:", ["Aluno", "Professor", "Academia"], horizontal=True)
    links = {
        "Professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?embedded=true",
        "Aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?embedded=true",
        "Academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform?embedded=true"
    }
    st.markdown(f'<iframe src="{links[perfil]}" width="100%" height="800" frameborder="0" style="background:white; border-radius:20px;"></iframe>', unsafe_allow_html=True)

elif st.session_state.pagina == "Contato":
    st.markdown("""
        <div class="contact-card">
            <h1>André Aranha</h1>
            <p style="font-size: 20px;">✉️ aranha.corp@gmail.com.br<br>📱 (11) 97142-5028</p>
            <hr style="border-color: rgba(255,255,255,0.1);">
            <p style="font-size: 12px; color: rgba(255,255,255,0.5);">TENNIS CLASS © 2026</p>
        </div>
    """, unsafe_allow_html=True)
