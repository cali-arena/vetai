"""
Script para treinar o modelo Gradient Boosting separadamente
Execute este script para treinar o modelo que será usado no app de predição
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from datetime import datetime
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

def carregar_dados():
    """Carrega dados reais da pasta data"""
    print("🔄 Carregando dados...")
    
    data_path = Path("data")
    if not data_path.exists():
        raise FileNotFoundError("Pasta 'data' não encontrada!")
    
    csv_files = list(data_path.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError("Nenhum arquivo CSV encontrado na pasta 'data'!")
    
    # Priorizar datasets específicos
    datasets_prioritarios = [
        'veterinary_complete_real_dataset.csv',
        'veterinary_master_dataset.csv', 
        'veterinary_realistic_dataset.csv',
        'clinical_veterinary_data.csv',
        'laboratory_complete_panel.csv'
    ]
    
    for dataset_name in datasets_prioritarios:
        dataset_path = data_path / dataset_name
        if dataset_path.exists():
            df = pd.read_csv(dataset_path)
            if len(df) > 0:
                print(f"✅ Dataset carregado: {dataset_name} ({len(df)} registros)")
                return df, dataset_name
    
    # Se não encontrar os prioritários, usar qualquer CSV
    if csv_files:
        df = pd.read_csv(csv_files[0])
        print(f"✅ Dataset carregado: {csv_files[0].name} ({len(df)} registros)")
        return df, csv_files[0].name
    
    raise FileNotFoundError("Nenhum dataset válido encontrado!")

def preparar_dados(df):
    """Prepara dados para treinamento"""
    print("🔄 Preparando dados...")
    
    df_ml = df.copy()
    
    # Verificar se tem coluna de diagnóstico
    if 'diagnostico' not in df_ml.columns:
        raise ValueError("Coluna 'diagnostico' não encontrada!")
    
    # Codificação de variáveis categóricas
    le_especie = LabelEncoder()
    le_sexo = LabelEncoder()
    le_diagnostico = LabelEncoder()
    
    if 'especie' in df_ml.columns:
        df_ml['especie_encoded'] = le_especie.fit_transform(df_ml['especie'])
    if 'sexo' in df_ml.columns:
        df_ml['sexo_encoded'] = le_sexo.fit_transform(df_ml['sexo'])
    
    df_ml['diagnostico_encoded'] = le_diagnostico.fit_transform(df_ml['diagnostico'])
    
    # Feature Engineering Avançado
    print("🔧 Criando features avançadas...")
    
    # Features de idade
    if 'idade_anos' in df_ml.columns:
        # Categorização de idade
        df_ml['idade_categoria'] = pd.cut(
            df_ml['idade_anos'], 
            bins=[0, 1, 3, 7, 12, 100], 
            labels=[0, 1, 2, 3, 4]
        ).astype(int)
        
        # Features derivadas de idade
        df_ml['idade_senior'] = (df_ml['idade_anos'] > 7).astype(int)
        df_ml['idade_filhote'] = (df_ml['idade_anos'] < 1).astype(int)
        df_ml['idade_quadrado'] = df_ml['idade_anos'] ** 2
        df_ml['idade_log'] = np.log1p(df_ml['idade_anos'])
    
    # Features de sintomas
    sintoma_cols = [
        'febre', 'apatia', 'perda_peso', 'vomito', 'diarreia', 
        'tosse', 'letargia', 'feridas_cutaneas', 'poliuria', 'polidipsia'
    ]
    
    sintomas_presentes = [col for col in sintoma_cols if col in df_ml.columns]
    if sintomas_presentes:
        df_ml['total_sintomas'] = df_ml[sintomas_presentes].sum(axis=1)
        df_ml['severidade_sintomas'] = df_ml['total_sintomas'].apply(
            lambda x: 0 if x == 0 else 1 if x <= 2 else 2 if x <= 4 else 3
        )
    
    # Features laboratoriais combinadas
    if 'hemoglobina' in df_ml.columns and 'hematocrito' in df_ml.columns:
        df_ml['indice_anemia'] = (df_ml['hemoglobina'] < 12).astype(int)
        df_ml['indice_policitemia'] = (df_ml['hematocrito'] > 50).astype(int)
    
    if 'ureia' in df_ml.columns and 'creatinina' in df_ml.columns:
        df_ml['indice_renal'] = ((df_ml['ureia'] > 40) | (df_ml['creatinina'] > 1.5)).astype(int)
    
    if 'alt' in df_ml.columns:
        df_ml['indice_hepatico'] = (df_ml['alt'] > 100).astype(int)
    
    # Selecionar features numéricas
    numeric_cols = df_ml.select_dtypes(include=[np.number]).columns.tolist()
    if 'diagnostico_encoded' in numeric_cols:
        numeric_cols.remove('diagnostico_encoded')
    
    X = df_ml[numeric_cols].fillna(0)
    y = df_ml['diagnostico_encoded']
    
    print(f"✅ Features preparadas: {X.shape[1]} features, {X.shape[0]} amostras")
    print(f"✅ Classes de diagnóstico: {len(le_diagnostico.classes_)}")
    
    return X, y, le_especie, le_sexo, le_diagnostico, numeric_cols

def treinar_modelo(X, y, cv_folds=5, random_state=42):
    """Treina o modelo Gradient Boosting otimizado"""
    print("🔄 Treinando modelo...")
    
    # Dividir dados
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )
    
    print(f"📊 Divisão: {X_train.shape[0]} treino, {X_test.shape[0]} teste")
    
    # Escalar features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Seleção de features
    print("🎯 Selecionando melhores features...")
    k_best = min(50, X.shape[1])
    selector = SelectKBest(score_func=f_classif, k=k_best)
    X_train_selected = selector.fit_transform(X_train_scaled, y_train)
    X_test_selected = selector.transform(X_test_scaled)
    
    print(f"✅ {k_best} features selecionadas de {X.shape[1]}")
    
    # Otimização de hiperparâmetros
    print("⚙️ Otimizando hiperparâmetros...")
    
    param_grid = {
        'n_estimators': [800, 1000, 1200, 1500],
        'learning_rate': [0.005, 0.01, 0.02, 0.03],
        'max_depth': [10, 12, 15, 18],
        'min_samples_split': [2, 3, 5],
        'subsample': [0.7, 0.8, 0.9],
        'max_features': ['sqrt', 'log2', 0.8]
    }
    
    gb_base = GradientBoostingClassifier(random_state=random_state)
    random_search = RandomizedSearchCV(
        gb_base, param_grid, n_iter=30, cv=cv_folds, 
        scoring='accuracy', random_state=random_state, n_jobs=-1
    )
    
    random_search.fit(X_train_selected, y_train)
    
    print(f"✅ Melhores parâmetros encontrados: {random_search.best_score_:.4f}")
    print(f"📊 Parâmetros: {random_search.best_params_}")
    
    # Treinar modelo final
    modelo_final = random_search.best_estimator_
    
    # Predições
    y_pred = modelo_final.predict(X_test_selected)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Validação cruzada
    cv_scores = cross_val_score(modelo_final, X_train_selected, y_train, cv=cv_folds)
    cv_mean = cv_scores.mean()
    cv_std = cv_scores.std()
    
    print(f"🎯 Acurácia final: {accuracy:.4f} ({accuracy:.1%})")
    print(f"📊 CV Mean: {cv_mean:.4f} ± {cv_std:.4f}")
    
    return modelo_final, scaler, selector, accuracy, cv_mean, cv_std, X_train.shape[0], X_test.shape[0]

def salvar_modelo(modelo, scaler, selector, le_especie, le_sexo, le_diagnostico, 
                  accuracy, cv_mean, cv_std, train_samples, test_samples, 
                  feature_names, dataset_name):
    """Salva o modelo treinado"""
    print("💾 Salvando modelo...")
    
    model_data = {
        'model': modelo,
        'scaler': scaler,
        'selector': selector,
        'le_especie': le_especie,
        'le_sexo': le_sexo,
        'le_diagnostico': le_diagnostico,
        'accuracy': accuracy,
        'cv_mean': cv_mean,
        'cv_std': cv_std,
        'timestamp': datetime.now().isoformat(),
        'training_samples': train_samples,
        'test_samples': test_samples,
        'feature_names': feature_names,
        'dataset_name': dataset_name,
        'model_type': 'GradientBoostingClassifier'
    }
    
    model_path = Path("models")
    model_path.mkdir(exist_ok=True)
    
    model_file = model_path / "gb_optimized_model.pkl"
    joblib.dump(model_data, model_file)
    
    print(f"✅ Modelo salvo em: {model_file}")
    
    # Salvar também informações detalhadas
    info_file = model_path / "model_info.txt"
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(f"=== VETDIAGNOSIS AI - INFORMAÇÕES DO MODELO ===\n\n")
        f.write(f"Data de Treinamento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Dataset Usado: {dataset_name}\n")
        f.write(f"Tipo de Modelo: GradientBoostingClassifier\n")
        f.write(f"Acurácia: {accuracy:.4f} ({accuracy:.1%})\n")
        f.write(f"CV Mean: {cv_mean:.4f} ± {cv_std:.4f}\n")
        f.write(f"Amostras de Treino: {train_samples:,}\n")
        f.write(f"Amostras de Teste: {test_samples:,}\n")
        f.write(f"Features Usadas: {len(feature_names)}\n")
        f.write(f"Classes de Diagnóstico: {len(le_diagnostico.classes_)}\n\n")
        
        f.write("Classes de Diagnóstico:\n")
        for i, classe in enumerate(le_diagnostico.classes_):
            f.write(f"  {i}: {classe}\n")
        
        f.write(f"\nFeatures Selecionadas:\n")
        for i, feature in enumerate(feature_names[:20]):  # Primeiras 20
            f.write(f"  {i}: {feature}\n")
        if len(feature_names) > 20:
            f.write(f"  ... e mais {len(feature_names) - 20} features\n")
    
    print(f"📋 Informações detalhadas salvas em: {info_file}")

def main():
    """Função principal"""
    print("🚀 VETDIAGNOSIS AI - TREINAMENTO DO MODELO")
    print("=" * 50)
    
    try:
        # 1. Carregar dados
        df, dataset_name = carregar_dados()
        
        # 2. Preparar dados
        X, y, le_especie, le_sexo, le_diagnostico, feature_names = preparar_dados(df)
        
        # 3. Treinar modelo
        modelo, scaler, selector, accuracy, cv_mean, cv_std, train_samples, test_samples = treinar_modelo(X, y)
        
        # 4. Salvar modelo
        salvar_modelo(modelo, scaler, selector, le_especie, le_sexo, le_diagnostico,
                     accuracy, cv_mean, cv_std, train_samples, test_samples,
                     feature_names, dataset_name)
        
        # 5. Status final
        print("\n" + "=" * 50)
        print("🎉 TREINAMENTO CONCLUÍDO COM SUCESSO!")
        print("=" * 50)
        
        if accuracy >= 0.85:
            print(f"🎯 META ALCANÇADA! Acurácia de {accuracy:.1%} >= 85%!")
        elif accuracy >= 0.75:
            print(f"⚠️  Acurácia aceitável: {accuracy:.1%}")
        else:
            print(f"❌ Acurácia baixa: {accuracy:.1%} - Considere mais dados ou feature engineering")
        
        print(f"\n📊 Resumo:")
        print(f"   • Acurácia: {accuracy:.1%}")
        print(f"   • CV Mean: {cv_mean:.3f} ± {cv_std:.3f}")
        print(f"   • Amostras: {train_samples:,} treino + {test_samples:,} teste")
        print(f"   • Features: {len(feature_names)}")
        print(f"   • Classes: {len(le_diagnostico.classes_)}")
        
        print(f"\n✅ Modelo pronto para uso no app de predição!")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        print("\nVerifique se:")
        print("   • A pasta 'data' existe")
        print("   • Há arquivos CSV na pasta 'data'")
        print("   • Os dados têm a coluna 'diagnostico'")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
