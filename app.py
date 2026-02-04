# ============================================
# TENNIS CLASS MANAGEMENT SYSTEM
# Versão 2.0 - Corrigido e Otimizado
# ============================================

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import re
import uuid
import os
import logging
from datetime import datetime, date
from typing import Dict, Any, Optional, Tuple

# ============================================
# 1. CONFIGURAÇÃO INICIAL
# ============================================

# Configurar logging simplificado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('tennis_class')

# Configuração da página Streamlit
st.set_page_config(
    page_title="TENNIS CLASS PRO",
    layout="wide",
    page_icon="🎾",
    initial_sidebar_state="expanded"
)

# ============================================
# 2. CONSTANTES E CONFIGURAÇÕES
# ============================================

# Senha admin - usando secrets do Streamlit
try:
    SENHA_ADMIN = st.secrets.get("ADMIN_PASSWORD", "tennispro2024")
except:
    SENHA_ADMIN = "tennispro2024"

# Serviços disponíveis - ESTRUTURA CORRIGIDA
SERVICOS = {
    "AULA PARTICULAR": {
        "nome": "Aula particular", 
        "preco": 250, 
        "icone": "🎾",
        "descricao": "Aula individual com foco total no aluno",
        "categoria": "Aulas",
        "unidade": "/hora"
    },
    "AULA EM GRUPO": {
        "nome": "Aula em grupo", 
        "preco": 200, 
        "icone": "👥",
        "descricao": "Aula em grupo de até 4 pessoas",
        "categoria": "Aulas",
        "unidade": "/hora"
    },
    "AULA KIDS": {
        "nome": "Aula Kids", 
        "preco": 200, 
        "icone": "👶",
        "descricao": "Aula especializada para crianças",
        "categoria": "Aulas",
        "unidade": "/hora"
    },
    "PERSONAL TRAINER": {
        "nome": "Personal trainer", 
        "preco": 250, 
        "icone": "💪",
        "descricao": "Treinamento personalizado",
        "categoria": "Treinamento",
        "unidade": "/hora"
    },
    "COMPETITIVO": {
        "nome": "Treinamento competitivo", 
        "preco": 1400, 
        "icone": "🏆",
        "descricao": "Pacote mensal para competidores",
        "categoria": "Treinamento",
        "unidade": "/mês"
    },
    "EVENTOS": {
        "nome": "Eventos", 
        "preco": 0, 
        "icone": "🎉",
        "descricao": "Organização de eventos especiais",
        "categoria": "Especial",
        "unidade": "a combinar"
    }
}

# Academias parceiras
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

# Links dos formulários
FORM_LINKS = {
    "aluno": "https://docs.google.com/forms/d/e/1FAIpQLSdehkMHlLyCNd1owC-dSNO_-ROXq07w41jgymyKyFugvUZ0fA/viewform",
    "academia": "https://docs.google.com/forms/d/e/1FAIpQLScaC-XBLuzTPN78inOQPcXd6r0BzaessEke1MzOfGzOIlZpwQ/viewform",
    "professor": "https://docs.google.com/forms/d/e/1FAIpQLSdHicvD5MsOTnpfWwmpXOm8b268_S6gXoBZEysIo4Wj5cL2yw/viewform"
}

# Constantes de tempo
TEMPO_PAGAMENTO = 300  # 5 minutos em segundos

# ============================================
# 3. FUNÇÕES AUXILIARES
# ============================================

def validar_email(email: str) -> bool:
    """Valida formato de e-mail."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validar_nome(nome: str) -> bool:
    """Valida nome (mínimo 3 caracteres)."""
    nome_limpo = nome.strip()
    return len(nome_limpo) >= 3

def validar_telefone(telefone: str) -> bool:
    """Valida formato de telefone brasileiro."""
    telefone_limpo = re.sub(r'\D', '', telefone)
    return len(telefone_limpo) in [10, 11]

def formatar_moeda(valor: float) -> str:
    """Formata valor em moeda brasileira."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@st.cache_data(ttl=300)
