import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import re
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, Optional

# ============================================
# 1. CONFIGURAÇÃO E CONSTANTES
# ============================================

st.set_page_config(
    page_title="TENNIS CLASS",
    layout="wide",
    page_icon="🎾",
    initial_sidebar_state="expanded"
)

# Constantes organizadas
SERVICOS = {
    "particular": {"nome": "Aula particular", "preco": 250},
    "grupo": {"nome": "Aula em grupo", "preco": 200},
    "kids": {"nome": "Aula Kids", "preco": 200},
    "personal": {"nome": "Personal trainer", "preco": 250},
    "competitivo": {"nome": "Treinamento competitivo", "preco": 1400},
    "eventos": {"nome": "Eventos", "preco": 0}
}

ACADEMIAS = {
    "PLAY TENNIS Ibirapuera": {
        "endereco": "R. Estado de Israel, 860 - SP",
        "telefone": "(11) 97752-0488"
    },
    "TOP One Tennis": {
        "endereco": "Av. Indianópolis, 647 - SP",
        "telefone": "(11) 93236-3828"
    },
    "MELL Tennis": {
        "endereco": "Rua Oscar Gomes Cardim, 535 - SP",
        "telefone": "(11) 97142-5028"
    },
    "ARENA BTG Morumbi": {
        "endereco": "Av. Maj. Sylvio de Magalhães Padilha, 16741",
        "telefone": "(11) 98854-3860"
    }
}

# Links corrigidos dos formulários Google Forms
FORM_LINKS = {
    "aluno": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform",
    "academia": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform",
    "professor": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform"
}

# Configurações de e-mail (use secrets do Streamlit)
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": st.secrets.get("EMAIL_USER", "aranha.corp@gmail.com"),
    "sender_password": st.secrets.get("EMAIL_PASSWORD", ""),
    "sender_name": "TENNIS CLASS"
}

TEMPO_PAGAMENTO = 300  # 5 minutos em segundos

# ============================================
# 2. FUNÇÕES AUXILIARES (INCLUINDO E-MAIL)
# ============================================

@st.cache_data(ttl=300)  # Cache de 5 minutos
def carregar_dados() -> pd.DataFrame:
    """Carrega dados do Google Sheets com cache."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn.read(worksheet="Página1")
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

def salvar_reserva(reserva: Dict[str, Any]) -> bool:
    """Salva uma reserva no Google Sheets com tratamento de erros."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = carregar_dados()
        
        # Adiciona ID único e timestamp
        reserva["ID"] = str(uuid.uuid4())[:8]
        reserva["Timestamp"] = datetime.now().isoformat()
        reserva["Status"] = "Pendente"
        
        df_novo = pd.concat([df, pd.DataFrame([reserva])], ignore_index=True)
        conn.update(worksheet="Página1", data=df_novo)
        
        # Limpa cache para próxima leitura
        st.cache_data.clear()
        
        return True
    except Exception as e:
        st.error(f"❌ Erro ao salvar reserva: {str(e)}")
        return False

