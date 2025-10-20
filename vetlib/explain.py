"""
Módulo de explicabilidade de modelos (SHAP e Permutation Importance)
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Import SHAP (pode não estar disponível)
try:
    import shap
    SHAP_DISPONIVEL = True
except ImportError:
    SHAP_DISPONIVEL = False

from sklearn.inspection import permutation_importance


def calcular_shap_values(modelo, X, feature_names=None, max_samples=100):
    """
    Calcula SHAP values para explicabilidade
    
    Args:
        modelo: Modelo treinado
        X: Features (DataFrame ou array)
        feature_names: Nomes das features
        max_samples: Número máximo de samples para calcular (performance)
        
    Returns:
        shap_values, explainer, X_sample
    """
    if not SHAP_DISPONIVEL:
        st.warning("⚠️ Biblioteca SHAP não disponível. Instale com: pip install shap")
        return None, None, None
    
    # Converter para DataFrame se necessário
    if not isinstance(X, pd.DataFrame):
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        X = pd.DataFrame(X, columns=feature_names)
    
    # Limitar amostras para performance
    if len(X) > max_samples:
        X_sample = X.sample(n=max_samples, random_state=42)
    else:
        X_sample = X.copy()
    
    try:
        # Tentar TreeExplainer (para modelos baseados em árvore)
        if hasattr(modelo, 'tree_'):
            explainer = shap.TreeExplainer(modelo)
        else:
            # Usar KernelExplainer (mais geral, mas mais lento)
            explainer = shap.KernelExplainer(
                modelo.predict_proba,
                shap.sample(X_sample, min(100, len(X_sample)))
            )
        
        shap_values = explainer.shap_values(X_sample)
        
        return shap_values, explainer, X_sample
    
    except Exception as e:
        st.error(f"❌ Erro ao calcular SHAP values: {str(e)}")
        return None, None, None


def plotar_shap_summary(shap_values, X, feature_names=None, classe=None):
    """
    Cria gráfico de resumo SHAP (importância global)
    
    Args:
        shap_values: SHAP values calculados
        X: Features
        feature_names: Nomes das features
        classe: Índice da classe (para multiclasse)
        
    Returns:
        Plotly figure
    """
    if shap_values is None:
        return None
    
    # Para multiclasse, selecionar classe específica
    if isinstance(shap_values, list) and classe is not None:
        shap_vals = shap_values[classe]
    elif isinstance(shap_values, list):
        shap_vals = shap_values[0]  # Usar primeira classe por padrão
    else:
        shap_vals = shap_values
    
    # Calcular importância média absoluta
    mean_abs_shap = np.abs(shap_vals).mean(axis=0)
    
    if feature_names is None:
        feature_names = [f'feature_{i}' for i in range(len(mean_abs_shap))]
    
    # Criar DataFrame e ordenar
    df_shap = pd.DataFrame({
        'feature': feature_names,
        'importancia': mean_abs_shap
    }).sort_values('importancia', ascending=True).tail(20)  # Top 20
    
    # Plotar
    fig = go.Figure(go.Bar(
        x=df_shap['importancia'],
        y=df_shap['feature'],
        orientation='h',
        marker=dict(color=df_shap['importancia'], colorscale='Blues')
    ))
    
    fig.update_layout(
        title='Importância Global das Features (SHAP)',
        xaxis_title='|SHAP value| médio',
        yaxis_title='Feature',
        height=max(400, len(df_shap) * 25),
        showlegend=False
    )
    
    return fig


def plotar_shap_waterfall(shap_values, X, feature_names, instance_idx=0, classe=None):
    """
    Cria gráfico waterfall SHAP para uma predição específica
    
    Args:
        shap_values: SHAP values
        X: Features
        feature_names: Nomes das features
        instance_idx: Índice da instância a explicar
        classe: Índice da classe (multiclasse)
        
    Returns:
        Plotly figure
    """
    if shap_values is None:
        return None
    
    # Selecionar classe se multiclasse
    if isinstance(shap_values, list) and classe is not None:
        shap_vals = shap_values[classe][instance_idx]
    elif isinstance(shap_values, list):
        shap_vals = shap_values[0][instance_idx]
    else:
        shap_vals = shap_values[instance_idx]
    
    # Obter valores da instância
    if isinstance(X, pd.DataFrame):
        instance_values = X.iloc[instance_idx].values
    else:
        instance_values = X[instance_idx]
    
    # Criar DataFrame com features e SHAP values
    df_waterfall = pd.DataFrame({
        'feature': feature_names,
        'shap_value': shap_vals,
        'feature_value': instance_values
    })
    
    # Ordenar por valor absoluto de SHAP
    df_waterfall['abs_shap'] = np.abs(df_waterfall['shap_value'])
    df_waterfall = df_waterfall.sort_values('abs_shap', ascending=False).head(10)
    
    # Criar labels com valor da feature
    df_waterfall['label'] = df_waterfall.apply(
        lambda row: f"{row['feature']} = {row['feature_value']:.2f}", 
        axis=1
    )
    
    # Plotar
    colors = ['red' if x < 0 else 'green' for x in df_waterfall['shap_value']]
    
    fig = go.Figure(go.Bar(
        y=df_waterfall['label'],
        x=df_waterfall['shap_value'],
        orientation='h',
        marker=dict(color=colors)
    ))
    
    fig.update_layout(
        title=f'Contribuição das Features para Predição (Instância {instance_idx})',
        xaxis_title='SHAP value (← diminui | aumenta →)',
        yaxis_title='Feature',
        height=400,
        showlegend=False
    )
    
    return fig


def calcular_permutation_importance(modelo, X, y, feature_names=None, n_repeats=10):
    """
    Calcula importância por permutação (alternativa ao SHAP)
    
    Args:
        modelo: Modelo treinado
        X: Features
        y: Target
        feature_names: Nomes das features
        n_repeats: Número de repetições
        
    Returns:
        DataFrame com importâncias
    """
    try:
        result = permutation_importance(
            modelo, X, y,
            n_repeats=n_repeats,
            random_state=42,
            n_jobs=-1
        )
        
        if feature_names is None:
            if isinstance(X, pd.DataFrame):
                feature_names = X.columns.tolist()
            else:
                feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        
        df_importance = pd.DataFrame({
            'feature': feature_names,
            'importancia': result.importances_mean,
            'std': result.importances_std
        }).sort_values('importancia', ascending=False)
        
        return df_importance
    
    except Exception as e:
        st.error(f"❌ Erro ao calcular Permutation Importance: {str(e)}")
        return None


def plotar_permutation_importance(df_importance, top_n=20):
    """
    Plota importância por permutação
    
    Args:
        df_importance: DataFrame com importâncias
        top_n: Número de features a mostrar
        
    Returns:
        Plotly figure
    """
    if df_importance is None or len(df_importance) == 0:
        return None
    
    df_plot = df_importance.head(top_n).sort_values('importancia', ascending=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_plot['feature'],
        x=df_plot['importancia'],
        orientation='h',
        error_x=dict(type='data', array=df_plot['std']),
        marker=dict(color=df_plot['importancia'], colorscale='Viridis')
    ))
    
    fig.update_layout(
        title='Importância das Features (Permutation Importance)',
        xaxis_title='Importância',
        yaxis_title='Feature',
        height=max(400, len(df_plot) * 25),
        showlegend=False
    )
    
    return fig


def explicar_predicao_local(modelo, X_instance, feature_names, preprocessadores, 
                           usar_shap=True, modelo_type='tree'):
    """
    Explica uma predição individual
    
    Args:
        modelo: Modelo treinado
        X_instance: Instância a explicar (1 linha)
        feature_names: Nomes das features
        preprocessadores: Preprocessadores usados
        usar_shap: Se True, usa SHAP; caso contrário, usa feature importance do modelo
        modelo_type: 'tree' ou 'linear'
        
    Returns:
        dict com explicações
    """
    # Fazer predição
    y_pred = modelo.predict(X_instance)[0]
    y_proba = modelo.predict_proba(X_instance)[0]
    
    explicacao = {
        'predicao': y_pred,
        'probabilidades': dict(zip(modelo.classes_, y_proba)),
        'features_importantes': []
    }
    
    # Usar SHAP se disponível e solicitado
    if usar_shap and SHAP_DISPONIVEL:
        try:
            shap_values, explainer, _ = calcular_shap_values(modelo, X_instance, feature_names, max_samples=1)
            
            if shap_values is not None:
                # Pegar SHAP values da classe predita
                classe_idx = list(modelo.classes_).index(y_pred)
                
                if isinstance(shap_values, list):
                    shap_vals = shap_values[classe_idx][0]
                else:
                    shap_vals = shap_values[0]
                
                # Top features por impacto absoluto
                top_indices = np.argsort(np.abs(shap_vals))[::-1][:10]
                
                for idx in top_indices:
                    explicacao['features_importantes'].append({
                        'feature': feature_names[idx],
                        'valor': X_instance.iloc[0, idx] if isinstance(X_instance, pd.DataFrame) else X_instance[0, idx],
                        'impacto': shap_vals[idx],
                        'direcao': 'aumenta' if shap_vals[idx] > 0 else 'diminui'
                    })
        except:
            passar = True
    
    # Fallback: usar importância do modelo
    if len(explicacao['features_importantes']) == 0:
        if hasattr(modelo, 'feature_importances_'):
            importancias = modelo.feature_importances_
        elif hasattr(modelo, 'coef_'):
            classe_idx = list(modelo.classes_).index(y_pred)
            importancias = np.abs(modelo.coef_[classe_idx])
        else:
            importancias = np.ones(len(feature_names))
        
        # Top features
        top_indices = np.argsort(importancias)[::-1][:10]
        
        for idx in top_indices:
            valor = X_instance.iloc[0, idx] if isinstance(X_instance, pd.DataFrame) else X_instance[0, idx]
            explicacao['features_importantes'].append({
                'feature': feature_names[idx],
                'valor': valor,
                'importancia_global': importancias[idx]
            })
    
    return explicacao


def gerar_texto_explicacao(explicacao, diagnostico_real=None):
    """
    Gera texto explicativo em linguagem natural
    
    Args:
        explicacao: Dict com explicação
        diagnostico_real: Diagnóstico real (opcional, para comparação)
        
    Returns:
        String com explicação
    """
    texto = f"### 🔍 Explicação da Predição\n\n"
    
    texto += f"**Diagnóstico Predito:** {explicacao['predicao']}\n\n"
    
    # Probabilidades
    texto += "**Probabilidades:**\n"
    for classe, prob in sorted(explicacao['probabilidades'].items(), key=lambda x: x[1], reverse=True)[:3]:
        texto += f"- {classe}: {prob:.1%}\n"
    
    texto += "\n**Features Mais Influentes:**\n\n"
    
    for i, feat_info in enumerate(explicacao['features_importantes'][:5], 1):
        feature = feat_info['feature']
        valor = feat_info['valor']
        
        if 'impacto' in feat_info:
            impacto = feat_info['impacto']
            direcao = feat_info['direcao']
            texto += f"{i}. **{feature}** = {valor:.2f} → {direcao} probabilidade (impacto: {abs(impacto):.3f})\n"
        else:
            importancia = feat_info.get('importancia_global', 0)
            texto += f"{i}. **{feature}** = {valor:.2f} (importância global: {importancia:.3f})\n"
    
    if diagnostico_real and diagnostico_real != explicacao['predicao']:
        texto += f"\n⚠️ **Atenção:** Diagnóstico real ({diagnostico_real}) difere do predito.\n"
    
    return texto


def comparar_casos_similares(modelo, X_new, X_train, y_train, n_similares=5):
    """
    Encontra e compara casos similares no conjunto de treino
    
    Args:
        modelo: Modelo treinado
        X_new: Nova instância
        X_train: Features de treino
        y_train: Diagnósticos de treino
        n_similares: Número de casos similares a retornar
        
    Returns:
        DataFrame com casos similares
    """
    from sklearn.metrics.pairwise import cosine_similarity
    
    # Calcular similaridade
    similaridades = cosine_similarity(X_new, X_train)[0]
    
    # Top N mais similares
    indices_similares = np.argsort(similaridades)[::-1][:n_similares]
    
    df_similares = pd.DataFrame({
        'indice': indices_similares,
        'similaridade': similaridades[indices_similares],
        'diagnostico': y_train.iloc[indices_similares].values
    })
    
    return df_similares