def carregar_dados() -> pd.DataFrame:
    """Carrega dados do Google Sheets com cache."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Página1")
        
        if not df.empty:
            if 'Data' in df.columns:
                df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
            if 'Timestamp' in df.columns:
                df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        
        return df
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {str(e)}")
        st.error(f"❌ Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

def salvar_reserva(reserva: Dict[str, Any]) -> bool:
    """Salva uma reserva no Google Sheets."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = carregar_dados()
        
        # Adiciona ID único e timestamp
        reserva["ID"] = str(uuid.uuid4())[:8]
        reserva["Timestamp"] = datetime.now().isoformat()
        reserva["Status"] = "Pendente"
        
        df_novo = pd.concat([df, pd.DataFrame([reserva])], ignore_index=True)
        conn.update(worksheet="Página1", data=df_novo)
        
        # Limpa cache
        st.cache_data.clear()
        
        logger.info(f"Reserva salva: {reserva.get('Aluno')}")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar reserva: {str(e)}")
        st.error(f"❌ Erro ao salvar reserva: {str(e)}")
        return False

def mostrar_timer(tempo_total: int, inicio_time: float) -> Tuple[bool, str]:
    """Calcula e formata o tempo restante."""
    restante = tempo_total - (time.time() - inicio_time)
    if restante <= 0:
        return False, "⏰ Tempo esgotado!"
    
    m, s = divmod(int(restante), 60)
    return True, f"⏱️ Expira em: {m:02d}:{s:02d}"

# ============================================
# 4. ESTADOS DA SESSÃO
# ============================================

# Inicializar estados da sessão
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
# 5. CSS ATUALIZADO (COM BALÕES CINZA TRANSPARENTES)
# ============================================

