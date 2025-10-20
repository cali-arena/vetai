"""
Módulo de modelagem e treinamento de Machine Learning
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score, roc_curve
)
from sklearn.preprocessing import label_binarize, LabelEncoder
import streamlit as st

# Imports opcionais para modelos avançados
try:
    import lightgbm as lgb
    LIGHTGBM_DISPONIVEL = True
except ImportError:
    LIGHTGBM_DISPONIVEL = False

try:
    import xgboost as xgb
    XGBOOST_DISPONIVEL = True
except ImportError:
    XGBOOST_DISPONIVEL = False


def obter_modelos_disponiveis():
    """
    Retorna dicionário de modelos disponíveis
    
    Returns:
        dict: {nome: classe_do_modelo}
    """
    modelos = {
        'Logistic Regression': LogisticRegression,
        'Random Forest': RandomForestClassifier,
    }
    
    if LIGHTGBM_DISPONIVEL:
        modelos['LightGBM'] = lgb.LGBMClassifier
    
    if XGBOOST_DISPONIVEL:
        modelos['XGBoost'] = xgb.XGBClassifier
    
    return modelos


def obter_parametros_grid(nome_modelo):
    """
    Retorna grid de hiperparâmetros para o modelo
    
    Args:
        nome_modelo: Nome do modelo
        
    Returns:
        dict: Grid de parâmetros
    """
    if nome_modelo == 'Logistic Regression':
        return {
            'C': [0.1, 1.0, 10.0],
            'max_iter': [1000],
            'class_weight': ['balanced']
        }
    
    elif nome_modelo == 'Random Forest':
        return {
            'n_estimators': [100, 200],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5],
            'class_weight': ['balanced', 'balanced_subsample']
        }
    
    elif nome_modelo == 'LightGBM' and LIGHTGBM_DISPONIVEL:
        return {
            'n_estimators': [100, 200],
            'max_depth': [5, 10, -1],
            'learning_rate': [0.01, 0.1],
            'num_leaves': [31, 50],
            'class_weight': ['balanced']
        }
    
    elif nome_modelo == 'XGBoost' and XGBOOST_DISPONIVEL:
        return {
            'n_estimators': [100, 200],
            'max_depth': [3, 6, 10],
            'learning_rate': [0.01, 0.1],
            'scale_pos_weight': [1, 2, 5]  # Balanceamento
        }
    
    return {}


def treinar_modelo(X_train, y_train, nome_modelo='Random Forest', 
                   usar_grid_search=False, cv_folds=5, random_state=42):
    """
    Treina um modelo de classificação
    
    Args:
        X_train: Features de treino
        y_train: Target de treino
        nome_modelo: Nome do modelo a treinar
        usar_grid_search: Se True, usa GridSearchCV
        cv_folds: Número de folds para CV
        random_state: Seed
        
    Returns:
        modelo treinado, histórico de treinamento
    """
    # Codificar classes se necessário (XGBoost precisa de classes numéricas)
    label_encoder = None
    if isinstance(y_train.iloc[0] if hasattr(y_train, 'iloc') else y_train[0], str):
        label_encoder = LabelEncoder()
        y_train_encoded = label_encoder.fit_transform(y_train)
        classes_originais = label_encoder.classes_
    else:
        y_train_encoded = y_train
        classes_originais = np.unique(y_train)
    
    modelos_disponiveis = obter_modelos_disponiveis()
    
    if nome_modelo not in modelos_disponiveis:
        raise ValueError(f"Modelo '{nome_modelo}' não disponível")
    
    ModeloClasse = modelos_disponiveis[nome_modelo]
    
    historico = {
        'modelo': nome_modelo,
        'n_samples_treino': len(X_train),
        'n_features': X_train.shape[1],
        'classes': classes_originais.tolist(),
        'label_encoder': label_encoder
    }
    
    # Configurar modelo base
    if nome_modelo == 'Logistic Regression':
        modelo_base = ModeloClasse(random_state=random_state, max_iter=1000, class_weight='balanced')
    elif nome_modelo in ['Random Forest', 'LightGBM']:
        modelo_base = ModeloClasse(random_state=random_state, class_weight='balanced')
    elif nome_modelo == 'XGBoost':
        # XGBoost usa scale_pos_weight ao invés de class_weight
        modelo_base = ModeloClasse(
            random_state=random_state, 
            eval_metric='mlogloss',
            enable_categorical=False
        )
    else:
        modelo_base = ModeloClasse(random_state=random_state)
    
    # Grid Search ou treino direto
    if usar_grid_search:
        param_grid = obter_parametros_grid(nome_modelo)
        
        if param_grid:
            cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
            
            grid_search = GridSearchCV(
                modelo_base,
                param_grid,
                cv=cv,
                scoring='f1_macro',
                n_jobs=-1,
                verbose=0
            )
            
            grid_search.fit(X_train, y_train_encoded)
            
            modelo = grid_search.best_estimator_
            historico['melhores_parametros'] = grid_search.best_params_
            historico['melhor_score_cv'] = grid_search.best_score_
        else:
            modelo = modelo_base
            modelo.fit(X_train, y_train_encoded)
    else:
        modelo = modelo_base
        modelo.fit(X_train, y_train_encoded)
    
    # Validação cruzada
    cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
    
    cv_scores = cross_val_score(modelo, X_train, y_train_encoded, cv=cv, scoring='f1_macro')
    historico['cv_f1_mean'] = cv_scores.mean()
    historico['cv_f1_std'] = cv_scores.std()
    
    return modelo, historico


def avaliar_modelo(modelo, X_test, y_test, nomes_classes=None, label_encoder=None):
    """
    Avalia modelo no conjunto de teste
    
    Args:
        modelo: Modelo treinado
        X_test: Features de teste
        y_test: Target de teste
        nomes_classes: Nomes das classes (opcional)
        label_encoder: LabelEncoder usado no treinamento (opcional)
        
    Returns:
        dict com métricas de avaliação
    """
    # Codificar y_test se necessário
    if label_encoder is not None:
        y_test_encoded = label_encoder.transform(y_test)
    else:
        y_test_encoded = y_test
    
    # Predições
    y_pred = modelo.predict(X_test)
    y_proba = modelo.predict_proba(X_test)
    
    # Decodificar predições se necessário
    if label_encoder is not None:
        y_pred_decoded = label_encoder.inverse_transform(y_pred)
    else:
        y_pred_decoded = y_pred
    
    # Métricas básicas
    metricas = {
        'accuracy': accuracy_score(y_test_encoded, y_pred),
        'precision_macro': precision_score(y_test_encoded, y_pred, average='macro', zero_division=0),
        'recall_macro': recall_score(y_test_encoded, y_pred, average='macro', zero_division=0),
        'f1_macro': f1_score(y_test_encoded, y_pred, average='macro', zero_division=0),
        'precision_weighted': precision_score(y_test_encoded, y_pred, average='weighted', zero_division=0),
        'recall_weighted': recall_score(y_test_encoded, y_pred, average='weighted', zero_division=0),
        'f1_weighted': f1_score(y_test_encoded, y_pred, average='weighted', zero_division=0),
    }
    
    # Matriz de confusão
    metricas['confusion_matrix'] = confusion_matrix(y_test_encoded, y_pred)
    
    # Classification report
    if nomes_classes is None:
        if label_encoder is not None:
            nomes_classes = label_encoder.classes_
        else:
            nomes_classes = modelo.classes_
    
    metricas['classification_report'] = classification_report(
        y_test_encoded, y_pred, 
        target_names=nomes_classes,
        output_dict=True,
        zero_division=0
    )
    
    # ROC AUC (multiclasse - One vs Rest)
    try:
        if len(modelo.classes_) == 2:
            metricas['roc_auc'] = roc_auc_score(y_test_encoded, y_proba[:, 1])
        else:
            metricas['roc_auc'] = roc_auc_score(
                y_test_encoded, y_proba, 
                multi_class='ovr', 
                average='macro'
            )
    except:
        metricas['roc_auc'] = None
    
    # Predições e probabilidades para análise posterior
    metricas['y_pred'] = y_pred
    metricas['y_proba'] = y_proba
    
    return metricas


def obter_importancia_features(modelo, feature_names):
    """
    Extrai importância de features do modelo
    
    Args:
        modelo: Modelo treinado
        feature_names: Nomes das features
        
    Returns:
        DataFrame com importâncias ordenadas
    """
    # Verificar se o modelo tem importância de features
    if hasattr(modelo, 'feature_importances_'):
        importancias = modelo.feature_importances_
    elif hasattr(modelo, 'coef_'):
        # Para modelos lineares, usar valor absoluto dos coeficientes
        importancias = np.abs(modelo.coef_).mean(axis=0)
    else:
        return None
    
    # Criar DataFrame
    df_importancia = pd.DataFrame({
        'feature': feature_names,
        'importancia': importancias
    }).sort_values('importancia', ascending=False)
    
    return df_importancia


def calcular_roc_curves(modelo, X_test, y_test):
    """
    Calcula curvas ROC para cada classe
    
    Args:
        modelo: Modelo treinado
        X_test: Features de teste
        y_test: Target de teste
        
    Returns:
        dict com curvas ROC por classe
    """
    y_proba = modelo.predict_proba(X_test)
    classes = modelo.classes_
    
    roc_curves = {}
    
    if len(classes) == 2:
        # Binário
        fpr, tpr, thresholds = roc_curve(y_test, y_proba[:, 1], pos_label=classes[1])
        roc_curves[classes[1]] = {'fpr': fpr, 'tpr': tpr, 'thresholds': thresholds}
    else:
        # Multiclasse - One vs Rest
        y_test_bin = label_binarize(y_test, classes=classes)
        
        for i, classe in enumerate(classes):
            fpr, tpr, thresholds = roc_curve(y_test_bin[:, i], y_proba[:, i])
            roc_curves[classe] = {'fpr': fpr, 'tpr': tpr, 'thresholds': thresholds}
    
    return roc_curves


def salvar_modelo(modelo, preprocessadores, feature_names, caminho_base='models/modelo'):
    """
    Salva modelo e preprocessadores em disco
    
    Args:
        modelo: Modelo treinado
        preprocessadores: Dict com preprocessadores
        feature_names: Lista de nomes das features
        caminho_base: Caminho base (sem extensão)
        
    Returns:
        Caminho completo do arquivo salvo
    """
    # Criar diretório se não existir
    Path('models').mkdir(exist_ok=True)
    
    # Salvar modelo
    caminho_modelo = f"{caminho_base}.pkl"
    with open(caminho_modelo, 'wb') as f:
        pickle.dump({
            'modelo': modelo,
            'preprocessadores': preprocessadores,
            'feature_names': feature_names,
            'classes': modelo.classes_.tolist()
        }, f)
    
    return caminho_modelo


def carregar_modelo(caminho='models/modelo.pkl'):
    """
    Carrega modelo e preprocessadores do disco
    
    Args:
        caminho: Caminho do arquivo
        
    Returns:
        modelo, preprocessadores, feature_names, classes
    """
    if not Path(caminho).exists():
        return None, None, None, None
    
    with open(caminho, 'rb') as f:
        dados = pickle.load(f)
    
    return (
        dados['modelo'],
        dados['preprocessadores'],
        dados['feature_names'],
        dados['classes']
    )


def prever_diagnostico(modelo, X, preprocessadores, feature_names, top_n=3):
    """
    Faz predição de diagnóstico com probabilidades
    
    Args:
        modelo: Modelo treinado
        X: Features (pode ser DataFrame ou dict)
        preprocessadores: Dict com preprocessadores
        feature_names: Lista de features esperadas
        top_n: Número de diagnósticos a retornar
        
    Returns:
        Lista de dicts com diagnósticos e probabilidades
    """
    # Converter dict para DataFrame se necessário
    if isinstance(X, dict):
        X = pd.DataFrame([X])
    
    # Garantir que todas as features necessárias existem
    for feat in feature_names:
        if feat not in X.columns:
            X[feat] = 0  # Preencher com 0 se ausente
    
    # Reordenar colunas na ordem correta
    X = X[feature_names]
    
    # Aplicar preprocessamento
    from vetlib.preprocessing import aplicar_preprocessamento
    X_proc, _ = aplicar_preprocessamento(X, preprocessadores, fit=False)
    
    # Predizer
    probabilidades = modelo.predict_proba(X_proc)[0]
    classes = modelo.classes_
    
    # Ordenar por probabilidade
    indices_ordenados = np.argsort(probabilidades)[::-1][:top_n]
    
    resultados = []
    for idx in indices_ordenados:
        resultados.append({
            'diagnostico': classes[idx],
            'probabilidade': probabilidades[idx],
            'confianca': 'Alta' if probabilidades[idx] > 0.7 else 'Média' if probabilidades[idx] > 0.4 else 'Baixa'
        })
    
    return resultados


def avaliar_por_especie(modelo, X_test, y_test, especie_col, label_encoder=None):
    """
    Avalia modelo separadamente por espécie
    
    Args:
        modelo: Modelo treinado
        X_test: Features de teste (com coluna de espécie)
        y_test: Target de teste
        especie_col: DataFrame com coluna de espécie alinhado com X_test
        label_encoder: LabelEncoder usado no treinamento (opcional)
        
    Returns:
        dict com métricas por espécie
    """
    metricas_especies = {}
    
    especies_unicas = especie_col.unique()
    
    for especie in especies_unicas:
        mask = (especie_col == especie)
        
        if mask.sum() == 0:
            continue
        
        X_esp = X_test[mask]
        y_esp = y_test[mask]
        
        # Codificar y_esp se necessário
        if label_encoder is not None:
            y_esp_encoded = label_encoder.transform(y_esp)
        else:
            y_esp_encoded = y_esp
        
        # Avaliar
        y_pred_esp = modelo.predict(X_esp)
        
        metricas_especies[especie] = {
            'n_samples': mask.sum(),
            'accuracy': accuracy_score(y_esp_encoded, y_pred_esp),
            'f1_macro': f1_score(y_esp_encoded, y_pred_esp, average='macro', zero_division=0),
            'confusion_matrix': confusion_matrix(y_esp_encoded, y_pred_esp)
        }
    
    return metricas_especies


def balancear_classes(y_train):
    """
    Calcula pesos de classes para balanceamento
    
    Args:
        y_train: Target de treino
        
    Returns:
        dict com pesos de classes
    """
    from sklearn.utils.class_weight import compute_class_weight
    
    classes = np.unique(y_train)
    class_weights = compute_class_weight('balanced', classes=classes, y=y_train)
    
    return dict(zip(classes, class_weights))


def comparar_modelos(X_train, y_train, X_test, y_test, modelos_treinar=None):
    """
    Treina e compara múltiplos modelos
    
    Args:
        X_train, y_train: Dados de treino
        X_test, y_test: Dados de teste
        modelos_treinar: Lista de nomes de modelos (None = todos disponíveis)
        
    Returns:
        DataFrame com comparação de métricas
    """
    if modelos_treinar is None:
        modelos_treinar = list(obter_modelos_disponiveis().keys())
    
    resultados = []
    
    for nome_modelo in modelos_treinar:
        try:
            # Treinar
            modelo, historico = treinar_modelo(X_train, y_train, nome_modelo)
            
            # Avaliar
            metricas = avaliar_modelo(modelo, X_test, y_test, label_encoder=historico.get('label_encoder'))
            
            resultados.append({
                'Modelo': nome_modelo,
                'Accuracy': metricas['accuracy'],
                'F1 (Macro)': metricas['f1_macro'],
                'F1 (Weighted)': metricas['f1_weighted'],
                'Precision (Macro)': metricas['precision_macro'],
                'Recall (Macro)': metricas['recall_macro'],
                'ROC AUC': metricas['roc_auc']
            })
        except Exception as e:
            st.warning(f"Erro ao treinar {nome_modelo}: {str(e)}")
    
    df_comparacao = pd.DataFrame(resultados).sort_values('F1 (Macro)', ascending=False)
    
    return df_comparacao

