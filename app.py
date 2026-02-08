# ============================================
# TENNIS CLASS APP - MASTER CODE DEEP SEEK v11 FINAL
# ============================================
# Sistema completo unificado com todas as melhorias
# Data: 2024-12-07
# Status: PRODUÇÃO
# ============================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import re
import uuid
import smtplib
import logging
import hashlib
import urllib.parse
import os
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, Tuple, List, Optional, Callable
import ssl
from functools import lru_cache, wraps
import json

# ============================================
# 1. CONFIGURAÇÃO INICIAL
# ============================================

st.set_page_config(
    page_title="TENNIS CLASS - Sistema Completo",
    layout="wide",
    page_icon="🎾",
    initial_sidebar_state="expanded"
)

# ============================================
# 2. SISTEMA DE LOGGING AVANÇADO
# ============================================

logger = logging.getLogger('tennis_class_v11')
logger.setLevel(logging.INFO)

if not logger.handlers:
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - '
        'module:%(module)s - func:%(funcName)s - line:%(lineno)d - %(message)s'
    )
    
    file_handler = logging.FileHandler('tennis_class.log')
    file_handler.setFormatter(formatter)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

# ============================================
# 3. SISTEMA DE RATE LIMITING
# ============================================

class RateLimiter:
    """Sistema de rate limiting para prevenir abusos."""
    
    def __init__(self):
        if 'request_times' not in st.session_state:
            st.session_state.request_times = {}
    
    def is_rate_limited(self, key: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
        current_time = time.time()
        
        if key not in st.session_state.request_times:
            st.session_state.request_times[key] = []
        
        st.session_state.request_times[key] = [
            t for t in st.session_state.request_times[key]
            if current_time - t < window_seconds
        ]
        
        if len(st.session_state.request_times[key]) >= max_requests:
            logger.warning(f"Rate limit excedido para: {key}")
            return True
        
        st.session_state.request_times[key].append(current_time)
        return False

# ============================================
# 4. CONFIGURAÇÕES DO SISTEMA
# ============================================

class Config:
    SPREADSHEET_URL = ""
    WORKSHEET_NAME = "Página1"
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587
    WHATSAPP_NUMBER = "5511971425028"
    MAX_ALUNOS_POR_HORARIO = 4
    TEMPO_PAGAMENTO = 300
    MAX_DIAS_ANTECEDENCIA = 60
    HORARIOS_DISPONIVEIS = [f"{h:02d}:00" for h in range(7, 23)]
    RATE_LIMIT_RESERVAS = 5
    RATE_LIMIT_GERAL = 20
    
    @classmethod
    def get_email_credentials(cls):
        try:
            secrets = st.secrets
            email_user = secrets.get("EMAIL_USER", "")
            email_password = secrets.get("EMAIL_PASSWORD", "")
            if email_user and email_password:
                return email_user, email_password
        except:
            pass
        return "", ""

# ============================================
# 5. DADOS DO SISTEMA
# ============================================

SERVICOS = {
    "particular_hora": {"nome": "Aula particular", "preco": 250, "tipo": "Hora", "pontos": 25},
    "grupo_hora": {"nome": "Aula em grupo", "preco": 200, "tipo": "Hora", "pontos": 20},
    "kids_hora": {"nome": "Aula Kids", "preco": 200, "tipo": "Hora", "pontos": 20},
    "personal_hora": {"nome": "Personal trainer", "preco": 250, "tipo": "Hora", "pontos": 25},
    "competitivo": {"nome": "Treinamento competitivo", "preco": 1400, "tipo": "Mês", "pontos": 140},
    "eventos": {"nome": "Eventos", "preco": 0, "tipo": "Hora", "pontos": 10},
    "pacote_particular_4": {"nome": "Pacote aula particular", "preco": 1000, "tipo": "4 aulas de 1 hora", "pontos": 100},
    "pacote_grupo_4": {"nome": "Pacote aula em grupo", "preco": 800, "tipo": "4 aulas de 1 hora", "pontos": 80},
    "pacote_particular_8": {"nome": "Pacote aula particular", "preco": 2000, "tipo": "8 aulas de 1 hora", "pontos": 200},
    "pacote_grupo_8": {"nome": "Pacote aula em grupo", "preco": 1600, "tipo": "8 aulas de 1 hora", "pontos": 160},
    "pacote_kids_4": {"nome": "Pacote aula Kids", "preco": 800, "tipo": "4 aulas de 1 hora", "pontos": 80},
    "pacote_personal_4": {"nome": "Pacote Personal Trainer", "preco": 1000, "tipo": "4 aulas de 1 hora", "pontos": 100}
}

ACADEMIAS = {
    "PLAY TENNIS Ibirapuera": {
        "endereco": "R. Estado de Israel, 860 - SP",
        "telefone": "(11) 97752-0488",
        "capacidade": 4
    },
    "TOP One Tennis": {
        "endereco": "Av. Indianópolis, 647 - SP",
        "telefone": "(11) 93236-3828",
        "capacidade": 4
    },
    "MELL Tennis": {
        "endereco": "Rua Oscar Gomes Cardim, 535 - SP",
        "telefone": "(11) 97142-5028",
        "capacidade": 4
    },
    "ARENA BTG Morumbi": {
        "endereco": "Av. Maj. Sylvio de Magalhães Padilha, 16741",
        "telefone": "(11) 98854-3860",
        "capacidade": 4
    }
}

# ============================================
# 6. VALIDAÇÕES
# ============================================

def validar_nome_completo(nome: str) -> Tuple[bool, str]:
    nome_limpo = nome.strip()
    
    if len(nome_limpo) < 3:
        return False, "Nome muito curto (mínimo 3 caracteres)"
    
    if not re.match(r'^[a-zA-ZÀ-ÿ\s\-\']+$', nome_limpo):
        return False, "Use apenas letras, espaços e hífens"
    
    if len(nome_limpo.split()) < 2:
        return False, "Digite nome e sobrenome"
    
    return True, ""

def validar_email_estrito(email: str) -> Tuple[bool, str]:
    email_limpo = email.strip().lower()
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email_limpo):
        return False, "Formato de e-mail inválido"
    
    return True, ""