def enviar_email_confirmacao(reserva: Dict[str, Any], destinatario: str) -> bool:
    """Envia e-mail de confirmação da reserva."""
    try:
        # Configurar credenciais de e-mail
        email_user = EMAIL_CONFIG["sender_email"]
        email_password = EMAIL_CONFIG["sender_password"]
        
        # Se não houver senha configurada, use alternativa (log apenas)
        if not email_password:
            st.warning("⚠️ Senha de e-mail não configurada. Configure em secrets.toml")
            return False
        
        # Criar mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"✅ Confirmação de Reserva - TENNIS CLASS"
        msg['From'] = f"{EMAIL_CONFIG['sender_name']} <{email_user}>"
        msg['To'] = destinatario
        msg['Reply-To'] = "aranha.corp@gmail.com"
        
        # Extrair informações da reserva
        data_reserva = reserva.get("Data", "Não informado")
        horario = reserva.get("Horário", "Não informado")
        aluno = reserva.get("Aluno", "Não informado")
        servico = reserva.get("Serviço", "Não informado")
        unidade = reserva.get("Unidade", "Não informado")
        reserva_id = reserva.get("ID", "N/A")
        
        # HTML do e-mail
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .details {{ background-color: white; border-left: 4px solid #4CAF50; padding: 20px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
                .button {{ display: inline-block; background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                .whatsapp {{ background-color: #25D366; margin-left: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎾 TENNIS CLASS</h1>
                    <h2>Reserva Confirmada!</h2>
                </div>
                
                <div class="content">
                    <p>Olá <strong>{aluno}</strong>,</p>
                    <p>Sua reserva foi confirmada com sucesso! Aqui estão os detalhes:</p>
                    
                    <div class="details">
                        <h3>📋 Detalhes da Reserva</h3>
                        <p><strong>ID da Reserva:</strong> {reserva_id}</p>
                        <p><strong>Data:</strong> {data_reserva}</p>
                        <p><strong>Horário:</strong> {horario}</p>
                        <p><strong>Serviço:</strong> {servico}</p>
                        <p><strong>Unidade:</strong> {unidade}</p>
                        <p><strong>Status:</strong> ✅ Confirmado</p>
                        <p><strong>Data da Confirmação:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    </div>
                    
                    <p>📝 <strong>Importante:</strong></p>
                    <ul>
                        <li>Chegue com 15 minutos de antecedência</li>
                        <li>Traga roupa esportiva adequada e tênis</li>
                        <li>Em caso de cancelamento, avise com 24h de antecedência</li>
                    </ul>
                    
                    <p>📍 <strong>Localização:</strong></p>
                    <p>Consulte o endereço completo da unidade {unidade} no nosso site.</p>
                    
                    <div style="text-align: center;">
                        <a href="https://tennis-class-app.streamlit.app/" class="button" target="_blank">
                            Acessar Portal
                        </a>
                        <a href="https://wa.me/5511971425028" class="button whatsapp" target="_blank">
                            WhatsApp
                        </a>
                    </div>
                </div>
                
                <div class="footer">
                    <p>TENNIS CLASS © {datetime.now().year}</p>
                    <p>Este é um e-mail automático, por favor não responda.</p>
                    <p>Dúvidas? Contate-nos: aranha.corp@gmail.com</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Versão texto simples (fallback)
        text_content = f"""
        TENNIS CLASS - Confirmação de Reserva
        
        Olá {aluno},
        
        Sua reserva foi confirmada com sucesso!
        
        📋 DETALHES DA RESERVA:
        ID: {reserva_id}
        Data: {data_reserva}
        Horário: {horario}
        Serviço: {servico}
        Unidade: {unidade}
        Status: Confirmado
        Data da Confirmação: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        
        📝 IMPORTANTE:
        - Chegue com 15 minutos de antecedência
        - Traga roupa esportiva adequada
        - Cancelamentos com 24h de antecedência
        
        📍 LOCALIZAÇÃO:
        Consulte o endereço da unidade {unidade} no nosso site.
        
        📞 CONTATO:
        WhatsApp: (11) 97142-5028
        E-mail: aranha.corp@gmail.com
        Site: https://tennis-class-app.streamlit.app/
        
        TENNIS CLASS © {datetime.now().year}
        Este é um e-mail automático.
        """
        
        # Adicionar partes ao e-mail
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Enviar e-mail
        with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
            server.starttls()
            server.login(email_user, email_password)
            server.send_message(msg)
        
        return True
        
    except smtplib.SMTPAuthenticationError:
        st.error("❌ Falha na autenticação do e-mail. Verifique as credenciais.")
        return False
    except Exception as e:
        st.error(f"❌ Erro ao enviar e-mail: {str(e)}")
        return False

def validar_email(email: str) -> bool:
    """Valida formato de e-mail."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validar_nome(nome: str) -> bool:
    """Valida nome (mínimo 3 caracteres, apenas letras e espaços)."""
    nome_limpo = nome.strip()
    if len(nome_limpo) < 3:
        return False
    return all(c.isalpha() or c.isspace() for c in nome_limpo)

def mostrar_timer(tempo_total: int, inicio_time: float) -> tuple[bool, str]:
    """Calcula e formata o tempo restante."""
    restante = tempo_total - (time.time() - inicio_time)
    if restante <= 0:
        return False, "⏰ Tempo esgotado!"
    
    m, s = divmod(int(restante), 60)
    return True, f"⏱️ Expira em: {m:02d}:{s:02d}"

def card_com_estilo(conteudo: str, classe: str = "custom-card") -> str:
    """Retorna HTML de card estilizado."""
    return f'<div class="{classe}">{conteudo}</div>'

# ============================================
# 3. ESTADOS DA SESSÃO
# ============================================

if 'pagina' not in st.session_state:
    st.session_state.pagina = "Home"

if 'pagamento_ativo' not in st.session_state:
    st.session_state.pagamento_ativo = False

if 'reserva_temp' not in st.session_state:
    st.session_state.reserva_temp = {}

if 'inicio_timer' not in st.session_state:
    st.session_state.inicio_timer = None

if 'admin_autenticado' not in st.session_state:
    st.session_state.admin_autenticado = False

if 'erros_form' not in st.session_state:
    st.session_state.erros_form = {}

# ============================================
# 4. CSS GLOBAL E COMPONENTES FIXOS
# ============================================

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; 
        background-position: center; 
        background-attachment: fixed;
    }
    .header-title { 
        color: white; 
        font-size: 50px; 
        font-weight: bold; 
        text-align: center; 
        margin-bottom: 20px; 
        text-shadow: 2px 2px 4px black; 
    }
    .custom-card { 
        background-color: rgba(255, 255, 255, 0.95); 
        padding: 30px; 
        border-radius: 20px; 
        color: #333; 
        position: relative; 
    }
    .translucent-balloon { 
        background-color: rgba(50, 50, 50, 0.85); 
        padding: 25px; 
        border-radius: 15px; 
        color: white; 
        backdrop-filter: blur(10px); 
        margin-bottom: 20px; 
        border: 1px solid rgba(255,255,255,0.1); 
    }
    .clean-link { 
        text-align: center; 
        text-decoration: none !important; 
        color: white !important; 
        transition: 0.3s; 
        display: block; 
        padding: 20px; 
    }
    .clean-link:hover { 
        transform: translateY(-8px); 
        color: #4CAF50 !important; 
    }
    .icon-text { 
        font-size: 80px; 
        margin-bottom: 10px; 
    }
    .label-text { 
        font-size: 20px; 
        font-weight: bold; 
        letter-spacing: 2px; 
    }
    .whatsapp-float { 
        position: fixed; 
        width: 60px; 
        height: 60px; 
        bottom: 40px; 
        right: 40px; 
        background-color: #25d366; 
        color: #FFF; 
        border-radius: 50px; 
        text-align: center; 
        font-size: 35px; 
        box-shadow: 2px 2px 3px #999; 
        z-index: 9999; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        text-decoration: none; 
    }
    .regulamento-icon { 
        display: block; 
        text-align: center; 
        margin-top: 20px; 
        text-decoration: none; 
        color: #555; 
        font-size: 14px; 
        transition: 0.3s; 
    }
    .regulamento-icon span { 
        font-size: 24px; 
        display: block; 
    }
    .regulamento-icon:hover { 
        color: #4CAF50; 
        transform: scale(1.05); 
    }
    .assinatura-footer { 
        position: fixed; 
        bottom: 15px; 
        left: 20px; 
        width: 130px; 
        z-index: 9999; 
        opacity: 0.8; 
    }
    .sidebar-detalhe { 
        font-size: 11px; 
        color: #ccc; 
        margin-bottom: 10px; 
        line-height: 1.2; 
    }
    .error-message {
        color: #ff4444;
        font-size: 14px;
        margin-top: 5px;
        padding: 5px;
        border-radius: 4px;
        background-color: rgba(255, 68, 68, 0.1);
    }
    .success-message {
        color: #00C851;
        font-size: 14px;
        margin-top: 5px;
        padding: 5px;
        border-radius: 4px;
        background-color: rgba(0, 200, 81, 0.1);
    }
    .timer-warning {
        color: #ff8800;
        font-weight: bold;
        font-size: 16px;
        text-align: center;
        padding: 10px;
        border: 2px solid #ff8800;
        border-radius: 10px;
        background-color: rgba(255, 136, 0, 0.1);
    }
    .form-link-note {
        text-align: center;
        margin-top: 20px;
        padding: 15px;
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        color: #ccc;
    }
    .form-link-note p {
        margin: 0;
    }
    .email-status {
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
        text-align: center;
    }
    .email-success {
        background-color: rgba(0, 200, 81, 0.2);
        border: 2px solid #00C851;
        color: #00C851;
    }
    .email-warning {
        background-color: rgba(255, 136, 0, 0.2);
        border: 2px solid #ff8800;
        color: #ff8800;
    }
</style>

<!-- Botão flutuante do WhatsApp -->
<a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank" 
   aria-label="Contato via WhatsApp">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" 
         width="35" alt="Ícone do WhatsApp">
</a>

<!-- Assinatura -->
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" 
     class="assinatura-footer" 
     alt="Assinatura André Aranha">
""", unsafe_allow_html=True)

# ============================================
# 5. MENU LATERAL
# ============================================

with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", 
                unsafe_allow_html=True)
    
    for item in ["Home", "Preços", "Cadastro", "Dashboard", "Contato"]:
        if st.button(item, key=f"nav_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 🏢 ACADEMIAS RECOMENDADAS")
    
    for nome, info in ACADEMIAS.items():
        st.markdown(
            f"📍 **{nome}**\n"
            f"<div class='sidebar-detalhe'>"
            f"{info['endereco']}<br>📞 {info['telefone']}"
            f"</div>", 
            unsafe_allow_html=True
        )

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# ============================================
# 6. LÓGICA DE PÁGINAS - COM ENVIO DE E-MAIL
# ============================================

# PÁGINA: HOME
if st.session_state.pagina == "Home":
    st.markdown(card_com_estilo(""), unsafe_allow_html=True)
    
    if not st.session_state.pagamento_ativo:
        with st.form("reserva_form", clear_on_submit=True):
            st.subheader("📅 Agendar Aula")
            
            # Campos do formulário com validação
            aluno = st.text_input(
                "Nome do Aluno *",
                help="Digite seu nome completo (mínimo 3 caracteres)",
                label_visibility="visible"
            )
            
            email = st.text_input(
                "E-mail *",
                help="Digite um e-mail válido para confirmação",
                label_visibility="visible"
            )
            
            # Lista de serviços formatada
            servicos_lista = [
                f"{SERVICOS[key]['nome']} R$ {SERVICOS[key]['preco']}"
                f"{'/hora' if key != 'competitivo' else '/mês'}"
                for key in SERVICOS.keys()
            ]
            
            servico = st.selectbox("Serviço *", servicos_lista)
            unidade = st.selectbox("Unidade *", list(ACADEMIAS.keys()))
            
            c1, c2 = st.columns(2)
            with c1:
                dt = st.date_input("Data *", format="DD/MM/YYYY")
            with c2:
                hr = st.selectbox("Horário *", [f"{h:02d}:00" for h in range(7, 23)])
            
            # Botão de submissão
            submit = st.form_submit_button(
                "AVANÇAR PARA PAGAMENTO", 
                use_container_width=True
            )
            
            if submit:
                st.session_state.erros_form = {}
                
                # Validação
                if not validar_nome(aluno):
                    st.session_state.erros_form['aluno'] = "Nome inválido. Use apenas letras (mínimo 3 caracteres)."
                
                if not validar_email(email):
                    st.session_state.erros_form['email'] = "E-mail inválido. Digite um e-mail válido."
                
                if not st.session_state.erros_form:
                    st.session_state.reserva_temp = {
                        "Data": dt.strftime("%d/%m/%Y"),
                        "Horário": hr,
                        "Aluno": aluno.strip(),
                        "Serviço": servico,
                        "Unidade": unidade,
                        "E-mail": email.lower().strip()
                    }
                    st.session_state.pagamento_ativo = True
                    st.session_state.inicio_timer = time.time()
                    st.rerun()
                else:
                    # Mostra erros
                    for campo, mensagem in st.session_state.erros_form.items():
                        st.markdown(f'<div class="error-message">❌ {mensagem}</div>', 
                                  unsafe_allow_html=True)
    
    else:  # PAGAMENTO ATIVO
        st.subheader("💳 Pagamento via PIX")
        
        # QR Code
        st.image(
            "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=aranha.corp@gmail.com",
            use_column_width=False,
            width=250
        )
        
        # Chave PIX
        st.code("aranha.corp@gmail.com", language="text")
        
        # Timer otimizado
        timer_box = st.empty()
        
        if st.session_state.inicio_timer:
            ativo, mensagem_timer = mostrar_timer(
                TEMPO_PAGAMENTO, 
                st.session_state.inicio_timer
            )
            
            if ativo:
                timer_box.markdown(
                    f'<div class="timer-warning">{mensagem_timer}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.session_state.pagamento_ativo = False
                timer_box.warning("⏰ Tempo esgotado! Por favor, inicie uma nova reserva.")
                time.sleep(2)
                st.rerun()
        
        # Botão de confirmação COM ENVIO DE E-MAIL
        if st.button("CONFIRMAR PAGAMENTO", type="primary", use_container_width=True):
            if salvar_reserva(st.session_state.reserva_temp):
                st.balloons()
                
                # ENVIAR E-MAIL DE CONFIRMAÇÃO
                email_destinatario = st.session_state.reserva_temp.get("E-mail", "")
                email_enviado = False
                
                if email_destinatario and validar_email(email_destinatario):
                    with st.spinner("📧 Enviando e-mail de confirmação..."):
                        email_enviado = enviar_email_confirmacao(
                            st.session_state.reserva_temp, 
                            email_destinatario
                        )
                
                # Mostrar mensagem de sucesso
                if email_enviado:
                    st.markdown(f"""
                    <div class="email-status email-success">
                        <h3>✅ Reserva confirmada!</h3>
                        <p>E-mail de confirmação enviado para <strong>{email_destinatario}</strong></p>
                        <p>Verifique sua caixa de entrada e spam.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="email-status email-warning">
                        <h3>✅ Reserva confirmada no sistema!</h3>
                        <p><strong>Atenção:</strong> Não foi possível enviar o e-mail de confirmação.</p>
                        <p>Por favor, anote os detalhes da sua reserva:</p>
                        <p><strong>ID:</strong> {st.session_state.reserva_temp.get("ID", "N/A")}</p>
                        <p>Entre em contato pelo WhatsApp se precisar de assistência.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Limpa estado e aguarda para redirecionar
                st.session_state.pagamento_ativo = False
                st.session_state.reserva_temp = {}
                time.sleep(5)
                st.rerun()
    
    # Ícone do regulamento
    st.markdown("""
    <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
    <a href="https://docs.google.com/document/d/1LW9CNdmgYxwnpXlDYRrE8rKsLdajbPi3fniwXVsBqco/edit?usp=sharing" 
       target="_blank" 
       class="regulamento-icon" 
       title="Clique para ler o regulamento">
        <span>📄</span>
        Ler Regulamento de Uso
    </a>
    """, unsafe_allow_html=True)

# PÁGINA: PREÇOS
elif st.session_state.pagina == "Preços":
    st.markdown(card_com_estilo(""), unsafe_allow_html=True)
    
    st.markdown("### 🎾 Tabela de Preços")
    st.markdown("---")
    
    for key, info in SERVICOS.items():
        if key == "eventos":
            st.markdown(f"* **{info['nome']}:** Valor a combinar")
        else:
            unidade = "/hora" if key != "competitivo" else "/mês"
            st.markdown(f"* **{info['nome']}:** R$ {info['preco']} {unidade}")

# PÁGINA: CADASTRO
elif st.session_state.pagina == "Cadastro":
    st.markdown(card_com_estilo(""), unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center;'>📝 Portal de Cadastros</h2><br>", 
                unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <a href="{FORM_LINKS['aluno']}" 
           class="clean-link" 
           target="_blank"
           aria-label="Cadastro de Aluno">
            <div class="icon-text">👤</div>
            <div class="label-text">ALUNO</div>
        </a>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <a href="{FORM_LINKS['academia']}" 
           class="clean-link" 
           target="_blank"
           aria-label="Cadastro de Academia">
            <div class="icon-text">🏢</div>
            <div class="label-text">ACADEMIA</div>
        </a>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <a href="{FORM_LINKS['professor']}" 
           class="clean-link" 
           target="_blank"
           aria-label="Cadastro de Professor">
            <div class="icon-text">🎾</div>
            <div class="label-text">PROFESSOR</div>
        </a>
        """, unsafe_allow_html=True)
    
    # Nota informativa sobre os formulários
    st.markdown("""
    <div class="form-link-note">
        <p><strong>Nota:</strong> Os formulários abrem em uma nova aba. 
        Caso tenha problemas, verifique se seu navegador permite pop-ups.</p>
    </div>
    """, unsafe_allow_html=True)

# PÁGINA: DASHBOARD
elif st.session_state.pagina == "Dashboard":
    st.markdown(card_com_estilo(""), unsafe_allow_html=True)
    
    if not st.session_state.admin_autenticado:
        st.subheader("🔐 Acesso Administrativo")
        
        # Usa secrets do Streamlit (configurar no .streamlit/secrets.toml)
        senha_correta = st.secrets.get("ADMIN_PASSWORD", "aranha2026")
        
        senha = st.text_input(
            "Digite a senha de administrador:", 
            type="password",
            label_visibility="visible",
            help="Senha para acesso ao dashboard"
        )
        
        if st.button("Acessar", use_container_width=True):
            if senha == senha_correta:
                st.session_state.admin_autenticado = True
                st.success("✅ Acesso concedido!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Senha incorreta!")
    
    else:
        st.subheader("📊 Dashboard - Reservas")
        
        # Botão de logout
        if st.button("🚪 Logout", use_container_width=False):
            st.session_state.admin_autenticado = False
            st.rerun()
        
        st.markdown("---")
        
        # Carrega e exibe dados
        try:
            df = carregar_dados()
            
            if not df.empty:
                # Formata colunas
                colunas_exibir = [col for col in df.columns if col not in ['ID', 'Timestamp']]
                df_display = df[colunas_exibir].copy()
                
                # Adiciona contadores
                total = len(df_display)
                pendentes = len(df_display[df_display['Status'] == 'Pendente'])
                confirmados = len(df_display[df_display['Status'] == 'Confirmado'])
                
                # Métricas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Reservas", total)
                with col2:
                    st.metric("Pendentes", pendentes)
                with col3:
                    st.metric("Confirmados", confirmados)
                
                st.markdown("---")
                
                # Tabela interativa
                st.dataframe(
                    df_display.sort_values('Data', ascending=False),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Status": st.column_config.SelectboxColumn(
                            "Status",
                            options=["Pendente", "Confirmado", "Cancelado"],
                            required=True,
                        )
                    }
                )
                
                # Botões de ação
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Atualizar Dados", use_container_width=True):
                        st.cache_data.clear()
                        st.success("Dados atualizados!")
                        st.rerun()
                
                with col2:
                    csv = df_display.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Exportar CSV",
                        data=csv,
                        file_name="reservas_tennis_class.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            else:
                st.info("📭 Nenhuma reserva encontrada.")
                
        except Exception as e:
            st.error(f"❌ Erro ao carregar dashboard: {str(e)}")

# PÁGINA: CONTATO
elif st.session_state.pagina == "Contato":
    st.markdown(card_com_estilo(""), unsafe_allow_html=True)
    
    st.subheader("📞 Canais de Atendimento")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📧 E-mail
