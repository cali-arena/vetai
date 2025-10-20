"""
Script para criar modelo otimizado baseado no que já estava funcionando
Usa os dados reais e configurações que davam 77% de acurácia
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from datetime import datetime
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

def criar_modelo_otimizado():
    """Cria modelo otimizado baseado no que já estava funcionando"""
    print("🚀 Criando modelo otimizado...")
    
    # Carregar dados reais
    data_path = Path("data")
    csv_files = list(data_path.glob("*.csv"))
    
    # Priorizar datasets específicos
    datasets_prioritarios = [
        'veterinary_complete_real_dataset.csv',
        'veterinary_realistic_dataset.csv',
        'veterinary_master_dataset.csv', 
        'clinical_veterinary_data.csv',
        'laboratory_complete_panel.csv'
    ]
    
    df = None
    dataset_name = None
    
    for dataset_name in datasets_prioritarios:
        dataset_path = data_path / dataset_name
        if dataset_path.exists():
            df = pd.read_csv(dataset_path)
            if len(df) > 0:
                print(f"✅ Dataset carregado: {dataset_name} ({len(df)} registros)")
                break
    
    if df is None and csv_files:
        df = pd.read_csv(csv_files[0])
        dataset_name = csv_files[0].name
        print(f"✅ Dataset carregado: {dataset_name} ({len(df)} registros)")
    
    if df is None:
        print("❌ Nenhum dataset encontrado!")
        return
    
    # Preparar dados (baseado no que funcionava no app.py)
    df_ml = df.copy()
    
    # Codificação
    le_especie = LabelEncoder()
    le_sexo = LabelEncoder()
    le_diagnostico = LabelEncoder()
    
    if 'especie' in df_ml.columns:
        df_ml['especie_encoded'] = le_especie.fit_transform(df_ml['especie'])
    if 'sexo' in df_ml.columns:
        df_ml['sexo_encoded'] = le_sexo.fit_transform(df_ml['sexo'])
    
    df_ml['diagnostico_encoded'] = le_diagnostico.fit_transform(df_ml['diagnostico'])
    
    # Feature Engineering (baseado no que funcionava)
    if 'idade_anos' in df_ml.columns:
        try:
            df_ml['idade_categoria'] = pd.cut(df_ml['idade_anos'], bins=[0, 1, 3, 7, 12, 100], labels=['Filhote', 'Jovem', 'Adulto', 'Maduro', 'Idoso'])
            df_ml['idade_categoria_encoded'] = LabelEncoder().fit_transform(df_ml['idade_categoria'])
        except:
            df_ml['idade_categoria_encoded'] = (df_ml['idade_anos'] // 5).astype(int)
        
        # Features de idade
        try:
            df_ml['idade_quadrado'] = df_ml['idade_anos'] ** 2
            df_ml['idade_log'] = np.log1p(df_ml['idade_anos'])
            df_ml['idade_senior'] = (df_ml['idade_anos'] > 7).astype(int)
            df_ml['idade_filhote'] = (df_ml['idade_anos'] < 1).astype(int)
        except:
            pass
    
    # Features de sintomas
    sintoma_cols = ['febre', 'apatia', 'perda_peso', 'vomito', 'diarreia', 'tosse', 'letargia', 'feridas_cutaneas', 'poliuria', 'polidipsia']
    sintomas_presentes = [col for col in sintoma_cols if col in df_ml.columns]
    
    if sintomas_presentes:
        df_ml['total_sintomas'] = df_ml[sintomas_presentes].sum(axis=1)
        df_ml['severidade_sintomas'] = df_ml['total_sintomas'].apply(lambda x: 0 if x == 0 else 1 if x <= 2 else 2 if x <= 4 else 3)
    
    # Features laboratoriais
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
    
    # Dividir dados
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Escalar
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Modelo Gradient Boosting otimizado (baseado no que funcionava)
    gb_model = GradientBoostingClassifier(
        n_estimators=1000,
        learning_rate=0.01,
        max_depth=12,
        min_samples_split=2,
        min_samples_leaf=1,
        subsample=0.8,
        max_features='sqrt',
        random_state=42,
        validation_fraction=0.1,
        n_iter_no_change=50,
        tol=1e-4
    )
    
    print("🔄 Treinando modelo...")
    gb_model.fit(X_train_scaled, y_train)
    
    # Predições
    y_pred = gb_model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Validação cruzada
    cv_scores = cross_val_score(gb_model, X_train_scaled, y_train, cv=5)
    cv_mean = cv_scores.mean()
    cv_std = cv_scores.std()
    
    print(f"🎯 Acurácia: {accuracy:.4f} ({accuracy:.1%})")
    print(f"📊 CV Mean: {cv_mean:.4f} ± {cv_std:.4f}")
    
    # Salvar modelo
    model_data = {
        'model': gb_model,
        'scaler': scaler,
        'le_diagnostico': le_diagnostico,
        'le_especie': le_especie,
        'le_sexo': le_sexo,
        'accuracy': accuracy,
        'cv_mean': cv_mean,
        'cv_std': cv_std,
        'timestamp': datetime.now().isoformat(),
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'feature_names': numeric_cols
    }
    
    model_path = Path("models")
    model_path.mkdir(exist_ok=True)
    
    model_file = model_path / "gb_optimized_model.pkl"
    joblib.dump(model_data, model_file)
    
    print(f"✅ Modelo salvo em: {model_file}")
    print(f"🎉 Modelo pronto para uso nos apps!")
    
    return model_data

if __name__ == "__main__":
    criar_modelo_otimizado()
