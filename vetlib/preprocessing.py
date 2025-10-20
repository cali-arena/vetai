"""
Módulo de pré-processamento de dados
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import mutual_info_classif
import streamlit as st


# Faixas de referência por espécie (simplificadas)
FAIXAS_REFERENCIA = {
    'Canina': {
        'hemoglobina': (12, 18),
        'hematocrito': (37, 55),
        'leucocitos': (6, 17),
        'plaquetas': (200, 500),
        'glicose': (70, 120),
        'ureia': (20, 50),
        'creatinina': (0.5, 1.6),
        'alt': (10, 100),
        'ast': (15, 50),
        'fosfatase_alcalina': (20, 150),
        'proteinas_totais': (5.4, 7.5),
        'albumina': (2.5, 3.8),
        'colesterol': (130, 270),
        'triglicerideos': (20, 150)
    },
    'Felina': {
        'hemoglobina': (9, 15),
        'hematocrito': (30, 45),
        'leucocitos': (5.5, 19.5),
        'plaquetas': (300, 700),
        'glicose': (70, 150),
        'ureia': (30, 60),
        'creatinina': (0.8, 2.0),
        'alt': (10, 80),
        'ast': (10, 50),
        'fosfatase_alcalina': (10, 80),
        'proteinas_totais': (6.0, 8.5),
        'albumina': (2.5, 3.9),
        'colesterol': (90, 200),
        'triglicerideos': (25, 100)
    },
    'Equina': {
        'hemoglobina': (11, 19),
        'hematocrito': (32, 53),
        'leucocitos': (5.5, 12.5),
        'plaquetas': (100, 600),
        'glicose': (75, 115),
        'ureia': (21, 51),
        'creatinina': (1.0, 2.0),
        'alt': (3, 20),
        'ast': (138, 409),
        'fosfatase_alcalina': (143, 395),
        'proteinas_totais': (5.9, 7.9),
        'albumina': (2.6, 3.7),
        'colesterol': (75, 150),
        'triglicerideos': (4, 44)
    }
}


def verificar_valores_referencia(df, especie=None):
    """
    Verifica quais valores estão fora da faixa de referência
    
    Args:
        df: DataFrame com exames
        especie: Espécie específica (se None, usa coluna 'especie')
        
    Returns:
        DataFrame com flags de valores anormais
    """
    df_flags = pd.DataFrame(index=df.index)
    
    if especie is None and 'especie' not in df.columns:
        return df_flags
    
    for exame in FAIXAS_REFERENCIA['Canina'].keys():
        if exame not in df.columns:
            continue
        
        df_flags[f'{exame}_status'] = 'normal'
        
        for idx, row in df.iterrows():
            esp = especie if especie else row.get('especie', 'Canina')
            
            if esp not in FAIXAS_REFERENCIA:
                continue
            
            valor = row[exame]
            if pd.isna(valor):
                df_flags.loc[idx, f'{exame}_status'] = 'ausente'
                continue
            
            min_ref, max_ref = FAIXAS_REFERENCIA[esp][exame]
            
            if valor < min_ref:
                df_flags.loc[idx, f'{exame}_status'] = 'baixo'
            elif valor > max_ref:
                df_flags.loc[idx, f'{exame}_status'] = 'alto'
    
    return df_flags


def criar_features_anormalidade(df):
    """
    Cria features indicando se valores estão fora da faixa de referência
    
    Args:
        df: DataFrame original
        
    Returns:
        DataFrame com features adicionais
    """
    df_novo = df.copy()
    
    if 'especie' not in df.columns:
        return df_novo
    
    for exame in FAIXAS_REFERENCIA['Canina'].keys():
        if exame not in df.columns:
            continue
        
        # Features: abaixo, dentro, acima da referência
        df_novo[f'{exame}_baixo'] = 0
        df_novo[f'{exame}_alto'] = 0
        
        for idx, row in df.iterrows():
            esp = row.get('especie', 'Canina')
            
            if esp not in FAIXAS_REFERENCIA:
                continue
            
            valor = row[exame]
            if pd.isna(valor):
                continue
            
            min_ref, max_ref = FAIXAS_REFERENCIA[esp][exame]
            
            if valor < min_ref:
                df_novo.loc[idx, f'{exame}_baixo'] = 1
            elif valor > max_ref:
                df_novo.loc[idx, f'{exame}_alto'] = 1
    
    return df_novo


def preparar_features_target(df, target_col='diagnostico', incluir_features_anormalidade=False):
    """
    Separa features (X) e target (y), removendo colunas não-feature
    
    Args:
        df: DataFrame completo
        target_col: Nome da coluna target
        incluir_features_anormalidade: Se True, cria features de anormalidade
        
    Returns:
        X (DataFrame), y (Series), lista de nomes de features
    """
    df_proc = df.copy()
    
    # Adicionar features de anormalidade se solicitado
    if incluir_features_anormalidade:
        df_proc = criar_features_anormalidade(df_proc)
    
    # Colunas a remover (não são features)
    colunas_remover = ['id', 'data', target_col]
    colunas_remover = [c for c in colunas_remover if c in df_proc.columns]
    
    # Separar target
    if target_col in df_proc.columns:
        y = df_proc[target_col].copy()
    else:
        y = None
    
    # Remover target e colunas não-feature
    X = df_proc.drop(columns=colunas_remover, errors='ignore')
    
    # Lista de features
    feature_names = X.columns.tolist()
    
    return X, y, feature_names


def criar_preprocessador(X, colunas_numericas=None, colunas_categoricas=None):
    """
    Cria objetos de pré-processamento (imputer e scaler)
    
    Args:
        X: DataFrame de features
        colunas_numericas: Lista de colunas numéricas (auto-detecta se None)
        colunas_categoricas: Lista de colunas categóricas (auto-detecta se None)
        
    Returns:
        dict com imputers e scalers
    """
    if colunas_numericas is None:
        colunas_numericas = X.select_dtypes(include=[np.number]).columns.tolist()
    
    if colunas_categoricas is None:
        colunas_categoricas = X.select_dtypes(include=['object', 'category']).columns.tolist()
    
    preprocessadores = {
        'imputer_numerico': SimpleImputer(strategy='median'),
        'imputer_categorico': SimpleImputer(strategy='most_frequent'),
        'scaler': StandardScaler(),
        'label_encoders': {},
        'colunas_numericas': colunas_numericas,
        'colunas_categoricas': colunas_categoricas
    }
    
    return preprocessadores


def aplicar_preprocessamento(X, preprocessadores, fit=True):
    """
    Aplica pré-processamento aos dados
    
    Args:
        X: DataFrame de features
        preprocessadores: Dict com objetos de pré-processamento
        fit: Se True, ajusta os preprocessadores; se False, apenas transforma
        
    Returns:
        DataFrame transformado, preprocessadores atualizados
    """
    X_proc = X.copy()
    
    colunas_num = preprocessadores['colunas_numericas']
    colunas_cat = preprocessadores['colunas_categoricas']
    
    # Filtrar colunas que existem em X
    colunas_num = [c for c in colunas_num if c in X_proc.columns]
    colunas_cat = [c for c in colunas_cat if c in X_proc.columns]
    
    # Imputação numérica
    if len(colunas_num) > 0:
        if fit:
            X_proc[colunas_num] = preprocessadores['imputer_numerico'].fit_transform(X_proc[colunas_num])
        else:
            X_proc[colunas_num] = preprocessadores['imputer_numerico'].transform(X_proc[colunas_num])
    
    # Imputação categórica e encoding
    if len(colunas_cat) > 0:
        if fit:
            X_proc[colunas_cat] = preprocessadores['imputer_categorico'].fit_transform(X_proc[colunas_cat])
        else:
            X_proc[colunas_cat] = preprocessadores['imputer_categorico'].transform(X_proc[colunas_cat])
        
        # Label encoding para cada coluna categórica
        for col in colunas_cat:
            if fit:
                le = LabelEncoder()
                X_proc[col] = le.fit_transform(X_proc[col].astype(str))
                preprocessadores['label_encoders'][col] = le
            else:
                le = preprocessadores['label_encoders'][col]
                # Tratar valores desconhecidos
                X_proc[col] = X_proc[col].apply(lambda x: x if x in le.classes_ else 'desconhecido')
                # Adicionar 'desconhecido' às classes se necessário
                if 'desconhecido' not in le.classes_:
                    le.classes_ = np.append(le.classes_, 'desconhecido')
                X_proc[col] = le.transform(X_proc[col].astype(str))
    
    # Escalonamento de todas as features numéricas finais
    if fit:
        X_proc[X_proc.columns] = preprocessadores['scaler'].fit_transform(X_proc)
    else:
        X_proc[X_proc.columns] = preprocessadores['scaler'].transform(X_proc)
    
    return X_proc, preprocessadores


def selecionar_features_importantes(X, y, n_features=None, threshold=0.01):
    """
    Seleciona features mais importantes usando mutual information
    
    Args:
        X: DataFrame de features
        y: Target
        n_features: Número de features a selecionar (None = todas acima do threshold)
        threshold: Threshold mínimo de importância
        
    Returns:
        Lista de features selecionadas, scores de importância
    """
    # Calcular mutual information
    mi_scores = mutual_info_classif(X, y, random_state=42)
    
    # Criar DataFrame com scores
    feature_scores = pd.DataFrame({
        'feature': X.columns,
        'score': mi_scores
    }).sort_values('score', ascending=False)
    
    # Filtrar por threshold
    feature_scores_filtrado = feature_scores[feature_scores['score'] >= threshold]
    
    # Selecionar top N se especificado
    if n_features is not None:
        feature_scores_filtrado = feature_scores_filtrado.head(n_features)
    
    features_selecionadas = feature_scores_filtrado['feature'].tolist()
    
    return features_selecionadas, feature_scores


def criar_features_interacao(df, features_base=None):
    """
    Cria features de interação entre variáveis importantes
    
    Args:
        df: DataFrame
        features_base: Lista de features para criar interações (None = todas numéricas)
        
    Returns:
        DataFrame com features de interação adicionadas
    """
    df_inter = df.copy()
    
    if features_base is None:
        features_base = df.select_dtypes(include=[np.number]).columns.tolist()[:5]  # Top 5
    
    # Criar algumas interações importantes
    interacoes = [
        ('creatinina', 'ureia'),  # Função renal
        ('alt', 'ast'),  # Função hepática
        ('hemoglobina', 'hematocrito'),  # Anemia
        ('glicose', 'ureia'),  # Diabetes x renal
    ]
    
    for feat1, feat2 in interacoes:
        if feat1 in df_inter.columns and feat2 in df_inter.columns:
            # Produto
            df_inter[f'{feat1}_x_{feat2}'] = df_inter[feat1] * df_inter[feat2]
            # Razão (evitar divisão por zero)
            df_inter[f'{feat1}_div_{feat2}'] = df_inter[feat1] / (df_inter[feat2] + 1e-8)
    
    return df_inter


def obter_estatisticas_exame(df, exame, por_especie=True):
    """
    Retorna estatísticas descritivas de um exame
    
    Args:
        df: DataFrame
        exame: Nome do exame
        por_especie: Se True, agrupa por espécie
        
    Returns:
        DataFrame ou Series com estatísticas
    """
    if exame not in df.columns:
        return None
    
    if por_especie and 'especie' in df.columns:
        stats = df.groupby('especie')[exame].describe()
    else:
        stats = df[exame].describe()
    
    return stats


def identificar_outliers(df, coluna, metodo='iqr', threshold=1.5):
    """
    Identifica outliers em uma coluna numérica
    
    Args:
        df: DataFrame
        coluna: Nome da coluna
        metodo: 'iqr' ou 'zscore'
        threshold: Threshold para detecção (1.5 para IQR, 3 para z-score)
        
    Returns:
        Boolean mask de outliers
    """
    if coluna not in df.columns:
        return pd.Series([False] * len(df), index=df.index)
    
    valores = df[coluna].dropna()
    
    if metodo == 'iqr':
        Q1 = valores.quantile(0.25)
        Q3 = valores.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - threshold * IQR
        upper = Q3 + threshold * IQR
        return (df[coluna] < lower) | (df[coluna] > upper)
    
    elif metodo == 'zscore':
        mean = valores.mean()
        std = valores.std()
        z_scores = np.abs((df[coluna] - mean) / std)
        return z_scores > threshold
    
    return pd.Series([False] * len(df), index=df.index)


def resumo_dados_faltantes(df):
    """
    Gera resumo de dados faltantes
    
    Args:
        df: DataFrame
        
    Returns:
        DataFrame com informações de missingness
    """
    missing = df.isnull().sum()
    missing_pct = 100 * missing / len(df)
    
    resumo = pd.DataFrame({
        'coluna': missing.index,
        'n_faltantes': missing.values,
        'pct_faltantes': missing_pct.values
    })
    
    resumo = resumo[resumo['n_faltantes'] > 0].sort_values('n_faltantes', ascending=False)
    
    return resumo