st.markdown("""
<style>
    /* Fundo principal */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/Fundo%20APP%20ver2.png");
        background-size: cover;
        background-position: center;
        min-height: 100vh;
    }
    
    /* Títulos */
    .header-title { 
        color: white; 
        font-size: 50px; 
        font-weight: bold; 
        text-align: center; 
        margin-bottom: 20px; 
        text-shadow: 2px 2px 4px black; 
    }
    
    /* Cards principais */
    .custom-card { 
        background-color: rgba(255, 255, 255, 0.95); 
        padding: 30px; 
        border-radius: 20px; 
        color: #333; 
        margin: 0 auto;
        max-width: 1000px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* Balões de contato - CINZA COM TRANSPARÊNCIA */
    .contact-bubble {
        background-color: rgba(100, 100, 100, 0.15) !important;
        padding: 25px;
        border-radius: 15px;
        margin: 15px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .contact-bubble:hover {
        background-color: rgba(100, 100, 100, 0.25) !important;
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .contact-bubble h3 {
        color: #FFD700;
        margin-top: 0;
    }
    
    .contact-bubble p {
        color: #f0f0f0;
        margin-bottom: 5px;
    }
    
    .contact-bubble strong {
        color: white;
        font-size: 18px;
    }
    
    /* Links */
    .clean-link { 
        text-align: center; 
        text-decoration: none !important; 
        color: white !important; 
        transition: all 0.3s ease; 
        display: block; 
        padding: 20px; 
        border-radius: 10px;
        background-color: rgba(0, 0, 0, 0.3);
        margin: 10px 0;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .clean-link:hover { 
        transform: translateY(-5px); 
        color: #FFD700 !important; 
        background-color: rgba(0, 0, 0, 0.5);
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        border-color: #FFD700;
    }
    
    .icon-text { 
        font-size: 50px;
        margin-bottom: 10px; 
    }
    
    .label-text { 
        font-size: 18px; 
        font-weight: bold; 
        letter-spacing: 1px; 
        margin-bottom: 8px;
    }
    
    /* WhatsApp flutuante */
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
        transition: all 0.3s ease;
    }
    
    .whatsapp-float:hover {
        transform: scale(1.1);
    }
    
    /* Assinatura */
    .assinatura-footer { 
        position: fixed; 
        bottom: 15px; 
        left: 20px; 
        width: 130px; 
        z-index: 9999; 
        opacity: 0.8;
    }
    
    /* Sidebar */
    .sidebar-detalhe { 
        font-size: 11px; 
        color: #ccc; 
        margin-bottom: 10px; 
        line-height: 1.2; 
    }
    
    /* Mensagens de erro/sucesso */
    .error-message {
        color: #ff4444;
        font-size: 14px;
        margin-top: 5px;
        padding: 8px 12px;
        border-radius: 6px;
        background-color: rgba(255, 68, 68, 0.1);
        border-left: 4px solid #ff4444;
    }
    
    .success-message {
        color: #00C851;
        font-size: 14px;
        margin-top: 5px;
        padding: 8px 12px;
        border-radius: 6px;
        background-color: rgba(0, 200, 81, 0.1);
        border-left: 4px solid #00C851;
    }
    
    /* Timer */
    .timer-warning {
        color: #ff8800;
        font-weight: bold;
        font-size: 16px;
        text-align: center;
        padding: 12px;
        border: 2px solid #ff8800;
        border-radius: 10px;
        background-color: rgba(255, 136, 0, 0.1);
    }
    
    /* Bola de tênis amarela */
    .tennis-ball-yellow {
        color: #FFD700 !important;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.7);
    }
    
    /* Botões */
    .stButton > button {
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    }
    
    /* Tabela de preços */
    .price-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #FFD700;
    }
    
    .price-title {
        color: #333;
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 5px;
    }
    
    .price-value {
        color: #4CAF50;
        font-weight: bold;
        font-size: 20px;
    }
    
    .price-description {
        color: #666;
        font-size: 14px;
        margin-top: 5px;
    }
</style>

<!-- Botão WhatsApp Flutuante -->
<a href="https://wa.me/5511971425028" class="whatsapp-float" target="_blank">
    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" 
         width="35" alt="WhatsApp">
</a>

<!-- Assinatura -->
<img src="https://raw.githubusercontent.com/Aranhacorp/Tennis-Class/main/By%20Andre%20Aranha.png" 
     class="assinatura-footer" 
     alt="Assinatura">
""", unsafe_allow_html=True)

# ============================================
# 6. MENU LATERAL
# ============================================

with st.sidebar:
    st.markdown("<h2 style='color: #FFD700; text-align: center;'>🎾 MENU</h2>", 
                unsafe_allow_html=True)
    
    menu_items = ["Home", "Preços", "Cadastro", "Dashboard", "Contato"]
    
    for item in menu_items:
        if st.button(f"🎾 {item}", key=f"nav_{item}", use_container_width=True):
            st.session_state.pagina = item
            st.session_state.pagamento_ativo = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("<h3 style='color: #FFD700;'>🎾 ACADEMIAS</h3>", 
                unsafe_allow_html=True)
    
    for nome, info in ACADEMIAS.items():
        st.markdown(
            f"📍 **{nome}**\n"
            f"<div class='sidebar-detalhe'>"
            f"{info['endereco']}<br>📞 {info['telefone']}"
            f"</div>", 
            unsafe_allow_html=True
        )

# ============================================
# 7. TÍTULO PRINCIPAL
# ============================================

st.markdown('<div class="header-title"><span class="tennis-ball-yellow">🎾</span> TENNIS CLASS PRO</div>', 
            unsafe_allow_html=True)

# ============================================
# 8. LÓGICA DAS PÁGINAS
# ============================================

