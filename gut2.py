import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime

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
</style>
""", unsafe_allow_html=True)

# ===================== ESTADOS =====================
if 'modo' not in st.session_state: st.session_state.modo = 'selecao'
if 'problemas_cadastrados' not in st.session_state: st.session_state.problemas_cadastrados = []
if 'votos' not in st.session_state: st.session_state.votos = {}
if 'participante_id' not in st.session_state: st.session_state.participante_id = None
if 'admin_logado' not in st.session_state: st.session_state.admin_logado = False

# ===================== FUNÇÕES =====================
def gerar_id_problema(nome): 
    return nome.lower().replace(' ', '_')[:20]

def adicionar_problema_admin(nome, descricao=""):
    pid = gerar_id_problema(nome)
    st.session_state.problemas_cadastrados.append({
        "id": pid, 
        "nome": nome, 
        "descricao": descricao, 
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    if pid not in st.session_state.votos: 
        st.session_state.votos[pid] = []

def votar_problema(pid, participante, g, u, t):
    voto = {
        "participante": participante, 
        "gravidade": g, 
        "urgencia": u, 
        "tendencia": t, 
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    if pid not in st.session_state.votos: 
        st.session_state.votos[pid] = []
    
    # Atualizar voto existente ou adicionar novo
    for i, v in enumerate(st.session_state.votos[pid]):
        if v['participante'] == participante:
            st.session_state.votos[pid][i] = voto
            return
    st.session_state.votos[pid].append(voto)

def calcular_medias(pid):
    votos = st.session_state.votos.get(pid, [])
    if not votos: return None
    n = len(votos)
    g = sum(v['gravidade'] for v in votos) / n
    u = sum(v['urgencia'] for v in votos) / n
    t = sum(v['tendencia'] for v in votos) / n
    return {
        "total": n, 
        "mg": round(g,2), 
        "mu": round(u,2), 
        "mt": round(t,2), 
        "gut": round(g*u*t,2)
    }

def classificar_prioridade(p): 
    return ("🔴 ALTA","priority-high") if p>=64 else ("🟡 MÉDIA","priority-medium") if p>=27 else ("🟢 BAIXA","priority-low")

# ===================== TELAS =====================

# ========== TELA SELEÇÃO ==========
if st.session_state.modo == 'selecao':
    st.markdown("""<div class="main-header"><h1>⚖️ Matriz GUT 2.0</h1><h3>Tribunal de Justiça de Rondônia</h3></div>""", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔐 Administrador", use_container_width=True): 
            st.session_state.modo='login_admin'
            st.rerun()
    with col2:
        if st.button("👥 Participante", use_container_width=True): 
            st.session_state.modo='login_participante'
            st.rerun()
    with col3:
        if st.button("📊 Resultados", use_container_width=True): 
            st.session_state.modo='resultados'
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
        if st.button("🗑️ Reiniciar Oficina (Apagar Todos os Dados)", type="secondary"):
            st.session_state.problemas_cadastrados = []
            st.session_state.votos = {}
            st.success("✅ Oficina reiniciada com sucesso!")
            st.rerun()
    
    st.markdown("---")
    
    # Cadastro de problemas
    st.subheader("➕ Cadastrar Novo Problema")
    nome = st.text_input("Nome do problema:")
    desc = st.text_area("Descrição (opcional):")
    
    if st.button("Adicionar Problema", type="primary"):
        if nome.strip(): 
            adicionar_problema_admin(nome.strip(), desc.strip())
            st.success(f"✅ Problema '{nome}' cadastrado com sucesso!")
            st.rerun()
        else:
            st.error("❌ Digite o nome do problema")
    
    st.markdown("---")
    
    # Lista de problemas cadastrados
    st.subheader("📋 Problemas Cadastrados")
    
    if not st.session_state.problemas_cadastrados:
        st.info("Nenhum problema cadastrado ainda.")
    else:
        for i, p in enumerate(st.session_state.problemas_cadastrados):
            with st.expander(f"📋 {p['nome']} ({len(st.session_state.votos.get(p['id'], []))} votos)"):
                if p['descricao']:
                    st.write(f"**Descrição:** {p['descricao']}")
                st.write(f"**Cadastrado em:** {p['timestamp']}")
                
                if st.button("🗑️ Remover", key=f"rm{i}", type="secondary"): 
                    st.session_state.problemas_cadastrados.pop(i)
                    if p['id'] in st.session_state.votos:
                        del st.session_state.votos[p['id']]
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

# ========== TELA PARTICIPANTE (COM EXPLICAÇÃO GUT) ==========
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
    
    if not st.session_state.problemas_cadastrados:
        st.warning("⚠️ Nenhum problema foi cadastrado ainda. Aguarde o administrador.")
    else:
        st.markdown("### 📋 Avalie cada problema nos critérios G-U-T:")
        st.markdown("*💡 Dica: Leia a explicação acima se tiver dúvidas sobre os critérios*")
        
        for i, prob in enumerate(st.session_state.problemas_cadastrados, 1):
            # Verificar se já votou neste problema
            votos_problema = st.session_state.votos.get(prob['id'], [])
            voto_existente = next((v for v in votos_problema if v['participante'] == st.session_state.participante_id), None)
            
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
                    votar_problema(prob['id'], st.session_state.participante_id, g, u, t)
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

# ========== RESULTADOS ==========
elif st.session_state.modo == 'resultados':
    st.markdown("""<div class="main-header"><h2>📊 Resultados Consolidados</h2></div>""", unsafe_allow_html=True)
    
    colR1, colR2 = st.columns(2)
    with colR1:
        if st.button("🏠 Voltar ao Início"): 
            st.session_state.modo = 'selecao'
            st.rerun()
    with colR2:
        if st.button("🔃 Atualizar Resultados"): 
            st.rerun()
    
    # Calcular resultados
    resultados = []
    for p in st.session_state.problemas_cadastrados:
        medias = calcular_medias(p['id'])
        if medias: 
            resultados.append({
                "Problema": p['nome'],
                "Total Votos": medias['total'],
                "Média Gravidade": medias['mg'], 
                "Média Urgência": medias['mu'],
                "Média Tendência": medias['mt'], 
                "Pontuação GUT": medias['gut']
            })
    
    if not resultados: 
        st.info("📊 Nenhum voto registrado ainda. Aguarde os participantes votarem.")
    else:
        df_resultados = pd.DataFrame(resultados).sort_values("Pontuação GUT", ascending=False)
        df_resultados["Prioridade"] = df_resultados["Pontuação GUT"].apply(lambda x: classificar_prioridade(x)[0])
        
        # Estatísticas gerais
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📋 Problemas", len(df_resultados))
        with col2:
            st.metric("🗳️ Total de Votos", df_resultados["Total Votos"].sum())
        with col3:
            participantes_unicos = set()
            for votos_problema in st.session_state.votos.values():
                for voto in votos_problema:
                    participantes_unicos.add(voto['participante'])
            st.metric("👥 Participantes", len(participantes_unicos))
        with col4:
            st.metric("🏆 Maior Pontuação", f"{df_resultados['Pontuação GUT'].max():.1f}")
        
        st.markdown("---")
        
        # Tabela de resultados
        st.subheader("📊 Ranking Final")
        st.dataframe(df_resultados, use_container_width=True)
        
        # Botão de exportação
        csv = df_resultados.to_csv(index=False)
        st.download_button(
            label="📥 Baixar Resultados (CSV)",
            data=csv,
            file_name=f"matriz_gut_resultados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )

        # -------- VISUALIZAÇÕES --------
        tab1, tab2, tab3, tab4 = st.tabs(["🏆 Ranking", "📊 Médias G-U-T", "🎯 Distribuição", "👥 Participação"])

        with tab1:
            st.subheader("🏆 Ranking por Pontuação GUT")
            fig = px.bar(
                df_resultados, 
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
            dfm = df_resultados.melt(
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
                df_resultados, 
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
                df_resultados, 
                x="Problema", 
                y="Total Votos", 
                text="Total Votos",
                color_discrete_sequence=["#2ca02c"],
                title="Número de votos recebidos por cada problema"
            )
            figp.update_traces(texttemplate='%{text}', textposition="outside")
            figp.update_layout(height=400)
            st.plotly_chart(figp, use_container_width=True)

# ========== FALLBACK ==========
else:
    st.error("❌ Estado inválido. Retornando ao início...")
    st.session_state.modo = 'selecao'
    st.rerun()