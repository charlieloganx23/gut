import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime
import numpy as np

st.set_page_config(
    page_title="Matriz GUT 2.0 - Votação Colaborativa",
    page_icon="⚖️",
    layout="wide"
)

# ===================== ESTILOS =====================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1rem; border-radius: 10px; color: white;
        text-align: center; margin-bottom: 2rem;
    }
    .admin-header {
        background: linear-gradient(90deg, #dc2626 0%, #ef4444 100%);
        padding: 1rem; border-radius: 10px; color: white;
        text-align: center; margin-bottom: 2rem;
    }
    .participant-header {
        background: linear-gradient(90deg, #059669 0%, #10b981 100%);
        padding: 1rem; border-radius: 10px; color: white;
        text-align: center; margin-bottom: 2rem;
    }
    .priority-high { background:#fee2e2; border-left:5px solid #dc2626; padding:1rem; }
    .priority-medium { background:#fef3c7; border-left:5px solid #f59e0b; padding:1rem; }
    .priority-low { background:#dcfce7; border-left:5px solid #16a34a; padding:1rem; }
    .vote-card { 
        background:#f8fafc; 
        border:1px solid #e2e8f0; 
        border-radius:8px; 
        padding:1.5rem; 
        margin:1.5rem 0; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .problem-title {
        background: linear-gradient(90deg, #3b82f6 0%, #1e40af 100%);
        color: white;
        padding: 0.8rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        font-weight: bold;
        font-size: 1.1em;
    }
    .problem-description {
        background: #f1f5f9;
        padding: 0.8rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        font-style: italic;
        color: #475569;
    }
    .consensus-high { color: #16a34a; font-weight: bold; }
    .consensus-medium { color: #f59e0b; font-weight: bold; }
    .consensus-low { color: #dc2626; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ===================== BANCO DE DADOS =====================
DATABASE_FILE = 'matriz_gut.db'

def init_database():
    """Inicializa o banco de dados SQLite"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Tabela de problemas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS problemas (
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            descricao TEXT,
            timestamp TEXT
        )
    ''')
    
    # Tabela de votos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problema_id TEXT,
            participante TEXT,
            gravidade INTEGER,
            urgencia INTEGER,
            tendencia INTEGER,
            timestamp TEXT,
            UNIQUE(problema_id, participante),
            FOREIGN KEY (problema_id) REFERENCES problemas (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Retorna conexão com o banco"""
    return sqlite3.connect(DATABASE_FILE)

def gerar_id_problema(nome):
    """Gera ID único para o problema"""
    import hashlib
    return hashlib.md5(nome.encode()).hexdigest()[:12]

def adicionar_problema_db(nome, descricao=""):
    """Adiciona problema no banco de dados"""
    pid = gerar_id_problema(nome)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO problemas (id, nome, descricao, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (pid, nome, descricao, timestamp))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Erro ao adicionar problema: {e}")
        return False
    finally:
        conn.close()

def listar_problemas_db():
    """Lista todos os problemas do banco"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, nome, descricao, timestamp FROM problemas ORDER BY timestamp')
    problemas = cursor.fetchall()
    conn.close()
    
    return [{"id": p[0], "nome": p[1], "descricao": p[2], "timestamp": p[3]} for p in problemas]

def remover_problema_db(problema_id):
    """Remove problema e seus votos do banco"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Remove votos do problema
        cursor.execute('DELETE FROM votos WHERE problema_id = ?', (problema_id,))
        # Remove o problema
        cursor.execute('DELETE FROM problemas WHERE id = ?', (problema_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Erro ao remover problema: {e}")
        return False
    finally:
        conn.close()

def votar_problema_db(problema_id, participante, gravidade, urgencia, tendencia):
    """Registra ou atualiza voto no banco"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO votos 
            (problema_id, participante, gravidade, urgencia, tendencia, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (problema_id, participante, gravidade, urgencia, tendencia, timestamp))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Erro ao registrar voto: {e}")
        return False
    finally:
        conn.close()

def obter_voto_participante_db(problema_id, participante):
    """Obtém voto específico de um participante para um problema"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT gravidade, urgencia, tendencia FROM votos 
        WHERE problema_id = ? AND participante = ?
    ''', (problema_id, participante))
    
    voto = cursor.fetchone()
    conn.close()
    
    if voto:
        return {"gravidade": voto[0], "urgencia": voto[1], "tendencia": voto[2]}
    return None

def calcular_estatisticas_completas_db(problema_id):
    """Calcula estatísticas completas incluindo somatórios e dispersão"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT gravidade, urgencia, tendencia FROM votos 
        WHERE problema_id = ?
    ''', (problema_id,))
    
    votos = cursor.fetchall()
    conn.close()
    
    if not votos:
        return None
    
    # Separar critérios
    g_values = [v[0] for v in votos]
    u_values = [v[1] for v in votos]
    t_values = [v[2] for v in votos]
    
    # Calcular estatísticas
    total_votos = len(votos)
    
    # Médias
    mg = np.mean(g_values)
    mu = np.mean(u_values)
    mt = np.mean(t_values)
    
    # Somatórios
    sg = sum(g_values)
    su = sum(u_values)
    st = sum(t_values)
    
    # Desvios padrão
    std_g = np.std(g_values) if len(g_values) > 1 else 0
    std_u = np.std(u_values) if len(u_values) > 1 else 0
    std_t = np.std(t_values) if len(t_values) > 1 else 0
    
    # Pontuação GUT
    gut_media = mg * mu * mt
    
    # Consenso (menor desvio = maior consenso)
    def avaliar_consenso(std_val):
        if std_val <= 0.8: return "Alto"
        elif std_val <= 1.5: return "Médio"
        else: return "Baixo"
    
    consenso_g = avaliar_consenso(std_g)
    consenso_u = avaliar_consenso(std_u)
    consenso_t = avaliar_consenso(std_t)
    
    return {
        "total": total_votos,
        "mg": round(mg, 2), "mu": round(mu, 2), "mt": round(mt, 2),
        "sg": sg, "su": su, "st": st,
        "std_g": round(std_g, 2), "std_u": round(std_u, 2), "std_t": round(std_t, 2),
        "gut": round(gut_media, 2),
        "consenso_g": consenso_g, "consenso_u": consenso_u, "consenso_t": consenso_t
    }

def obter_estatisticas_db():
    """Obtém estatísticas gerais do banco"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total de problemas
    cursor.execute('SELECT COUNT(*) FROM problemas')
    total_problemas = cursor.fetchone()[0]
    
    # Total de votos
    cursor.execute('SELECT COUNT(*) FROM votos')
    total_votos = cursor.fetchone()[0]
    
    # Participantes únicos
    cursor.execute('SELECT COUNT(DISTINCT participante) FROM votos')
    participantes_unicos = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "problemas": total_problemas,
        "votos": total_votos,
        "participantes": participantes_unicos
    }

def resetar_banco_db():
    """Reseta completamente o banco de dados"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM votos')
        cursor.execute('DELETE FROM problemas')
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Erro ao resetar banco: {e}")
        return False
    finally:
        conn.close()

def classificar_prioridade(pontuacao):
    """Classifica prioridade baseada na pontuação GUT"""
    return ("🔴 ALTA", "priority-high") if pontuacao >= 64 else ("🟡 MÉDIA", "priority-medium") if pontuacao >= 27 else ("🟢 BAIXA", "priority-low")

def formatar_consenso(consenso):
    """Formata consenso com cores"""
    if consenso == "Alto":
        return f'<span class="consensus-high">✅ {consenso}</span>'
    elif consenso == "Médio":
        return f'<span class="consensus-medium">⚠️ {consenso}</span>'
    else:
        return f'<span class="consensus-low">❌ {consenso}</span>'

# ===================== ESTADOS DE SESSÃO =====================
if 'modo' not in st.session_state: 
    st.session_state.modo = 'selecao'
if 'participante_id' not in st.session_state: 
    st.session_state.participante_id = None
if 'admin_logado' not in st.session_state: 
    st.session_state.admin_logado = False

# Inicializar banco na primeira execução
init_database()

# ===================== TELAS =====================

# ========== TELA SELEÇÃO ==========
if st.session_state.modo == 'selecao':
    st.markdown("""<div class="main-header"><h1>⚖️ Matriz GUT 2.0</h1><h3>Tribunal de Justiça de Rondônia</h3><p>Sistema de Votação Colaborativa com Dashboard Executivo</p></div>""", unsafe_allow_html=True)
    
    # Mostrar estatísticas gerais
    stats = obter_estatisticas_db()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📋 Problemas", stats["problemas"])
    with col2:
        st.metric("🗳️ Votos", stats["votos"])
    with col3:
        st.metric("👥 Participantes", stats["participantes"])
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔐 Administrador", use_container_width=True): 
            st.session_state.modo = 'login_admin'
            st.rerun()
    with col2:
        if st.button("👥 Participante", use_container_width=True): 
            st.session_state.modo = 'login_participante'
            st.rerun()
    with col3:
        if st.button("📊 Resultados", use_container_width=True): 
            st.session_state.modo = 'resultados'
            st.rerun()

# ========== LOGIN ADMIN ==========
elif st.session_state.modo == 'login_admin':
    st.markdown("""<div class="admin-header"><h2>🔐 Acesso Admin</h2></div>""", unsafe_allow_html=True)
    
    senha = st.text_input("Senha:", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Entrar", type="primary"):
            if senha == "0000": 
                st.session_state.admin_logado = True
                st.session_state.modo = 'admin'
                st.rerun() 
            else: 
                st.error("❌ Senha incorreta")
    with col2:
        if st.button("🏠 Voltar ao Início"): 
            st.session_state.modo = 'selecao'
            st.rerun()

# ========== PAINEL ADMIN ==========
elif st.session_state.modo == 'admin' and st.session_state.admin_logado:
    st.markdown("""<div class="admin-header"><h2>⚙️ Painel Administrativo</h2></div>""", unsafe_allow_html=True)
    
    # Botões de navegação
    colA, colB = st.columns(2)
    with colA:
        if st.button("🏠 Voltar ao Início"): 
            st.session_state.modo = 'selecao'
            st.rerun()
    with colB:
        if st.button("🗑️ Resetar Oficina (Apagar Todos os Dados)", type="secondary"):
            if resetar_banco_db():
                st.success("✅ Oficina resetada com sucesso!")
                st.rerun()
    
    st.markdown("---")
    
    # Cadastro de problemas
    st.subheader("➕ Cadastrar Novo Problema")
    nome = st.text_input("Nome do problema:")
    desc = st.text_area("Descrição (opcional):")
    
    if st.button("Adicionar Problema", type="primary"):
        if nome.strip(): 
            if adicionar_problema_db(nome.strip(), desc.strip()):
                st.success(f"✅ Problema '{nome}' cadastrado com sucesso!")
                st.rerun()
        else:
            st.error("❌ Digite o nome do problema")
    
    st.markdown("---")
    
    # Lista de problemas cadastrados
    st.subheader("📋 Problemas Cadastrados")
    problemas = listar_problemas_db()
    
    if not problemas:
        st.info("Nenhum problema cadastrado ainda.")
    else:
        for i, p in enumerate(problemas):
            # Contar votos para este problema
            stats = calcular_estatisticas_completas_db(p['id'])
            total_votos = stats['total'] if stats else 0
            
            with st.expander(f"📋 {p['nome']} ({total_votos} votos)"):
                if p['descricao']:
                    st.write(f"**Descrição:** {p['descricao']}")
                st.write(f"**Cadastrado em:** {p['timestamp']}")
                st.write(f"**ID:** {p['id']}")
                
                if st.button("🗑️ Remover", key=f"rm{i}", type="secondary"): 
                    if remover_problema_db(p['id']):
                        st.success(f"✅ Problema '{p['nome']}' removido!")
                        st.rerun()
    
    st.markdown("---")
    
    if st.button("🚪 Sair do Painel Admin"): 
        st.session_state.admin_logado = False
        st.session_state.modo = 'selecao'
        st.rerun()

# ========== LOGIN PARTICIPANTE ==========
elif st.session_state.modo == 'login_participante':
    st.markdown("""<div class="participant-header"><h2>👥 Login Participante</h2></div>""", unsafe_allow_html=True)
    
    nome = st.text_input("Seu nome ou matrícula:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Entrar na Votação", type="primary"):
            if nome.strip(): 
                st.session_state.participante_id = nome.strip()
                st.session_state.modo = 'participante'
                st.rerun()
            else: 
                st.error("❌ Digite seu nome")
    with col2:
        if st.button("🏠 Voltar ao Início"): 
            st.session_state.modo = 'selecao'
            st.rerun()

# ========== TELA PARTICIPANTE ==========
elif st.session_state.modo == 'participante' and st.session_state.participante_id:
    st.markdown(f"""<div class="participant-header"><h2>🗳️ Votação - {st.session_state.participante_id}</h2></div>""", unsafe_allow_html=True)
    
    # ========== EXPLICAÇÃO DA MATRIZ GUT ==========
    with st.expander("📚 **O que é a Matriz GUT? (Clique para ler)**", expanded=False):
        st.markdown("""
        ### 🎯 **Matriz GUT - Ferramenta de Priorização**
        
        A **Matriz GUT** é uma metodologia que nos ajuda a **priorizar problemas** de forma objetiva, 
        avaliando três critérios fundamentais:
        
        ---
        
        #### ⚠️ **GRAVIDADE** - *"Quão sério é este problema?"*
        - **1 = Pouco grave**: Problema simples, com impacto mínimo
        - **2 = Leve**: Causa pequenos transtornos ocasionais  
        - **3 = Moderado**: Impacto médio no trabalho/atendimento
        - **4 = Grave**: Prejudica significativamente as atividades
        - **5 = Muito grave**: Impacto severo, compromete resultados
        
        **💡 Exemplo**: *Sistema fora do ar por 1 hora = Gravidade 3 | Sistema fora do ar por 1 dia = Gravidade 5*
        
        ---
        
        #### ⏳ **URGÊNCIA** - *"Quão rápido precisa ser resolvido?"*
        - **1 = Pode esperar**: Sem pressa, pode ser resolvido em meses
        - **2 = Pouca urgência**: Algumas semanas para resolver
        - **3 = Urgência média**: Precisa ser resolvido em dias
        - **4 = Urgente**: Deve ser resolvido hoje/amanhã
        - **5 = Urgentíssimo**: Precisa ser resolvido AGORA
        
        **💡 Exemplo**: *Problema que afeta o atendimento ao público = Urgência 4 ou 5*
        
        ---
        
        #### 📈 **TENDÊNCIA** - *"Este problema vai piorar com o tempo?"*
        - **1 = Estável**: Problema não vai piorar, mantém-se igual
        - **2 = Piora lenta**: Pode piorar um pouco ao longo dos meses
        - **3 = Piora gradual**: Tende a se agravar progressivamente  
        - **4 = Piora rápida**: Vai piorar muito em pouco tempo
        - **5 = Piora crítica**: Se não resolver, vira uma catástrofe
        
        **💡 Exemplo**: *Equipamento antigo = Tendência 4 | Processo manual = Tendência 3*
        
        ---
        
        ### 🏆 **Como funciona a pontuação final?**
        
        **Pontuação GUT = Gravidade × Urgência × Tendência**
        
        - **🔴 PRIORIDADE ALTA** (64-125 pontos): Resolver PRIMEIRO
        - **🟡 PRIORIDADE MÉDIA** (27-63 pontos): Resolver em seguida  
        - **🟢 PRIORIDADE BAIXA** (1-26 pontos): Resolver quando possível
        
        ---
        
        ### ⚖️ **Dica para uma boa votação:**
        - **Seja realista**: Nem tudo é "muito grave" ou "urgentíssimo"
        - **Pense no impacto**: Como este problema afeta o trabalho/cidadão?
        - **Considere o futuro**: Este problema pode se tornar maior?
        - **Use toda a escala**: Varie entre 1, 2, 3, 4 e 5 conforme o caso
        
        **🎯 Lembre-se**: Sua avaliação será combinada com a de outros participantes para gerar o resultado final!
        """)
    
    # Carregar problemas do banco
    problemas = listar_problemas_db()
    
    if not problemas:
        st.warning("⚠️ Nenhum problema foi cadastrado ainda. Aguarde o administrador.")
    else:
        st.markdown("### 📋 Avalie cada problema nos critérios G-U-T:")
        st.markdown("*💡 Dica: Leia a explicação acima se tiver dúvidas sobre os critérios*")
        
        for i, prob in enumerate(problemas, 1):
            # Verificar se já votou neste problema
            voto_existente = obter_voto_participante_db(prob['id'], st.session_state.participante_id)
            
            # Card do problema
            st.markdown(f"""
            <div class="vote-card">
                <div class="problem-title">
                    📋 Problema {i}: {prob['nome']}
                </div>
                {f'<div class="problem-description">📝 {prob["descricao"]}</div>' if prob['descricao'] else ''}
            </div>
            """, unsafe_allow_html=True)
            
            with st.form(f"voto_{prob['id']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    g = st.slider(
                        "⚠️ **Gravidade**", 
                        1, 5, 
                        voto_existente['gravidade'] if voto_existente else 3,
                        key=f"g{prob['id']}",
                        help="Quão grave é este problema? (1=Pouco grave, 5=Muito grave)"
                    )
                
                with col2:
                    u = st.slider(
                        "⏳ **Urgência**", 
                        1, 5, 
                        voto_existente['urgencia'] if voto_existente else 3,
                        key=f"u{prob['id']}",
                        help="Quão urgente é resolver? (1=Pode esperar, 5=Urgentíssimo)"
                    )
                
                with col3:
                    t = st.slider(
                        "📈 **Tendência**", 
                        1, 5, 
                        voto_existente['tendencia'] if voto_existente else 3,
                        key=f"t{prob['id']}",
                        help="Tendência de piorar? (1=Estável, 5=Vai piorar muito)"
                    )
                
                # Preview da pontuação
                preview_pontuacao = g * u * t
                prioridade_preview, _ = classificar_prioridade(preview_pontuacao)
                
                st.info(f"**Sua pontuação**: {preview_pontuacao} | **Prioridade**: {prioridade_preview}")
                
                texto_botao = "🔄 Atualizar Voto" if voto_existente else "✅ Confirmar Voto"
                
                if st.form_submit_button(texto_botao, type="primary"):
                    if votar_problema_db(prob['id'], st.session_state.participante_id, g, u, t):
                        st.success(f"✅ Voto registrado para '{prob['nome']}'!")
                        st.rerun()
            
            st.markdown("---")  # Separador entre problemas
    
    # Botões de navegação
    colX, colY = st.columns(2)
    with colX:
        if st.button("🚪 Sair da Votação"): 
            st.session_state.participante_id = None
            st.session_state.modo = 'selecao'
            st.rerun()
    with colY:
        if st.button("🏠 Voltar ao Início"): 
            st.session_state.participante_id = None
            st.session_state.modo = 'selecao'
            st.rerun()

# ========== RESULTADOS COM DASHBOARD EXECUTIVO ==========
elif st.session_state.modo == 'resultados':
    st.markdown("""<div class="main-header"><h2>📊 Dashboard Executivo - Resultados</h2></div>""", unsafe_allow_html=True)
    
    colR1, colR2 = st.columns(2)
    with colR1:
        if st.button("🏠 Voltar ao Início"): 
            st.session_state.modo = 'selecao'
            st.rerun()
    with colR2:
        if st.button("🔃 Atualizar Resultados"): 
            st.rerun()
    
    # Carregar problemas e calcular resultados
    problemas = listar_problemas_db()
    
    if not problemas:
        st.info("📊 Nenhum problema cadastrado ainda.")
    else:
        # Calcular estatísticas completas
        resultados_completos = []
        dados_simples = []
        
        for p in problemas:
            stats = calcular_estatisticas_completas_db(p['id'])
            if stats:
                resultados_completos.append({
                    "🏷️ Problema": p['nome'],
                    "👥 Votos": stats['total'],
                    
                    # GRAVIDADE
                    "⚠️ G (Média)": f"{stats['mg']:.1f}",
                    "📊 G (Soma)": stats['sg'],
                    "🎯 G (Consenso)": stats['consenso_g'],
                    
                    # URGÊNCIA  
                    "⏳ U (Média)": f"{stats['mu']:.1f}",
                    "📊 U (Soma)": stats['su'],
                    "🎯 U (Consenso)": stats['consenso_u'],
                    
                    # TENDÊNCIA
                    "📈 T (Média)": f"{stats['mt']:.1f}",
                    "📊 T (Soma)": stats['st'],
                    "🎯 T (Consenso)": stats['consenso_t'],
                    
                    # RESULTADO FINAL
                    "🏆 Pontuação GUT": f"{stats['gut']:.1f}",
                    "🎖️ Prioridade": classificar_prioridade(stats['gut'])[0]
                })
                
                # Para gráficos
                dados_simples.append({
                    "Problema": p['nome'],
                    "Total Votos": stats['total'],
                    "Média Gravidade": stats['mg'], 
                    "Média Urgência": stats['mu'],
                    "Média Tendência": stats['mt'], 
                    "Pontuação GUT": stats['gut'],
                    "Desvio Gravidade": stats['std_g'],
                    "Desvio Urgência": stats['std_u'],
                    "Desvio Tendência": stats['std_t']
                })
        
        if not resultados_completos:
            st.info("📊 Nenhum voto registrado ainda. Aguarde os participantes votarem.")
        else:
            df_completo = pd.DataFrame(resultados_completos)
            df_simples = pd.DataFrame(dados_simples).sort_values("Pontuação GUT", ascending=False)
            df_simples["Prioridade"] = df_simples["Pontuação GUT"].apply(lambda x: classificar_prioridade(x)[0])
            
            # Estatísticas gerais
            stats = obter_estatisticas_db()
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📋 Problemas", stats["problemas"])
            with col2:
                st.metric("🗳️ Total de Votos", stats["votos"])
            with col3:
                st.metric("👥 Participantes", stats["participantes"])
            with col4:
                st.metric("🏆 Maior Pontuação", f"{df_simples['Pontuação GUT'].max():.1f}")
            
            st.markdown("---")
            
            # ========== TABELA EXECUTIVA ==========
            st.subheader("📊 Tabela Executiva Completa")
            
            # Função para colorir linhas baseada na prioridade
            def colorir_linha(row):
                if "🔴 ALTA" in str(row["🎖️ Prioridade"]):
                    return ['background-color: #fee2e2; color: #7f1d1d'] * len(row)
                elif "🟡 MÉDIA" in str(row["🎖️ Prioridade"]):
                    return ['background-color: #fef3c7; color: #78350f'] * len(row)
                else:
                    return ['background-color: #dcfce7; color: #14532d'] * len(row)
            
            # Ordenar por pontuação GUT
            df_ordenado = df_completo.sort_values("🏆 Pontuação GUT", ascending=False, key=lambda x: pd.to_numeric(x, errors='coerce'))
            
            # Mostrar tabela estilizada
            st.dataframe(
                df_ordenado.style.apply(colorir_linha, axis=1),
                use_container_width=True,
                height=400
            )
            
            # Botão de exportação
            csv = df_simples.to_csv(index=False)
            st.download_button(
                label="📥 Baixar Resultados Completos (CSV)",
                data=csv,
                file_name=f"matriz_gut_dashboard_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
            
            st.markdown("---")
            
            # ========== CARDS RESUMO POR PROBLEMA ==========
            st.subheader("🎯 Análise Detalhada por Problema")
            
            for p in problemas:
                stats = calcular_estatisticas_completas_db(p['id'])
                if stats:
                    prioridade, classe_css = classificar_prioridade(stats['gut'])
                    
                    with st.expander(f"📋 {p['nome']} - {prioridade} ({stats['gut']:.1f} pontos)"):
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric(
                                "👥 Total de Votos", 
                                stats['total'],
                                help="Número de pessoas que avaliaram este problema"
                            )
                        
                        with col2:
                            st.metric(
                                "⚠️ Gravidade", 
                                f"{stats['mg']:.1f}",
                                delta=f"Soma: {stats['sg']}",
                                help="Média das avaliações de gravidade"
                            )
                        
                        with col3:
                            st.metric(
                                "⏳ Urgência", 
                                f"{stats['mu']:.1f}",
                                delta=f"Soma: {stats['su']}",
                                help="Média das avaliações de urgência"
                            )
                        
                        with col4:
                            st.metric(
                                "📈 Tendência", 
                                f"{stats['mt']:.1f}",
                                delta=f"Soma: {stats['st']}",
                                help="Média das avaliações de tendência"
                            )
                        
                        # Consenso
                        col_cons1, col_cons2, col_cons3 = st.columns(3)
                        with col_cons1:
                            st.markdown(f"**Consenso G:** {formatar_consenso(stats['consenso_g'])}", unsafe_allow_html=True)
                        with col_cons2:
                            st.markdown(f"**Consenso U:** {formatar_consenso(stats['consenso_u'])}", unsafe_allow_html=True)
                        with col_cons3:
                            st.markdown(f"**Consenso T:** {formatar_consenso(stats['consenso_t'])}", unsafe_allow_html=True)
                        
                        # Barras de progresso visuais
                        st.markdown("**📊 Intensidade dos Critérios:**")
                        
                        col_g, col_u, col_t = st.columns(3)
                        
                        with col_g:
                            st.progress(stats['mg']/5, text=f"Gravidade: {stats['mg']:.1f}/5")
                        with col_u:
                            st.progress(stats['mu']/5, text=f"Urgência: {stats['mu']:.1f}/5")
                        with col_t:
                            st.progress(stats['mt']/5, text=f"Tendência: {stats['mt']:.1f}/5")
                        
                        # Interpretação automática
                        st.markdown("**🤖 Interpretação Automática:**")
                        
                        interpretacao = []
                        if stats['mg'] >= 4: interpretacao.append("⚠️ **Problema muito grave**")
                        if stats['mu'] >= 4: interpretacao.append("⏰ **Requer ação imediata**") 
                        if stats['mt'] >= 4: interpretacao.append("📈 **Vai piorar rapidamente**")
                        if stats['consenso_g'] == "Baixo": interpretacao.append("🤔 **Divergência sobre gravidade - discutir mais**")
                        if stats['consenso_u'] == "Baixo": interpretacao.append("🤔 **Divergência sobre urgência - discutir mais**")
                        if stats['consenso_t'] == "Baixo": interpretacao.append("🤔 **Divergência sobre tendência - discutir mais**")
                        
                        if interpretacao:
                            for item in interpretacao:
                                st.markdown(f"- {item}")
                        else:
                            st.markdown("- ✅ **Problema bem avaliado e consensual**")
            
            st.markdown("---")

            # -------- VISUALIZAÇÕES AVANÇADAS --------
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏆 Ranking", "📊 Médias G-U-T", "🎯 Distribuição", "👥 Participação", "🎯 Análise de Consenso"])

            with tab1:
                st.subheader("🏆 Ranking por Pontuação GUT")
                fig = px.bar(
                    df_simples, 
                    x="Pontuação GUT", 
                    y="Problema", 
                    orientation="h",
                    text="Pontuação GUT",
                    color="Pontuação GUT",
                    color_continuous_scale=px.colors.sequential.Blues,
                    title="Problemas ordenados por prioridade (maior pontuação = maior prioridade)"
                )
                fig.update_traces(texttemplate='%{text:.1f}', textposition="outside")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                st.subheader("📊 Comparação dos Critérios G-U-T")
                dfm = df_simples.melt(
                    id_vars="Problema",
                    value_vars=["Média Gravidade", "Média Urgência", "Média Tendência"],
                    var_name="Critério",
                    value_name="Média"
                )
                dfm['Critério'] = dfm['Critério'].str.replace("Média ", "")
                
                figm = px.bar(
                    dfm, 
                    x="Problema", 
                    y="Média", 
                    color="Critério", 
                    barmode="group",
                    text="Média",
                    color_discrete_map={
                        "Gravidade": "#1f77b4",
                        "Urgência": "#2ca02c", 
                        "Tendência": "#ff7f0e"
                    },
                    title="Médias por critério para cada problema"
                )
                figm.update_traces(texttemplate='%{text:.2f}', textposition="outside")
                figm.update_layout(height=400)
                st.plotly_chart(figm, use_container_width=True)

            with tab3:
                st.subheader("🎯 Distribuição das Pontuações")
                figh = px.histogram(
                    df_simples, 
                    x="Pontuação GUT", 
                    nbins=10, 
                    text_auto=True,
                    color_discrete_sequence=["#1f77b4"],
                    title="Distribuição das pontuações GUT"
                )
                figh.update_layout(height=400)
                st.plotly_chart(figh, use_container_width=True)

            with tab4:
                st.subheader("👥 Participação por Problema")
                figp = px.bar(
                    df_simples, 
                    x="Problema", 
                    y="Total Votos", 
                    text="Total Votos",
                    color_discrete_sequence=["#2ca02c"],
                    title="Número de votos recebidos por cada problema"
                )
                figp.update_traces(texttemplate='%{text}', textposition="outside")
                figp.update_layout(height=400)
                st.plotly_chart(figp, use_container_width=True)

            with tab5:
                st.subheader("🎯 Análise de Consenso")
                
                # Gráfico de dispersão dos desvios
                dados_consenso = []
                for p in problemas:
                    stats = calcular_estatisticas_completas_db(p['id'])
                    if stats:
                        nome_curto = p['nome'][:20] + "..." if len(p['nome']) > 20 else p['nome']
                        dados_consenso.append({
                            "Problema": nome_curto,
                            "Desvio Gravidade": stats['std_g'],
                            "Desvio Urgência": stats['std_u'], 
                            "Desvio Tendência": stats['std_t'],
                            "Pontuação GUT": stats['gut']
                        })
                
                if dados_consenso:
                    df_consenso = pd.DataFrame(dados_consenso)
                    
                    fig_consenso = px.scatter(
                        df_consenso,
                        x="Desvio Gravidade",
                        y="Desvio Urgência", 
                        size="Pontuação GUT",
                        color="Desvio Tendência",
                        hover_name="Problema",
                        title="Consenso vs Divergência (menor desvio = maior consenso)",
                        labels={
                            "Desvio Gravidade": "Divergência na Gravidade",
                            "Desvio Urgência": "Divergência na Urgência"
                        }
                    )
                    
                    fig_consenso.add_hline(y=0.8, line_dash="dash", line_color="green", 
                                          annotation_text="Limite consenso alto")
                    fig_consenso.add_vline(x=0.8, line_dash="dash", line_color="green")
                    fig_consenso.add_hline(y=1.5, line_dash="dash", line_color="orange", 
                                          annotation_text="Limite consenso médio")
                    fig_consenso.add_vline(x=1.5, line_dash="dash", line_color="orange")
                    
                    st.plotly_chart(fig_consenso, use_container_width=True)
                    
                    st.markdown("""
                    **💡 Como interpretar o gráfico de consenso:**
                    - **🟢 Área verde (canto inferior esquerdo)**: Alto consenso - todos concordam
                    - **🟡 Área amarela**: Consenso médio - algumas divergências
                    - **🔴 Área vermelha**: Baixo consenso - muitas divergências (discutir mais)
                    - **Tamanho das bolhas**: Pontuação GUT (maior = mais prioritário)
                    - **Cor das bolhas**: Divergência na Tendência
                    """)
                    
                    # Tabela de consenso
                    st.subheader("📋 Resumo de Consenso")
                    df_consenso_resumo = df_consenso.copy()
                    df_consenso_resumo['Status Consenso'] = df_consenso_resumo.apply(
                        lambda row: "🟢 Alto" if row['Desvio Gravidade'] <= 0.8 and row['Desvio Urgência'] <= 0.8 
                        else "🟡 Médio" if row['Desvio Gravidade'] <= 1.5 and row['Desvio Urgência'] <= 1.5 
                        else "🔴 Baixo", axis=1
                    )
                    
                    st.dataframe(
                        df_consenso_resumo[['Problema', 'Pontuação GUT', 'Status Consenso', 'Desvio Gravidade', 'Desvio Urgência', 'Desvio Tendência']],
                        use_container_width=True
                    )

# ========== FALLBACK ==========
else:
    st.error("❌ Estado inválido. Retornando ao início...")
    st.session_state.modo = 'selecao'
    st.rerun()