"""
Página: Treinar Modelo
Pipeline completo de Machine Learning para diagnóstico veterinário
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path
from sklearn.model_selection import train_test_split

# Adicionar path da biblioteca
sys.path.insert(0, str(Path(__file__).parent.parent))

from vetlib.preprocessing import (
    preparar_features_target, criar_preprocessador,
    aplicar_preprocessamento, selecionar_features_importantes
)
from vetlib.modeling import (
    obter_modelos_disponiveis, treinar_modelo, avaliar_modelo,
    obter_importancia_features, salvar_modelo, calcular_roc_curves,
    avaliar_por_especie
)

st.set_page_config(page_title="Treinar Modelo", page_icon="🤖", layout="wide")

# Título
st.title("🤖 Treinar Modelo de Machine Learning")
st.markdown("Pipeline completo de treinamento, avaliação e explicabilidade")

# Verificar dados
if st.session_state.get('df_main') is None:
    st.warning("⚠️ Nenhum dataset carregado. Vá para **📥 Upload de Dados** primeiro.")
    st.stop()

df = st.session_state.df_main.copy()

# Verificar se tem coluna de diagnóstico
if 'diagnostico' not in df.columns:
    st.error("❌ Coluna 'diagnostico' não encontrada. Necessária para treinar modelos supervisionados.")
    st.stop()

# ============================================================================
# SEÇÃO 1: CONFIGURAÇÕES DO MODELO
# ============================================================================

st.markdown("## ⚙️ Configurações do Modelo")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎯 Algoritmo")
    
    modelos_disponiveis = obter_modelos_disponiveis()
    modelo_selecionado = st.selectbox(
        "Selecione o algoritmo:",
        list(modelos_disponiveis.keys()),
        help="Diferentes algoritmos para classificação"
    )
    
    st.markdown(f"**Modelo selecionado:** {modelo_selecionado}")

with col2:
    st.markdown("### 🔧 Hiperparâmetros")
    
    usar_grid_search = st.checkbox(
        "Usar Grid Search",
        value=False,
        help="Busca automática pelos melhores hiperparâmetros (mais lento)"
    )
    
    test_size = st.slider(
        "Tamanho do conjunto de teste (%)",
        10, 40, 20,
        help="Percentual dos dados para teste"
    ) / 100
    
    random_state = st.number_input(
        "Random State (seed)",
        value=42,
        help="Semente para reprodutibilidade"
    )

# Opções avançadas
with st.expander("🔬 Opções Avançadas"):
    incluir_features_anormalidade = st.checkbox(
        "Criar features de anormalidade (valores fora de referência)",
        value=False,
        help="Adiciona features indicando se valores estão alto/baixo"
    )
    
    usar_selecao_features = st.checkbox(
        "Usar seleção de features (Mutual Information)",
        value=False,
        help="Seleciona apenas features mais importantes"
    )
    
    if usar_selecao_features:
        n_features = st.slider(
            "Número de features a selecionar",
            5, 50, 20
        )
    else:
        n_features = None
    
    cv_folds = st.slider(
        "Número de folds para validação cruzada",
        3, 10, 5
    )

st.markdown("---")

# ============================================================================
# SEÇÃO 2: PREPARAÇÃO DOS DADOS
# ============================================================================

st.markdown("## 📊 Preparação dos Dados")

with st.spinner("Preparando dados..."):
    # Preparar features e target
    X, y, feature_names = preparar_features_target(
        df,
        target_col='diagnostico',
        incluir_features_anormalidade=incluir_features_anormalidade
    )
    
    # Informações
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Casos", len(X))
    
    with col2:
        st.metric("Features", len(feature_names))
    
    with col3:
        st.metric("Classes", len(y.unique()))
    
    with col4:
        min_class = y.value_counts().min()
        st.metric("Menor Classe", min_class)
        if min_class < 5:
            st.warning("⚠️ Classe pequena!")

# Distribuição de classes
st.markdown("### 📊 Distribuição de Classes")

class_dist = y.value_counts().reset_index()
class_dist.columns = ['Diagnóstico', 'Quantidade']

fig_dist = px.bar(
    class_dist,
    x='Quantidade',
    y='Diagnóstico',
    orientation='h',
    title='Distribuição de Diagnósticos',
    color='Quantidade',
    color_continuous_scale='Blues'
)
fig_dist.update_layout(height=max(300, len(class_dist) * 30))

st.plotly_chart(fig_dist, use_container_width=True)

# Botão de treinar
st.markdown("---")
st.markdown("## 🚀 Treinamento")

if st.button("🎯 Treinar Modelo", type="primary", use_container_width=False):
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # 1. Split dos dados
        status_text.text("📊 Dividindo dados em treino e teste...")
        progress_bar.progress(10)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            stratify=y
        )
        
        # Guardar espécie para análise posterior
        if 'especie' in X_train.columns:
            especie_train = X_train['especie'].copy()
            especie_test = X_test['especie'].copy()
        else:
            especie_train = None
            especie_test = None
        
        # 2. Pré-processamento
        status_text.text("🔧 Aplicando pré-processamento...")
        progress_bar.progress(20)
        
        preprocessadores = criar_preprocessador(X_train)
        X_train_proc, preprocessadores = aplicar_preprocessamento(
            X_train, preprocessadores, fit=True
        )
        X_test_proc, _ = aplicar_preprocessamento(
            X_test, preprocessadores, fit=False
        )
        
        # 3. Seleção de features (opcional)
        if usar_selecao_features:
            status_text.text("🎯 Selecionando features importantes...")
            progress_bar.progress(30)
            
            features_selecionadas, feature_scores = selecionar_features_importantes(
                X_train_proc, y_train, n_features=n_features
            )
            
            X_train_proc = X_train_proc[features_selecionadas]
            X_test_proc = X_test_proc[features_selecionadas]
            feature_names = features_selecionadas
            
            st.info(f"✅ {len(features_selecionadas)} features selecionadas")
        
        # 4. Treinamento
        status_text.text(f"🤖 Treinando {modelo_selecionado}...")
        progress_bar.progress(50)
        
        modelo, historico = treinar_modelo(
            X_train_proc, y_train,
            nome_modelo=modelo_selecionado,
            usar_grid_search=usar_grid_search,
            cv_folds=cv_folds,
            random_state=random_state
        )
        
        # 5. Avaliação
        status_text.text("📈 Avaliando modelo...")
        progress_bar.progress(70)
        
        metricas = avaliar_modelo(modelo, X_test_proc, y_test, nomes_classes=modelo.classes_, label_encoder=historico.get('label_encoder'))
        
        # 6. Importância de features
        status_text.text("🔍 Calculando importância de features...")
        progress_bar.progress(85)
        
        df_importancia = obter_importancia_features(modelo, feature_names)
        
        # 7. ROC curves
        roc_curves = calcular_roc_curves(modelo, X_test_proc, y_test)
        
        # 8. Avaliar por espécie
        if especie_test is not None:
            metricas_especies = avaliar_por_especie(modelo, X_test_proc, y_test, especie_test, historico.get('label_encoder'))
        else:
            metricas_especies = None
        
        progress_bar.progress(100)
        status_text.text("✅ Treinamento concluído!")
        
        # Salvar no session_state
        st.session_state.modelo_treinado = modelo
        st.session_state.preprocessor = preprocessadores
        st.session_state.feature_names = feature_names
        st.session_state.target_names = modelo.classes_.tolist()
        st.session_state.metricas_modelo = metricas
        st.session_state.historico_treino = historico
        st.session_state.df_importancia = df_importancia
        st.session_state.roc_curves = roc_curves
        st.session_state.metricas_especies = metricas_especies
        
        st.success("🎉 Modelo treinado com sucesso!")
        st.balloons()
        
        # ====================================================================
        # RESULTADOS
        # ====================================================================
        
        st.markdown("---")
        st.markdown("## 📊 Resultados do Treinamento")
        
        # Métricas principais
        st.markdown("### 🎯 Métricas de Avaliação")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Accuracy", f"{metricas['accuracy']:.3f}")
        
        with col2:
            st.metric("F1 Score (Macro)", f"{metricas['f1_macro']:.3f}")
        
        with col3:
            st.metric("Precision (Macro)", f"{metricas['precision_macro']:.3f}")
        
        with col4:
            if metricas['roc_auc']:
                st.metric("ROC AUC", f"{metricas['roc_auc']:.3f}")
            else:
                st.metric("ROC AUC", "N/A")
        
        # Validação cruzada
        if 'cv_f1_mean' in historico:
            st.info(f"📊 **Validação Cruzada (F1 Macro):** {historico['cv_f1_mean']:.3f} ± {historico['cv_f1_std']:.3f}")
        
        # Matriz de confusão
        st.markdown("### 📊 Matriz de Confusão")
        
        conf_matrix = metricas['confusion_matrix']
        
        fig_conf = px.imshow(
            conf_matrix,
            labels=dict(x="Predito", y="Real", color="Casos"),
            x=modelo.classes_,
            y=modelo.classes_,
            color_continuous_scale='Blues',
            text_auto=True,
            aspect="auto"
        )
        fig_conf.update_layout(height=max(400, len(modelo.classes_) * 50))
        
        st.plotly_chart(fig_conf, use_container_width=True)
        
        # Relatório de classificação
        st.markdown("### 📋 Relatório de Classificação")
        
        class_report = metricas['classification_report']
        
        # Converter para DataFrame
        df_report = pd.DataFrame(class_report).transpose()
        df_report = df_report[df_report.index != 'accuracy']  # Remover linha accuracy
        df_report = df_report.iloc[:-2]  # Remover macro/weighted avg
        
        st.dataframe(
            df_report.style.format({
                'precision': '{:.3f}',
                'recall': '{:.3f}',
                'f1-score': '{:.3f}',
                'support': '{:.0f}'
            }).background_gradient(subset=['f1-score'], cmap='RdYlGn', vmin=0, vmax=1),
            use_container_width=True
        )
        
        # Curvas ROC
        if roc_curves and len(roc_curves) > 0:
            st.markdown("### 📈 Curvas ROC")
            
            fig_roc = go.Figure()
            
            for classe, dados in roc_curves.items():
                fpr = dados['fpr']
                tpr = dados['tpr']
                
                # Calcular AUC
                from sklearn.metrics import auc
                roc_auc = auc(fpr, tpr)
                
                fig_roc.add_trace(go.Scatter(
                    x=fpr, y=tpr,
                    name=f'{classe} (AUC = {roc_auc:.3f})',
                    mode='lines'
                ))
            
            # Linha diagonal
            fig_roc.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1],
                name='Chance',
                mode='lines',
                line=dict(dash='dash', color='gray')
            ))
            
            fig_roc.update_layout(
                title='Curvas ROC (One-vs-Rest)',
                xaxis_title='False Positive Rate',
                yaxis_title='True Positive Rate',
                height=500
            )
            
            st.plotly_chart(fig_roc, use_container_width=True)
        
        # Importância de features
        if df_importancia is not None:
            st.markdown("### 🔍 Importância das Features")
            
            df_imp_top = df_importancia.head(20)
            
            fig_imp = px.bar(
                df_imp_top,
                x='importancia',
                y='feature',
                orientation='h',
                title='Top 20 Features Mais Importantes',
                color='importancia',
                color_continuous_scale='Viridis'
            )
            fig_imp.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                height=max(400, len(df_imp_top) * 25)
            )
            
            st.plotly_chart(fig_imp, use_container_width=True)
        
        # Avaliação por espécie
        if metricas_especies:
            st.markdown("### 🐾 Avaliação por Espécie")
            
            df_especies_eval = pd.DataFrame(metricas_especies).T
            df_especies_eval = df_especies_eval[['n_samples', 'accuracy', 'f1_macro']]
            
            st.dataframe(
                df_especies_eval.style.format({
                    'n_samples': '{:.0f}',
                    'accuracy': '{:.3f}',
                    'f1_macro': '{:.3f}'
                }),
                use_container_width=True
            )
        
        # Salvar modelo
        st.markdown("---")
        st.markdown("## 💾 Salvar Modelo")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            nome_modelo = st.text_input(
                "Nome do modelo",
                value=f"modelo_{modelo_selecionado.replace(' ', '_').lower()}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 Salvar Modelo", use_container_width=True):
                try:
                    caminho_salvo = salvar_modelo(
                        modelo,
                        preprocessadores,
                        feature_names,
                        caminho_base=f'models/{nome_modelo}'
                    )
                    st.success(f"✅ Modelo salvo em: {caminho_salvo}")
                    st.info("👉 Agora você pode usar o modelo na página **🔍 Predição**!")
                except Exception as e:
                    st.error(f"❌ Erro ao salvar: {str(e)}")
        
    except Exception as e:
        st.error(f"❌ Erro durante o treinamento: {str(e)}")
        import traceback
        with st.expander("Ver detalhes do erro"):
            st.code(traceback.format_exc())

# ============================================================================
# SEÇÃO: MODELO ATUAL
# ============================================================================

if st.session_state.get('modelo_treinado') is not None:
    st.markdown("---")
    st.markdown("## ✅ Modelo Atual na Sessão")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("✅ Modelo treinado disponível")
    
    with col2:
        if st.session_state.get('metricas_modelo'):
            f1_score = st.session_state.metricas_modelo['f1_macro']
            st.metric("F1 Score", f"{f1_score:.3f}")
    
    with col3:
        if st.button("🗑️ Limpar Modelo"):
            st.session_state.modelo_treinado = None
            st.session_state.preprocessor = None
            st.session_state.feature_names = None
            st.session_state.target_names = None
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>💡 Após treinar, use a página **🔍 Predição** para fazer diagnósticos</p>
    <p>⚠️ Sempre valide os modelos com dados independentes antes de uso clínico</p>
</div>
""", unsafe_allow_html=True)

