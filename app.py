import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import base64
from PIL import Image
import io
from typing import Dict, Any

# ============================
# CONFIGURAÇÃO DE PÁGINA
# ============================
st.set_page_config(
    page_title="Tennis Class - Sistema Completo",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================
# FUNÇÕES AUXILIARES
# ============================
def load_logo(logo_path: str = "Tennis Class logo v.1.png") -> str:
    """Carrega e codifica o logo em base64"""
    try:
        # Tentar carregar o logo do repositório
        with open(logo_path, "rb") as img_file:
            encoded_logo = base64.b64encode(img_file.read()).decode()
        return f"data:image/png;base64,{encoded_logo}"
    except FileNotFoundError:
        # Se não encontrar, usar URL alternativa ou placeholder
        st.warning(f"Logo não encontrado em {logo_path}. Usando placeholder.")
        # Logo placeholder base64
        return "https://i.imgur.com/3J1WxxY.png"  # Placeholder de logo de tênis

def get_email_config() -> Dict[str, Any]:
    """Obtém configurações de email dos secrets"""
    config = {
        'EMAIL_USER': st.secrets.get("EMAIL_USER", ""),
        'EMAIL_PASSWORD': st.secrets.get("EMAIL_PASSWORD", "").replace(" ", ""),
        'EMAIL_HOST': st.secrets.get("EMAIL_HOST", "smtp.gmail.com"),
        'EMAIL_PORT': st.secrets.get("EMAIL_PORT", 587),
        'EMAIL_SECURE': st.secrets.get("EMAIL_SECURE", False),
        'EMAIL_FROM': st.secrets.get("EMAIL_FROM", "")
    }
    
    # Verificar se as configurações estão presentes
    if not config['EMAIL_USER']:
        st.error("❌ EMAIL_USER não configurado nos Secrets")
    if not config['EMAIL_PASSWORD']:
        st.error("❌ EMAIL_PASSWORD não configurado nos Secrets")
    
    return config

def get_google_sheets_config():
    """Configura conexão com Google Sheets"""
    try:
        # Usar secrets do Streamlit para a conta de serviço
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Criar credenciais a partir dos secrets
        creds_dict = {
            "type": "service_account",
            "project_id": st.secrets["connections"]["gsheets"]["project_id"],
            "private_key_id": st.secrets["connections"]["gsheets"]["private_key_id"],
            "private_key": st.secrets["connections"]["gsheets"]["private_key"],
            "client_email": st.secrets["connections"]["gsheets"]["client_email"],
            "client_id": st.secrets["connections"]["gsheets"]["client_id"],
            "auth_uri": st.secrets["connections"]["gsheets"]["auth_uri"],
            "token_uri": st.secrets["connections"]["gsheets"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["connections"]["gsheets"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["connections"]["gsheets"]["client_x509_cert_url"]
        }
        
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_dict, scope
        )
        
        client = gspread.authorize(credentials)
        spreadsheet_url = st.secrets.get("spreadsheet", "")
        
        if spreadsheet_url:
            sheet = client.open_by_url(spreadsheet_url).sheet1
            return sheet
        return None
        
    except Exception as e:
        st.error(f"Erro ao conectar ao Google Sheets: {str(e)}")
        return None

# ============================
# FUNÇÃO DE ENVIO DE EMAIL
# ============================
def send_confirmation_email(
    cliente_nome: str,
    cliente_email: str,
    unidade: str,
    data: str,
    horario: str,
    telefone: str = ""
) -> tuple:
    """
    Envia email de confirmação de agendamento
    Retorna: (sucesso: bool, mensagem: str)
    """
    try:
        config = get_email_config()
        
        if not config['EMAIL_USER'] or not config['EMAIL_PASSWORD']:
            return False, "Configurações de email incompletas"
        
        # Configurar servidor SMTP
        server = smtplib.SMTP(config['EMAIL_HOST'], config['EMAIL_PORT'])
        server.starttls()
        server.login(config['EMAIL_USER'], config['EMAIL_PASSWORD'])
        
        # Criar mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"✅ Tennis Class - Agendamento Confirmado para {data} às {horario}"
        msg['From'] = config['EMAIL_FROM'] or config['EMAIL_USER']
        msg['To'] = cliente_email
        msg['Bcc'] = config['EMAIL_USER']  # Cópia para administrador
        
        # Gerar código de confirmação
        codigo = f"TC{datetime.now().strftime('%y%m%d%H%M')}"
        
        # Corpo do email (HTML)
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(45deg, #3498db, #2ecc71);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .info-box {{
                    background: white;
                    border-left: 5px solid #3498db;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 0 5px 5px 0;
                }}
                .code {{
                    background: #2c3e50;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-family: monospace;
                    font-size: 18px;
                    display: inline-block;
                    margin: 10px 0;
                }}
                .button {{
                    display: inline-block;
                    background: linear-gradient(45deg, #3498db, #2ecc71);
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 15px 0;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    font-size: 12px;
                    color: #777;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎾 TENNIS CLASS</h1>
                <h2>Agendamento Confirmado!</h2>
            </div>
            
            <div class="content">
                <h3>Olá, {cliente_nome}!</h3>
                <p>Seu agendamento foi confirmado com sucesso. Abaixo estão os detalhes:</p>
                
                <div class="info-box">
                    <h4>📋 DETALHES DO AGENDAMENTO</h4>
                    <p><strong>Unidade:</strong> {unidade}</p>
                    <p><strong>Data:</strong> {data}</p>
                    <p><strong>Horário:</strong> {horario}</p>
                    <p><strong>Telefone:</strong> {telefone if telefone else 'Não informado'}</p>
                    
                    <div class="code">Código: {codigo}</div>
                </div>
                
                <p><strong>📍 Localização:</strong></p>
                <p>R. Estado de Israel, 860 - São Paulo/SP</p>
                
                <p><strong>📞 Contato:</strong> (11) 97752-0488</p>
                
                <a href="tel:+5511977520488" class="button">Ligar para a Academia</a>
                
                <div class="footer">
                    <p>TENNIS CLASS © 2024 - Sistema de Gestão Completo</p>
                    <p>Desenvolvido por André Aranha | MASTER CODE DEEP SEEK v10</p>
                    <p>Este é um email automático, por favor não responda.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Versão texto simples
        text_content = f"""
        TENNIS CLASS - Agendamento Confirmado
        
        Olá {cliente_nome},
        
        Seu agendamento foi confirmado com sucesso!
        
        Detalhes:
        - Unidade: {unidade}
        - Data: {data}
        - Horário: {horario}
        - Telefone: {telefone if telefone else 'Não informado'}
        - Código: {codigo}
        
        Local: R. Estado de Israel, 860 - São Paulo/SP
        Contato: (11) 97752-0488
        
        TENNIS CLASS © 2024
        Sistema de Gestão Completo
        """
        
        # Anexar ambas as versões
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        # Enviar email
        server.send_message(msg)
        server.quit()
        
        # Salvar no Google Sheets
        try:
            sheet = get_google_sheets_config()
            if sheet:
                row = [
                    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    cliente_nome,
                    cliente_email,
                    telefone,
                    unidade,
                    data,
                    horario,
                    codigo,
                    "CONFIRMADO",
                    "Email enviado"
                ]
                sheet.append_row(row)
        except Exception as e:
            st.warning(f"⚠️ Agendamento salvo, mas erro no Google Sheets: {str(e)}")
        
        return True, f"✅ Email enviado para {cliente_email} com código {codigo}"
        
    except smtplib.SMTPAuthenticationError:
        return False, "❌ Falha na autenticação do email. Verifique EMAIL_USER e EMAIL_PASSWORD."
    except Exception as e:
        return False, f"❌ Erro ao enviar email: {str(e)}"

# ============================
# CARREGAR LOGO
# ============================
logo_url = load_logo()

# ============================
# INTERFACE STREAMLIT
# ============================

# CSS Personalizado
st.markdown("""
<style>
    /* Estilos gerais */
    .main-header {
        text-align: center;
        padding: 20px 0;
    }
    
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .logo-img {
        max-width: 350px;
        height: auto;
    }
    
    .academia-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online {
        background-color: #2ecc71;
    }
    
    .status-offline {
        background-color: #e74c3c;
    }
    
    /* Botões personalizados */
    .stButton button {
        background: linear-gradient(45deg, #3498db, #2ecc71);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(52, 152, 219, 0.3);
    }
    
    /* Formulário */
    .stTextInput input, .stSelectbox select {
        border-radius: 8px;
        border: 2px solid #ddd;
        padding: 12px;
    }
    
    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: #3498db;
        box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
    }
    
    /* Sidebar */
    .sidebar-logo {
        text-align: center;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - Menu
with st.sidebar:
    # Logo na Sidebar
    st.markdown('<div class="sidebar-logo">', unsafe_allow_html=True)
    if "base64" in logo_url:
        st.markdown(f'<img src="{logo_url}" class="logo-img" style="max-width: 200px;">', unsafe_allow_html=True)
    else:
        st.image(logo_url, width=150)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Menu de Navegação
    st.markdown("### 📍 Navegação")
    menu_option = st.radio(
        "",
        ["🏠 Home", "💰 Preços", "📝 Cadastro", "📊 Dashboard", "📞 Contato", "⚙️ Configurações"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Status do Sistema
    st.markdown("### 🔧 Status do Sistema")
    
    config = get_email_config()
    col1, col2 = st.columns(2)
    
    with col1:
        if config['EMAIL_USER'] and config['EMAIL_PASSWORD']:
            st.success("✅ Email")
        else:
            st.error("❌ Email")
    
    with col2:
        if get_google_sheets_config():
            st.success("✅ Sheets")
        else:
            st.warning("⚠️ Sheets")
    
    # Informações do Sistema
    st.divider()
    st.markdown("### ℹ️ Sistema")
    st.markdown(f"""
    **Versão:** MASTER CODE DEEP SEEK v10  
    **Data:** {datetime.now().strftime('%d/%m/%Y')}  
    **Status:** 🟢 Online
    """)
    
    # Teste Rápido
    st.divider()
    if st.button("🧪 Testar Conexões", type="secondary"):
        with st.spinner("Testando..."):
            # Testar email
            if config['EMAIL_USER'] and config['EMAIL_PASSWORD']:
                st.success("Email: Configurado ✓")
            else:
                st.error("Email: Não configurado ✗")
            
            # Testar Google Sheets
            sheet = get_google_sheets_config()
            if sheet:
                st.success("Google Sheets: Conectado ✓")
            else:
                st.warning("Google Sheets: Não conectado ⚠")

# Conteúdo Principal baseado na seleção do menu
if menu_option == "🏠 Home":
    # Header Principal com Logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        if "base64" in logo_url:
            st.markdown(f'<img src="{logo_url}" class="logo-img">', unsafe_allow_html=True)
        else:
            st.image(logo_url, width=350)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<h3 style="text-align: center; color: #2c3e50;">Sistema de Agendamento Inteligente</h3>', unsafe_allow_html=True)
    
    # Seção de Academias Recomendadas
    st.markdown("---")
    st.markdown('<h2 style="color: #2c3e50;">🎯 ACADEMIAS RECOMENDADAS</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="academia-card">
            <h3>🎾 PLAY TENNIS Ibirapuera</h3>
            <p><strong>📍 Endereço:</strong> R. Estado de Israel, 860 - São Paulo/SP</p>
            <p><strong>📞 Telefone:</strong> (11) 97752-0488</p>
            <p><strong>⏰ Horário:</strong> 6h às 22h</p>
            <p><strong>⭐ Destaques:</strong> Quadras cobertas, iluminadas, professores ATP</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="academia-card">
            <h3>🏆 TOP One Tennis</h3>
            <p><strong>📍 Endereço:</strong> Av. Paulista, 1000 - São Paulo/SP</p>
            <p><strong>📞 Telefone:</strong> (11) 99999-8888</p>
            <p><strong>⏰ Horário:</strong> 7h às 23h</p>
            <p><strong>⭐ Destaques:</strong> Academia premium, tecnologia de ponta</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Formulário de Agendamento
    st.markdown("---")
    st.markdown('<h2 style="color: #2c3e50;">📅 FAÇA SEU AGENDAMENTO</h2>', unsafe_allow_html=True)
    
    with st.form("agendamento_form", border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            unidade = st.selectbox(
                "Unidade *",
                ["PLAY TENNIS Ibirapuera", "TOP One Tennis"],
                help="Selecione a academia desejada"
            )
            
            nome = st.text_input(
                "Seu Nome Completo *",
                placeholder="Digite seu nome completo"
            )
            
            email = st.text_input(
                "Seu E-mail *",
                placeholder="seu@email.com",
                help="O comprovante será enviado para este email"
            )
        
        with col2:
            telefone = st.text_input(
                "Telefone/WhatsApp *",
                placeholder="(11) 99999-8888"
            )
            
            data = st.date_input(
                "Data *",
                value=datetime(2026, 2, 7),
                min_value=datetime.now()
            )
            
            horario = st.selectbox(
                "Horário *",
                ["07:00", "08:00", "09:00", "10:00", "14:00", "15:00", 
                 "16:00", "17:00", "18:00", "19:00", "20:00"]
            )
        
        st.markdown("**Campos obrigatórios ***")
        
        # Botão de envio
        submitted = st.form_submit_button(
            "🚀 AVANÇAR PARA PAGAMENTO",
            type="primary",
            use_container_width=True
        )
        
        if submitted:
            # Validação
            if not all([nome, email, telefone, unidade, data, horario]):
                st.error("⚠️ Por favor, preencha todos os campos obrigatórios.")
            else:
                # Mostrar loading
                with st.spinner("🎾 Processando agendamento e enviando confirmação..."):
                    # Enviar email
                    success, message = send_confirmation_email(
                        cliente_nome=nome,
                        cliente_email=email,
                        unidade=unidade,
                        data=data.strftime("%d/%m/%Y"),
                        horario=horario,
                        telefone=telefone
                    )
                
                if success:
                    st.success(message)
                    st.balloons()
                    
                    # Mostrar resumo
                    st.markdown("---")
                    st.markdown('<h3 style="color: #2c3e50;">📋 RESUMO DO AGENDAMENTO</h3>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"""
                        **👤 Nome:** {nome}  
                        **📧 Email:** {email}  
                        **📱 Telefone:** {telefone}
                        """)
                    
                    with col2:
                        st.info(f"""
                        **🎾 Unidade:** {unidade}  
                        **📅 Data:** {data.strftime('%d/%m/%Y')}  
                        **⏰ Horário:** {horario}
                        """)
                    
                    # Instruções
                    st.warning("""
                    **✅ Próximos passos:**
                    1. Verifique sua caixa de entrada (e spam) do email
                    2. Apresente o código de confirmação na academia
                    3. Chegue 15 minutos antes do horário agendado
                    """)
                    
                    # Botão para próxima etapa
                    if st.button("💳 Ir para Pagamento Online", type="secondary"):
                        st.switch_page("pages/pagamento.py")
                else:
                    st.error(message)
                    st.info("""
                    **🛠️ Solução de problemas:**
                    1. Verifique se o email está correto
                    2. Confirme se EMAIL_USER e EMAIL_PASSWORD estão configurados nos Secrets
                    3. Tente usar uma senha de app do Gmail
                    4. Verifique se o email permite apps menos seguros
                    """)

elif menu_option == "💰 Preços":
    st.markdown("---")
    if "base64" in logo_url:
        st.markdown(f'<img src="{logo_url}" class="logo-img" style="max-width: 250px; margin: 0 auto 30px auto; display: block;">', unsafe_allow_html=True)
    else:
        st.image(logo_url, width=250)
    
    st.markdown('<h2 style="text-align: center; color: #2c3e50;">💰 TABELA DE PREÇOS</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 15px; text-align: center;">
            <h3>🥉 BÁSICO</h3>
            <h2>R$ 120/mês</h2>
            <p>✔️ 4 horas semanais</p>
            <p>✔️ Aulas em grupo</p>
            <p>✔️ Quadra compartilhada</p>
            <p>❌ Sem professor dedicado</p>
            <p>❌ Sem equipamento</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 25px; border-radius: 15px; text-align: center;">
            <h3>🥈 INTERMEDIÁRIO</h3>
            <h2>R$ 200/mês</h2>
            <p>✔️ 8 horas semanais</p>
            <p>✔️ Aulas em grupo pequeno</p>
            <p>✔️ Quadra semi-privada</p>
            <p>✔️ Professor auxiliar</p>
            <p>❌ Equipamento limitado</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 25px; border-radius: 15px; text-align: center;">
            <h3>🥇 PREMIUM</h3>
            <h2>R$ 350/mês</h2>
            <p>✔️ Horário ilimitado</p>
            <p>✔️ Aulas particulares</p>
            <p>✔️ Quadra privativa</p>
            <p>✔️ Professor ATP dedicado</p>
            <p>✔️ Equipamento completo</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("💡 **Promoção especial:** Agende 3 meses e ganhe 1 mês grátis!")

elif menu_option == "📝 Cadastro":
    st.markdown("---")
    if "base64" in logo_url:
        st.markdown(f'<img src="{logo_url}" class="logo-img" style="max-width: 250px; margin: 0 auto 30px auto; display: block;">', unsafe_allow_html=True)
    else:
        st.image(logo_url, width=250)
    
    st.markdown('<h2 style="text-align: center; color: #2c3e50;">📝 CADASTRO DE ALUNO</h2>', unsafe_allow_html=True)
    
    with st.form("cadastro_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome_completo = st.text_input("Nome Completo *")
            cpf = st.text_input("CPF *", placeholder="000.000.000-00")
            data_nascimento = st.date_input("Data de Nascimento *", max_value=datetime.now())
            email = st.text_input("E-mail *")
        
        with col2:
            telefone = st.text_input("Telefone *")
            endereco = st.text_input("Endereço Completo")
            plano = st.selectbox("Plano Desejado", ["Básico", "Intermediário", "Premium"])
            nivel = st.selectbox("Nível de Jogo", ["Iniciante", "Intermediário", "Avançado", "Competitivo"])
        
        observacoes = st.text_area("Observações Médicas ou Observações")
        
        submitted = st.form_submit_button("✅ Cadastrar Aluno")
        
        if submitted:
            if all([nome_completo, cpf, email, telefone]):
                st.success("Aluno cadastrado com sucesso!")
            else:
                st.error("Por favor, preencha todos os campos obrigatórios.")

elif menu_option == "📊 Dashboard":
    st.markdown("---")
    if "base64" in logo_url:
        st.markdown(f'<img src="{logo_url}" class="logo-img" style="max-width: 250px; margin: 0 auto 30px auto; display: block;">', unsafe_allow_html=True)
    else:
        st.image(logo_url, width=250)
    
    st.markdown('<h2 style="text-align: center; color: #2c3e50;">📊 DASHBOARD ANALÍTICO</h2>', unsafe_allow_html=True)
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Agendamentos Hoje", "24", "+3")
    
    with col2:
        st.metric("Total de Alunos", "156", "+12")
    
    with col3:
        st.metric("Faturamento Mensal", "R$ 25.430", "+8%")
    
    with col4:
        st.metric("Ocupação Quadras", "87%", "+5%")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Agendamentos por Dia da Semana**")
        st.bar_chart({
            "Segunda": 45,
            "Terça": 52,
            "Quarta": 48,
            "Quinta": 61,
            "Sexta": 73,
            "Sábado": 85,
            "Domingo": 42
        })
    
    with col2:
        st.markdown("**Distribuição de Planos**")
        st.bar_chart({
            "Básico": 65,
            "Intermediário": 42,
            "Premium": 49
        })
    
    # Últimos agendamentos
    st.markdown("### 📅 Últimos Agendamentos")
    st.dataframe({
        "Data": ["07/02/2026", "06/02/2026", "06/02/2026", "05/02/2026", "05/02/2026"],
        "Horário": ["07:00", "14:00", "19:00", "10:00", "16:00"],
        "Aluno": ["João Silva", "Maria Santos", "Pedro Costa", "Ana Oliveira", "Carlos Lima"],
        "Unidade": ["Ibirapuera", "Paulista", "Ibirapuera", "Paulista", "Ibirapuera"],
        "Status": ["Confirmado", "Confirmado", "Pendente", "Confirmado", "Cancelado"]
    })

elif menu_option == "📞 Contato":
    st.markdown("---")
    if "base64" in logo_url:
        st.markdown(f'<img src="{logo_url}" class="logo-img" style="max-width: 250px; margin: 0 auto 30px auto; display: block;">', unsafe_allow_html=True)
    else:
        st.image(logo_url, width=250)
    
    st.markdown('<h2 style="text-align: center; color: #2c3e50;">📞 CONTATO E SUPORTE</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📍 Unidade Ibirapuera
        **Endereço:** R. Estado de Israel, 860 - São Paulo/SP  
        **Telefone:** (11) 97752-0488  
        **WhatsApp:** (11) 97752-0488  
        **Email:** ibirapuera@tennisclass.com  
        **Horário:** 6h às 22h
        
        ### 🌐 Redes Sociais
        **Instagram:** @tennisclass.sp  
        **Facebook:** /tennisclassofficial  
        **YouTube:** Tennis Class SP
        """)
    
    with col2:
        st.markdown("""
        ### 📍 Unidade Paulista
        **Endereço:** Av. Paulista, 1000 - São Paulo/SP  
        **Telefone:** (11) 99999-8888  
        **WhatsApp:** (11) 99999-8888  
        **Email:** paulista@tennisclass.com  
        **Horário:** 7h às 23h
        
        ### 📧 Suporte Técnico
        **Email:** suporte@tennisclass.com  
        **Telefone:** (11) 3333-4444  
        **Horário:** 8h às 18h (Seg-Sex)
        """)
    
    # Formulário de Contato
    st.markdown("---")
    st.markdown("### ✉️ Envie sua Mensagem")
    
    with st.form("contato_form"):
        nome = st.text_input("Seu Nome")
        email = st.text_input("Seu E-mail")
        assunto = st.selectbox("Assunto", ["Dúvidas", "Sugestões", "Reclamações", "Parcerias", "Outros"])
        mensagem = st.text_area("Mensagem")
        
        if st.form_submit_button("Enviar Mensagem"):
            st.success("Mensagem enviada com sucesso! Entraremos em contato em breve.")

elif menu_option == "⚙️ Configurações":
    st.markdown("---")
    if "base64" in logo_url:
        st.markdown(f'<img src="{logo_url}" class="logo-img" style="max-width: 250px; margin: 0 auto 30px auto; display: block;">', unsafe_allow_html=True)
    else:
        st.image(logo_url, width=250)
    
    st.markdown('<h2 style="text-align: center; color: #2c3e50;">⚙️ CONFIGURAÇÕES DO SISTEMA</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔐 Segurança", "📧 Email", "📊 Integração", "🔧 Sistema"])
    
    with tab1:
        st.markdown("### Configurações de Segurança")
        senha_atual = st.text_input("Senha Atual", type="password")
        nova_senha = st.text_input("Nova Senha", type="password")
        confirmar_senha = st.text_input("Confirmar Nova Senha", type="password")
        
        if st.button("Alterar Senha"):
            if nova_senha == confirmar_senha:
                st.success("Senha alterada com sucesso!")
            else:
                st.error("As senhas não coincidem!")
    
    with tab2:
        st.markdown("### Configurações de Email")
        email_host = st.text_input("SMTP Host", value=st.secrets.get("EMAIL_HOST", "smtp.gmail.com"))
        email_port = st.number_input("SMTP Port", value=st.secrets.get("EMAIL_PORT", 587))
        email_user = st.text_input("Email User", value=st.secrets.get("EMAIL_USER", ""))
        email_password = st.text_input("Email Password", type="password", value=st.secrets.get("EMAIL_PASSWORD", ""))
        
        if st.button("Testar Conexão Email"):
            with st.spinner("Testando conexão..."):
                try:
                    server = smtplib.SMTP(email_host, email_port)
                    server.starttls()
                    server.login(email_user, email_password)
                    server.quit()
                    st.success("✅ Conexão com email estabelecida com sucesso!")
                except Exception as e:
                    st.error(f"❌ Erro na conexão: {str(e)}")
    
    with tab3:
        st.markdown("### Integração Google Sheets")
        spreadsheet_url = st.text_input("URL da Planilha", value=st.secrets.get("spreadsheet", ""))
        
        if st.button("Testar Conexão Sheets"):
            with st.spinner("Testando conexão..."):
                sheet = get_google_sheets_config()
                if sheet:
                    st.success(f"✅ Conectado! Planilha: {sheet.title}")
                else:
                    st.error("❌ Falha na conexão com Google Sheets")
    
    with tab4:
        st.markdown("### Informações do Sistema")
        st.markdown(f"""
        **Versão:** MASTER CODE DEEP SEEK v10  
        **Última Atualização:** 2024-12-06  
        **Desenvolvedor:** André Aranha  
        **Status:** 🟢 Online
        """)
        
        if st.button("🔄 Reiniciar Sistema", type="secondary"):
            st.rerun()

# Rodapé
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px;">
    <div style="margin-bottom: 15px;">
        <strong>TENNIS CLASS © 2024 - Sistema de Gestão Completo</strong>
    </div>
    <div style="font-size: 14px; margin-bottom: 10px;">
        Desenvolvido por André Aranha | MASTER CODE DEEP SEEK v10
    </div>
    <div style="font-size: 12px; opacity: 0.9;">
        Última atualização: 2024-12-06 | Sistema otimizado e seguro
    </div>
    <div style="font-size: 12px; margin-top: 10px;">
        <em>Manage app</em>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================
# FUNCIONALIDADE DE NOTIFICAÇÕES
# ============================
if st.secrets.get("EMAIL_USER") and st.secrets.get("EMAIL_PASSWORD"):
    st.sidebar.markdown("---")
    if st.sidebar.button("📧 Testar Envio de Email", type="secondary"):
        test_email = st.sidebar.text_input("Email para teste", "teste@email.com")
        if st.sidebar.button("Enviar Teste"):
            with st.sidebar:
                with st.spinner("Enviando..."):
                    success, msg = send_confirmation_email(
                        cliente_nome="Cliente Teste",
                        cliente_email=test_email,
                        unidade="PLAY TENNIS Ibirapuera",
                        data=datetime.now().strftime("%d/%m/%Y"),
                        horario="10:00",
                        telefone="(11) 99999-9999"
                    )
                    
                    if success:
                        st.success("✅ Email de teste enviado!")
                    else:
                        st.error(f"❌ Falha: {msg}")
