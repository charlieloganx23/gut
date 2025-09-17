import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Matriz GUT - Oficina Tribunal de Justiça",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Matriz GUT - Oficina de Priorização de Problemas")
st.markdown("""
Bem-vindos à **Oficina de Priorização com a Matriz GUT**.  
Aqui aplicaremos a ferramenta para organizar e priorizar problemas de forma **técnica e objetiva**, 
auxiliando a tomada de decisão no contexto do **Poder Judiciário**.  
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
    st.session_state.problemas.pop(indice)

# Layout dividido: formulário ao lado dos problemas
col1, col2 = st.columns([1, 2])

with col1:
    with st.form("novo_problema_form"):
        st.subheader("➕ Adicionar Novo Problema")
        nome_problema = st.text_input("📝 Nome do Problema")
        gravidade = st.slider("⚠️ Gravidade", 1, 5, 3)
        urgencia = st.slider("⏳ Urgência", 1, 5, 3)
        tendencia = st.slider("📈 Tendência", 1, 5, 3)

        st.write(f"**Gravidade**: {gravidade_map[gravidade]}")
        st.write(f"**Urgência**: {urgencia_map[urgencia]}")
        st.write(f"**Tendência**: {tendencia_map[tendencia]}")

        submitted = st.form_submit_button("Adicionar Problema")
        if submitted and nome_problema.strip():
            adicionar_problema(nome_problema.strip(), gravidade, urgencia, tendencia)
            st.success(f"Problema **{nome_problema}** adicionado!")
        elif submitted:
            st.error("Insira um nome válido para o problema.")

with col2:
    if st.session_state.problemas:
        st.subheader("📋 Lista de Problemas")
        df = pd.DataFrame(st.session_state.problemas)
        df_sorted = df.sort_values(by="Pontuação GUT", ascending=False).reset_index(drop=True)

        st.dataframe(df_sorted, use_container_width=True)

        # Botões para remover problemas
        for i, problema in enumerate(df_sorted["Problema"]):
            if st.button(f"❌ Remover: {problema}", key=f"del_{i}"):
                remover_problema(i)
                st.experimental_rerun()

        # Gráficos interativos
        st.subheader("📊 Visualização das Prioridades")
        fig = px.bar(
            df_sorted,
            x="Problema",
            y="Pontuação GUT",
            color="Pontuação GUT",
            color_continuous_scale="Reds",
            title="Ranking de Problemas por Pontuação GUT"
        )
        st.plotly_chart(fig, use_container_width=True)

        radar_fig = px.line_polar(
            df_sorted.melt(id_vars="Problema", value_vars=["Gravidade", "Urgência", "Tendência"]),
            r="value",
            theta="variable",
            color="Problema",
            line_close=True,
            title="Visão Radar - Comparação G, U, T"
        )
        st.plotly_chart(radar_fig, use_container_width=True)

        # Exportação
        st.subheader("📥 Exportar Resultados")
        csv = df_sorted.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Baixar CSV", data=csv, file_name="matriz_gut.csv", mime="text/csv")

        excel = df_sorted.to_excel("matriz_gut.xlsx", index=False)
        with open("matriz_gut.xlsx", "rb") as f:
            st.download_button("⬇️ Baixar Excel", data=f, file_name="matriz_gut.xlsx", mime="application/vnd.ms-excel")

        # Destaque da conclusão
        st.markdown("### 🔎 Conclusão")
        top_problema = df_sorted.loc[0, "Problema"]
        st.success(f"O problema prioritário identificado é: **{top_problema}** 🎯")

    else:
        st.info("Nenhum problema cadastrado ainda. Adicione um no painel ao lado.")