# PÁGINA: HOME
if st.session_state.pagina == "Home":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    if not st.session_state.pagamento_ativo:
        with st.form("reserva_form", clear_on_submit=True):
            st.markdown('<h3 style="text-align: center; color: #333;">🎾 Agendar Aula</h3>', 
                       unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                aluno = st.text_input(
                    "Nome do Aluno *",
                    placeholder="Ex: João Silva"
                )
            with col2:
                email = st.text_input(
                    "E-mail *",
                    placeholder="Ex: joao.silva@email.com"
                )
            
            # Lista de serviços formatada corretamente
            servicos_lista = [
                f"{info['icone']} {info['nome']} - R$ {info['preco']} {info['unidade']}"
                for key, info in SERVICOS.items()
            ]
            
            col3, col4 = st.columns(2)
            with col3:
                servico = st.selectbox("Serviço *", servicos_lista)
            with col4:
                unidade = st.selectbox("Unidade *", list(ACADEMIAS.keys()))
            
            col5, col6 = st.columns(2)
            with col5:
                dt = st.date_input("Data *", format="DD/MM/YYYY")
            with col6:
                hr = st.selectbox("Horário *", [f"{h:02d}:00" for h in range(7, 23)])
            
            telefone = st.text_input(
                "Telefone (opcional)",
                placeholder="(11) 99999-9999"
            )
            
            observacoes = st.text_area(
                "Observações (opcional)",
                placeholder="Alguma observação especial..."
            )
            
            submit = st.form_submit_button(
                "🎾 AVANÇAR PARA PAGAMENTO", 
                use_container_width=True,
                type="primary"
            )
            
            if submit:
                st.session_state.erros_form = {}
                
                if not validar_nome(aluno):
                    st.session_state.erros_form['aluno'] = "Nome deve ter pelo menos 3 caracteres."
                
                if not validar_email(email):
                    st.session_state.erros_form['email'] = "E-mail inválido."
                
                if telefone and not validar_telefone(telefone):
                    st.session_state.erros_form['telefone'] = "Telefone inválido."
                
                if not st.session_state.erros_form:
                    st.session_state.reserva_temp = {
                        "Data": dt.strftime("%d/%m/%Y"),
                        "Horário": hr,
                        "Aluno": aluno.strip(),
                        "Serviço": servico,
                        "Unidade": unidade,
                        "E-mail": email.lower().strip(),
                        "Telefone": telefone.strip() if telefone else "",
                        "Observações": observacoes.strip() if observacoes else ""
                    }
                    st.session_state.pagamento_ativo = True
                    st.session_state.inicio_timer = time.time()
                    st.rerun()
                else:
                    for campo, mensagem in st.session_state.erros_form.items():
                        st.markdown(f'<div class="error-message">❌ {mensagem}</div>', 
                                  unsafe_allow_html=True)
    
    else:  # PAGAMENTO ATIVO
        st.subheader("💳 Pagamento via PIX")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # QR Code
            st.image(
                "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=aranha.corp@gmail.com",
                width=250
            )
            
            # Chave PIX
            st.markdown("""
            <div style="background: #f5f5f5; padding: 15px; border-radius: 10px; margin: 20px 0; text-align: center;">
                <p style="font-family: monospace; font-size: 18px; margin: 0;">
                    <strong>aranha.corp@gmail.com</strong>
                </p>
                <p style="font-size: 14px; color: #666; margin-top: 10px;">
                    Copie a chave PIX e faça o pagamento
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Timer
        if st.session_state.inicio_timer:
            ativo, mensagem_timer = mostrar_timer(
                TEMPO_PAGAMENTO, 
                st.session_state.inicio_timer
            )
            
            if ativo:
                st.markdown(
                    f'<div class="timer-warning">{mensagem_timer}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.session_state.pagamento_ativo = False
                st.error("⏰ Tempo esgotado! Por favor, inicie uma nova reserva.")
                st.rerun()
        
        # Botão de confirmação
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎾 CONFIRMAR PAGAMENTO", type="primary", use_container_width=True):
                if salvar_reserva(st.session_state.reserva_temp):
                    st.balloons()
                    st.markdown(
                        '<div class="success-message">'
                        '✅ Reserva confirmada! Você receberá um e-mail de confirmação.'
                        '</div>',
                        unsafe_allow_html=True
                    )
                    
                    # Limpa estado
                    st.session_state.pagamento_ativo = False
                    st.session_state.reserva_temp = {}
                    time.sleep(3)
                    st.rerun()
        
        # Botão para cancelar
        if st.button("❌ Cancelar Pagamento", type="secondary", use_container_width=True):
            st.session_state.pagamento_ativo = False
            st.rerun()
    
    # Regulamento
    st.markdown("""
    <hr style="margin: 30px 0;">
    <div style="text-align: center;">
        <a href="https://docs.google.com/document/d/1LW9CNdmgYxwnpXlDYrE8rKsLdajbPi3fniwXVsBqco/edit" 
           target="_blank" 
           style="text-decoration: none; color: #555; padding: 10px; display: inline-block;">
            📄 Ler Regulamento de Uso
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA: PREÇOS - CORRIGIDA
elif st.session_state.pagina == "Preços":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    st.markdown('<h3 style="text-align: center; color: #333;">🎾 Tabela de Preços</h3>', 
               unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Agrupar serviços por categoria
    categorias = {}
    for key, info in SERVICOS.items():
        categoria = info.get('categoria', 'Outros')
        if categoria not in categorias:
            categorias[categoria] = []
        categorias[categoria].append((key, info))
    
    # Exibir por categoria
    for categoria, servicos in categorias.items():
        st.markdown(f"### {categoria}")
        
        for key, info in servicos:
            if key == "EVENTOS":
                st.markdown(f"""
                <div class="price-card">
                    <div class="price-title">{info['icone']} {info['nome']}</div>
                    <div class="price-value">Valor a combinar</div>
                    <div class="price-description">{info['descricao']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="price-card">
                    <div class="price-title">{info['icone']} {info['nome']}</div>
                    <div class="price-value">R$ {info['preco']} {info['unidade']}</div>
                    <div class="price-description">{info['descricao']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.info("💡 *Valores sujeitos a alteração. Consulte condições especiais para pacotes.*")
    
    st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA: CADASTRO
elif st.session_state.pagina == "Cadastro":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    st.markdown('<h3 style="text-align: center; color: #333;">🎾 Portal de Cadastros</h3>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; margin-bottom: 30px; color: #666;'>
        Clique em uma das opções abaixo para preencher o formulário correspondente
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <a href="{FORM_LINKS['aluno']}" 
           class="clean-link" 
           target="_blank">
            <div class="icon-text">👤</div>
            <div class="label-text">ALUNO</div>
            <div style="font-size: 13px; color: rgba(255, 255, 255, 0.8); margin-top: 10px;">
                Formulário para novos alunos
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <a href="{FORM_LINKS['academia']}" 
           class="clean-link" 
           target="_blank">
            <div class="icon-text">🏢</div>
            <div class="label-text">ACADEMIA</div>
            <div style="font-size: 13px; color: rgba(255, 255, 255, 0.8); margin-top: 10px;">
                Para academias parceiras
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <a href="{FORM_LINKS['professor']}" 
           class="clean-link" 
           target="_blank">
            <div class="icon-text">🎾</div>
            <div class="label-text">PROFESSOR</div>
            <div style="font-size: 13px; color: rgba(255, 255, 255, 0.8); margin-top: 10px;">
                Para professores parceiros
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA: CONTATO - COM BALÕES CINZA TRANSPARENTES
elif st.session_state.pagina == "Contato":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    st.markdown('<h3 style="text-align: center; color: #333;">🎾 Canais de Atendimento</h3>', 
               unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # BALÃO DE E-MAIL - CINZA TRANSPARENTE
        st.markdown("""
        <div class="contact-bubble">
            <h3>📧 E-mail</h3>
            <p><strong>aranha.corp@gmail.com</strong></p>
            <p>Respondemos em até 24 horas úteis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # BALÃO DE WHATSAPP - CINZA TRANSPARENTE
        st.markdown("""
        <div class="contact-bubble">
            <h3>📱 WhatsApp</h3>
            <p><strong>(11) 97142-5028</strong></p>
            <p>Atendimento direto</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Formulário de contato
    st.markdown("### ✉️ Envie uma mensagem")
    
    with st.form("contato_form"):
        nome_contato = st.text_input("Seu nome *")
        email_contato = st.text_input("Seu e-mail *")
        mensagem = st.text_area("Mensagem *", height=150)
        
        enviar = st.form_submit_button("📤 Enviar Mensagem", type="primary")
        
        if enviar:
            if nome_contato and email_contato and mensagem:
                if validar_email(email_contato):
                    st.success("✅ Mensagem enviada! Entraremos em contato em breve.")
                    # Aqui você poderia adicionar lógica para enviar o e-mail
                else:
                    st.error("❌ E-mail inválido. Digite um e-mail válido.")
            else:
                st.warning("⚠️ Preencha todos os campos obrigatórios (*).")
    
    st.markdown('</div>', unsafe_allow_html=True)

# PÁGINA: DASHBOARD
elif st.session_state.pagina == "Dashboard":
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    
    if not st.session_state.admin_autenticado:
        st.markdown('<h3 style="text-align: center; color: #333;">🎾 Acesso Administrativo</h3>', 
                   unsafe_allow_html=True)
        
        senha = st.text_input(
            "Digite a senha de administrador:", 
            type="password",
            placeholder="Digite a senha..."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔓 Acessar", use_container_width=True):
                if senha == SENHA_ADMIN:
                    st.session_state.admin_autenticado = True
                    st.success("✅ Acesso concedido!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")
        
        with col2:
            if st.button("🔙 Voltar", use_container_width=True):
                st.session_state.pagina = "Home"
                st.rerun()
    
    else:
        st.markdown('<h3 style="text-align: center; color: #333;">🎾 Dashboard - Reservas</h3>', 
                   unsafe_allow_html=True)
        
        # Botão de logout
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            st.session_state.admin_autenticado = False
            st.rerun()
        
        st.markdown("---")
        
        # Carregar dados
        try:
            df = carregar_dados()
            
            if not df.empty:
                # Métricas
                total = len(df)
                pendentes = len(df[df['Status'] == 'Pendente']) if 'Status' in df.columns else 0
                confirmados = len(df[df['Status'] == 'Confirmado']) if 'Status' in df.columns else 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Reservas", total)
                with col2:
                    st.metric("Pendentes", pendentes)
                with col3:
                    st.metric("Confirmados", confirmados)
                
                st.markdown("---")
                
                # Tabela
                st.dataframe(
                    df.sort_values('Data', ascending=False) if 'Data' in df.columns else df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Data": st.column_config.DateColumn(
                            "Data",
                            format="DD/MM/YYYY"
                        ),
                        "Status": st.column_config.SelectboxColumn(
                            "Status",
                            options=["Pendente", "Confirmado", "Cancelado"]
                        )
                    }
                )
                
                # Ações
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Atualizar Dados", use_container_width=True):
                        st.cache_data.clear()
                        st.success("✅ Dados atualizados!")
                        time.sleep(1)
                        st.rerun()
                
                with col2:
                    if not df.empty:
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Exportar CSV",
                            data=csv,
                            file_name=f"reservas_tennis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
            else:
                st.info("📭 Nenhuma reserva encontrada.")
                
        except Exception as e:
            st.error(f"❌ Erro ao carregar dashboard: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# 9. RODAPÉ
# ============================================

st.markdown("""
<div style="text-align: center; color: #888; margin-top: 50px; padding: 20px; font-size: 12px;">
    <hr style="border: none; border-top: 1px solid #444; margin: 20px auto; width: 50%;">
    <p>Tennis Class Pro &copy; 2024 - Sistema de Gestão de Aulas de Tênis</p>
    <p style="font-size: 11px;">v2.0 - Desenvolvido com Streamlit</p>
</div>
""", unsafe_allow_html=True)
