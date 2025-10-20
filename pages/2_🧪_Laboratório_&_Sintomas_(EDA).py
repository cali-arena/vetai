"""
Página: Laboratório & Sintomas (EDA)
Análise exploratória interativa de exames e sintomas
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# Adicionar path da biblioteca
sys.path.insert(0, str(Path(__file__).parent.parent))

from vetlib.preprocessing import (
    FAIXAS_REFERENCIA, verificar_valores_referencia,
    identificar_outliers, obter_estatisticas_exame
)
from vetlib.data_io import SCHEMA_COLUNAS

st.set_page_config(page_title="Laboratório & Sintomas (EDA)", page_icon="🧪", layout="wide")

# Título
st.title("🧪 Laboratório & Sintomas (EDA)")
st.markdown("Análise exploratória interativa de exames laboratoriais e sintomas clínicos")

# Verificar dados
if st.session_state.get('df_main') is None:
    st.warning("⚠️ Nenhum dataset carregado. Vá para **📥 Upload de Dados** primeiro.")
    st.stop()

df = st.session_state.df_main.copy()

# ============================================================================
# SIDEBAR: FILTROS
# ============================================================================

st.sidebar.markdown("## 🔍 Filtros")

# Filtro de Espécie
if 'especie' in df.columns:
    especies_disponiveis = ['Todas'] + sorted(df['especie'].unique().tolist())
    filtro_especie = st.sidebar.selectbox("Espécie", especies_disponiveis)
    
    if filtro_especie != 'Todas':
        df = df[df['especie'] == filtro_especie]

# Filtro de Raça
if 'raca' in df.columns and len(df) > 0:
    racas_disponiveis = ['Todas'] + sorted(df['raca'].unique().tolist())
    filtro_raca = st.sidebar.selectbox("Raça", racas_disponiveis)
    
    if filtro_raca != 'Todas':
        df = df[df['raca'] == filtro_raca]

# Filtro de Sexo
if 'sexo' in df.columns and len(df) > 0:
    sexos_disponiveis = ['Todos'] + sorted(df['sexo'].unique().tolist())
    filtro_sexo = st.sidebar.selectbox("Sexo", sexos_disponiveis)
    
    if filtro_sexo != 'Todos':
        df = df[df['sexo'] == filtro_sexo]

# Filtro de Faixa Etária
if 'idade_anos' in df.columns and len(df) > 0:
    idade_min, idade_max = float(df['idade_anos'].min()), float(df['idade_anos'].max())
    filtro_idade = st.sidebar.slider(
        "Faixa Etária (anos)",
        idade_min, idade_max, (idade_min, idade_max)
    )
    df = df[(df['idade_anos'] >= filtro_idade[0]) & (df['idade_anos'] <= filtro_idade[1])]

# Filtro de Diagnóstico
if 'diagnostico' in df.columns and len(df) > 0:
    diagnosticos_disponiveis = ['Todos'] + sorted(df['diagnostico'].unique().tolist())
    filtro_diagnostico = st.sidebar.selectbox("Diagnóstico", diagnosticos_disponiveis)
    
    if filtro_diagnostico != 'Todos':
        df = df[df['diagnostico'] == filtro_diagnostico]

# Mostrar quantidade filtrada
st.sidebar.markdown("---")
st.sidebar.metric("Registros Filtrados", len(df))

if len(df) == 0:
    st.error("❌ Nenhum registro corresponde aos filtros selecionados.")
    st.stop()

# ============================================================================
# SEÇÃO 1: SELEÇÃO DE ANÁLISE
# ============================================================================

st.markdown("## 📊 Tipo de Análise")

analise_tipo = st.radio(
    "Selecione o tipo de análise:",
    ["Exames Laboratoriais", "Sintomas Clínicos", "Correlações", "Outliers"],
    horizontal=True
)

st.markdown("---")

# ============================================================================
# ANÁLISE: EXAMES LABORATORIAIS
# ============================================================================

if analise_tipo == "Exames Laboratoriais":
    st.markdown("## 🔬 Análise de Exames Laboratoriais")
    
    # Selecionar exame
    exames_disponiveis = [col for col in SCHEMA_COLUNAS['exames'] if col in df.columns]
    
    if not exames_disponiveis:
        st.warning("⚠️ Nenhum exame laboratorial encontrado no dataset.")
        st.stop()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        exame_selecionado = st.selectbox(
            "Selecione o exame para análise:",
            exames_disponiveis,
            format_func=lambda x: x.replace('_', ' ').title()
        )
    
    with col2:
        tipo_grafico = st.selectbox(
            "Tipo de gráfico:",
            ["Boxplot", "Histograma", "Violin Plot", "Estatísticas"]
        )
    
    # Obter faixas de referência
    especie_ref = filtro_especie if filtro_especie != 'Todas' else 'Canina'
    if especie_ref in FAIXAS_REFERENCIA and exame_selecionado in FAIXAS_REFERENCIA[especie_ref]:
        min_ref, max_ref = FAIXAS_REFERENCIA[especie_ref][exame_selecionado]
    else:
        min_ref, max_ref = None, None
    
    # Gráficos
    if tipo_grafico == "Boxplot":
        if 'especie' in df.columns:
            fig = px.box(
                df,
                x='especie',
                y=exame_selecionado,
                color='especie',
                title=f'Distribuição de {exame_selecionado.replace("_", " ").title()} por Espécie',
                points='outliers'
            )
        else:
            fig = px.box(
                df,
                y=exame_selecionado,
                title=f'Distribuição de {exame_selecionado.replace("_", " ").title()}',
                points='outliers'
            )
        
        # Adicionar linhas de referência
        if min_ref and max_ref:
            fig.add_hline(y=min_ref, line_dash="dash", line_color="red", 
                         annotation_text="Mín Referência")
            fig.add_hline(y=max_ref, line_dash="dash", line_color="red", 
                         annotation_text="Máx Referência")
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    elif tipo_grafico == "Histograma":
        fig = px.histogram(
            df,
            x=exame_selecionado,
            color='especie' if 'especie' in df.columns else None,
            title=f'Histograma de {exame_selecionado.replace("_", " ").title()}',
            marginal="box",
            nbins=30
        )
        
        if min_ref and max_ref:
            fig.add_vline(x=min_ref, line_dash="dash", line_color="red")
            fig.add_vline(x=max_ref, line_dash="dash", line_color="red")
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    elif tipo_grafico == "Violin Plot":
        if 'especie' in df.columns:
            fig = px.violin(
                df,
                x='especie',
                y=exame_selecionado,
                color='especie',
                title=f'Violin Plot - {exame_selecionado.replace("_", " ").title()}',
                box=True,
                points='outliers'
            )
        else:
            fig = px.violin(
                df,
                y=exame_selecionado,
                title=f'Violin Plot - {exame_selecionado.replace("_", " ").title()}',
                box=True,
                points='outliers'
            )
        
        if min_ref and max_ref:
            fig.add_hline(y=min_ref, line_dash="dash", line_color="red")
            fig.add_hline(y=max_ref, line_dash="dash", line_color="red")
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    elif tipo_grafico == "Estatísticas":
        st.markdown("### 📊 Estatísticas Descritivas")
        
        if 'especie' in df.columns:
            stats = obter_estatisticas_exame(df, exame_selecionado, por_especie=True)
            st.dataframe(stats, use_container_width=True)
        else:
            stats = obter_estatisticas_exame(df, exame_selecionado, por_especie=False)
            st.write(stats)
    
    # Valores fora da faixa de referência
    if min_ref and max_ref:
        st.markdown("### ⚠️ Valores Fora da Faixa de Referência")
        
        valores_baixos = df[df[exame_selecionado] < min_ref]
        valores_altos = df[df[exame_selecionado] > max_ref]
        valores_normais = df[(df[exame_selecionado] >= min_ref) & (df[exame_selecionado] <= max_ref)]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "↓ Baixo",
                len(valores_baixos),
                f"{100*len(valores_baixos)/len(df):.1f}%",
                delta_color="inverse"
            )
        
        with col2:
            st.metric(
                "✓ Normal",
                len(valores_normais),
                f"{100*len(valores_normais)/len(df):.1f}%"
            )
        
        with col3:
            st.metric(
                "↑ Alto",
                len(valores_altos),
                f"{100*len(valores_altos)/len(df):.1f}%",
                delta_color="inverse"
            )
        
        # Mostrar faixa de referência
        st.info(f"📏 **Faixa de Referência ({especie_ref}):** {min_ref} - {max_ref}")

# ============================================================================
# ANÁLISE: SINTOMAS CLÍNICOS
# ============================================================================

elif analise_tipo == "Sintomas Clínicos":
    st.markdown("## 💊 Análise de Sintomas Clínicos")
    
    sintomas_disponiveis = [col for col in SCHEMA_COLUNAS['sintomas'] if col in df.columns]
    
    if not sintomas_disponiveis:
        st.warning("⚠️ Nenhum sintoma encontrado no dataset.")
        st.stop()
    
    # Prevalência de sintomas
    st.markdown("### 📊 Prevalência de Sintomas")
    
    prevalencia_sintomas = {}
    for sintoma in sintomas_disponiveis:
        prevalencia_sintomas[sintoma.replace('_', ' ').title()] = df[sintoma].mean() * 100
    
    df_prev = pd.DataFrame.from_dict(prevalencia_sintomas, orient='index', columns=['Prevalência (%)'])
    df_prev = df_prev.sort_values('Prevalência (%)', ascending=False)
    
    fig_prev = px.bar(
        df_prev,
        x=df_prev.index,
        y='Prevalência (%)',
        title='Prevalência de Sintomas no Dataset Filtrado',
        color='Prevalência (%)',
        color_continuous_scale='Reds'
    )
    fig_prev.update_layout(xaxis_title='Sintoma', yaxis_title='Prevalência (%)', height=400)
    
    st.plotly_chart(fig_prev, use_container_width=True)
    
    # Sintomas por diagnóstico
    if 'diagnostico' in df.columns:
        st.markdown("### 🔬 Sintomas por Diagnóstico")
        
        # Selecionar diagnóstico
        diagnosticos = sorted(df['diagnostico'].unique())
        diag_selecionado = st.selectbox("Selecione o diagnóstico:", diagnosticos)
        
        df_diag = df[df['diagnostico'] == diag_selecionado]
        
        prevalencia_diag = {}
        for sintoma in sintomas_disponiveis:
            prevalencia_diag[sintoma.replace('_', ' ').title()] = df_diag[sintoma].mean() * 100
        
        df_prev_diag = pd.DataFrame.from_dict(prevalencia_diag, orient='index', columns=['Prevalência (%)'])
        df_prev_diag = df_prev_diag.sort_values('Prevalência (%)', ascending=False)
        
        fig_diag = px.bar(
            df_prev_diag,
            x=df_prev_diag.index,
            y='Prevalência (%)',
            title=f'Sintomas em Casos de {diag_selecionado}',
            color='Prevalência (%)',
            color_continuous_scale='Oranges'
        )
        fig_diag.update_layout(xaxis_title='Sintoma', height=400)
        
        st.plotly_chart(fig_diag, use_container_width=True)
    
    # Heatmap de sintomas
    st.markdown("### 🔥 Heatmap de Co-ocorrência de Sintomas")
    
    df_sintomas = df[sintomas_disponiveis].copy()
    corr_sintomas = df_sintomas.corr()
    
    fig_heatmap = px.imshow(
        corr_sintomas,
        labels=dict(color="Correlação"),
        x=[s.replace('_', ' ').title() for s in corr_sintomas.columns],
        y=[s.replace('_', ' ').title() for s in corr_sintomas.index],
        color_continuous_scale='RdBu_r',
        aspect="auto"
    )
    fig_heatmap.update_layout(title='Correlação entre Sintomas', height=500)
    
    st.plotly_chart(fig_heatmap, use_container_width=True)

# ============================================================================
# ANÁLISE: CORRELAÇÕES
# ============================================================================

elif analise_tipo == "Correlações":
    st.markdown("## 🔗 Análise de Correlações")
    
    # Selecionar apenas colunas numéricas
    colunas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Remover colunas não relevantes
    colunas_relevantes = [c for c in colunas_numericas if c not in ['id']]
    
    if len(colunas_relevantes) < 2:
        st.warning("⚠️ Não há colunas numéricas suficientes para análise de correlação.")
        st.stop()
    
    # Matriz de correlação
    st.markdown("### 🔥 Matriz de Correlação (Heatmap)")
    
    df_corr = df[colunas_relevantes].corr()
    
    fig_corr = px.imshow(
        df_corr,
        labels=dict(color="Correlação"),
        x=[c.replace('_', ' ').title() for c in df_corr.columns],
        y=[c.replace('_', ' ').title() for c in df_corr.index],
        color_continuous_scale='RdBu_r',
        zmin=-1,
        zmax=1,
        aspect="auto"
    )
    fig_corr.update_layout(height=700)
    
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Correlações mais fortes
    st.markdown("### 🔍 Correlações Mais Fortes")
    
    # Extrair correlações (exceto diagonal)
    correlacoes = []
    for i in range(len(df_corr.columns)):
        for j in range(i+1, len(df_corr.columns)):
            correlacoes.append({
                'Variável 1': df_corr.columns[i],
                'Variável 2': df_corr.columns[j],
                'Correlação': df_corr.iloc[i, j]
            })
    
    df_correlacoes = pd.DataFrame(correlacoes)
    df_correlacoes['Abs Correlação'] = df_correlacoes['Correlação'].abs()
    df_correlacoes = df_correlacoes.sort_values('Abs Correlação', ascending=False).head(15)
    
    st.dataframe(
        df_correlacoes[['Variável 1', 'Variável 2', 'Correlação']].style.format({'Correlação': '{:.3f}'}),
        use_container_width=True,
        hide_index=True
    )
    
    # Scatter plot de correlação selecionada
    st.markdown("### 📈 Scatter Plot")
    
    col1, col2 = st.columns(2)
    
    with col1:
        var_x = st.selectbox("Variável X:", colunas_relevantes)
    
    with col2:
        var_y = st.selectbox("Variável Y:", [c for c in colunas_relevantes if c != var_x])
    
    fig_scatter = px.scatter(
        df,
        x=var_x,
        y=var_y,
        color='diagnostico' if 'diagnostico' in df.columns else None,
        title=f'Relação entre {var_x.replace("_", " ").title()} e {var_y.replace("_", " ").title()}',
        trendline="ols",
        opacity=0.6
    )
    fig_scatter.update_layout(height=500)
    
    st.plotly_chart(fig_scatter, use_container_width=True)

# ============================================================================
# ANÁLISE: OUTLIERS
# ============================================================================

elif analise_tipo == "Outliers":
    st.markdown("## 🎯 Detecção de Outliers")
    
    st.markdown("""
    Outliers são valores que se desviam significativamente da maioria dos dados.
    Podem indicar:
    - ⚠️ Erros de medição ou registro
    - 🔬 Casos clínicos extremos que requerem atenção
    - 📊 Variabilidade natural em casos específicos
    """)
    
    # Selecionar exame
    exames_disponiveis = [col for col in SCHEMA_COLUNAS['exames'] if col in df.columns]
    
    if not exames_disponiveis:
        st.warning("⚠️ Nenhum exame laboratorial encontrado.")
        st.stop()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        exame_outlier = st.selectbox("Selecione o exame:", exames_disponiveis)
    
    with col2:
        metodo = st.selectbox("Método de detecção:", ["IQR (Interquartile Range)", "Z-Score"])
    
    # Detectar outliers
    metodo_param = 'iqr' if 'IQR' in metodo else 'zscore'
    mask_outliers = identificar_outliers(df, exame_outlier, metodo=metodo_param)
    
    df_outliers = df[mask_outliers].copy()
    df_normais = df[~mask_outliers].copy()
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Casos", len(df))
    
    with col2:
        st.metric("Outliers Detectados", len(df_outliers), 
                 f"{100*len(df_outliers)/len(df):.1f}%")
    
    with col3:
        st.metric("Valores Normais", len(df_normais))
    
    # Visualização
    fig = go.Figure()
    
    # Valores normais
    fig.add_trace(go.Box(
        y=df_normais[exame_outlier],
        name='Normais',
        marker_color='lightblue',
        boxmean='sd'
    ))
    
    # Outliers
    if len(df_outliers) > 0:
        fig.add_trace(go.Scatter(
            y=df_outliers[exame_outlier],
            mode='markers',
            name='Outliers',
            marker=dict(color='red', size=10, symbol='x')
        ))
    
    fig.update_layout(
        title=f'Detecção de Outliers - {exame_outlier.replace("_", " ").title()}',
        yaxis_title=exame_outlier.replace('_', ' ').title(),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela de outliers
    if len(df_outliers) > 0:
        st.markdown("### 📋 Casos com Outliers")
        
        colunas_mostrar = ['id', 'especie', 'raca', exame_outlier, 'diagnostico']
        colunas_mostrar = [c for c in colunas_mostrar if c in df_outliers.columns]
        
        st.dataframe(
            df_outliers[colunas_mostrar].sort_values(exame_outlier, ascending=False),
            use_container_width=True,
            hide_index=True
        )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>💡 Use os filtros na barra lateral para análises mais específicas</p>
</div>
""", unsafe_allow_html=True)



