# ============================================
# MASTER CODE DEEP SEEK v.12.4 (SQLite - revisado)
# ============================================
# ... (cabeçalho igual, apenas adicionei melhorias)
# ============================================

import streamlit as st
import pandas as pd
import time
import re
import uuid
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, List, Optional
import logging
from functools import lru_cache

# ... (todo o código anterior, mas com as melhorias abaixo)

# ============================================
# 2. CONFIGURAÇÕES DO SISTEMA
# ============================================

class Config:
    """Classe de configuração centralizada do sistema."""
    
    # Caminho absoluto do banco SQLite
    DB_PATH = os.path.abspath("tennis_class.db")
    
    # ... (restante igual)

# ============================================
# 4. FUNÇÕES DE BANCO DE DADOS (SQLite) - MELHORADAS
# ============================================

def check_write_permission():
    """Verifica se o diretório tem permissão de escrita."""
    try:
        test_file = os.path.join(os.path.dirname(Config.DB_PATH), "test_write.tmp")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        return True, None
    except Exception as e:
        return False, str(e)

def get_db_connection():
    """Retorna uma conexão com o banco SQLite."""
    return sqlite3.connect(Config.DB_PATH)

def init_database():
    """Cria a tabela de reservas se não existir."""
    try:
        # Verifica permissão
        ok, err = check_write_permission()
        if not ok:
            st.error(f"❌ Sem permissão de escrita no diretório: {err}")
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservas (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                horario TEXT NOT NULL,
                aluno TEXT NOT NULL,
                servico TEXT NOT NULL,
                unidade TEXT NOT NULL,
                email TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT DEFAULT 'Confirmado',
                data_criacao TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        logger.info(f"Banco de dados inicializado em: {Config.DB_PATH}")
        return True
    except Exception as e:
        logger.error(f"Erro ao inicializar banco: {e}")
        st.error(f"❌ Erro ao criar banco de dados: {e}")
        return False

# Chama a inicialização e guarda o resultado
DB_INIT_SUCCESS = init_database()

@st.cache_data(ttl=300)
def carregar_dados() -> pd.DataFrame:
    """Carrega todas as reservas do banco SQLite."""
    if not DB_INIT_SUCCESS:
        st.error("❌ Banco de dados não foi inicializado corretamente.")
        return pd.DataFrame()
    try:
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT * FROM reservas", conn)
        conn.close()
        logger.info(f"Dados carregados: {len(df)} registros")
        return df
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {str(e)}")
        st.error(f"❌ Erro ao carregar dados do banco: {str(e)}")
        return pd.DataFrame()

@lru_cache(maxsize=128)
def carregar_disponibilidade(data: str, unidade: str) -> Dict[str, int]:
    """Calcula vagas disponíveis para uma data/unidade."""
    try:
        df = carregar_dados()
        if df.empty:
            return {hora: Config.MAX_ALUNOS_POR_HORARIO for hora in Config.HORARIOS_DISPONIVEIS}
        
        # Filtra reservas ativas
        filtrado = df[
            (df['data'] == data) &
            (df['unidade'] == unidade) &
            (df['status'].isin(['Pendente', 'Confirmado']))
        ]
        
        # Conta por horário
        disponibilidade = {}
        for hora in Config.HORARIOS_DISPONIVEIS:
            count = len(filtrado[filtrado['horario'] == hora])
            disponibilidade[hora] = Config.MAX_ALUNOS_POR_HORARIO - count
        return disponibilidade
    except Exception as e:
        logger.error(f"Erro ao carregar disponibilidade: {e}")
        return {hora: Config.MAX_ALUNOS_POR_HORARIO for hora in Config.HORARIOS_DISPONIVEIS}

def salvar_reserva(reserva: Dict[str, Any]) -> Tuple[bool, str]:
    """Salva uma nova reserva no banco SQLite."""
    if not DB_INIT_SUCCESS:
        return False, "Banco de dados não inicializado"
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        reserva_id = str(uuid.uuid4())[:8].upper()
        
        cursor.execute('''
            INSERT INTO reservas 
            (id, data, horario, aluno, servico, unidade, email, timestamp, status, data_criacao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            reserva_id,
            reserva.get('Data'),
            reserva.get('Horário'),
            reserva.get('Aluno'),
            reserva.get('Serviço'),
            reserva.get('Unidade'),
            reserva.get('E-mail'),
            datetime.now().isoformat(),
            'Confirmado',
            datetime.now().strftime("%d/%m/%Y %H:%M")
        ))
        
        conn.commit()
        conn.close()
        st.cache_data.clear()
        carregar_disponibilidade.cache_clear()  # limpa cache da disponibilidade
        logger.info(f"Reserva {reserva_id} salva com sucesso")
        return True, reserva_id
    except Exception as e:
        logger.error(f"Erro ao salvar reserva: {str(e)}")
        return False, f"Erro no banco de dados: {str(e)}"

# ... (restante do código permanece igual, mas adicionei no Dashboard uma seção de diagnóstico)

# ============================================
# 14. PÁGINA DASHBOARD (com diagnóstico)
# ============================================

elif st.session_state.pagina == "Dashboard":
    st.markdown(card_com_estilo(), unsafe_allow_html=True)
    if not st.session_state.admin_autenticado:
        st.subheader("🔐 Acesso Administrativo")
        senha = st.text_input("Senha de administrador:", type="password", placeholder="Digite a senha...")
        col1, _ = st.columns([3, 1])
        with col1:
            if st.button("🔓 Acessar", use_container_width=True):
                if verificar_senha_admin(senha):
                    st.session_state.admin_autenticado = True
                    st.success("✅ Acesso concedido!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Senha incorreta!")
    else:
        st.subheader("📊 Dashboard - Reservas")
        
        # Diagnóstico do banco de dados
        with st.expander("🛠️ Diagnóstico do Banco de Dados"):
            st.write(f"**Caminho do banco:** `{Config.DB_PATH}`")
            st.write(f"**Arquivo existe?** {os.path.exists(Config.DB_PATH)}")
            if os.path.exists(Config.DB_PATH):
                st.write(f"**Tamanho:** {os.path.getsize(Config.DB_PATH)} bytes")
            # Teste de conexão
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reservas'")
                table_exists = cursor.fetchone() is not None
                conn.close()
                if table_exists:
                    st.success("✅ Tabela 'reservas' existe.")
                else:
                    st.error("❌ Tabela 'reservas' NÃO existe.")
            except Exception as e:
                st.error(f"❌ Erro ao conectar: {e}")
        
        try:
            df = carregar_dados()
            # ... (restante do código do dashboard)
