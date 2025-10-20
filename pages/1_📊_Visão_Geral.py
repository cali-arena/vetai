"""
Página: Visão Geral
Dashboard com métricas principais, cards e gráficos resumidos
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

# Adicionar path da biblioteca
sys.path.insert(0, str(Path(__file__).parent.parent))

from vetlib.data_io import obter_info_dataset
from vetlib.preprocessing import verificar_valores_referencia, FAIXAS_REFERENCIA

st.set_page_config(page_title="Visão Geral", page_icon="📊", layout="wide")

# Título
st.title("📊 Visão Geral do Dataset")
st.markdown("Dashboard com métricas principais e análises resumidas")

# Verificar se há dados carregados
if st.session_state.get('df_main') is None:
    st.warning("⚠️ Nenhum dataset carregado. Vá para **📥 Upload de Dados** para começar.")
    
    # Botão para carregar dataset de exemplo
    if st.button("🔄 Carregar Dataset de Exemplo"):
        from vetlib.data_io import carregar_dataset_exemplo
        df_exemplo = carregar_dataset_exemplo()
        if df_exemplo is not None:
            st.session_state.df_main = df_exemplo
            st.success("✅ Dataset de exemplo carregado!")
            st.rerun()
    
    st.stop()

df = st.session_state.df_main

# Obter informações do dataset
info = obter_info_dataset(df)

# ============================================================================
# SEÇÃO 1: CARDS DE MÉTRICAS PRINCIPAIS
# ============================================================================

st.markdown("## 📈 Métricas Principais")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📝 Total de Registros",
        value=f"{info['n_registros']:,}",
        help="Número total de casos no dataset"
    )

with col2:
    n_diagnosticos = len(info['diagnosticos'])
    st.metric(
        label="🏥 Diagnósticos Únicos",
        value=n_diagnosticos,
        help="Número de diagnósticos diferentes"
    )

with col3:
    n_especies = len(info['especies'])
    st.metric(
        label="🐾 Espécies",
        value=n_especies,
        help="Número de espécies diferentes"
    )

with col4:
    n_exames = len(info['exames_disponiveis'])
    st.metric(
        label="🧪 Exames Disponíveis",
        value=n_exames,
        help="Número de tipos de exames laboratoriais"
    )

st.markdown("---")

# ============================================================================
# SEÇÃO 2: DISTRIBUIÇÕES PRINCIPAIS
# ============================================================================

st.markdown("## 📊 Distribuições")

col1, col2 = st.columns(2)

# Distribuição de Espécies
with col1:
    st.markdown("### 🐾 Distribuição de Espécies")
    
    if info['especies']:
        df_especies = pd.DataFrame.from_dict(info['especies'], orient='index', columns=['count'])
        df_especies = df_especies.reset_index().rename(columns={'index': 'Espécie', 'count': 'Quantidade'})
        
        fig_especies = px.pie(
            df_especies,
            values='Quantidade',
            names='Espécie',
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0.4
        )
        fig_especies.update_traces(textposition='inside', textinfo='percent+label')
        fig_especies.update_layout(height=350)
        
        st.plotly_chart(fig_especies, use_container_width=True)
    else:
        st.info("Informação de espécie não disponível")

# Top Diagnósticos
with col2:
    st.markdown("### 🏥 Top 10 Diagnósticos")
    
    if info['diagnosticos']:
        df_diag = pd.DataFrame.from_dict(info['diagnosticos'], orient='index', columns=['count'])
        df_diag = df_diag.reset_index().rename(columns={'index': 'Diagnóstico', 'count': 'Quantidade'})
        df_diag = df_diag.sort_values('Quantidade', ascending=False).head(10)
        
        fig_diag = px.bar(
            df_diag,
            x='Quantidade',
            y='Diagnóstico',
            orientation='h',
            color='Quantidade',
            color_continuous_scale='Blues'
        )
        fig_diag.update_layout(height=350, showlegend=False)
        
        st.plotly_chart(fig_diag, use_container_width=True)
    else:
        st.info("Informação de diagnóstico não disponível")

st.markdown("---")

# ============================================================================
# SEÇÃO 3: ANÁLISE TEMPORAL (se houver data)
# ============================================================================

if 'data' in df.columns:
    st.markdown("## 📅 Análise Temporal")
    
    try:
        df_temp = df.copy()
        df_temp['data'] = pd.to_datetime(df_temp['data'])
        df_temp['mes_ano'] = df_temp['data'].dt.to_period('M').astype(str)
        
        casos_por_mes = df_temp.groupby('mes_ano').size().reset_index(name='casos')
        
        fig_temporal = px.line(
            casos_por_mes,
            x='mes_ano',
            y='casos',
            title='Evolução do Número de Casos por Mês',
            markers=True
        )
        fig_temporal.update_layout(
            xaxis_title='Mês/Ano',
            yaxis_title='Número de Casos',
            height=400
        )
        
        st.plotly_chart(fig_temporal, use_container_width=True)
        
    except Exception as e:
        st.info(f"Não foi possível gerar análise temporal: {str(e)}")
    
    st.markdown("---")

# ============================================================================
# SEÇÃO 4: VALORES CRÍTICOS E ALERTAS
# ============================================================================

st.markdown("## ⚠️ Alertas de Valores Críticos")

st.markdown("""
Valores que estão **significativamente fora** das faixas de referência por espécie.
""")

# Calcular valores fora de referência
valores_criticos = []

for exame in ['creatinina', 'ureia', 'glicose', 'alt', 'ast']:
    if exame not in df.columns or 'especie' not in df.columns:
        continue
    
    for especie in df['especie'].unique():
        if especie not in FAIXAS_REFERENCIA:
            continue
        
        df_esp = df[df['especie'] == especie]
        min_ref, max_ref = FAIXAS_REFERENCIA[especie][exame]
        
        # Valores muito fora da faixa (>50% fora)
        muito_alto = df_esp[df_esp[exame] > max_ref * 1.5]
        muito_baixo = df_esp[df_esp[exame] < min_ref * 0.5]
        
        if len(muito_alto) > 0:
            valores_criticos.append({
                'Exame': exame.capitalize(),
                'Espécie': especie,
                'Tipo': 'Muito Alto',
                'N_Casos': len(muito_alto),
                'Pct': f"{100*len(muito_alto)/len(df_esp):.1f}%"
            })
        
        if len(muito_baixo) > 0:
            valores_criticos.append({
                'Exame': exame.capitalize(),
                'Espécie': especie,
                'Tipo': 'Muito Baixo',
                'N_Casos': len(muito_baixo),
                'Pct': f"{100*len(muito_baixo)/len(df_esp):.1f}%"
            })

if valores_criticos:
    df_criticos = pd.DataFrame(valores_criticos)
    df_criticos = df_criticos.sort_values('N_Casos', ascending=False)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.dataframe(df_criticos, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### 🔍 Interpretação")
        st.markdown("""
        **Muito Alto:** > 150% do limite superior
        
        **Muito Baixo:** < 50% do limite inferior
        
        Estes casos requerem **atenção prioritária** e reavaliação clínica.
        """)
else:
    st.success("✅ Nenhum valor crítico detectado no dataset atual.")

st.markdown("---")

# ============================================================================
# SEÇÃO 5: DISTRIBUIÇÃO ETÁRIA E SEXO
# ============================================================================

st.markdown("## 📊 Demografia")

col1, col2 = st.columns(2)

# Distribuição Etária
with col1:
    st.markdown("### 📅 Distribuição Etária")
    
    if 'idade_anos' in df.columns:
        fig_idade = px.histogram(
            df,
            x='idade_anos',
            nbins=20,
            color='especie' if 'especie' in df.columns else None,
            title='Distribuição de Idade (anos)',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_idade.update_layout(
            xaxis_title='Idade (anos)',
            yaxis_title='Frequência',
            height=350
        )
        
        st.plotly_chart(fig_idade, use_container_width=True)
        
        # Estatísticas
        st.markdown(f"""
        - **Média:** {df['idade_anos'].mean():.1f} anos
        - **Mediana:** {df['idade_anos'].median():.1f} anos
        - **Min/Max:** {df['idade_anos'].min():.1f} - {df['idade_anos'].max():.1f} anos
        """)
    else:
        st.info("Informação de idade não disponível")

# Distribuição de Sexo
with col2:
    st.markdown("### ♂️♀️ Distribuição de Sexo")
    
    if 'sexo' in df.columns:
        sexo_count = df['sexo'].value_counts()
        
        fig_sexo = go.Figure(data=[
            go.Bar(
                x=sexo_count.index,
                y=sexo_count.values,
                marker_color=['#4472C4', '#ED7D31'],
                text=sexo_count.values,
                textposition='outside'
            )
        ])
        
        fig_sexo.update_layout(
            xaxis_title='Sexo',
            yaxis_title='Quantidade',
            height=350,
            showlegend=False
        )
        
        st.plotly_chart(fig_sexo, use_container_width=True)
        
        # Percentuais
        total = len(df)
        st.markdown(f"""
        - **Machos (M):** {sexo_count.get('M', 0)} ({100*sexo_count.get('M', 0)/total:.1f}%)
        - **Fêmeas (F):** {sexo_count.get('F', 0)} ({100*sexo_count.get('F', 0)/total:.1f}%)
        """)
    else:
        st.info("Informação de sexo não disponível")

st.markdown("---")

# ============================================================================
# SEÇÃO 6: RAÇAS MAIS COMUNS
# ============================================================================

if 'raca' in df.columns:
    st.markdown("## 🐕 Raças Mais Comuns")
    
    col1, col2 = st.columns(2)
    
    # Caninos
    with col1:
        if 'especie' in df.columns:
            df_canino = df[df['especie'] == 'Canina']
            if len(df_canino) > 0:
                st.markdown("### Caninos")
                racas_caninas = df_canino['raca'].value_counts().head(10)
                
                fig_racas_can = px.bar(
                    x=racas_caninas.values,
                    y=racas_caninas.index,
                    orientation='h',
                    color=racas_caninas.values,
                    color_continuous_scale='Oranges'
                )
                fig_racas_can.update_layout(
                    xaxis_title='Quantidade',
                    yaxis_title='Raça',
                    height=350,
                    showlegend=False
                )
                
                st.plotly_chart(fig_racas_can, use_container_width=True)
    
    # Felinos
    with col2:
        if 'especie' in df.columns:
            df_felino = df[df['especie'] == 'Felina']
            if len(df_felino) > 0:
                st.markdown("### Felinos")
                racas_felinas = df_felino['raca'].value_counts().head(10)
                
                fig_racas_fel = px.bar(
                    x=racas_felinas.values,
                    y=racas_felinas.index,
                    orientation='h',
                    color=racas_felinas.values,
                    color_continuous_scale='Purples'
                )
                fig_racas_fel.update_layout(
                    xaxis_title='Quantidade',
                    yaxis_title='Raça',
                    height=350,
                    showlegend=False
                )
                
                st.plotly_chart(fig_racas_fel, use_container_width=True)
    
    st.markdown("---")

# ============================================================================
# SEÇÃO 7: TAXA DE POSITIVIDADE POR DOENÇA
# ============================================================================

if 'diagnostico' in df.columns:
    st.markdown("## 📊 Taxa de Positividade")
    
    st.markdown("""
    Percentual de casos positivos para cada diagnóstico (excluindo "Saudável").
    """)
    
    total_casos = len(df)
    diagnosticos_count = df['diagnostico'].value_counts()
    
    # Remover "Saudável" se existir
    diagnosticos_count = diagnosticos_count[diagnosticos_count.index != 'Saudável']
    
    df_positividade = pd.DataFrame({
        'Diagnóstico': diagnosticos_count.index,
        'Casos': diagnosticos_count.values,
        'Taxa (%)': 100 * diagnosticos_count.values / total_casos
    }).sort_values('Taxa (%)', ascending=False).head(15)
    
    fig_positiv = px.bar(
        df_positividade,
        x='Taxa (%)',
        y='Diagnóstico',
        orientation='h',
        text='Taxa (%)',
        color='Taxa (%)',
        color_continuous_scale='Reds'
    )
    fig_positiv.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_positiv.update_layout(
        xaxis_title='Taxa de Positividade (%)',
        yaxis_title='',
        height=max(400, len(df_positividade) * 30),
        showlegend=False
    )
    
    st.plotly_chart(fig_positiv, use_container_width=True)

st.markdown("---")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>💡 Use os filtros nas páginas de análise para explorar os dados em detalhes</p>
    <p>⚠️ Dados apresentados para fins educacionais e de pesquisa</p>
</div>
""", unsafe_allow_html=True)



