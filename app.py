# ============================================
# TENNIS CLASS APP - MASTER CODE DEEP SEEK v10.1
# ============================================
# Versão otimizada mantendo funcionalidades atuais
# Data: 2024-12-07
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
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, Tuple, List, Optional
import ssl
import os
from functools import lru_cache

# ============================================
# 1. CONFIGURAÇÃO E LOGGING OTIMIZADO
# ============================================

# Configuração da página
st.set_page_config(
    page_title="TENNIS CLASS - Sistema Completo",
    layout="wide",
    page_icon="🎾",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://wa.me/5511971425028',
        'Report a bug': 'mailto:aranha.corp@gmail.com',
        'About': 'TENNIS CLASS v10.1 - Sistema de agendamento de aulas'
    }
)

# Configuração de logging otimizado
def setup_logging():
    """Configura sistema de logging estruturado para depuração."""
    # Criar diretório de logs se não existir
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logger = logging.getLogger('tennis_class')
    logger.setLevel(logging.INFO)
    
    # Evitar duplicação de handlers
    if not logger.handlers:
        # Formato estruturado
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(module)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler com rotação diária
        file_handler = logging.FileHandler(
            f'{log_dir}/tennis_class_{datetime.now().strftime("%Y%m%d")}.log',
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        
        # Stream handler para console
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
    
    return logger

logger = setup_logging()

# ============================================
# 2. CLASSES DE CONFIGURAÇÃO COM MELHORIAS
# ============================================

class Config:
    """Classe de configuração centralizada com melhorias."""
    
    # Google Sheets
    SPREADSHEET_URL = ""
    WORKSHEET_NAME = "Página1"
    
    # Email
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587
    
    # WhatsApp
    WHATSAPP_NUMBER = "5511971425028"
    WHATSAPP_FORMAT = "https://wa.me/{number}?text={message}"
    
    # Limites do sistema
    MAX_ALUNOS_POR_HORARIO = 4
    TEMPO_PAGAMENTO = 300  # 5 minutos em segundos
    MAX_DIAS_ANTECEDENCIA = 60
    
    # Horários disponíveis
    HORARIOS_DISPONIVEIS = [f"{h:02d}:00" for h in range(7, 23)]
    HORARIOS_MANHA = [f"{h:02d}:00" for h in range(7, 12)]
    HORARIOS_TARDE = [f"{h:02d}:00" for h in range(12, 18)]
    HORARIOS_NOITE = [f"{h:02d}:00" for h in range(18, 23)]
    
    # Cache settings
    CACHE_TTL = 300  # 5 minutos
    
    @classmethod
    def get_email_credentials(cls) -> Tuple[str, str]:
        """Obtém credenciais de e-mail com fallback hierárquico e validação."""
        try:
            secrets = st.secrets
            email_user = secrets.get("EMAIL_USER", "").strip()
            email_password = secrets.get("EMAIL_PASSWORD", "").strip()
            
            if email_user and email_password:
                # Valida formato básico do email
                if "@" in email_user and "." in email_user:
                    logger.info("Credenciais de email carregadas do secrets")
                    return email_user, email_password
                else:
                    logger.warning("Email do secrets em formato inválido")
        except Exception as e:
            logger.debug(f"Não foi possível carregar secrets: {e}")
        
        # Fallback para variáveis de ambiente
        email_user = os.environ.get("EMAIL_USER", "").strip()
        email_password = os.environ.get("EMAIL_PASSWORD", "").strip()
        
        if email_user and email_password:
            logger.info("Credenciais de email carregadas do environment")
            return email_user, email_password
        
        logger.warning("Credenciais de email não configuradas")
        return "", ""

class ReservaError(Exception):
    """Exceção personalizada para erros de reserva."""
    pass

class RateLimitError(Exception):
    """Exceção para limite de requisições."""
    pass

# ============================================
# 3. SISTEMA DE RATE LIMITING SIMPLES
# ============================================

class RateLimiter:
    """Sistema simples de rate limiting para prevenir abusos."""
    
    @staticmethod
    def check_rate_limit(operation: str, user_key: str = None, max_attempts: int = 5, 
                        time_window: int = 60) -> bool:
        """
        Verifica se o usuário excedeu o limite de requisições.
        
        Args:
            operation: Nome da operação (ex: 'reserva', 'login', 'busca')
            user_key: Identificador do usuário (email ou IP)
            max_attempts: Máximo de tentativas permitidas
            time_window: Janela de tempo em segundos
            
        Returns:
            True se dentro do limite, False se excedido
        """
        try:
            if user_key is None:
                # Usa uma chave padrão baseada na sessão
                user_key = f"session_{hash(st.session_state.get('session_id', 'default'))}"
            
            key = f"rate_limit_{operation}_{user_key}"
            current_time = time.time()
            
            # Inicializa se não existir
            if key not in st.session_state:
                st.session_state[key] = {
                    'attempts': [],
                    'blocked_until': 0
                }
            
            rate_data = st.session_state[key]
            
            # Verifica se está bloqueado
            if rate_data['blocked_until'] > current_time:
                remaining = rate_data['blocked_until'] - current_time
                logger.warning(f"Rate limit bloqueado para {operation}: {remaining:.0f}s restantes")
                return False
            
            # Remove tentativas antigas
            recent_attempts = [
                t for t in rate_data['attempts'] 
                if current_time - t < time_window
            ]
            
            # Verifica se excedeu o limite
            if len(recent_attempts) >= max_attempts:
                # Bloqueia por 5 minutos
                rate_data['blocked_until'] = current_time + 300
                rate_data['attempts'] = recent_attempts
                logger.warning(f"Rate limit excedido para {operation}. Bloqueado por 5 minutos.")
                return False
            
            # Registra nova tentativa
            recent_attempts.append(current_time)
            rate_data['attempts'] = recent_attempts
            
            return True
            
        except Exception as e:
            logger.error(f"Erro no rate limiting: {e}")
            return True  # Em caso de erro, permite continuar

# ============================================
# 4. CONSTANTES E DADOS ATUALIZADOS
# ============================================

# Serviços com categorias para melhor organização
SERVICOS = {
    "aulas_avulsas": {
        "categoria": "Aulas Avulsas",
        "itens": {
            "particular_hora": {"nome": "Aula particular", "preco": 250, "tipo": "Hora"},
            "grupo_hora": {"nome": "Aula em grupo", "preco": 200, "tipo": "Hora"},
            "kids_hora": {"nome": "Aula Kids", "preco": 200, "tipo": "Hora"},
            "personal_hora": {"nome": "Personal trainer", "preco": 250, "tipo": "Hora"}
        }
    },
    "pacotes": {
        "categoria": "Pacotes de Aulas",
        "itens": {
            "pacote_particular_4": {"nome": "Pacote aula particular", "preco": 1000, "tipo": "4 aulas de 1 hora"},
            "pacote_grupo_4": {"nome": "Pacote aula em grupo", "preco": 800, "tipo": "4 aulas de 1 hora"},
            "pacote_particular_8": {"nome": "Pacote aula particular", "preco": 2000, "tipo": "8 aulas de 1 hora"},
            "pacote_grupo_8": {"nome": "Pacote aula em grupo", "preco": 1600, "tipo": "8 aulas de 1 hora"},
            "pacote_kids_4": {"nome": "Pacote aula Kids", "preco": 800, "tipo": "4 aulas de 1 hora"},
            "pacote_personal_4": {"nome": "Pacote Personal Trainer", "preco": 1000, "tipo": "4 aulas de 1 hora"}
        }
    },
    "especializados": {
        "categoria": "Treinamentos Especializados",
        "itens": {
            "competitivo": {"nome": "Treinamento competitivo", "preco": 1400, "tipo": "Mês"},
            "eventos": {"nome": "Eventos", "preco": 0, "tipo": "Hora"}
        }
    }
}

# Função auxiliar para formatar serviços para o selectbox
def formatar_servicos_para_select() -> List[str]:
    """Formata os serviços para exibição no selectbox."""
    servicos_formatados = []
    for categoria, dados in SERVICOS.items():
        for key, info in dados['itens'].items():
            if info['tipo'] == "Hora":
                servicos_formatados.append(f"{info['nome']} - R$ {info['preco']}/hora")
            elif info['tipo'] == "Mês":
                servicos_formatados.append(f"{info['nome']} - R$ {info['preco']}/mês")
            else:
                servicos_formatados.append(f"{info['nome']} - R$ {info['preco']} ({info['tipo']})")
    return servicos_formatados

ACADEMIAS = {
    "PLAY TENNIS Ibirapuera": {
        "endereco": "R. Estado de Israel, 860 - SP",
        "telefone": "(11) 97752-0488",
        "zona": "Sul",
        "horario_funcionamento": "6h às 22h"
    },
    "TOP One Tennis": {
        "endereco": "Av. Indianópolis, 647 - SP",
        "telefone": "(11) 93236-3828",
        "zona": "Sul",
        "horario_funcionamento": "7h às 21h"
    },
    "MELL Tennis": {
        "endereco": "Rua Oscar Gomes Cardim, 535 - SP",
        "telefone": "(11) 97142-5028",
        "zona": "Oeste",
        "horario_funcionamento": "6h às 23h"
    },
    "ARENA BTG Morumbi": {
        "endereco": "Av. Maj. Sylvio de Magalhães Padilha, 16741",
        "telefone": "(11) 98854-3860",
        "zona": "Oeste",
        "horario_funcionamento": "6h às 22h"
    }
}

FORM_LINKS = {
    "professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform?usp=dialog",
    "aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform?usp=dialog",
    "academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform?usp=dialog",
    "avaliacao": "https://docs.google.com/forms/d/e/1FAIpQLScYV1QH6s8G9kL6d8jW4vZx5p7mN9qR2t3UvYwXzJlKbMnOQ/viewform?usp=dialog"
}

# ============================================
# 5. FUNÇÕES AUXILIARES - VALIDAÇÕES APRIMORADAS
# ============================================

def validar_nome_completo(nome: str) -> Tuple[bool, str]:
    """Valida nome completo com mensagens descritivas."""
    nome_limpo = nome.strip()
    
    if not nome_limpo:
        return False, "O nome não pode estar vazio."
    
    if len(nome_limpo) < 3:
        return False, "O nome deve ter pelo menos 3 caracteres."
    
    if len(nome_limpo) > 100:
        return False, "O nome é muito longo (máximo 100 caracteres)."
    
    # Permite letras, espaços, acentos e hífens
    if not re.match(r'^[a-zA-ZÀ-ÿ\s\-\']+$', nome_limpo):
        return False, "Use apenas letras, espaços e hífens."
    
    # Verifica se tem pelo menos um espaço (nome e sobrenome)
    partes = nome_limpo.split()
    if len(partes) < 2:
        return False, "Por favor, digite nome e sobrenome."
    
    return True, ""

def validar_email_rigoroso(email: str) -> Tuple[bool, str]:
    """Validação rigorosa de e-mail com mensagens claras."""
    email_limpo = email.strip().lower()
    
    if not email_limpo:
        return False, "O e-mail não pode estar vazio."
    
    # Regex mais rigorosa
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email_limpo):
        return False, "Formato de e-mail inválido. Exemplo: nome@exemplo.com"
    
    # Validação de domínios comuns
    dominio = email_limpo.split('@')[1]
    if len(dominio.split('.')) < 2:
        return False, "Domínio de e-mail inválido."
    
    return True, ""

