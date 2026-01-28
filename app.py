import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="TENNIS CLASS", layout="wide", page_icon="🎾")

# 2. CONEXÃO COM A PLANILHA (TennisClass_DB)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. ESTADOS DA SESSÃO
if 'pagina' not in st.session_state: st.session_state.pagina = "Home"
if 'pagamento_ativo' not in st.session_state: st.session_state.pagamento_ativo = False
if 'reserva_temp' not in st.session_state: st.session_state.reserva_temp = {}
if 'academia_foco' not in st.session_state: st.session_state.academia_foco = None

# 4. FUNÇÃO DE ENVIO DE E-MAIL
def enviar_confirmacao(dados):
    remetente = "aranha.corp@gmail.com"
    senha = "xmtw pnyq wsav iock" 
    try:
        msg = MIMEMultipart()
        msg['From'], msg['To'] = remetente, dados['Email_Aluno']
        msg['Subject'] = "Reserva Confirmada - TENNIS CLASS"
        corpo = f"Olá {dados['Aluno']},\n\nSua reserva foi confirmada!\nLocal: {dados['Academia']}\nData: {dados['Data']} às {dados['Horario']}\nServiço: {dados['Servico']}"
        msg.attach(MIMEText(corpo, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remetente, senha)
        server.send_message(msg)
        server.quit()
        return True
    except: return False

# 5. DESIGN, ASSINATURA E WHATSAPP FLUTUANTE
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    .header-title { color: white; font-size: 50px; font-weight: bold; text-align: center; margin-bottom: 20px; text-shadow: 2px 2px 4px black; }
    .custom-card { background-color: rgba(255, 255, 255, 0.95); padding: 30px; border-radius: 20px; color: #333; }
    .translucent-balloon { background-color: rgba(50, 50, 50, 0.85); padding: 25px; border-radius: 15px; color: white; backdrop-filter: blur(10px); margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1); }
    .btn-cadastro { display: block; width: 100%; background-color: #1e5e20; color: white !important; padding: 15px; margin: 10px 0; border-radius: 10px; text-decoration: none; font-weight: bold; text-align: center; }
    .sidebar-detalhe { color: #f0f0f0; font-size: 13px; margin: -10px 0 15px 35px; border-left: 2px solid #ff4b4b; padding-left: 10px; }
    .assinatura-footer { position: fixed; bottom: 20px; left: 20px; width: 150px; z-index: 1000; }
    .whatsapp-footer { position: fixed; bottom: 20px; right: 20px; width: 60px; z-index: 1000; transition: 0.3s; }
    .whatsapp-footer:hover { transform: scale(1.1); }
</style>
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" class="assinatura-footer">
<a href="https://wa.me/5511971425028" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" class="whatsapp-footer">
</a>
""", unsafe_allow_html=True)

# 6. MENU LATERAL E ACADEMIAS
info_academias = {
    "Play Tennis Ibirapuera": "R. Joinville, 401 - Vila Mariana | 📞 (11) 5081-3000",
    "Top One Tennis": "R. João Lourenço, 629 - Vila Nova Conceição | 📞 (11) 3845-6688",
    "Fontes & Barbeta Tennis": "Av. Prof. Ascendino Reis, 724 | 📞 (11) 99911-3000",
    "Arena BTG": "Av. das Nações Unidas, 13797 | 📞 (11) 94555-2200"
}

with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", unsafe_allow_html=True)
    for item in ["Home", "Serviços", "Produtos", "Cadastro", "Contato"]:
        if st.button(item, key=f"nav_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("<h3 style='color: white;'>🏢 Academias</h3>", unsafe_allow_html=True)
    for nome in info_academias.keys():
        if st.button(f"📍 {nome}", key=f"side_{nome}", use_container_width=True):
            st.session_state.academia_foco = nome if st.session_state.academia_foco != nome else None
        if st.session_state.academia_foco == nome:
            st.markdown(f'<div class="sidebar-detalhe">{info_academias[nome]}</div>', unsafe_allow_html=True)

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# 7. LÓGICA DAS PÁGINAS
if st.session_state.pagina == "Home":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    if not st.session_state.pagamento_ativo:
        with st.form("form_reserva"): # Correção de indentação
            st.subheader("📅 Agendar Aula")
            aluno = st.text_input("Nome do Aluno")
            email = st.text_input("E-mail para Confirmação")
            servico = st.selectbox("Serviço", ["Aula Individual (R$ 250/h)", "Aula em Grupo (R$ 200/h)", "Aula Kids (R$ 200/h)", "Treinamento (R$ 1.200/mês)"])
            local = st.selectbox("Unidade", list(info_academias.keys()))
            data_aula = st.date_input("Data", format="DD/MM/YYYY")
            hora_aula = st.selectbox("Horário", [f"{h:02d}:00" for h in range(7, 22)])
            
            if st.form_submit_button("AVANÇAR PARA PAGAMENTO"):
                if aluno and email:
                    st.session_state.reserva_temp = {
                        "Data": data_aula.strftime("%Y-%m-%d"), "Horario": hora_aula,
                        "Aluno": aluno, "Servico": servico, "Status": "Pendente",
                        "Academia": local, "Email_Aluno": email
                    } # Fechamento correto de chave
                    st.session_state.pagamento_ativo = True
                    st.rerun()
    else:
        st.subheader("💳 Pagamento via PIX")
        col_qr, col_info = st.columns([1, 1])
        with col_qr:
            # Gerador de QR Code simplificado via API pública
            qr_url = "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=aranha.corp@gmail.com"
            st.image(qr_url, caption="Escaneie para Pagar")
        with col_info:
            st.write(f"**Valor:** {st.session_state.reserva_temp['Servico']}")
            st.info("Chave PIX: aranha.corp@gmail.com")
            st.code("aranha.corp@gmail.com", language="text") # Copia e Cola
        
        if st.button("CONFIRMAR AGENDAMENTO FINAL"):
            try:
                df_existente = conn.read(worksheet="Página1")
                df_novo = pd.concat([df_existente, pd.DataFrame([st.session_state.reserva_temp])], ignore_index=True)
                conn.update(worksheet="Página1", data=df_novo) # Fechamento de parêntese
                enviar_confirmacao(st.session_state.reserva_temp)
                st.success("Reserva salva e e-mail enviado!")
                st.balloons()
                st.session_state.pagamento_ativo = False
            except Exception as e: st.error(f"Erro ao salvar: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Serviços": #
    st.markdown('<div class="translucent-balloon">', unsafe_allow_html=True)
    st.markdown("## 🎾 Tabela de Preços")
    st.write("- **Individual:** R$ 250/h")
    st.write("- **Grupo/Kids:** R$ 200/h")
    st.write("- **Treinamento:** R$ 1.200/mês")
    st.write("- **Eventos:** Sob consulta")
    st.markdown('</div>', unsafe_allow_html=True) # Fechamento correto de markdown

elif st.session_state.pagina == "Cadastro": #
    st.markdown('<div class="translucent-balloon">', unsafe_allow_html=True)
    st.subheader("📝 Portal de Cadastros")
    st.markdown('<a href="https://docs.google.com/forms/d/e/1FAIpQLSdyHq5Wf1uCjL9fQG-Alp6N7qYqY/viewform" class="btn-cadastro">👤 Cadastro de Aluno</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://docs.google.com/forms/d/e/1FAIpQLSdO7N_E2vP6P-fS9jR_Wk7K-G_X_v/viewform" class="btn-cadastro">🏢 Cadastro de Academia</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://docs.google.com/forms/d/e/1FAIpQLSffh7vW9Z_rYvYvYvYvYvYvYvYv/viewform" class="btn-cadastro">🎾 Cadastro de Professor</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Contato":
    st.markdown('<div class="translucent-balloon">', unsafe_allow_html=True)
    st.subheader("📞 Fale com Andre Aranha")
    st.write("📩 aranha.corp@gmail.com")
    st.write("📱 (11) 97142-5028")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Produtos": # Correção de aspas triplas
    st.markdown('<div class="translucent-balloon"><h3>🎒 Loja Tennis Class</h3><p>Equipamentos em breve.</p></div>', unsafe_allow_html=True)
