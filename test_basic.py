"""
Script de teste básico para verificar funcionalidades principais
"""

import pandas as pd
from pathlib import Path

print("=" * 60)
print("🧪 TESTE BÁSICO - VetDiagnosisAI")
print("=" * 60)

# 1. Testar importação de módulos
print("\n1️⃣ Testando importação de módulos...")
try:
    from vetlib import data_io, preprocessing, modeling, explain, insights
    print("   ✅ Todos os módulos importados com sucesso")
except Exception as e:
    print(f"   ❌ Erro na importação: {e}")
    exit(1)

# 2. Verificar dataset de exemplo
print("\n2️⃣ Verificando dataset de exemplo...")
dataset_path = Path('data/exemplo_vet.csv')
if dataset_path.exists():
    df = pd.read_csv(dataset_path)
    print(f"   ✅ Dataset encontrado: {len(df)} registros, {len(df.columns)} colunas")
    print(f"   📊 Espécies: {df['especie'].value_counts().to_dict()}")
    print(f"   🏥 Diagnósticos: {len(df['diagnostico'].unique())} únicos")
else:
    print("   ❌ Dataset de exemplo não encontrado")
    exit(1)

# 3. Testar funções básicas
print("\n3️⃣ Testando funções básicas...")

try:
    # data_io
    info = data_io.obter_info_dataset(df)
    print(f"   ✅ data_io.obter_info_dataset: OK")
    
    # preprocessing
    X, y, feature_names = preprocessing.preparar_features_target(df, target_col='diagnostico')
    print(f"   ✅ preprocessing.preparar_features_target: {len(feature_names)} features")
    
    # insights
    insights_list = insights.gerar_insights_dataset(df)
    print(f"   ✅ insights.gerar_insights_dataset: {len(insights_list)} insights")
    
except Exception as e:
    print(f"   ❌ Erro nas funções: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# 4. Testar treinamento rápido
print("\n4️⃣ Testando treinamento de modelo...")
try:
    from sklearn.model_selection import train_test_split
    
    # Preparar dados
    X, y, feature_names = preprocessing.preparar_features_target(df, target_col='diagnostico')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Preprocessar
    preprocessadores = preprocessing.criar_preprocessador(X_train)
    X_train_proc, preprocessadores = preprocessing.aplicar_preprocessamento(X_train, preprocessadores, fit=True)
    X_test_proc, _ = preprocessing.aplicar_preprocessamento(X_test, preprocessadores, fit=False)
    
    # Treinar modelo simples
    modelo, historico = modeling.treinar_modelo(
        X_train_proc, y_train,
        nome_modelo='Logistic Regression',
        usar_grid_search=False,
        cv_folds=3,
        random_state=42
    )
    
    print(f"   ✅ Modelo treinado com sucesso")
    print(f"   📊 CV F1 Score: {historico['cv_f1_mean']:.3f} ± {historico['cv_f1_std']:.3f}")
    
    # Avaliar
    metricas = modeling.avaliar_modelo(modelo, X_test_proc, y_test)
    print(f"   📈 Test Accuracy: {metricas['accuracy']:.3f}")
    print(f"   📈 Test F1 (Macro): {metricas['f1_macro']:.3f}")
    
except Exception as e:
    print(f"   ❌ Erro no treinamento: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# 5. Testar predição
print("\n5️⃣ Testando predição...")
try:
    # Pegar primeira amostra
    amostra = df.iloc[0].to_dict()
    
    resultados = modeling.prever_diagnostico(
        modelo,
        amostra,
        preprocessadores,
        feature_names,
        top_n=3
    )
    
    print(f"   ✅ Predição realizada com sucesso")
    print(f"   🏥 Top 3 diagnósticos:")
    for i, res in enumerate(resultados, 1):
        print(f"      {i}. {res['diagnostico']}: {res['probabilidade']:.1%}")
    
except Exception as e:
    print(f"   ❌ Erro na predição: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
print("=" * 60)
print("\n🚀 Execute o aplicativo com: streamlit run app.py")
print("=" * 60)



