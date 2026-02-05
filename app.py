import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import re
import uuid
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, Optional
import ssl
import os

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

# LINKS CORRIGIDOS DOS FORMULÁRIOS
FORM_LINKS = {
    "professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?usp=dialog",
    "aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?usp=dialog",
    "academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform?usp=dialog"
}

TEMPO_PAGAMENTO = 300  # 5 minutos em segundos

# ============================================
# 2. FUNÇÕES AUXILIARES
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

def obter_credenciais_email():
    """Obtém credenciais de e-mail com fallback hierárquico."""
    # 1. Tentar secrets do Streamlit primeiro
    try:
        secrets = st.secrets
        email_user = secrets.get("EMAIL_USER", "aranha.corp@gmail.com")
        email_password = secrets.get("EMAIL_PASSWORD", "")
        
        if email_password:
            return email_user, email_password
    except Exception:
        pass
    
    # 2. Tentar variáveis de ambiente
    email_password_env = os.environ.get("EMAIL_PASSWORD", "")
    if email_password_env:
        return "aranha.corp@gmail.com", email_password_env
    
    # 3. Retornar None se não encontrar
    return "aranha.corp@gmail.com", ""

def enviar_email_confirmacao(aluno: str, email: str, reserva_info: Dict[str, Any], reserva_id: str) -> bool:
    """Envia e-mail de confirmação de reserva para o aluno."""
    try:
        # Obter credenciais
        email_remetente, email_senha = obter_credenciais_email()
        
        if not email_senha:
            st.error("❌ Senha do e-mail não configurada. Configure EMAIL_PASSWORD nos secrets do Streamlit.")
            st.info("📝 Instruções de configuração:")
            st.markdown("""
            1. Crie um arquivo `.streamlit/secrets.toml` no diretório do projeto
            2. Adicione as seguintes linhas:
            ```toml
            EMAIL_USER = "aranha.corp@gmail.com"
            EMAIL_PASSWORD = "sua_senha_de_app_gerada"
            ```
            3. Para Gmail, gere uma "senha de app" em: Google Account → Segurança → Senhas de app
            """)
            return False
        
        # Configurações do servidor SMTP (Gmail)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # Criar mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🎾 Tennis Class - Confirmação de Reserva #{reserva_id}"
        msg['From'] = f"Tennis Class <{email_remetente}>"
        msg['To'] = email
        msg['Reply-To'] = "aranha.corp@gmail.com"
        
        # Extrair dados da reserva
        servico = reserva_info.get('Serviço', '')
        unidade = reserva_info.get('Unidade', '')
        data = reserva_info.get('Data', '')
        horario = reserva_info.get('Horário', '')
        
        # Obter informações da academia
        info_academia = ACADEMIAS.get(unidade, {})
        endereco_academia = info_academia.get('endereco', '')
        telefone_academia = info_academia.get('telefone', '')
        
        # Corpo do e-mail em HTML (versão corrigida)
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Confirmação de Reserva - TENNIS CLASS</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    line-height: 1.6;
                    color: #333333;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: #ffffff;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #1a5f7a 0%, #2a8bb8 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: bold;
                }}
                .content {{
                    padding: 30px;
                }}
                .reserva-id {{
                    background: #f8f9fa;
                    border-left: 4px solid #3498db;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                    font-family: 'Courier New', monospace;
                    font-size: 16px;
                    font-weight: bold;
                }}
                .info-box {{
                    background: #f8f9fa;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                    border: 1px solid #eaeaea;
                }}
                .info-item {{
                    margin-bottom: 10px;
                    padding-bottom: 10px;
                    border-bottom: 1px solid #eeeeee;
                    display: flex;
                }}
                .info-label {{
                    font-weight: bold;
                    color: #2c3e50;
                    min-width: 120px;
                }}
                .info-value {{
                    color: #34495e;
                }}
                .status {{
                    display: inline-block;
                    background: #27ae60;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 14px;
                }}
                .instructions {{
                    background: #e8f4fc;
                    border-left: 4px solid #3498db;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .instructions ul {{
                    margin: 10px 0;
                    padding-left: 20px;
                }}
                .instructions li {{
                    margin-bottom: 8px;
                }}
                .whatsapp-btn {{
                    display: inline-block;
                    background: #25D366;
                    color: white;
                    text-decoration: none;
                    padding: 12px 25px;
                    border-radius: 5px;
                    margin-top: 15px;
                    font-weight: bold;
                    font-size: 16px;
                }}
                .whatsapp-btn:hover {{
                    background: #128C7E;
                }}
                .footer {{
                    background: #2c3e50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                }}
                .footer a {{
                    color: #3498db;
                    text-decoration: none;
                }}
                @media (max-width: 600px) {{
                    .container {{
                        width: 100%;
                        border-radius: 0;
                    }}
                    .content {{
                        padding: 15px;
                    }}
                    .info-item {{
                        flex-direction: column;
                    }}
                    .info-label {{
                        min-width: 100%;
                        margin-bottom: 5px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎾 TENNIS CLASS</h1>
                    <p>Confirmação de Reserva</p>
                </div>
                
                <div class="content">
                    <h2 style="color: #2c3e50; margin-top: 0;">Olá, {aluno}!</h2>
                    <p>Sua reserva foi confirmada com sucesso. Abaixo estão os detalhes:</p>
                    
                    <div class="reserva-id">
                        <strong>ID da Reserva:</strong> {reserva_id}
                    </div>
                    
                    <div class="info-box">
                        <h3 style="color: #2c3e50; margin-top: 0;">📋 Detalhes da Reserva</h3>
                        <div class="info-item">
                            <div class="info-label">Aluno:</div>
                            <div class="info-value">{aluno}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Serviço:</div>
                            <div class="info-value">{servico}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Data:</div>
                            <div class="info-value">{data}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Horário:</div>
                            <div class="info-value">{horario}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Unidade:</div>
                            <div class="info-value">{unidade}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Status:</div>
                            <div class="info-value">
                                <span class="status">CONFIRMADO</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="info-box">
                        <h3 style="color: #2c3e50; margin-top: 0;">📍 Informações da Academia</h3>
                        <div class="info-item">
                            <div class="info-label">Endereço:</div>
                            <div class="info-value">{endereco_academia}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Telefone:</div>
                            <div class="info-value">{telefone_academia}</div>
                        </div>
                    </div>
                    
                    <div class="instructions">
                        <h3 style="color: #2c3e50; margin-top: 0;">📝 Instruções Importantes</h3>
                        <ul>
                            <li>Chegue <strong>15 minutos antes</strong> do horário marcado</li>
                            <li>Use roupas esportivas apropriadas para prática de tênis</li>
                            <li>Traga sua raquete ou alugue na recepção (R$ 20,00)</li>
                            <li>Em caso de cancelamento, avise com <strong>24h de antecedência</strong></li>
                            <li>Apresente o <strong>ID da reserva</strong> na chegada</li>
                            <li>Traga uma garrafa de água ou compre na academia</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="https://wa.me/5511971425028?text=Olá!%20Tenho%20uma%20reserva%20com%20ID%20{reserva_id}" 
                           class="whatsapp-btn" 
                           target="_blank">
                            📱 Falar no WhatsApp
                        </a>
                    </div>
                    
                    <p style="margin-top: 30px; color: #7f8c8d; font-size: 14px;">
                        <strong>Observação:</strong> Em caso de dúvidas, entre em contato através do WhatsApp acima 
                        ou responda este e-mail.
                    </p>
                </div>
                
                <div class="footer">
                    <p><strong>TENNIS CLASS</strong> © {datetime.now().year}</p>
                    <p>Este é um e-mail automático, por favor não responda diretamente.</p>
                    <p>
                        <strong>Contato:</strong> 
                        <a href="mailto:aranha.corp@gmail.com">aranha.corp@gmail.com</a> | 
                        (11) 97142-5028
                    </p>
                    <p style="font-size: 10px; opacity: 0.8; margin-top: 10px;">
                        Para sua segurança, nunca compartilhe suas credenciais de acesso.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Versão alternativa em texto puro para clientes de e-mail que não suportam HTML
        texto = f"""
        TENNIS CLASS - Confirmação de Reserva #{reserva_id}
        
        Olá, {aluno}!
        
        Sua reserva foi confirmada com sucesso. Abaixo estão os detalhes:
        
        ID da Reserva: {reserva_id}
        
        DETALHES DA RESERVA:
        - Aluno: {aluno}
        - Serviço: {servico}
        - Data: {data}
        - Horário: {horario}
        - Unidade: {unidade}
        - Status: CONFIRMADO
        
        INFORMAÇÕES DA ACADEMIA:
        - Endereço: {endereco_academia}
        - Telefone: {telefone_academia}
        
        INSTRUÇÕES IMPORTANTES:
        1. Chegue 15 minutos antes do horário marcado
        2. Use roupas esportivas apropriadas
        3. Traga sua raquete ou alugue na recepção
        4. Em caso de cancelamento, avise com 24h de antecedência
        5. Apresente o ID da reserva na chegada
        
        Contato WhatsApp: (11) 97142-5028
        
        TENNIS CLASS © {datetime.now().year}
        Este é um e-mail automático, por favor não responda diretamente.
        """
        
        # Anexar partes HTML e texto
        msg.attach(MIMEText(texto, 'plain'))
        msg.attach(MIMEText(html, 'html'))
        
        # Enviar e-mail com tratamento de erro detalhado
        try:
            # Criar contexto SSL seguro
            context = ssl.create_default_context()
            
            # Conectar ao servidor SMTP
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            
            # Fazer login
            server.login(email_remetente, email_senha)
            
            # Enviar e-mail
            server.send_message(msg)
            
            # Encerrar conexão
            server.quit()
            
            st.success(f"✅ E-mail de confirmação enviado para {email}")
            return True
            
        except smtplib.SMTPAuthenticationError as auth_err:
            st.error("❌ Erro de autenticação SMTP. Verifique:")
            st.error("1. Se o usuário e senha estão corretos")
            st.error("2. Se a 'senha de app' foi gerada corretamente no Google")
            st.error("3. Se a verificação em duas etapas está ativada")
            return False
            
        except smtplib.SMTPException as smtp_err:
            st.error(f"❌ Erro SMTP: {str(smtp_err)}")
            return False
            
        except Exception as conn_err:
            st.error(f"❌ Erro de conexão: {str(conn_err)}")
            return False
        
    except Exception as e:
        st.error(f"❌ Erro ao preparar e-mail: {str(e)}")
        return False

def salvar_reserva(reserva: Dict[str, Any]) -> tuple[bool, str]:
    """Salva uma reserva no Google Sheets com tratamento de erros."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = carregar_dados()
        
        # Adiciona ID único e timestamp
        reserva_id = str(uuid.uuid4())[:8]
        reserva["ID"] = reserva_id
        reserva["Timestamp"] = datetime.now().isoformat()
        reserva["Status"] = "Pendente"
        
        df_novo = pd.concat([df, pd.DataFrame([reserva])], ignore_index=True)
        conn.update(worksheet="Página1", data=df_novo)
        
        # Limpa cache para próxima leitura
        st.cache_data.clear()
        
        return True, reserva_id
        
    except Exception as e:
        st.error(f"❌ Erro ao salvar reserva: {str(e)}")
        return False, ""

def validar_email(email: str) -> bool:
    """Valida formato de e-mail."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validar_nome(nome: str) -> bool:
    """Valida nome (mínimo 3 caracteres, apenas letras e espaços)."""
    nome_limpo = nome.strip()
    if len(nome_limpo) < 3:
        return False
    # Permite letras, espaços e caracteres acentuados comuns em português
    return bool(re.match(r'^[a-zA-ZÀ-ÿ\s]+$', nome_limpo))

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

if 'reserva_id_gerada' not in st.session_state:
    st.session_state.reserva_id_gerada = None

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
    .reserva-id-box {
        background-color: #f8f9fa;
        border: 2px solid #28a745;
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
        text-align: center;
        font-family: 'Courier New', monospace;
        font-size: 1.2rem;
        font-weight: bold;
        color: #28a745;
    }
    .email-confirmation {
        background-color: #e8f5e9;
        border: 2px solid #4CAF50;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        text-align: center;
    }
    .email-confirmation h3 {
        color: #2e7d32;
        margin-top: 0;
    }
    .email-status {
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        text-align: center;
        font-weight: bold;
    }
    .email-success {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .email-error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .email-instructions {
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
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
    
    # Informações sobre configuração de e-mail
    st.markdown("---")
    with st.expander("⚙️ Configuração de E-mail"):
        st.markdown("""
        ### Para configurar o envio de e-mails:
        
        1. **Crie um arquivo `.streamlit/secrets.toml`**
        
        2. **Adicione as credenciais:**
        
        ```toml
        EMAIL_USER = "aranha.corp@gmail.com"
        EMAIL_PASSWORD = "sua_senha_de_app"
        
        ADMIN_PASSWORD = "aranha2026"
        ```
        
        3. **Para Gmail, gere uma "senha de app":**
           - Acesse: [Google Account → Segurança](https://myaccount.google.com/security)
           - Ative "Verificação em duas etapas" (se não estiver ativa)
           - Em "Senhas de app", gere uma senha para "E-mail"
           - Use essa senha no campo `EMAIL_PASSWORD`
        
        4. **Teste o sistema:**
           - Faça uma reserva de teste
           - Verifique se o e-mail chega
           - Verifique a pasta de spam se necessário
        """)

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

# ============================================
# 6. LÓGICA DE PÁGINAS
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
                label_visibility="visible",
                placeholder="Ex: João Silva"
            )
            
            email = st.text_input(
                "E-mail *",
                help="Digite um e-mail válido para confirmação",
                label_visibility="visible",
                placeholder="exemplo@email.com"
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
                dt = st.date_input("Data *", format="DD/MM/YYYY", min_value=datetime.now().date())
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
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(
                "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=aranha.corp@gmail.com",
                use_column_width=False,
                width=250
            )
        
        # Chave PIX
        st.markdown("### Chave PIX (Copie e Cole):")
        st.code("aranha.corp@gmail.com", language="text")
        
        # Informações da reserva
        st.markdown("### 📋 Resumo da Reserva")
        st.info(f"""
        **Aluno:** {st.session_state.reserva_temp.get('Aluno', '')}  
        **Serviço:** {st.session_state.reserva_temp.get('Serviço', '')}  
        **Unidade:** {st.session_state.reserva_temp.get('Unidade', '')}  
        **Data:** {st.session_state.reserva_temp.get('Data', '')} às {st.session_state.reserva_temp.get('Horário', '')}
        **E-mail:** {st.session_state.reserva_temp.get('E-mail', '')}
        """)
        
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
        
        # Botão de confirmação
        if st.button("✅ CONFIRMAR PAGAMENTO", type="primary", use_container_width=True):
            with st.spinner("Processando reserva e enviando confirmação..."):
                # Salva reserva no Google Sheets
                sucesso, reserva_id = salvar_reserva(st.session_state.reserva_temp)
                
                if sucesso:
                    # Envia e-mail de confirmação
                    email_enviado = enviar_email_confirmacao(
                        aluno=st.session_state.reserva_temp["Aluno"],
                        email=st.session_state.reserva_temp["E-mail"],
                        reserva_info=st.session_state.reserva_temp,
                        reserva_id=reserva_id
                    )
                    
                    # Limpa estado
                    st.session_state.reserva_id_gerada = reserva_id
                    st.session_state.pagamento_ativo = False
                    
                    # Mostra confirmação
                    st.balloons()
                    
                    # Container de confirmação
                    st.markdown(f"""
                    <div class="email-confirmation">
                        <h3>✅ Reserva Confirmada!</h3>
                        <p>Sua reserva foi registrada com sucesso.</p>
                        <div class="reserva-id-box">
                            ID da Reserva: {reserva_id}
                        </div>
                        <p>Guarde este ID para futuras consultas.</p>
                        <div class="{'email-success' if email_enviado else 'email-error'}">
                            <strong>Status do e-mail:</strong> {"✅ Enviado com sucesso!" if email_enviado else "⚠️ O e-mail não pôde ser enviado"}
                        </div>
                        <p><em>{'Verifique sua caixa de entrada (e spam).' if email_enviado else 'Entre em contato conosco para confirmar sua reserva.'}</em></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Instruções se o e-mail não foi enviado
                    if not email_enviado:
                        st.markdown("""
                        <div class="email-instructions">
                        <h4>📝 O que fazer se não recebeu o e-mail:</h4>
                        <ol>
                            <li>Verifique sua pasta de spam/lixo eletrônico</li>
                            <li>Entre em contato pelo WhatsApp (11) 97142-5028 com seu ID de reserva</li>
                            <li>Guarde o ID da reserva acima para referência</li>
                            <li>Verifique se digitou o e-mail corretamente</li>
                        </ol>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Botão para nova reserva
                    if st.button("📅 Fazer Nova Reserva", use_container_width=True):
                        st.session_state.reserva_temp = {}
                        st.rerun()
                    
                    time.sleep(5)
                    st.session_state.reserva_temp = {}
                    st.rerun()
                else:
                    st.error("❌ Erro ao processar a reserva. Tente novamente.")
    
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
    
    # Criar tabela de preços mais organizada
    col1, col2 = st.columns(2)
    
    with col1:
        for key, info in SERVICOS.items():
            if key in ["particular", "grupo", "kids"]:
                unidade = "/hora"
                st.markdown(f"""
                <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                    <h4 style='margin: 0; color: white;'>{info['nome']}</h4>
                    <p style='margin: 5px 0 0 0; color: #4CAF50; font-weight: bold;'>R$ {info['preco']} {unidade}</p>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        for key, info in SERVICOS.items():
            if key in ["personal", "competitivo", "eventos"]:
                if key == "competitivo":
                    unidade = "/mês"
                    st.markdown(f"""
                    <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                        <h4 style='margin: 0; color: white;'>{info['nome']}</h4>
                        <p style='margin: 5px 0 0 0; color: #4CAF50; font-weight: bold;'>R$ {info['preco']} {unidade}</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif key == "eventos":
                    st.markdown(f"""
                    <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                        <h4 style='margin: 0; color: white;'>{info['nome']}</h4>
                        <p style='margin: 5px 0 0 0; color: #FF9800; font-weight: bold;'>Valor a combinar</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    unidade = "/hora"
                    st.markdown(f"""
                    <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                        <h4 style='margin: 0; color: white;'>{info['nome']}</h4>
                        <p style='margin: 5px 0 0 0; color: #4CAF50; font-weight: bold;'>R$ {info['preco']} {unidade}</p>
                    </div>
                    """, unsafe_allow_html=True)

# PÁGINA: CADASTRO (COM LINKS CORRIGIDOS)
elif st.session_state.pagina == "Cadastro":
    st.markdown(card_com_estilo(""), unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center;'>📝 Portal de Cadastros</h2><br>", 
                unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <a href="{FORM_LINKS['professor']}" 
           class="clean-link" 
           target="_blank"
           aria-label="Cadastro de Professor de Tênis">
            <div class="icon-text">👨‍🏫</div>
            <div class="label-text">PROFESSOR</div>
            <div style="font-size: 12px; margin-top: 10px; opacity: 0.8;">
                Cadastre-se como professor
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <a href="{FORM_LINKS['aluno']}" 
           class="clean-link" 
           target="_blank"
           aria-label="Cadastro de Aluno de Tênis">
            <div class="icon-text">👤</div>
            <div class="label-text">ALUNO</div>
            <div style="font-size: 12px; margin-top: 10px; opacity: 0.8;">
                Cadastre-se como aluno
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <a href="{FORM_LINKS['academia']}" 
           class="clean-link" 
           target="_blank"
           aria-label="Cadastro de Academia de Tênis">
            <div class="icon-text">🏢</div>
            <div class="label-text">ACADEMIA</div>
            <div style="font-size: 12px; margin-top: 10px; opacity: 0.8;">
                Cadastre sua academia
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    # Nota informativa sobre os formulários
    st.markdown("""
    <div class="form-link-note">
        <p><strong>📋 Instruções:</strong> Os formulários abrem em uma nova aba.</p>
        <p>Preencha todos os campos obrigatórios e clique em "Enviar" ao final.</p>
        <p>Após o envio, você receberá um e-mail de confirmação.</p>
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
            help="Senha para acesso ao dashboard",
            placeholder="Digite a senha..."
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
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("🚪 Logout", use_container_width=True):
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
                
                # Ordena por data (mais recente primeiro)
                if 'Data' in df_display.columns:
                    # Converte datas para formato ordenável
                    try:
                        df_display['Data_Ordenavel'] = pd.to_datetime(df_display['Data'], format='%d/%m/%Y', errors='coerce')
                        df_display = df_display.sort_values('Data_Ordenavel', ascending=False)
                        df_display = df_display.drop('Data_Ordenavel', axis=1)
                    except:
                        df_display = df_display.sort_values('Data', ascending=False)
                
                # Adiciona contadores
                total = len(df_display)
                pendentes = len(df_display[df_display['Status'] == 'Pendente'])
                confirmados = len(df_display[df_display['Status'] == 'Confirmado'])
                
                # Métricas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Reservas", total)
                with col2:
                    st.metric("Pendentes", pendentes, delta=None)
                with col3:
                    st.metric("Confirmados", confirmados, delta=None)
                
                st.markdown("---")
                
                # Tabela interativa
                st.dataframe(
                    df_display,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Status": st.column_config.SelectboxColumn(
                            "Status",
                            options=["Pendente", "Confirmado", "Cancelado"],
                            required=True,
                        ),
                        "Aluno": st.column_config.TextColumn("Aluno", width="medium"),
                        "E-mail": st.column_config.TextColumn("E-mail", width="large"),
                        "Serviço": st.column_config.TextColumn("Serviço", width="medium"),
                        "Unidade": st.column_config.TextColumn("Unidade", width="medium"),
                        "Data": st.column_config.TextColumn("Data", width="small"),
                        "Horário": st.column_config.TextColumn("Horário", width="small"),
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
                        file_name=f"reservas_tennis_class_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    
                # Funcionalidade extra: reenviar e-mail
                st.markdown("### 📧 Reenviar E-mail de Confirmação")
                col_id, col_btn = st.columns([3, 1])
                with col_id:
                    reserva_id = st.text_input("ID da Reserva para reenviar e-mail:", placeholder="Ex: abc12345")
                with col_btn:
                    if st.button("↻ Reenviar", use_container_width=True):
                        if reserva_id and not df.empty:
                            reserva = df[df['ID'] == reserva_id]
                            if not reserva.empty:
                                reserva_info = reserva.iloc[0].to_dict()
                                with st.spinner("Enviando e-mail..."):
                                    if enviar_email_confirmacao(
                                        aluno=reserva_info.get('Aluno', ''),
                                        email=reserva_info.get('E-mail', ''),
                                        reserva_info=reserva_info,
                                        reserva_id=reserva_id
                                    ):
                                        st.success(f"✅ E-mail reenviado para {reserva_info.get('E-mail', '')}")
                                    else:
                                        st.error("❌ Erro ao reenviar e-mail")
                            else:
                                st.error("❌ Reserva não encontrada")
                        else:
                            st.warning("⚠️ Digite um ID válido")
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
        st.markdown("### 📧 E-mail")
        st.markdown("""
        <div style='padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px;'>
            <h4 style='margin:0; color: white;'>aranha.corp@gmail.com</h4>
            <p style='margin:5px 0 0 0; color: #ccc;'>
            Respondemos em até 24h
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🏢 Endereço Principal")
        st.markdown("""
        <div style='padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px;'>
            <p style='margin:0; color: white;'>São Paulo - SP</p>
            <p style='margin:5px 0 0 0; color: #ccc;'>
            Atendemos em todas as academias parceiras
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📱 WhatsApp")
        st.markdown("""
        <div style='padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px;'>
            <h4 style='margin:0; color: white;'>(11) 97142-5028</h4>
            <p style='margin:5px 0 0 0; color: #ccc;'>
            Segunda a Sábado, 8h às 20h
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### ⏰ Horário de Atendimento")
        st.markdown("""
        <div style='padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px;'>
            <p style='margin:0; color:
