import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

st.set_page_config(
    page_title="Matriz GUT - Oficina Tribunal de Justiça",
    page_icon="⚖️",
    layout="wide"
)

# CSS customizado para deixar mais profissional
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .priority-high {
        background-color: #fee2e2;
        border-left: 5px solid #dc2626;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .priority-medium {
        background-color: #fef3c7;
        border-left: 5px solid #f59e0b;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .priority-low {
        background-color: #dcfce7;
        border-left: 5px solid #16a34a;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>⚖️ Matriz GUT - Oficina de Priorização</h1>
    <h3>Tribunal de Justiça - Ferramenta de Gestão Estratégica</h3>
</div>
""", unsafe_allow_html=True)

st.markdown("""
**Bem-vindos à Oficina de Priorização com a Matriz GUT**  
Aplicaremos esta ferramenta para organizar e priorizar problemas de forma **técnica e objetiva**, 
auxiliando a tomada de decisão estratégica no contexto do **Poder Judiciário**.
""")

# Dicionários para mapear pontuações para descrições
gravidade_map = {
    1: "1 - Nenhuma gravidade",
    2: "2 - Pouco grave", 
    3: "3 - Grave",
    4: "4 - Muito grave",
    5: "5 - Extremamente grave"
}

urgencia_map = {
    1: "1 - Pode esperar",
    2: "2 - Pouco urgente",
    3: "3 - Urgente", 
    4: "4 - Muito urgente",
    5: "5 - Com prazo imediato"
}

tendencia_map = {
    1: "1 - Não vai piorar",
    2: "2 - Vai piorar a longo prazo",
    3: "3 - Vai piorar a médio prazo",
    4: "4 - Vai piorar a curto prazo", 
    5: "5 - Vai piorar drasticamente"
}

# Estado inicial
if 'problemas' not in st.session_state:
    st.session_state.problemas = []

def adicionar_problema(nome, gravidade, urgencia, tendencia):
    pontuacao_gut = gravidade * urgencia * tendencia
    st.session_state.problemas.append({
        "Problema": nome,
        "Gravidade": gravidade,
        "Urgência": urgencia, 
        "Tendência": tendencia,
        "Pontuação GUT": pontuacao_gut
    })

def remover_problema(indice):
    if 0 <= indice < len(st.session_state.problemas):
        st.session_state.problemas.pop(indice)

def classificar_prioridade(pontuacao):
    if pontuacao >= 64:  # 4*4*4 ou superior
        return "🔴 ALTA", "priority-high"
    elif pontuacao >= 27:  # 3*3*3 ou superior  
        return "🟡 MÉDIA", "priority-medium"
    else:
        return "🟢 BAIXA", "priority-low"

# Botão para carregar exemplos do judiciário
if st.button("📋 Carregar Exemplos do Judiciário"):
    exemplos = [
        {"nome": "Atraso na análise de processos urgentes", "g": 4, "u": 5, "t": 4},
        {"nome": "Sistema de peticionamento eletrônico instável", "g": 5, "u": 4, "t": 5},
        {"nome": "Falta de capacitação em nova legislação", "g": 3, "u": 2, "t": 3},
        {"nome": "Acúmulo de processos em cartório", "g": 4, "u": 3, "t": 4},
        {"nome": "Equipamentos de TI desatualizados", "g": 3, "u": 2, "t": 4}
    ]
    
    st.session_state.problemas = []
    for ex in exemplos:
        adicionar_problema(ex["nome"], ex["g"], ex["u"], ex["t"])
    st.success("✅ Exemplos carregados com sucesso!")
    st.rerun()

# Layout dividido: formulário ao lado dos problemas
col1, col2 = st.columns([1, 2])

with col1:
    with st.form("novo_problema_form"):
        st.subheader("➕ Adicionar Novo Problema")
        nome_problema = st.text_input("📝 Nome do Problema")
        
        col_g, col_u, col_t = st.columns(3)
        with col_g:
            gravidade = st.slider("⚠️ Gravidade", 1, 5, 3)
        with col_u:
            urgencia = st.slider("⏳ Urgência", 1, 5, 3)
        with col_t:
            tendencia = st.slider("📈 Tendência", 1, 5, 3)

        # Preview da pontuação
        preview_pontuacao = gravidade * urgencia * tendencia
        prioridade_preview, _ = classificar_prioridade(preview_pontuacao)
        
        st.info(f"**Pontuação GUT**: {preview_pontuacao} | **Prioridade**: {prioridade_preview}")
        
        with st.expander("ℹ️ Ver descrições dos critérios"):
            st.write(f"**Gravidade**: {gravidade_map[gravidade]}")
            st.write(f"**Urgência**: {urgencia_map[urgencia]}")
            st.write(f"**Tendência**: {tendencia_map[tendencia]}")

        submitted = st.form_submit_button("Adicionar Problema", type="primary")
        if submitted and nome_problema.strip():
            adicionar_problema(nome_problema.strip(), gravidade, urgencia, tendencia)
            st.success(f"✅ Problema **{nome_problema}** adicionado!")
            st.rerun()
        elif submitted:
            st.error("❌ Insira um nome válido para o problema.")

    # Botão para limpar todos os problemas
    if st.session_state.problemas:
        if st.button("🗑️ Limpar Todos os Problemas", type="secondary"):
            st.session_state.problemas = []
            st.success("✅ Todos os problemas foram removidos!")
            st.rerun()

with col2:
    if st.session_state.problemas:
        st.subheader("📋 Problemas Priorizados")
        df = pd.DataFrame(st.session_state.problemas)
        df_sorted = df.sort_values(by="Pontuação GUT", ascending=False).reset_index(drop=True)
        
        # Adicionar classificação de prioridade
        df_sorted["Prioridade"] = df_sorted["Pontuação GUT"].apply(lambda x: classificar_prioridade(x)[0])
        
        # Exibir tabela com formatação
        st.dataframe(
            df_sorted[["Problema", "Gravidade", "Urgência", "Tendência", "Pontuação GUT", "Prioridade"]], 
            use_container_width=True,
            hide_index=True
        )

        # Seção de remoção de problemas
        with st.expander("🗑️ Remover Problemas"):
            for i, row in df_sorted.iterrows():
                col_info, col_btn = st.columns([3, 1])
                with col_info:
                    st.write(f"**{row['Problema']}** - GUT: {row['Pontuação GUT']}")
                with col_btn:
                    if st.button("❌", key=f"del_{i}", help=f"Remover: {row['Problema']}"):
                        # Encontrar o índice original no array não ordenado
                        original_index = next(
                            idx for idx, prob in enumerate(st.session_state.problemas) 
                            if prob["Problema"] == row["Problema"]
                        )
                        remover_problema(original_index)
                        st.rerun()

        # Análise de prioridades
        st.subheader("🎯 Análise de Prioridades")
        
        alta_prioridade = df_sorted[df_sorted["Pontuação GUT"] >= 64]
        media_prioridade = df_sorted[(df_sorted["Pontuação GUT"] >= 27) & (df_sorted["Pontuação GUT"] < 64)]
        baixa_prioridade = df_sorted[df_sorted["Pontuação GUT"] < 27]
        
        col_alta, col_media, col_baixa = st.columns(3)
        
        with col_alta:
            st.metric("🔴 Alta Prioridade", len(alta_prioridade))
        with col_media:
            st.metric("🟡 Média Prioridade", len(media_prioridade))
        with col_baixa:
            st.metric("🟢 Baixa Prioridade", len(baixa_prioridade))

        # Gráficos interativos
        st.subheader("📊 Visualizações")
        
        tab1, tab2, tab3 = st.tabs(["📊 Ranking", "🎯 Radar", "📈 Distribuição"])
        
        with tab1:
            fig_bar = px.bar(
                df_sorted,
                x="Pontuação GUT",
                y="Problema",
                orientation="h",
                color="Pontuação GUT",
                color_continuous_scale="RdYlGn_r",
                title="Ranking de Problemas por Pontuação GUT"
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with tab2:
            if len(df_sorted) <= 5:  # Limitar radar para não ficar confuso
                fig_radar = go.Figure()
                
                for _, row in df_sorted.iterrows():
                    fig_radar.add_trace(go.Scatterpolar(
                        r=[row["Gravidade"], row["Urgência"], row["Tendência"]],
                        theta=["Gravidade", "Urgência", "Tendência"],
                        fill='toself',
                        name=row["Problema"][:20] + "..." if len(row["Problema"]) > 20 else row["Problema"]
                    ))
                
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                    title="Comparação G-U-T por Problema"
                )
                st.plotly_chart(fig_radar, use_container_width=True)
            else:
                st.info("📝 Gráfico radar disponível para até 5 problemas. Remova alguns para visualizar.")
        
        with tab3:
            fig_hist = px.histogram(
                df_sorted,
                x="Pontuação GUT",
                nbins=10,
                title="Distribuição das Pontuações GUT"
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        # Exportação melhorada
        st.subheader("📥 Exportar Resultados")
        
        col_csv, col_excel = st.columns(2)
        
        with col_csv:
            csv = df_sorted.to_csv(index=False).encode('utf-8')
            st.download_button(
                "⬇️ Baixar CSV",
                data=csv,
                file_name=f"matriz_gut_tribunal_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        
        with col_excel:
            # Criar Excel em memória
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_sorted.to_excel(writer, sheet_name='Matriz GUT', index=False)
            
            st.download_button(
                "⬇️ Baixar Excel",
                data=output.getvalue(),
                file_name=f"matriz_gut_tribunal_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # Conclusão destacada
        st.markdown("---")
        st.subheader("🔍 Conclusões da Análise")
        
        if not df_sorted.empty:
            top_problema = df_sorted.iloc[0]
            prioridade_top, classe_css = classificar_prioridade(top_problema["Pontuação GUT"])
            
            st.markdown(f"""
            <div class="{classe_css}">
                <h4>🎯 Problema Prioritário</h4>
                <p><strong>{top_problema['Problema']}</strong></p>
                <p>Pontuação GUT: <strong>{top_problema['Pontuação GUT']}</strong> | Prioridade: <strong>{prioridade_top}</strong></p>
                <p>G: {top_problema['Gravidade']} | U: {top_problema['Urgência']} | T: {top_problema['Tendência']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if len(alta_prioridade) > 0:
                st.warning(f"⚠️ **{len(alta_prioridade)} problema(s)** requer(em) atenção imediata (Alta Prioridade)")
            
            if len(media_prioridade) > 0:
                st.info(f"📋 **{len(media_prioridade)} problema(s)** deve(m) ser planejado(s) (Média Prioridade)")

    else:
        st.info("📝 Nenhum problema cadastrado ainda. Adicione problemas no painel ao lado ou carregue os exemplos do judiciário.")
        
        # Explicação da metodologia quando não há dados
        with st.expander("📚 Como funciona a Matriz GUT?"):
            st.markdown("""
            ### Critérios de Avaliação:
            
            **⚠️ Gravidade (G)**: Impacto do problema se não for resolvido
            - 1: Nenhuma gravidade
            - 2: Pouco grave  
            - 3: Grave
            - 4: Muito grave
            - 5: Extremamente grave
            
            **⏳ Urgência (U)**: Tempo disponível para resolver
            - 1: Pode esperar
            - 2: Pouco urgente
            - 3: Urgente
            - 4: Muito urgente  
            - 5: Com prazo imediato
            
            **📈 Tendência (T)**: Probabilidade de piorar
            - 1: Não vai piorar
            - 2: Vai piorar a longo prazo
            - 3: Vai piorar a médio prazo
            - 4: Vai piorar a curto prazo
            - 5: Vai piorar drasticamente
            
            ### Cálculo:
            **Pontuação GUT = G × U × T**
            
            ### Classificação de Prioridades:
            - 🔴 **Alta**: ≥ 64 pontos
            - 🟡 **Média**: 27-63 pontos  
            - 🟢 **Baixa**: < 27 pontos
            """)