# ============================================
# 7. SISTEMA DE DADOS OTIMIZADO
# ============================================

@st.cache_data(ttl=30)
def carregar_dados_otimizado():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Página1")
        
        colunas_necessarias = ['ID', 'Data', 'Horário', 'Aluno', 'E-mail', 'Serviço', 'Unidade', 'Status', 'Data_Criacao']
        for col in colunas_necessarias:
            if col not in df.columns:
                df[col] = None
        
        logger.info(f"Dados carregados: {len(df)} registros")
        return df
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

# ============================================
# 8. SISTEMA DE FIDELIDADE
# ============================================

class SistemaFidelidade:
    @staticmethod
    def calcular_pontos(valor_gasto: float) -> int:
        pontos_base = int(valor_gasto / 10)
        return max(10, pontos_base)
    
    @staticmethod
    def obter_pontos_aluno(email: str) -> int:
        try:
            df = carregar_dados_otimizado()
            if df.empty:
                return 0
            
            reservas_aluno = df[
                (df['E-mail'] == email.lower()) & 
                (df['Status'] == 'Confirmado')
            ]
            
            total_pontos = 0
            for _, reserva in reservas_aluno.iterrows():
                match = re.search(r'R\$ (\d+)', str(reserva.get('Serviço', '')))
                if match:
                    valor = float(match.group(1))
                    total_pontos += SistemaFidelidade.calcular_pontos(valor)
            
            return total_pontos
        except Exception as e:
            logger.error(f"Erro ao calcular pontos: {e}")
            return 0

# ============================================
# 9. SISTEMA DE RESERVAS
# ============================================