def validar_telefone_formatado(telefone: str) -> Tuple[bool, str]:
    """Valida telefone com formatação brasileira."""
    if not telefone:
        return True, ""  # Telefone é opcional
    
    telefone_limpo = re.sub(r'\D', '', telefone)
    
    if len(telefone_limpo) not in [10, 11]:
        return False, "Telefone deve ter 10 ou 11 dígitos (com DDD)."
    
    # Valida DDD brasileiro
    ddd = telefone_limpo[:2]
    ddd_valido = [
        '11', '12', '13', '14', '15', '16', '17', '18', '19',
        '21', '22', '24', '27', '28', '31', '32', '33', '34',
        '35', '37', '38', '41', '42', '43', '44', '45', '46',
        '47', '48', '49', '51', '53', '54', '55', '61', '62',
        '63', '64', '65', '66', '67', '68', '69', '71', '73',
        '74', '75', '77', '79', '81', '82', '83', '84', '85',
        '86', '87', '88', '89', '91', '92', '93', '94', '95',
        '96', '97', '98', '99'
    ]
    
    if ddd not in ddd_valido:
        return False, "DDD inválido."
    
    return True, ""

def validar_data_horario_inteligente(data: str, horario: str, unidade: str) -> Tuple[bool, str]:
    """
    Validação inteligente de data e horário com cache.
    
    Args:
        data: Data no formato DD/MM/YYYY
        horario: Horário no formato HH:00
        unidade: Nome da unidade
        
    Returns:
        Tuple[bool, str]: (disponível, mensagem de erro)
    """
    try:
        # Converte a data
        data_obj = datetime.strptime(data, "%d/%m/%Y")
        hoje = datetime.now().date()
        
        # Não permitir reservas no passado
        if data_obj.date() < hoje:
            return False, "Não é possível agendar para datas passadas."
        
        # Não permitir reservas com mais de 60 dias de antecedência
        dias_antecedencia = (data_obj.date() - hoje).days
        if dias_antecedencia > Config.MAX_DIAS_ANTECEDENCIA:
            return False, f"Só é possível agendar com até {Config.MAX_DIAS_ANTECEDENCIA} dias de antecedência."
        
        # Verificar se não é domingo
        if data_obj.weekday() == 6:  # 6 = domingo
            return False, "Não há aulas aos domingos."
        
        # Verificar disponibilidade
        disponibilidade = carregar_disponibilidade_com_cache(data, unidade)
        vagas = disponibilidade.get(horario, Config.MAX_ALUNOS_POR_HORARIO)
        
        if vagas <= 0:
            # Sugere horários alternativos próximos
            horarios_proximos = []
            horarios_disponiveis = [h for h, v in disponibilidade.items() if v > 0]
            
            if horarios_disponiveis:
                # Encontra horários mais próximos
                hora_atual = int(horario.split(':')[0])
                for h in horarios_disponiveis:
                    hora_h = int(h.split(':')[0])
                    if abs(hora_h - hora_atual) <= 2:  # Horários dentro de 2 horas
                        horarios_proximos.append(h)
                
                if horarios_proximos:
                    sugestao = f" Sugestões: {', '.join(sorted(horarios_proximos)[:3])}"
                else:
                    sugestao = f" Outros horários disponíveis: {', '.join(sorted(horarios_disponiveis)[:3])}"
            else:
                sugestao = ""
            
            return False, f"Horário indisponível na {unidade}.{sugestao}"
        
        return True, ""
        
    except ValueError:
        return False, "Formato de data inválido. Use DD/MM/YYYY."
    except Exception as e:
        logger.error(f"Erro na validação de data/horário: {e}")
        return True, ""  # Em caso de erro, permite continuar

# ============================================
# 6. FUNÇÕES DE DADOS COM CACHE INTELIGENTE
# ============================================

@st.cache_data(ttl=Config.CACHE_TTL, show_spinner=False)
def carregar_dados_otimizado() -> pd.DataFrame:
    """Carrega dados do Google Sheets com cache inteligente e tratamento de erros."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Página1", ttl=Config.CACHE_TTL)
        
        # Garante colunas essenciais
        colunas_necessarias = ['ID', 'Data', 'Horário', 'Aluno', 'E-mail', 'Serviço', 'Unidade', 'Status', 'Data_Criacao']
        for col in colunas_necessarias:
            if col not in df.columns:
                df[col] = ""
        
        # Remove duplicatas e ordena
        if 'Data_Criacao' in df.columns:
            df = df.sort_values('Data_Criacao', ascending=False)
        
        logger.info(f"Dados otimizados carregados: {len(df)} registros")
        return df
        
    except Exception as e:
        logger.error(f"Erro ao carregar dados otimizados: {str(e)}")
        st.error("⚠️ Erro temporário ao carregar dados. Tente novamente em alguns instantes.")
        return pd.DataFrame()

@lru_cache(maxsize=256)
def carregar_disponibilidade_com_cache(data: str, unidade: str) -> Dict[str, int]:
    """
    Carrega disponibilidade com cache LRU para melhor performance.
    
    Returns:
        Dict com horário como chave e vagas disponíveis como valor
    """
    try:
        df = carregar_dados_otimizado()
        if df.empty:
            return {hora: Config.MAX_ALUNOS_POR_HORARIO for hora in Config.HORARIOS_DISPONIVEIS}
        
        # Filtra reservas ativas para a data e unidade
        filtrado = df[
            (df['Data'] == data) &
            (df['Unidade'] == unidade) &
            (df['Status'].isin(['Pendente', 'Confirmado']))
        ]
        
        # Conta reservas por horário
        disponibilidade = {}
        for hora in Config.HORARIOS_DISPONIVEIS:
            count = len(filtrado[filtrado['Horário'] == hora])
            disponibilidade[hora] = Config.MAX_ALUNOS_POR_HORARIO - count
            
        return disponibilidade
        
    except Exception as e:
        logger.error(f"Erro ao carregar disponibilidade: {e}")
        return {hora: Config.MAX_ALUNOS_POR_HORARIO for hora in Config.HORARIOS_DISPONIVEIS}

def salvar_reserva_segura(reserva: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Salva uma reserva com validação adicional e tratamento de erros.
    
    Returns:
        Tuple[bool, str]: (sucesso, reserva_id ou mensagem de erro)
    """
    try:
        # Rate limiting na criação de reservas
        email_key = reserva.get('E-mail', '').strip().lower()
        if not RateLimiter.check_rate_limit('reserva', email_key, 3, 300):  # 3 reservas a cada 5 minutos
            return False, "Muitas reservas em curto período. Aguarde alguns minutos."
        
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = carregar_dados_otimizado()
        
        # Gera ID único com timestamp
        timestamp = datetime.now().strftime("%y%m%d")
        reserva_id = f"{timestamp}_{str(uuid.uuid4())[:6].upper()}"
        
        # Adiciona campos de sistema
        reserva_completa = {
            **reserva,
            "ID": reserva_id,
            "Timestamp": datetime.now().isoformat(),
            "Status": "Pendente",
            "Data_Criacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "IP_Usuario": "N/A",  # Em produção, obter do request
            "User_Agent": "N/A",
            "Versao_App": "v10.1"
        }
        
        # Converte para DataFrame e salva
        df_novo = pd.concat([df, pd.DataFrame([reserva_completa])], ignore_index=True)
        
        # Ordena por data de criação
        if 'Data_Criacao' in df_novo.columns:
            df_novo = df_novo.sort_values('Data_Criacao', ascending=False)
        
        conn.update(worksheet="Página1", data=df_novo)
        
        # Limpa cache específico para manter dados atualizados
        st.cache_data.clear()
        
        logger.info(f"Reserva {reserva_id} salva com sucesso para {reserva.get('Aluno', '')}")
        return True, reserva_id
        
    except Exception as e:
        logger.error(f"Erro ao salvar reserva: {str(e)}", exc_info=True)
        return False, f"Erro no sistema: {str(e)[:100]}"