def processar_reserva_seguro(reserva: Dict[str, Any]) -> Tuple[bool, str, str]:
    try:
        # Validações
        nome_valido, msg_nome = validar_nome_completo(reserva.get('Aluno', ''))
        if not nome_valido:
            return False, "", f"Nome: {msg_nome}"
            
        email_valido, msg_email = validar_email_estrito(reserva.get('E-mail', ''))
        if not email_valido:
            return False, "", f"E-mail: {msg_email}"
        
        # Salvar reserva
        sucesso, reserva_id = salvar_reserva_completa(reserva)
        
        if not sucesso:
            return False, "", "Falha ao salvar reserva no sistema."
        
        # Enviar e-mail
        email_enviado = enviar_email_confirmacao_avancado(
            aluno=reserva["Aluno"],
            email=reserva["E-mail"],
            reserva_info=reserva,
            reserva_id=reserva_id
        )
        
        # Calcular pontos
        pontos = SistemaFidelidade.calcular_pontos(250)
        st.session_state.setdefault('pontos_aluno', {})[reserva["E-mail"]] = \
            st.session_state.get('pontos_aluno', {}).get(reserva["E-mail"], 0) + pontos
        
        mensagem_final = f"✅ Reserva {reserva_id} confirmada com sucesso!"
        if not email_enviado:
            mensagem_final += " (E-mail não enviado, mas reserva está confirmada)"
        
        return True, reserva_id, mensagem_final
        
    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
        return False, "", f"Erro: {str(e)}"

def salvar_reserva_completa(reserva: Dict[str, Any]) -> Tuple[bool, str]:
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = carregar_dados_otimizado()
        
        # Gera ID único
        timestamp = datetime.now().strftime("%y%m%d")
        reserva_id = f"{timestamp}_{str(uuid.uuid4())[:6].upper()}"
        
        # Extrai valor do serviço
        valor_servico = 0
        for serv in SERVICOS.values():
            if serv['nome'] in reserva.get('Serviço', ''):
                valor_servico = serv['preco']
                break
        
        # Adiciona campos de sistema
        reserva_completa = {
            **reserva,
            "ID": reserva_id,
            "Timestamp": datetime.now().isoformat(),
            "Status": "Pendente",
            "Data_Criacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Valor_Servico": valor_servico,
            "Pontos_Gerados": SistemaFidelidade.calcular_pontos(valor_servico)
        }
        
        # Converte para DataFrame e salva
        df_novo = pd.concat([df, pd.DataFrame([reserva_completa])], ignore_index=True)
        conn.update(worksheet="Página1", data=df_novo)
        
        # Limpa cache
        st.cache_data.clear()
        
        logger.info(f"Reserva {reserva_id} salva com sucesso")
        return True, reserva_id
        
    except Exception as e:
        logger.error(f"Erro ao salvar reserva: {str(e)}")
        return False, str(e)

# ============================================
# 10. SISTEMA DE EMAIL AVANÇADO
# ============================================