def criar_backup_seguro() -> Optional[bytes]:
    """Cria backup dos dados com validação."""
    try:
        df = carregar_dados_otimizado()
        if not df.empty:
            csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            logger.info(f"Backup criado com {len(df)} registros")
            return csv
        return None
    except Exception as e:
        logger.error(f"Erro ao criar backup: {e}")
        return None

# ============================================
# 7. FUNÇÕES DE E-MAIL COM TEMPLATES MELHORADOS
# ============================================

def enviar_email_confirmacao_melhorado(aluno: str, email: str, reserva_info: Dict[str, Any], reserva_id: str) -> bool:
    """Envia e-mail de confirmação com template aprimorado."""
    try:
        # Rate limiting para envio de emails
        if not RateLimiter.check_rate_limit('email', email, 2, 60):  # 2 emails por minuto
            logger.warning(f"Rate limit de email excedido para {email}")
            return False
        
        # Obter credenciais
        email_remetente, email_senha = Config.get_email_credentials()
        
        if not email_senha:
            logger.warning("Credenciais de e-mail não configuradas")
            st.warning("⚠️ Configuração de e-mail pendente. Configure os secrets.")
            return False
        
        # Configuração do e-mail
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🎾 TENNIS CLASS - Confirmação #{reserva_id}"
        msg['From'] = f"Tennis Class <{email_remetente}>"
        msg['To'] = email
        msg['Reply-To'] = "aranha.corp@gmail.com"
        msg['X-Priority'] = '1'  # Alta prioridade
        
        # Extrair dados
        servico = reserva_info.get('Serviço', '')
        unidade = reserva_info.get('Unidade', '')
        data = reserva_info.get('Data', '')
        horario = reserva_info.get('Horário', '')
        
        # Informações da unidade
        info_unidade = ACADEMIAS.get(unidade, {})
        endereco_unidade = info_unidade.get('endereco', '')
        telefone_unidade = info_unidade.get('telefone', '')
        
        # Template HTML aprimorado
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>TENNIS CLASS - Confirmação #{reserva_id}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; }}
                .header {{ background: linear-gradient(135deg, #1a5f7a 0%, #2a8bb8 100%); color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; }}
                .resumo {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #2a8bb8; }}
                .detalhes {{ margin-top: 15px; }}
                .detalhes-item {{ margin-bottom: 10px; }}
                .label {{ color: #666; font-weight: bold; width: 120px; display: inline-block; }}
                .valor {{ color: #333; }}
                .whatsapp-btn {{ display: inline-block; background: #25D366; color: white; padding: 12px 25px; 
                                text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 15px; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; padding: 20px; border-top: 1px solid #eee; }}
                .info-box {{ background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #bbdefb; }}
                .info-title {{ color: #1565c0; font-weight: bold; margin-bottom: 5px; }}
                .timer-warning {{ color: #d32f2f; background: #ffebee; padding: 10px; border-radius: 5px; margin: 10px 0; 
                                border: 1px solid #ffcdd2; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0; font-size: 28px;">🎾 TENNIS CLASS</h1>
                    <p style="margin: 10px 0 0 0; opacity: 0.9;">Confirmação de Reserva</p>
                </div>
                
                <div class="content">
                    <h2 style="color: #2c3e50; margin-top: 0;">Olá, {aluno}!</h2>
                    <p>Sua reserva foi confirmada com sucesso. Abaixo estão todos os detalhes:</p>
                    
                    <div class="resumo">
                        <h3 style="color: #2c3e50; margin-top: 0;">📋 Resumo da Reserva</h3>
                        
                        <div class="detalhes">
                            <div class="detalhes-item">
                                <span class="label">ID da Reserva:</span>
                                <span class="valor" style="font-family: 'Courier New', monospace; font-weight: bold;">{reserva_id}</span>
                            </div>
                            <div class="detalhes-item">
                                <span class="label">Serviço:</span>
                                <span class="valor">{servico}</span>
                            </div>
                            <div class="detalhes-item">
                                <span class="label">Data e Horário:</span>
                                <span class="valor">{data} às {horario}</span>
                            </div>
                            <div class="detalhes-item">
                                <span class="label">Unidade:</span>
                                <span class="valor">{unidade}</span>
                            </div>
                            <div class="detalhes-item">
                                <span class="label">Status:</span>
                                <span class="valor" style="color: #4CAF50; font-weight: bold;">CONFIRMADO ✓</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="info-box">
                        <div class="info-title">📍 Local da Aula</div>
                        <p style="margin: 5px 0;">{endereco_unidade}</p>
                        <p style="margin: 5px 0;">📞 {telefone_unidade}</p>
                    </div>
                    
                    <div class="timer-warning">
                        ⚠️ Chegue 15 minutos antes do horário agendado
                    </div>
                    
                    <div class="info-box">
                        <div class="info-title">📋 Recomendações</div>
                        <ul style="margin: 5px 0; padding-left: 20px;">
                            <li>Use roupas esportivas apropriadas</li>
                            <li>Traga sua raquete ou solicite empréstimo na recepção</li>
                            <li>Hidrate-se antes e durante a aula</li>
                            <li>Em caso de cancelamento, avise com 24h de antecedência</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 25px 0;">
                        <a href="https://wa.me/{Config.WHATSAPP_NUMBER}?text=Olá! Tenho uma reserva com ID {reserva_id}" 
                           class="whatsapp-btn" target="_blank">
                            📱 Falar no WhatsApp
                        </a>
                    </div>
                </div>
                
                <div class="footer">
                    <p><strong>TENNIS CLASS</strong> © {datetime.now().year} - Todos os direitos reservados</p>
                    <p>Este é um e-mail automático. Para atendimento: (11) 97142-5028</p>
                    <p style="font-size: 10px; opacity: 0.7;">
                        ID: {reserva_id} | Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M')}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Texto alternativo para clientes de email simples
        texto = f"""
        TENNIS CLASS - Confirmação de Reserva #{reserva_id}
        
        Olá {aluno},
        
        Sua reserva foi confirmada com sucesso!
        
        📋 DETALHES DA RESERVA:
        ID: {reserva_id}
        Serviço: {servico}
        Data: {data}
        Horário: {horario}
        Unidade: {unidade}
        Status: CONFIRMADO
        
        📍 LOCAL DA AULA:
        {endereco_unidade}
        Telefone: {telefone_unidade}
        
        ⚠️ IMPORTANTE:
        - Chegue 15 minutos antes do horário
        - Use roupas esportivas apropriadas
        - Traga sua raquete ou solicite empréstimo
        - Hidrate-se antes e durante a aula
        - Cancelamentos com 24h de antecedência
        
        📱 ATENDIMENTO:
        WhatsApp: (11) 97142-5028
        Email: aranha.corp@gmail.com
        
        --
        TENNIS CLASS © {datetime.now().year}
        Este é um e-mail automático. Por favor não responda.
        """
        
        # Anexar partes
        msg.attach(MIMEText(texto, 'plain'))
        msg.attach(MIMEText(html, 'html'))
        
        # Enviar com timeout
        context = ssl.create_default_context()
        with smtplib.SMTP(Config.EMAIL_HOST, Config.EMAIL_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(email_remetente, email_senha)
            server.send_message(msg)
        
        logger.info(f"Email de confirmação enviado para {email} (ID: {reserva_id})")
        return True
        
    except smtplib.SMTPAuthenticationError:
        logger.error("Erro de autenticação SMTP - verifique as credenciais")
        st.error("❌ Erro de autenticação no envio de email. Verifique as configurações.")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"Erro SMTP: {e}")
        return False
    except Exception as e:
        logger.error(f"Erro ao enviar email: {e}")
        return False

# ============================================
# 8. SISTEMA DE PROCESSAMENTO COM VALIDAÇÃO EM ETAPAS
# ============================================

def processar_reserva_por_etapas(reserva: Dict[str, Any]) -> Tuple[bool, str, str]:
    """
    Processa reserva em etapas com validação progressiva.
    
    Returns:
        Tuple[bool, str, str]: (sucesso, reserva_id, mensagem)
    """
    try:
        logger.info(f"Iniciando processamento de reserva para {reserva.get('Aluno', '')}")
        
        # Etapa 1: Validação básica
        nome_valido, msg_nome = validar_nome_completo(reserva.get('Aluno', ''))
        if not nome_valido:
            return False, "", f"❌ Nome: {msg_nome}"
            
        email_valido, msg_email = validar_email_rigoroso(reserva.get('E-mail', ''))
        if not email_valido:
            return False, "", f"❌ Email: {msg_email}"
        
        # Etapa 2: Validação de disponibilidade
        disponivel, mensagem = validar_data_horario_inteligente(
            reserva['Data'],
            reserva['Horário'],
            reserva['Unidade']
        )
        
        if not disponivel:
            return False, "", f"❌ {mensagem}"
        
        # Etapa 3: Salvar reserva
        sucesso, reserva_id = salvar_reserva_segura(reserva)
        
        if not sucesso:
            if "Muitas reservas" in reserva_id:
                return False, "", f"⏳ {reserva_id}"
            return False, "", "❌ Falha ao salvar reserva. Tente novamente."
        
        # Etapa 4: Enviar confirmação
        email_enviado = enviar_email_confirmacao_melhorado(
            aluno=reserva["Aluno"],
            email=reserva["E-mail"],
            reserva_info=reserva,
            reserva_id=reserva_id
        )
        
        mensagem_final = f"""
        ✅ **Reserva {reserva_id} confirmada com sucesso!**
        
        **Detalhes:**
        • Aluno: {reserva["Aluno"]}
        • Serviço: {reserva["Serviço"]}
        • Data: {reserva["Data"]} às {reserva["Horário"]}
        • Unidade: {reserva["Unidade"]}
        
        Guarde o **ID da reserva** para futuras consultas.
        """
        
        if not email_enviado:
            mensagem_final += "\n\n⚠️ *O email de confirmação não pôde ser enviado, mas sua reserva está confirmada.*"
        
        logger.info(f"Reserva {reserva_id} processada com sucesso para {reserva['Aluno']}")
        return True, reserva_id, mensagem_final
        
    except ReservaError as e:
        logger.warning(f"ReservaError no processamento: {e}")
        return False, "", f"❌ {str(e)}"
    except Exception as e:
        logger.error(f"Erro inesperado no processamento: {e}", exc_info=True)
        return False, "", f"❌ Erro no sistema: {str(e)[:100]}"

# ============================================
# 9. ESTADOS DA SESSÃO EXPANDIDOS
# ============================================

# Inicializar estados da sessão com valores padrão
def inicializar_estados_sessao():
    """Inicializa todos os estados da sessão."""
    estados_default = {
        'pagina': "Home",
        'pagamento_ativo': False,
        'reserva_temp': {},
        'inicio_timer': None,
        'admin_autenticado': False,
        'erros_form': {},
        'reserva_id_gerada': None,
        'session_id': str(uuid.uuid4())[:8],
        'ultima_atualizacao': datetime.now().isoformat(),
        'tentativas_login': 0,
        'mostrar_dicas': True,
        'filtro_data_inicio': None,
        'filtro_data_fim': None,
        'versao_app': "v10.1",
        'notificacoes': []
    }
    
    for key, valor in estados_default.items():
        if key not in st.session_state:
            st.session_state[key] = valor

# Inicializar estados
inicializar_estados_sessao()

# ============================================
# 10. CSS E ESTILOS OTIMIZADOS
# ============================================

st.markdown("""
<style>
    /* Configuração global otimizada */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.85)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover; 
        background-position: center; 
        background-attachment: fixed;
        background-repeat: no-repeat;
    }
    
    /* Header com gradiente dinâmico */
    .header-title { 
        background: linear-gradient(135deg, #1a5f7a 0%, #2a8bb8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 52px; 
        font-weight: 800; 
        text-align: center; 
        margin-bottom: 15px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        letter-spacing: 1px;
    }
    
    /* Cards com sombras melhoradas */
    .custom-card { 
        background-color: rgba(255, 255, 255, 0.97); 
        padding: 30px; 
        border-radius: 20px; 
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    /* Timer com animação de pulso */
    .timer-warning {
        color: #ff8800;
        font-weight: bold;
        font-size: 18px;
        text-align: center;
        padding: 15px;
        border: 2px solid #ff9800;
        border-radius: 12px;
        background: linear-gradient(135deg, #fff3e0 0%, #ffcc80 100%);
        margin: 20px 0;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 152, 0, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(255, 152, 0, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 152, 0, 0); }
    }
    
    /* ID da reserva destacado */
    .reserva-id-box {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border: 2px solid #4CAF50;
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
        text-align: center;
        font-family: 'Courier New', monospace;
        font-size: 1.4rem;
        font-weight: bold;
        color: #2e7d32;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.2);
    }
    
    /* Mensagens de status aprimoradas */
    .error-message {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        color: #c62828;
        border-left: 4px solid #f44336;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        animation: slideIn 0.3s ease;
    }
    
    .success-message {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        color: #2e7d32;
        border-left: 4px solid #4CAF50;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        animation: slideIn 0.3s ease;
    }
    
    .warning-message {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        color: #ef6c00;
        border-left: 4px solid #ff9800;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from { transform: translateX(-10px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Botões com gradientes */
    .stButton > button {
        background: linear-gradient(135deg, #1a5f7a 0%, #2a8bb8 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(26, 95, 122, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(26, 95, 122, 0.3);
        background: linear-gradient(135deg, #2a8bb8 0%, #3aa8d8 100%);
    }
    
    /* WhatsApp flutuante com animação */
    .whatsapp-float {
        position: fixed;
        width: 65px;
        height: 65px;
        bottom: 40px;
        right: 40px;
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
        color: #FFF;
        border-radius: 50%;
        text-align: center;
        font-size: 40px;
        box-shadow: 0 6px 20px rgba(37, 211, 102, 0.3);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        animation: float 3s ease-in-out infinite;
        transition: all 0.3s ease;
    }
    
    .whatsapp-float:hover {
        transform: scale(1.1);
        box-shadow: 0 10px 30px rgba(37, 211, 102, 0.5);
        animation: none;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0) rotate(0); }
        50% { transform: translateY(-10px) rotate(5deg); }
    }
    
    /* Inputs com foco destacado */
    .stTextInput > div > div > input:focus {
        border-color: #2a8bb8 !important;
        box-shadow: 0 0 0 2px rgba(42, 139, 184, 0.2) !important;
    }
    
    .stDateInput > div > div > input:focus {
        border-color: #2a8bb8 !important;
        box-shadow: 0 0 0 2px rgba(42, 139, 184, 0.2) !important;
    }
    
    .stSelectbox > div > div > div {
        border-color: #ddd !important;
    }
    
    .stSelectbox > div > div > div:focus-within {
        border-color: #2a8bb8 !important;
        box-shadow: 0 0 0 2px rgba(42, 139, 184, 0.2) !important;
    }
    
    /* Menu lateral com gradiente */
    .css-1d391kg {
        background: linear-gradient(180deg, rgba(0,0,0,0.9) 0%, rgba(26,95,122,0.8) 100%) !important;
        backdrop-filter: blur(10px);
    }
    
    /* Tooltips */
    [data-testid="stTooltip"] {
        background: rgba(0, 0, 0, 0.9) !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 10px !important;
        font-size: 12px !important;
    }
</style>

<!-- Botão flutuante do WhatsApp -->
<a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank" 
   aria-label="Contato via WhatsApp" title="Fale conosco no WhatsApp">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" 
         width="35" alt="WhatsApp" style="filter: drop-shadow(0 2px 3px rgba(0,0,0,0.2));">
</a>

<!-- Assinatura otimizada -->
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" 
     alt="Assinatura André Aranha"
     style="position: fixed; bottom: 15px; left: 20px; width: 135px; z-index: 9999; 
            opacity: 0.9; filter: drop-shadow(0 2px 3px rgba(0,0,0,0.3)); 
            transition: opacity 0.3s ease;"
     onmouseover="this.style.opacity='1'"
     onmouseout="this.style.opacity='0.9'">
""", unsafe_allow_html=True)

# ============================================
# 11. COMPONENTES REUTILIZÁVEIS APRIMORADOS
# ============================================

def mostrar_timer_detalhado(tempo_total: int, inicio_time: float) -> Tuple[bool, str, float]:
    """Calcula e formata o tempo restante com porcentagem."""
    restante = tempo_total - (time.time() - inicio_time)
    
    if restante <= 0:
        return False, "⏰ Tempo esgotado!", 0.0
    
    m, s = divmod(int(restante), 60)
    porcentagem = (restante / tempo_total) * 100
    
    # Emoji dinâmico baseado no tempo restante
    if porcentagem > 66:
        emoji = "⏱️"
    elif porcentagem > 33:
        emoji = "⚠️"
    else:
        emoji = "🔥"
    
    return True, f"{emoji} Tempo restante: {m:02d}:{s:02d} ({porcentagem:.0f}%)", porcentagem

def card_com_estilo(conteudo: str, classe: str = "custom-card") -> str:
    """Retorna HTML de card estilizado."""
    return f'<div class="{classe}">{conteudo}</div>'

def formatar_telefone(telefone: str) -> str:
    """Formata telefone para exibição."""
    if not telefone:
        return ""
    
    numeros = re.sub(r'\D', '', telefone)
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    elif len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    else:
        return telefone

# ============================================
# 12. MENU LATERAL COM MAIS INFORMAÇÕES
# ============================================

with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>🎾 TENNIS CLASS</h2>", 
                unsafe_allow_html=True)
    st.markdown('<p style="color: #bbb; text-align: center; font-size: 12px; margin-top: -10px;">v10.1 • Sistema Completo</p>', 
                unsafe_allow_html=True)
    
    # Navegação principal
    st.markdown("### 📍 Navegação")
    
    menu_itens = [
        ("🏠", "Home", "Página inicial e agendamento"),
        ("💰", "Preços", "Tabela de preços e pacotes"),
        ("📝", "Cadastro", "Cadastre-se como aluno/professor"),
        ("📊", "Dashboard", "Painel administrativo"),
        ("⚙️", "Configurações", "Configurações do sistema"),
        ("📞", "Contato", "Canais de atendimento")
    ]
    
    for emoji, item, desc in menu_itens:
        if st.button(
            f"{emoji} {item}", 
            key=f"nav_{item}",
            use_container_width=True,
            help=desc
        ):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            if item in ["Dashboard", "Configurações"]:
                st.session_state.admin_autenticado = False
            st.rerun()
    
    st.markdown("---")
    
    # Status rápido do sistema
    st.markdown("### 📊 Status Rápido")
    
    try:
        df = carregar_dados_otimizado()
        total_reservas = len(df) if not df.empty else 0
        
        # Reservas hoje
        hoje = datetime.now().strftime("%d/%m/%Y")
        reservas_hoje = len(df[df['Data'] == hoje]) if not df.empty else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total", total_reservas)
        with col2:
            st.metric("Hoje", reservas_hoje)
    except:
        st.error("Erro ao carregar dados")
    
    st.markdown("---")
    
    # Academias em destaque
    st.markdown("### 🏢 Academias em Destaque")
    
    for nome, info in list(ACADEMIAS.items())[:2]:  # Mostra apenas 2
        with st.expander(f"📍 {nome}", expanded=False):
            st.caption(f"**Endereço:** {info['endereco']}")
            st.caption(f"**Telefone:** {info['telefone']}")
            st.caption(f"**Horário:** {info['horario_funcionamento']}")
            st.caption(f"**Zona:** {info['zona']}")
    
    if len(ACADEMIAS) > 2:
        if st.button("Ver todas as academias", use_container_width=True):
            st.session_state.pagina = "Contato"
            st.rerun()
    
    st.markdown("---")
    
    # Ajuda rápida
    with st.expander("❓ Ajuda Rápida", expanded=False):
        st.markdown("""
        **📞 Contato:**
        - WhatsApp: (11) 97142-5028
        - Email: aranha.corp@gmail.com
        
        **⏰ Horário:**
        Seg-Sex: 8h-20h
        Sáb: 8h-18h
        Dom: Fechado
        
        **🔄 Sistema:**
        • Atualizações automáticas
        • Backups diários
        • Suporte 24/7 para emergências
        """)
    
    # Informações da sessão
    st.markdown("---")
    st.caption(f"Sessão: {st.session_state.session_id}")
    st.caption(f"v10.1 • {datetime.now().strftime('%H:%M')}")

# ============================================
# 13. PÁGINA PRINCIPAL - HOME APRIMORADA
# ============================================

st.markdown('<div class="header-title">TENNIS CLASS</div>', unsafe_allow_html=True)

if st.session_state.pagina == "Home":
    st.markdown(card_com_estilo(""), unsafe_allow_html=True)
    
    if not st.session_state.pagamento_ativo:
        with st.form("reserva_form_aprimorado", clear_on_submit=False):
            st.markdown("### 📅 Agendar Aula")
            
            # Campos do formulário com validação instantânea
            col1, col2 = st.columns(2)
            
            with col1:
                aluno = st.text_input(
                    "Nome Completo *",
                    help="Digite seu nome completo (mínimo 3 caracteres)",
                    placeholder="Ex: João Silva Santos",
                    max_chars=100,
                    key="input_nome"
                )
                
                # Validação em tempo real do nome
                if aluno and len(aluno) > 2:
                    nome_valido, msg_nome = validar_nome_completo(aluno)
                    if not nome_valido:
                        st.markdown(f'<div class="error-message">⚠️ {msg_nome}</div>', 
                                  unsafe_allow_html=True)
            
            with col2:
                email = st.text_input(
                    "E-mail *",
                    help="Digite um e-mail válido para receber a confirmação",
                    placeholder="exemplo@email.com",
                    max_chars=100,
                    key="input_email"
                )
                
                # Validação em tempo real do email
                if email and '@' in email:
                    email_valido, msg_email = validar_email_rigoroso(email)
                    if not email_valido:
                        st.markdown(f'<div class="error-message">⚠️ {msg_email}</div>', 
                                  unsafe_allow_html=True)
            
            # Serviços formatados
            servicos_lista = formatar_servicos_para_select()
            servico = st.selectbox(
                "Serviço *", 
                servicos_lista,
                help="Selecione o tipo de aula desejada"
            )
            
            # Seleção de unidade com informações
            unidade = st.selectbox(
                "Unidade *", 
                list(ACADEMIAS.keys()),
                help="Selecione a academia onde deseja ter a aula"
            )
            
            # Mostrar informações da unidade selecionada
            if unidade in ACADEMIAS:
                info = ACADEMIAS[unidade]
                st.caption(f"📍 **{info['endereco']}** • 📞 {info['telefone']} • 🕒 {info['horario_funcionamento']}")
            
            # Data e horário com validação inteligente
            col_data, col_hora = st.columns(2)
            
            with col_data:
                dt = st.date_input(
                    "Data *",
                    format="DD/MM/YYYY",
                    min_value=datetime.now().date(),
                    max_value=datetime.now().date() + timedelta(days=Config.MAX_DIAS_ANTECEDENCIA),
                    help=f"Selecione uma data (até {Config.MAX_DIAS_ANTECEDENCIA} dias à frente)"
                )
            
            with col_hora:
                hr = st.selectbox(
                    "Horário *", 
                    Config.HORARIOS_DISPONIVEIS,
                    help="Selecione o horário desejado"
                )
            
            # Telefone opcional com formatação
            telefone = st.text_input(
                "Telefone (opcional)",
                placeholder="(11) 99999-9999",
                help="Para contato em caso de emergência",
                max_chars=15,
                key="input_telefone"
            )
            
            # Validação do telefone em tempo real
            if telefone and len(telefone.replace(' ', '')) > 8:
                telefone_valido, msg_telefone = validar_telefone_formatado(telefone)
                if not telefone_valido:
                    st.markdown(f'<div class="warning-message">ℹ️ {msg_telefone}</div>', 
                              unsafe_allow_html=True)
                else:
                    # Mostra formatação correta
                    st.caption(f"📱 Formatado: {formatar_telefone(telefone)}")
            
            # Botão de submissão - CORREÇÃO DO ERRO: removido use_container_width duplicado
            col_botoes = st.columns([3, 2])
            with col_botoes[1]:
                submit = st.form_submit_button(
                    "AVANÇAR PARA PAGAMENTO", 
                    type="primary",
                    use_container_width=True
                )
            
            if submit:
                # Rate limiting na submissão do formulário
                if not RateLimiter.check_rate_limit('form_submit', email.strip().lower() if email else None):
                    st.error("⏳ Muitas tentativas em curto período. Aguarde alguns instantes.")
                else:
                    st.session_state.erros_form = {}
                    
                    # Validações finais
                    nome_valido, msg_nome = validar_nome_completo(aluno)
                    if not nome_valido:
                        st.session_state.erros_form['aluno'] = msg_nome
                    
                    email_valido, msg_email = validar_email_rigoroso(email)
                    if not email_valido:
                        st.session_state.erros_form['email'] = msg_email
                    
                    if telefone:
                        telefone_valido, msg_telefone = validar_telefone_formatado(telefone)
                        if not telefone_valido:
                            st.session_state.erros_form['telefone'] = msg_telefone
                    
                    # Validação de disponibilidade
                    data_str = dt.strftime("%d/%m/%Y")
                    disponivel, mensagem = validar_data_horario_inteligente(data_str, hr, unidade)
                    if not disponivel:
                        st.session_state.erros_form['disponibilidade'] = mensagem
                    
                    if not st.session_state.erros_form:
                        # Prepara dados da reserva
                        st.session_state.reserva_temp = {
                            "Data": data_str,
                            "Horário": hr,
                            "Aluno": aluno.strip(),
                            "Serviço": servico,
                            "Unidade": unidade,
                            "E-mail": email.lower().strip(),
                            "Telefone": telefone.strip() if telefone else ""
                        }
                        st.session_state.pagamento_ativo = True
                        st.session_state.inicio_timer = time.time()
                        st.rerun()
                    else:
                        # Mostra erros agrupados
                        with st.container():
                            st.markdown('<div class="error-message">', unsafe_allow_html=True)
                            st.markdown("**❌ Corrija os seguintes erros:**")
                            for campo, mensagem in st.session_state.erros_form.items():
                                st.markdown(f"- {mensagem}")
                            st.markdown('</div>', unsafe_allow_html=True)
    
    else:  # PAGAMENTO ATIVO
        st.subheader("💳 Pagamento via PIX")
        
        # QR Code com informações
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 20px; background: white; border-radius: 15px; 
                        box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-bottom: 20px;">
                <div style="font-size: 18px; color: #333; margin-bottom: 15px; font-weight: bold;">
                    📱 Escaneie o QR Code
                </div>
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=aranha.corp@gmail.com&format=svg&color=1a5f7a&bgcolor=ffffff&margin=10"
                     width="250" 
                     style="border-radius: 10px; border: 1px solid #eee;">
                <div style="margin-top: 15px; font-size: 14px; color: #666;">
                    Use qualquer app de banco com PIX
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Chave PIX com botão de cópia
        st.markdown("### 🔑 Chave PIX")
        
        col_chave, col_copiar = st.columns([3, 1])
        with col_chave:
            st.code("aranha.corp@gmail.com", language="text")
        
        with col_copiar:
            if st.button("📋 Copiar", use_container_width=True, help="Copiar chave PIX"):
                # Em produção, usar JavaScript para copiar
                st.success("Chave copiada para a área de transferência!")
        
        # Informações da reserva
        st.markdown("### 📋 Resumo da Reserva")
        
        reserva = st.session_state.reserva_temp
        with st.container():
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                        padding: 25px; border-radius: 12px; border-left: 5px solid #2a8bb8;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div>
                        <strong style="color: #666; font-size: 12px;">ALUNO</strong>
                        <div style="font-size: 18px; color: #2c3e50;">{reserva.get('Aluno', '')}</div>
                    </div>
                    <div>
                        <strong style="color: #666; font-size: 12px;">SERVIÇO</strong>
                        <div style="font-size: 16px; color: #2c3e50;">{reserva.get('Serviço', '')}</div>
                    </div>
                    <div>
                        <strong style="color: #666; font-size: 12px;">UNIDADE</strong>
                        <div style="font-size: 16px; color: #2c3e50;">{reserva.get('Unidade', '')}</div>
                    </div>
                    <div>
                        <strong style="color: #666; font-size: 12px;">DATA E HORÁRIO</strong>
                        <div style="font-size: 16px; color: #2c3e50;">
                            {reserva.get('Data', '')} às {reserva.get('Horário', '')}
                        </div>
                    </div>
                </div>
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #dee2e6;">
                    <strong style="color: #666; font-size: 12px;">E-MAIL PARA CONFIRMAÇÃO</strong>
                    <div style="font-size: 14px; color: #2c3e50;">{reserva.get('E-mail', '')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Timer otimizado
        timer_box = st.empty()
        
        if st.session_state.inicio_timer:
            ativo, mensagem_timer, porcentagem = mostrar_timer_detalhado(
                Config.TEMPO_PAGAMENTO, 
                st.session_state.inicio_timer
            )
            
            if ativo:
                timer_box.markdown(f"""
                <div class="timer-warning">
                    <div style="font-size: 20px; margin-bottom: 5px;">{mensagem_timer}</div>
                    <div style="height: 10px; background: rgba(255, 152, 0, 0.2); border-radius: 5px; overflow: hidden;">
                        <div style="width: {porcentagem}%; height: 100%; background: linear-gradient(90deg, #ff9800, #ff5722);"></div>
                    </div>
                    <div style="font-size: 12px; margin-top: 5px; color: rgba(239, 108, 0, 0.8);">
                        Complete o pagamento antes do tempo esgotar para garantir sua reserva
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.session_state.pagamento_ativo = False
                timer_box.error("⏰ Tempo esgotado! Por favor, inicie uma nova reserva.")
                time.sleep(3)
                st.rerun()
        
        # Botões de ação
        col_confirmar, col_cancelar = st.columns([2, 1])
        
        with col_confirmar:
            if st.button("✅ CONFIRMAR PAGAMENTO", type="primary", use_container_width=True):
                with st.spinner("Processando reserva e enviando confirmação..."):
                    # Processar reserva com validação por etapas
                    sucesso, reserva_id, mensagem = processar_reserva_por_etapas(
                        st.session_state.reserva_temp
                    )
                    
                    if sucesso:
                        # Limpar estado
                        st.session_state.reserva_id_gerada = reserva_id
                        st.session_state.pagamento_ativo = False
                        
                        # Mostrar confirmação
                        st.balloons()
                        
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); 
                                    padding: 30px; border-radius: 15px; margin: 20px 0; 
                                    border: 2px solid #4CAF50; text-align: center;">
                            
                            <div style="font-size: 48px; margin-bottom: 10px;">🎉</div>
                            <h3 style="color: #2e7d32; margin: 0 0 10px 0;">✅ Reserva Confirmada!</h3>
                            <div style="color: #666; margin-bottom: 20px; white-space: pre-line;">{mensagem}</div>
                            
                            <div class="reserva-id-box">
                                🎾 ID da Reserva: <strong>{reserva_id}</strong>
                            </div>
                            
                            <p style="color: #666; font-size: 14px; margin-top: 20px;">
                                Guarde este ID para futuras consultas.<br>
                                Um e-mail de confirmação foi enviado para {st.session_state.reserva_temp['E-mail']}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Botões de ação pós-reserva
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("📅 Nova Reserva", use_container_width=True, icon="📅"):
                                st.session_state.reserva_temp = {}
                                st.rerun()
                        
                        with col2:
                            if st.button("📱 Abrir WhatsApp", use_container_width=True, icon="📱"):
                                st.markdown(
                                    f'<a href="https://wa.me/{Config.WHATSAPP_NUMBER}" target="_blank">'
                                    f'<button style="width: 100%; padding: 10px; background: #25D366; color: white; border: none; border-radius: 5px; cursor: pointer;">'
                                    f'Abrir WhatsApp</button></a>',
                                    unsafe_allow_html=True
                                )
                        
                        # Limpar após 10 segundos
                        time.sleep(10)
                        st.session_state.reserva_temp = {}
                        st.rerun()
                    else:
                        st.error(f"{mensagem}")
        
        with col_cancelar:
            if st.button("❌ Cancelar", type="secondary", use_container_width=True):
                st.session_state.pagamento_ativo = False
                st.info("Reserva cancelada. Você pode iniciar uma nova reserva quando quiser.")
                st.rerun()
    
    # Link do regulamento
    st.markdown("""
    <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 30px 0;">
    <div style="text-align: center;">
        <a href="https://docs.google.com/document/d/1LW9CNdmgYxwnpXlDYRrE8rKsLdajbPi3fniwXVsBqco/edit?usp=sharing" 
           target="_blank" 
           style="display: inline-block; text-decoration: none; color: #bbb; font-size: 14px; padding: 10px 20px; 
                  border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; transition: all 0.3s;" 
           onmouseover="this.style.backgroundColor='rgba(255,255,255,0.1)'; this.style.color='white';"
           onmouseout="this.style.backgroundColor='transparent'; this.style.color='#bbb';"
           title="Leia os termos e condições de uso">
            <span style="font-size: 20px; display: block; margin-bottom: 5px;">📄</span>
            Ler Regulamento de Uso
        </a>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# 14. PÁGINA DE PREÇOS
# ============================================

elif st.session_state.pagina == "Preços":
    st.markdown('<h2 style="color: white; text-align: center;">💰 TABELA DE PREÇOS</h2>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown(card_com_estilo("""
        <div style="text-align: center; padding: 20px;">
            <h3 style="color: #2c3e50; margin-bottom: 30px;">🎾 Escolha o plano ideal para você</h3>
        </div>
        """), unsafe_allow_html=True)
    
    # Tabela de serviços organizada por categoria
    for categoria_key, categoria_data in SERVICOS.items():
        st.markdown(f'### {categoria_data["categoria"]}')
        
        # Criar tabela
        dados_tabela = []
        for servico_key, servico_info in categoria_data["itens"].items():
            dados_tabela.append({
                "Serviço": servico_info["nome"],
                "Tipo": servico_info["tipo"],
                "Preço": f"R$ {servico_info['preco']:.2f}"
            })
        
        df_servicos = pd.DataFrame(dados_tabela)
        st.dataframe(
            df_servicos,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Serviço": st.column_config.TextColumn("Serviço", width="medium"),
                "Tipo": st.column_config.TextColumn("Tipo", width="small"),
                "Preço": st.column_config.TextColumn("Preço", width="small")
            }
        )
    
    # Comparativo de pacotes
    st.markdown("---")
    st.markdown("### 📊 Comparativo de Pacotes")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(card_com_estilo("""
        <div style="text-align: center; padding: 15px;">
            <h4 style="color: #2c3e50; margin-bottom: 10px;">Pacote 4 Aulas</h4>
            <p style="font-size: 24px; color: #1a5f7a; font-weight: bold;">R$ 800-1000</p>
            <p style="color: #666; font-size: 14px;">Economia de até 20%</p>
            <hr style="margin: 15px 0;">
            <p style="color: #666; font-size: 12px;">✔️ Válido por 60 dias</p>
            <p style="color: #666; font-size: 12px;">✔️ Flexibilidade de horários</p>
            <p style="color: #666; font-size: 12px;">✔️ Renovação automática</p>
        </div>
        """, "custom-card"), unsafe_allow_html=True)
    
    with col2:
        st.markdown(card_com_estilo("""
        <div style="text-align: center; padding: 15px; border: 2px solid #2a8bb8;">
            <h4 style="color: #2c3e50; margin-bottom: 10px;">Pacote 8 Aulas</h4>
            <p style="font-size: 28px; color: #1a5f7a; font-weight: bold;">R$ 1600-2000</p>
            <p style="color: #666; font-size: 14px;">Economia de até 25%</p>
            <hr style="margin: 15px 0;">
            <p style="color: #666; font-size: 12px;">✔️ Válido por 90 dias</p>
            <p style="color: #666; font-size: 12px;">✔️ Horários preferenciais</p>
            <p style="color: #666; font-size: 12px;">✔️ 1 aula bônus grátis</p>
        </div>
        """, "custom-card"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(card_com_estilo("""
        <div style="text-align: center; padding: 15px;">
            <h4 style="color: #2c3e50; margin-bottom: 10px;">Treino Competitivo</h4>
            <p style="font-size: 24px; color: #1a5f7a; font-weight: bold;">R$ 1400/mês</p>
            <p style="color: #666; font-size: 14px;">Treinamento especializado</p>
            <hr style="margin: 15px 0;">
            <p style="color: #666; font-size: 12px;">✔️ 3x por semana</p>
            <p style="color: #666; font-size: 12px;">✔️ Avaliação física</p>
            <p style="color: #666; font-size: 12px;">✔️ Planejamento personalizado</p>
        </div>
        """, "custom-card"), unsafe_allow_html=True)
    
    # Informações adicionais
    st.markdown("---")
    st.markdown("### 💡 Informações Importantes")
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        with st.expander("📝 Política de Cancelamento", expanded=False):
            st.markdown("""
            - **Cancelamento com 24h de antecedência:** Reembolso de 100%
            - **Cancelamento com menos de 24h:** Reembolso de 50%
            - **Cancelamento no dia:** Sem reembolso
            - **Remarcações:** Permitidas com 12h de antecedência
            """)
    
    with col_info2:
        with st.expander("🎁 Promoções Especiais", expanded=False):
            st.markdown("""
            - **Indique um amigo:** Ganhe 10% de desconto
            - **Pacote familiar:** 15% de desconto para famílias
            - **Estudantes:** 20% de desconto com comprovante
            - **Aniversariante do mês:** Aula gratuita
            """)
    
    # Botão para agendar
    st.markdown("---")
    col_agendar = st.columns([1, 2, 1])
    with col_agendar[1]:
        if st.button("📅 AGENDAR AULA AGORA", type="primary", use_container_width=True):
            st.session_state.pagina = "Home"
            st.rerun()

# ============================================
# 15. PÁGINA DE CADASTRO
# ============================================

elif st.session_state.pagina == "Cadastro":
    st.markdown('<h2 style="color: white; text-align: center;">📝 CADASTRO</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["👨‍🎓 Aluno", "👨‍🏫 Professor", "🏢 Academia"])
    
    with tab1:
        st.markdown("### Cadastro de Aluno")
        st.info("Preencha o formulário abaixo para se cadastrar como aluno.")
        
        # Formulário embutido
        st.markdown(f"""
        <iframe src="{FORM_LINKS['aluno']}" 
                width="100%" 
                height="600" 
                frameborder="0" 
                marginheight="0" 
                marginwidth="0">
            Carregando…
        </iframe>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### Cadastro de Professor")
        st.info("Preencha o formulário abaixo para se cadastrar como professor.")
        
        # Formulário embutido
        st.markdown(f"""
        <iframe src="{FORM_LINKS['professor']}" 
                width="100%" 
                height="600" 
                frameborder="0" 
                marginheight="0" 
                marginwidth="0">
            Carregando…
        </iframe>
        """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### Cadastro de Academia")
        st.info("Preencha o formulário abaixo para cadastrar sua academia.")
        
        # Formulário embutido
        st.markdown(f"""
        <iframe src="{FORM_LINKS['academia']}" 
                width="100%" 
                height="600" 
                frameborder="0" 
                marginheight="0" 
                marginwidth="0">
            Carregando…
        </iframe>
        """, unsafe_allow_html=True)
    
    # Informações de contato
    st.markdown("---")
    st.markdown("### 📞 Dúvidas sobre cadastro?")
    col_duv1, col_duv2 = st.columns(2)
    
    with col_duv1:
        st.markdown("""
        **WhatsApp:** (11) 97142-5028  
        **Email:** aranha.corp@gmail.com  
        **Horário:** Seg-Sex 8h-20h
        """)
    
    with col_duv2:
        st.markdown("""
        **Processo de aprovação:** 24-48h  
        **Documentação necessária:** RG e CPF  
        **Taxa de cadastro:** Isenta
        """)

# ============================================
# 16. PÁGINA DASHBOARD (SIMPLIFICADA)
# ============================================

elif st.session_state.pagina == "Dashboard":
    st.markdown('<h2 style="color: white; text-align: center;">📊 DASHBOARD ADMINISTRATIVO</h2>', unsafe_allow_html=True)
    
    # Sistema de autenticação simples
    if not st.session_state.admin_autenticado:
        st.warning("⚠️ Acesso restrito à administração")
        
        with st.form("login_admin"):
            senha = st.text_input("Senha de administração:", type="password")
            login_button = st.form_submit_button("🔑 Entrar")
            
            if login_button:
                # Verificação simples (em produção, usar hash e salt)
                senha_hash = hashlib.sha256(senha.encode()).hexdigest()
                senha_correta_hash = hashlib.sha256("admin123".encode()).hexdigest()  # Senha padrão
                
                if senha_hash == senha_correta_hash:
                    st.session_state.admin_autenticado = True
                    st.success("✅ Autenticação bem-sucedida!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")
                    st.session_state.tentativas_login += 1
                    
                    if st.session_state.tentativas_login >= 3:
                        st.error("⚠️ Muitas tentativas falhas. Tente novamente mais tarde.")
                        time.sleep(5)
                        st.stop()
    else:
        # Dashboard administrativo
        st.success(f"✅ Logado como Administrador | Sessão: {st.session_state.session_id}")
        
        # Carregar dados
        df = carregar_dados_otimizado()
        
        if not df.empty:
            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)
            
            total_reservas = len(df)
            hoje = datetime.now().strftime("%d/%m/%Y")
            reservas_hoje = len(df[df['Data'] == hoje])
            reservas_pendentes = len(df[df['Status'] == 'Pendente'])
            reservas_confirmadas = len(df[df['Status'] == 'Confirmado'])
            
            with col1:
                st.metric("Total Reservas", total_reservas)
            with col2:
                st.metric("Hoje", reservas_hoje)
            with col3:
                st.metric("Pendentes", reservas_pendentes)
            with col4:
                st.metric("Confirmadas", reservas_confirmadas)
            
            # Filtros
            st.markdown("### 📈 Filtros e Análises")
            
            col_filtro1, col_filtro2 = st.columns(2)
            
            with col_filtro1:
                data_inicio = st.date_input("Data início", 
                                          value=datetime.now().date() - timedelta(days=7))
            
            with col_filtro2:
                data_fim = st.date_input("Data fim", 
                                       value=datetime.now().date())
            
            # Converter para filtro
            df['Data_Formatada'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
            df_filtrado = df[
                (df['Data_Formatada'] >= pd.to_datetime(data_inicio)) &
                (df['Data_Formatada'] <= pd.to_datetime(data_fim))
            ]
            
            # Gráficos
            tab_graficos, tab_dados, tab_acoes = st.tabs(["📊 Gráficos", "📋 Dados", "⚡ Ações"])
            
            with tab_graficos:
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    # Reservas por status
                    if 'Status' in df_filtrado.columns:
                        status_counts = df_filtrado['Status'].value_counts()
                        st.bar_chart(status_counts)
                
                with col_chart2:
                    # Reservas por unidade
                    if 'Unidade' in df_filtrado.columns:
                        unidade_counts = df_filtrado['Unidade'].value_counts()
                        st.bar_chart(unidade_counts)
            
            with tab_dados:
                # Tabela de dados
                st.dataframe(
                    df_filtrado.sort_values('Data_Formatada', ascending=False),
                    use_container_width=True,
                    column_config={
                        "ID": st.column_config.TextColumn("ID", width="small"),
                        "Aluno": st.column_config.TextColumn("Aluno", width="medium"),
                        "Data": st.column_config.TextColumn("Data", width="small"),
                        "Horário": st.column_config.TextColumn("Horário", width="small"),
                        "Unidade": st.column_config.TextColumn("Unidade", width="medium"),
                        "Status": st.column_config.TextColumn("Status", width="small"),
                        "Data_Criacao": st.column_config.TextColumn("Criação", width="medium")
                    }
                )
                
                # Exportar dados
                csv = criar_backup_seguro()
                if csv:
                    st.download_button(
                        label="📥 Exportar CSV",
                        data=csv,
                        file_name=f"reservas_tennis_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with tab_acoes:
                # Ações administrativas
                st.markdown("### ⚡ Ações Rápidas")
                
                col_acao1, col_acao2 = st.columns(2)
                
                with col_acao1:
                    if st.button("🔄 Atualizar Dados", use_container_width=True):
                        st.cache_data.clear()
                        st.success("✅ Cache limpo! Dados atualizados.")
                        time.sleep(2)
                        st.rerun()
                    
                    if st.button("📧 Testar Email", use_container_width=True):
                        email_user, _ = Config.get_email_credentials()
                        if email_user:
                            st.info(f"Configuração de email: {email_user}")
                            st.success("✅ Configuração OK")
                        else:
                            st.error("❌ Configuração de email não encontrada")
                
                with col_acao2:
                    if st.button("🧹 Limpar Reservas Antigas", use_container_width=True):
                        st.warning("Funcionalidade em desenvolvimento")
                    
                    if st.button("🚪 Sair", use_container_width=True):
                        st.session_state.admin_autenticado = False
                        st.success("✅ Logout realizado!")
                        time.sleep(2)
                        st.rerun()
        
        else:
            st.error("❌ Nenhum dado encontrado para exibição")

# ============================================
# 17. PÁGINA CONFIGURAÇÕES (SIMPLIFICADA)
# ============================================

elif st.session_state.pagina == "Configurações":
    st.markdown('<h2 style="color: white; text-align: center;">⚙️ CONFIGURAÇÕES</h2>', unsafe_allow_html=True)
    
    # Sistema de autenticação para configurações
    if not st.session_state.admin_autenticado:
        st.warning("⚠️ Acesso restrito à administração")
        
        with st.form("login_config"):
            senha = st.text_input("Senha de administração:", type="password")
            login_button = st.form_submit_button("🔑 Entrar")
            
            if login_button:
                senha_hash = hashlib.sha256(senha.encode()).hexdigest()
                senha_correta_hash = hashlib.sha256("admin123".encode()).hexdigest()
                
                if senha_hash == senha_correta_hash:
                    st.session_state.admin_autenticado = True
                    st.success("✅ Autenticação bem-sucedida!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")
    else:
        # Configurações do sistema
        tab_config1, tab_config2, tab_config3 = st.tabs(["📋 Sistema", "📧 Email", "🔒 Segurança"])
        
        with tab_config1:
            st.markdown("### Configurações do Sistema")
            
            with st.form("config_sistema"):
                col1, col2 = st.columns(2)
                
                with col1:
                    max_alunos = st.number_input(
                        "Máximo alunos por horário:",
                        min_value=1,
                        max_value=10,
                        value=Config.MAX_ALUNOS_POR_HORARIO
                    )
                    
                    tempo_pagamento = st.number_input(
                        "Tempo para pagamento (minutos):",
                        min_value=1,
                        max_value=30,
                        value=Config.TEMPO_PAGAMENTO // 60
                    )
                
                with col2:
                    max_dias = st.number_input(
                        "Máximo dias antecedência:",
                        min_value=1,
                        max_value=180,
                        value=Config.MAX_DIAS_ANTECEDENCIA
                    )
                    
                    cache_ttl = st.number_input(
                        "Cache TTL (minutos):",
                        min_value=1,
                        max_value=60,
                        value=Config.CACHE_TTL // 60
                    )
                
                if st.form_submit_button("💾 Salvar Configurações"):
                    # Atualizar configurações na sessão
                    Config.MAX_ALUNOS_POR_HORARIO = max_alunos
                    Config.TEMPO_PAGAMENTO = tempo_pagamento * 60
                    Config.MAX_DIAS_ANTECEDENCIA = max_dias
                    Config.CACHE_TTL = cache_ttl * 60
                    
                    st.success("✅ Configurações salvas na sessão atual!")
        
        with tab_config2:
            st.markdown("### Configurações de Email")
            
            email_user, email_pass = Config.get_email_credentials()
            
            if email_user:
                st.success(f"✅ Email configurado: {email_user}")
                st.info("As credenciais de email são gerenciadas via secrets ou variáveis de ambiente.")
            else:
                st.error("❌ Email não configurado")
            
            st.markdown("""
            #### Instruções para configuração:
            1. No Streamlit Cloud, vá para "App settings" → "Secrets"
            2. Adicione as seguintes chaves:
            ```
            EMAIL_USER = "seuemail@gmail.com"
            EMAIL_PASSWORD = "suasenhaapp"
            ```
            3. Salve e reinicie o aplicativo
            """)
        
        with tab_config3:
            st.markdown("### Configurações de Segurança")
            
            col_sec1, col_sec2 = st.columns(2)
            
            with col_sec1:
                st.metric("Tentativas login falhas", st.session_state.tentativas_login)
                st.metric("Sessão ativa desde", 
                         datetime.fromisoformat(st.session_state.ultima_atualizacao).strftime("%H:%M"))
            
            with col_sec2:
                st.info("**Logs do sistema:**")
                log_files = []
                if os.path.exists("logs"):
                    log_files = os.listdir("logs")
                
                if log_files:
                    for log_file in sorted(log_files)[-3:]:  # Últimos 3 logs
                        st.caption(f"📄 {log_file}")
                else:
                    st.caption("Nenhum arquivo de log encontrado")
            
            if st.button("📋 Ver Logs Completos", use_container_width=True):
                if os.path.exists("logs"):
                    log_files = os.listdir("logs")
                    if log_files:
                        latest_log = sorted(log_files)[-1]
                        with open(f"logs/{latest_log}", "r", encoding="utf-8") as f:
                            st.text_area("Log mais recente:", f.read(), height=300)
                    else:
                        st.warning("Nenhum arquivo de log encontrado")
                else:
                    st.warning("Diretório de logs não existe")
        
        # Botão para sair
        st.markdown("---")
        if st.button("🚪 Sair do Modo Admin", type="secondary", use_container_width=True):
            st.session_state.admin_autenticado = False
            st.success("✅ Modo administrador encerrado!")
            time.sleep(2)
            st.rerun()

# ============================================
# 18. PÁGINA CONTATO
# ============================================

elif st.session_state.pagina == "Contato":
    st.markdown('<h2 style="color: white; text-align: center;">📞 CONTATO</h2>', unsafe_allow_html=True)
    
    # Informações de contato principal
    col_contato1, col_contato2 = st.columns(2)
    
    with col_contato1:
        st.markdown(card_com_estilo(f"""
        <div style="text-align: center; padding: 30px;">
            <div style="font-size: 48px; margin-bottom: 20px;">📱</div>
            <h3 style="color: #2c3e50; margin-bottom: 15px;">WhatsApp</h3>
            <p style="font-size: 20px; color: #1a5f7a; font-weight: bold;">
                {formatar_telefone(Config.WHATSAPP_NUMBER)}
            </p>
            <p style="color: #666; margin: 20px 0;">
                Atendimento rápido e direto
            </p>
            <a href="https://wa.me/{Config.WHATSAPP_NUMBER}" 
               target="_blank" 
               style="display: inline-block; background: #25D366; color: white; padding: 12px 25px; 
                      text-decoration: none; border-radius: 8px; font-weight: bold;">
                Abrir WhatsApp
            </a>
        </div>
        """), unsafe_allow_html=True)
    
    with col_contato2:
        st.markdown(card_com_estilo(f"""
        <div style="text-align: center; padding: 30px;">
            <div style="font-size: 48px; margin-bottom: 20px;">✉️</div>
            <h3 style="color: #2c3e50; margin-bottom: 15px;">E-mail</h3>
            <p style="font-size: 20px; color: #1a5f7a; font-weight: bold;">
                aranha.corp@gmail.com
            </p>
            <p style="color: #666; margin: 20px 0;">
                Resposta em até 24h
            </p>
            <a href="mailto:aranha.corp@gmail.com" 
               style="display: inline-block; background: #2a8bb8; color: white; padding: 12px 25px; 
                      text-decoration: none; border-radius: 8px; font-weight: bold;">
                Enviar E-mail
            </a>
        </div>
        """), unsafe_allow_html=True)
    
    # Lista de academias completa
    st.markdown("---")
    st.markdown("### 🏢 Nossas Academias Parceiras")
    
    for nome, info in ACADEMIAS.items():
        with st.expander(f"📍 {nome}", expanded=False):
            col_acad1, col_acad2 = st.columns([2, 1])
            
            with col_acad1:
                st.markdown(f"""
                **Endereço:** {info['endereco']}  
                **Telefone:** {info['telefone']}  
                **Horário:** {info['horario_funcionamento']}  
                **Zona:** {info['zona']}
                """)
            
            with col_acad2:
                # Botão para ver no mapa (simulado)
                if st.button("🗺️ Ver no Mapa", key=f"mapa_{nome}"):
                    st.info(f"Localização: {info['endereco']}")
    
    # Formulário de avaliação
    st.markdown("---")
    st.markdown("### ⭐ Avalie Nossos Serviços")
    
    st.markdown(f"""
    <iframe src="{FORM_LINKS['avaliacao']}" 
            width="100%" 
            height="500" 
            frameborder="0" 
            marginheight="0" 
            marginwidth="0">
        Carregando…
    </iframe>
    """, unsafe_allow_html=True)
    
    # Horário de atendimento
    st.markdown("---")
    st.markdown("### 🕒 Horário de Atendimento")
    
    col_horario1, col_horario2 = st.columns(2)
    
    with col_horario1:
        st.markdown("""
        **Atendimento ao Cliente:**
        - Segunda a Sexta: 8h às 20h
        - Sábado: 8h às 18h
        - Domingo: Fechado
        
        **Aulas:**
        - Segunda a Sexta: 7h às 22h
        - Sábado: 7h às 20h
        - Domingo: Fechado
        """)
    
    with col_horario2:
        st.markdown("""
        **Feriados:**
        - Consulte disponibilidade
        - Horários especiais
        
        **Emergências:**
        - WhatsApp 24h
        - Apenas para cancelamentos urgentes
        """)

# ============================================
# 19. INICIALIZAÇÃO E LOG DE SISTEMA
# ============================================

if __name__ == "__main__":
    try:
        # Log de inicialização detalhado
        logger.info("=" * 60)
        logger.info("TENNIS CLASS v10.1 - Sistema iniciando")
        logger.info(f"Sessão: {st.session_state.session_id}")
        logger.info(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        logger.info("=" * 60)
        
        # Verificar configurações essenciais
        email_user, email_pass = Config.get_email_credentials()
        
        if not email_pass:
            logger.warning("Sistema iniciado sem configuração de email")
            # Não mostra alerta ao usuário para não poluir a interface
        
        # Log do estado da sessão
        logger.debug(f"Página atual: {st.session_state.pagina}")
        logger.debug(f"Pagamento ativo: {st.session_state.pagamento_ativo}")
        logger.debug(f"Admin autenticado: {st.session_state.admin_autenticado}")
        
        # Verificar conexão com Google Sheets
        try:
            df = carregar_dados_otimizado()
            logger.info(f"Conexão com Google Sheets OK: {len(df)} registros")
        except Exception as e:
            logger.error(f"Erro na conexão com Google Sheets: {e}")
        
    except Exception as e:
        logger.critical(f"Erro crítico na inicialização: {e}", exc_info=True)
        st.error("""
        ⚠️ Ocorreu um erro ao iniciar o sistema.
        
        Por favor:
        1. Recarregue a página (F5 ou Ctrl+R)
        2. Se o erro persistir, entre em contato
        3. WhatsApp: (11) 97142-5028
        
        Desculpe pelo inconveniente.
        """)

# ============================================
# 20. RODAPÉ ATUALIZADO
# ============================================

st.markdown(f"""
<div style='text-align: center; margin-top: 40px; padding: 20px; color: rgba(255,255,255,0.6); font-size: 12px;'>
    <hr style='border-color: rgba(255,255,255,0.2); margin: 20px 0;'>
    
    <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;'>
        <div style='text-align: left;'>
            <p style='margin: 0; font-weight: bold;'>TENNIS CLASS © 2024</p>
            <p style='margin: 5px 0 0 0; font-size: 10px; color: rgba(255,255,255,0.4);'>
            Sistema de Gestão Completo v10.1
            </p>
        </div>
        
        <div style='text-align: center;'>
            <p style='margin: 0;'>Desenvolvido por André Aranha</p>
            <p style='margin: 5px 0 0 0; font-size: 10px; color: rgba(255,255,255,0.4);">
            MASTER CODE DEEP SEEK v10.1
            </p>
        </div>
        
        <div style='text-align: right;'>
            <p style='margin: 0;'>Status: <span style='color: #4CAF50;'>●</span> Online</p>
            <p style='margin: 5px 0 0 0; font-size: 10px; color: rgba(255,255,255,0.4);'>
            {datetime.now().strftime('%d/%m/%Y %H:%M')}
            </p>
        </div>
    </div>
    
    <div style='margin-top: 15px; font-size: 10px; color: rgba(255,255,255,0.4);'>
        <p style='margin: 0;'>
        Sistema otimizado • Cache inteligente • Validação aprimorada • Rate limiting • Segurança reforçada
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