def enviar_email_confirmacao_avancado(aluno: str, email: str, reserva_info: Dict[str, Any], reserva_id: str) -> bool:
    try:
        email_user, email_password = Config.get_email_credentials()
        
        if not email_password:
            logger.warning("Credenciais de e-mail não configuradas")
            return False
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🎾 Tennis Class - Confirmação #{reserva_id}"
        msg['From'] = f"Tennis Class <{email_user}>"
        msg['To'] = email
        
        # Extrair dados
        servico = reserva_info.get('Serviço', '')
        unidade = reserva_info.get('Unidade', '')
        data = reserva_info.get('Data', '')
        horario = reserva_info.get('Horário', '')
        
        # Calcula pontos
        pontos = SistemaFidelidade.calcular_pontos(250)
        total_pontos = SistemaFidelidade.obter_pontos_aluno(email) + pontos
        
        # HTML do e-mail
        html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; background: #f9f9f9; padding: 20px;">
                <div style="background: linear-gradient(135deg, #1a5f7a, #2a8bb8); color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0;">🎾 TENNIS CLASS</h1>
                    <p style="margin: 10px 0 0 0;">Confirmação de Reserva #{reserva_id}</p>
                </div>
                
                <div style="background: white; padding: 30px; margin-top: 20px; border-radius: 10px;">
                    <h2 style="color: #2c3e50;">Olá, {aluno}!</h2>
                    <p>Sua reserva foi confirmada com sucesso:</p>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #2c3e50;">📋 Detalhes da Reserva</h3>
                        <p><strong>ID:</strong> {reserva_id}</p>
                        <p><strong>Serviço:</strong> {servico}</p>
                        <p><strong>Data:</strong> {data}</p>
                        <p><strong>Horário:</strong> {horario}</p>
                        <p><strong>Unidade:</strong> {unidade}</p>
                        <p><strong>Status:</strong> <span style="color: green; font-weight: bold;">CONFIRMADO</span></p>
                    </div>
                    
                    <div style="background: #fff8e1; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #2c3e50;">⭐ Sistema de Fidelidade</h3>
                        <p>Parabéns! Você ganhou <strong>{pontos} pontos</strong>!</p>
                        <p><strong>Total acumulado:</strong> {total_pontos} pontos</p>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://wa.me/{Config.WHATSAPP_NUMBER}?text=Olá! Tenho uma reserva com ID {reserva_id}" 
                           style="background: #25D366; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                            📱 Falar no WhatsApp
                        </a>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
                    <p>TENNIS CLASS © {datetime.now().year}</p>
                    <p>Este é um e-mail automático, por favor não responda.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        texto = f"""
        TENNIS CLASS - Confirmação de Reserva #{reserva_id}
        
        Olá {aluno},
        
        Sua reserva foi confirmada:
        
        ID: {reserva_id}
        Serviço: {servico}
        Data: {data}
        Horário: {horario}
        Unidade: {unidade}
        Status: CONFIRMADO
        
        Pontos ganhos: {pontos}
        Total acumulado: {total_pontos} pontos
        
        Entre em contato: (11) 97142-5028
        
        TENNIS CLASS © {datetime.now().year}
        """
        
        msg.attach(MIMEText(texto, 'plain'))
        msg.attach(MIMEText(html, 'html'))
        
        context = ssl.create_default_context()
        with smtplib.SMTP(Config.EMAIL_HOST, Config.EMAIL_PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(email_user, email_password)
            server.send_message(msg)
        
        logger.info(f"E-mail enviado para {email}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail: {e}")
        return False

# ============================================
# 11. INICIALIZAÇÃO DA SESSÃO
# ============================================

def inicializar_sessao():
    estados_padrao = {
        'pagina': "Home",
        'pagamento_ativo': False,
        'reserva_temp': {},
        'inicio_timer': None,
        'admin_autenticado': False,
        'erros_form': {},
        'reserva_id_gerada': None,
        'session_id': str(uuid.uuid4()),
        'email_usuario': None,
        'pontos_aluno': {},
        'rate_limiter': RateLimiter()
    }
    
    for key, valor in estados_padrao.items():
        if key not in st.session_state:
            st.session_state[key] = valor

# ============================================
# 12. CSS E ESTILOS
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
    
    .stButton > button {
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>

<a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="35" alt="WhatsApp">
</a>

<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" 
     style="position: fixed; bottom: 15px; left: 20px; width: 130px; z-index: 9999; opacity: 0.8;">
""", unsafe_allow_html=True)

# ============================================
# 13. MENU LATERAL
# ============================================

def criar_menu_lateral():
    with st.sidebar:
        st.markdown("<h2 style='color: white; text-align: center;'>🎾 MENU</h2>", 
                    unsafe_allow_html=True)
        
        menu_itens = ["Home", "Preços", "Cadastro", "Dashboard", "Minhas Reservas", "Configurações", "Contato"]
        
        for item in menu_itens:
            if st.button(item, key=f"nav_{item}", use_container_width=True):
                st.session_state.pagina = item
                st.session_state.pagamento_ativo = False
                if item in ["Dashboard", "Configurações"]:
                    st.session_state.admin_autenticado = False
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 🏢 ACADEMIAS")
        
        for nome, info in ACADEMIAS.items():
            st.markdown(
                f"📍 **{nome}**\n"
                f"<div style='font-size: 11px; color: #ccc; margin-bottom: 10px;'>"
                f"{info['endereco']}<br>📞 {info['telefone']}"
                f"</div>", 
                unsafe_allow_html=True
            )
        
        # Sistema de pontos do usuário
        if st.session_state.get('email_usuario'):
            pontos = SistemaFidelidade.obter_pontos_aluno(st.session_state.email_usuario)
            if pontos > 0:
                st.markdown("---")
                st.markdown(f"### ⭐ Seus Pontos: {pontos}")
        
        st.markdown("---")
        try:
            df = carregar_dados_otimizado()
            total_reservas = len(df) if not df.empty else 0
            st.metric("Reservas totais", total_reservas)
        except:
            st.metric("Reservas totais", "0")

# ============================================
# 14. PÁGINA HOME (PRINCIPAL)
# ============================================

def pagina_home():
    st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)
    
    if not st.session_state.pagamento_ativo:
        with st.form("reserva_form", clear_on_submit=True):
            st.subheader("📅 Agendar Aula")
            
            col1, col2 = st.columns(2)
            with col1:
                aluno = st.text_input("Nome do Aluno *", placeholder="Ex: João Silva")
            with col2:
                email = st.text_input("E-mail *", placeholder="exemplo@email.com")
            
            # Serviços
            servicos_lista = []
            for key, info in SERVICOS.items():
                pontos_str = f" ⭐ {info['pontos']} pts" if info.get('pontos', 0) > 0 else ""
                if info['tipo'] == "Hora":
                    servicos_lista.append(f"{info['nome']} R$ {info['preco']}/hora{pontos_str}")
                elif info['tipo'] == "Mês":
                    servicos_lista.append(f"{info['nome']} R$ {info['preco']}/mês{pontos_str}")
                else:
                    servicos_lista.append(f"{info['nome']} R$ {info['preco']} / {info['tipo']}{pontos_str}")
            
            servico = st.selectbox("Serviço *", servicos_lista)
            unidade = st.selectbox("Unidade *", list(ACADEMIAS.keys()))
            
            col1, col2 = st.columns(2)
            with col1:
                dt = st.date_input(
                    "Data *",
                    format="DD/MM/YYYY",
                    min_value=datetime.now().date(),
                    max_value=datetime.now().date() + timedelta(days=60)
                )
            with col2:
                hr = st.selectbox("Horário *", Config.HORARIOS_DISPONIVEIS)
            
            telefone = st.text_input("Telefone (opcional)", placeholder="(11) 99999-9999")
            
            submit = st.form_submit_button("AVANÇAR PARA PAGAMENTO", use_container_width=True, type="primary")
            
            if submit:
                st.session_state.erros_form = {}
                
                # Validações
                nome_valido, msg_nome = validar_nome_completo(aluno)
                if not nome_valido:
                    st.session_state.erros_form['aluno'] = msg_nome
                
                email_valido, msg_email = validar_email_estrito(email)
                if not email_valido:
                    st.session_state.erros_form['email'] = msg_email
                
                if not st.session_state.erros_form:
                    # Rate limiting
                    limiter = RateLimiter()
                    if limiter.is_rate_limited(f"reserva_{email}", Config.RATE_LIMIT_RESERVAS, 60):
                        st.error("⏳ Muitas tentativas. Aguarde 1 minuto.")
                    else:
                        st.session_state.reserva_temp = {
                            "Data": dt.strftime("%d/%m/%Y"),
                            "Horário": hr,
                            "Aluno": aluno.strip(),
                            "Serviço": servico,
                            "Unidade": unidade,
                            "E-mail": email.lower().strip(),
                            "Telefone": telefone.strip() if telefone else ""
                        }
                        st.session_state.pagamento_ativo = True
                        st.session_state.inicio_timer = time.time()
                        st.session_state.email_usuario = email.lower().strip()
                        st.rerun()
                else:
                    for campo, mensagem in st.session_state.erros_form.items():
                        st.error(f"❌ {mensagem}")
    
    else:
        # Página de pagamento
        st.subheader("💳 Pagamento via PIX")
        
        # QR Code
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(
                "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=aranha.corp@gmail.com",
                width=250
            )
        
        st.markdown("### Chave PIX:")
        st.code("aranha.corp@gmail.com", language="text")
        
        # Resumo
        reserva = st.session_state.reserva_temp
        st.info(f"""
        **Aluno:** {reserva.get('Aluno', '')}  
        **Serviço:** {reserva.get('Serviço', '')}  
        **Unidade:** {reserva.get('Unidade', '')}  
        **Data:** {reserva.get('Data', '')} às {reserva.get('Horário', '')}
        **E-mail:** {reserva.get('E-mail', '')}
        """)
        
        # Timer
        timer_box = st.empty()
        if st.session_state.inicio_timer:
            restante = Config.TEMPO_PAGAMENTO - (time.time() - st.session_state.inicio_timer)
            if restante > 0:
                m, s = divmod(int(restante), 60)
                timer_box.warning(f"⏱️ Expira em: {m:02d}:{s:02d}")
            else:
                st.session_state.pagamento_ativo = False
                timer_box.warning("⏰ Tempo esgotado!")
                time.sleep(2)
                st.rerun()
        
        # Botão de confirmação
        if st.button("✅ CONFIRMAR PAGAMENTO", type="primary", use_container_width=True):
            with st.spinner("Processando..."):
                sucesso, reserva_id, mensagem = processar_reserva_seguro(st.session_state.reserva_temp)
                
                if sucesso:
                    st.session_state.reserva_id_gerada = reserva_id
                    st.session_state.pagamento_ativo = False
                    st.balloons()
                    
                    st.markdown(f"""
                    <div style='background: #e8f5e9; border: 2px solid #4CAF50; border-radius: 10px; padding: 20px; margin: 20px 0; text-align: center;'>
                        <h3>✅ Reserva Confirmada!</h3>
                        <p>{mensagem}</p>
                        <div class="reserva-id-box">
                            ID da Reserva: {reserva_id}
                        </div>
                        <p>Guarde este ID para futuras consultas.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📅 Nova Reserva", use_container_width=True):
                            st.session_state.reserva_temp = {}
                            st.rerun()
                    
                    time.sleep(5)
                    st.session_state.reserva_temp = {}
                    st.rerun()
                else:
                    st.error(f"❌ {mensagem}")

# ============================================
# 15. PÁGINA MINHAS RESERVAS
# ============================================

def pagina_minhas_reservas():
    st.markdown("<h2 style='text-align: center;'>🔍 Minhas Reservas</h2>", unsafe_allow_html=True)
    
    with st.form("busca_reservas"):
        email_busca = st.text_input("Digite seu e-mail:", placeholder="exemplo@email.com")
        buscar = st.form_submit_button("🔍 Buscar", use_container_width=True)
    
    if buscar and email_busca:
        email_valido, msg_email = validar_email_estrito(email_busca)
        
        if not email_valido:
            st.error(f"❌ {msg_email}")
        else:
            with st.spinner("Buscando..."):
                # Rate limiting
                limiter = RateLimiter()
                if limiter.is_rate_limited(f"busca_{email_busca}", 5, 60):
                    st.warning("⏳ Aguarde antes de nova busca.")
                else:
                    try:
                        df = carregar_dados_otimizado()
                        reservas = df[df['E-mail'].str.lower() == email_busca.lower()]
                        
                        if not reservas.empty:
                            st.success(f"✅ Encontradas {len(reservas)} reservas!")
                            
                            # Pontos
                            pontos = SistemaFidelidade.obter_pontos_aluno(email_busca)
                            if pontos > 0:
                                st.markdown(f"### ⭐ Seus Pontos: **{pontos}**")
                            
                            # Exibe reservas
                            for _, reserva in reservas.iterrows():
                                with st.container():
                                    st.markdown(f"""
                                    **{reserva['Serviço']}**  
                                    📍 {reserva['Unidade']}  
                                    📅 {reserva['Data']} às {reserva['Horário']}  
                                    🆔 {reserva['ID']}  
                                    Status: {reserva['Status']}
                                    """)
                                    st.markdown("---")
                        else:
                            st.info("📭 Nenhuma reserva encontrada.")
                    except Exception as e:
                        st.error(f"Erro na busca: {str(e)}")

# ============================================
# 16. PÁGINAS ADICIONAIS (SIMPLIFICADAS)
# ============================================

def pagina_precos():
    st.markdown("### 🎾 Tabela de Preços")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 Aulas Avulsas")
        for info in [s for s in SERVICOS.values() if s['tipo'] == "Hora" and "Pacote" not in s['nome']]:
            st.markdown(f"**{info['nome']}** - R$ {info['preco']}/hora ⭐ {info['pontos']} pts")
    
    with col2:
        st.markdown("#### 📦 Pacotes")
        for info in [s for s in SERVICOS.values() if "Pacote" in s['nome']]:
            st.markdown(f"**{info['nome']}** - R$ {info['preco']} ⭐ {info['pontos']} pts")

def pagina_dashboard():
    if not st.session_state.admin_autenticado:
        senha = st.text_input("Senha admin:", type="password")
        if st.button("Acessar") and verificar_senha_admin(senha):
            st.session_state.admin_autenticado = True
            st.rerun()
    else:
        st.subheader("📊 Dashboard")
        df = carregar_dados_otimizado()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            st.metric("Total Reservas", len(df))
        else:
            st.info("Nenhuma reserva encontrada.")

def pagina_configuracoes():
    st.subheader("⚙️ Configurações")
    st.info("Configurações do sistema")
    # Implementar conforme necessário

# ============================================
# 17. FUNÇÕES AUXILIARES
# ============================================

def verificar_senha_admin(senha_digitada: str) -> bool:
    try:
        senha_correta_hash = st.secrets.get("ADMIN_PASSWORD_HASH", "")
        if not senha_correta_hash:
            senha_correta = st.secrets.get("ADMIN_PASSWORD", "aranha2026")
            return senha_digitada == senha_correta
        hash_digitado = hashlib.sha256(senha_digitada.encode()).hexdigest()
        return hash_digitado == senha_correta_hash
    except:
        return False

# ============================================
# 18. APLICAÇÃO PRINCIPAL
# ============================================

def main():
    inicializar_sessao()
    criar_menu_lateral()
    
    if st.session_state.pagina == "Home":
        pagina_home()
    elif st.session_state.pagina == "Preços":
        pagina_precos()
    elif st.session_state.pagina == "Minhas Reservas":
        pagina_minhas_reservas()
    elif st.session_state.pagina == "Dashboard":
        pagina_dashboard()
    elif st.session_state.pagina == "Configurações":
        pagina_configuracoes()
    elif st.session_state.pagina == "Cadastro":
        st.info("Página de cadastro - Em desenvolvimento")
    elif st.session_state.pagina == "Contato":
        st.info("Página de contato - Em desenvolvimento")

# ============================================
# 19. EXECUÇÃO
# ============================================

if __name__ == "__main__":
    try:
        main()
        logger.info("Aplicação executada com sucesso")
    except Exception as e:
        logger.critical(f"Erro crítico: {e}", exc_info=True)
        st.error("Erro no sistema. Recarregue a página.")
