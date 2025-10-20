#!/usr/bin/env python3
"""
Script de teste para verificar se os datasets estão sendo encontrados corretamente
"""

import pandas as pd
from pathlib import Path

def test_datasets():
    """Testa se os datasets estão sendo encontrados"""
    print("🔍 Testando carregamento de datasets...")
    
    # Verificar pasta data
    data_path = Path("data")
    print(f"📁 Pasta data existe: {data_path.exists()}")
    
    if data_path.exists():
        csv_files = list(data_path.glob("*.csv"))
        print(f"📊 Arquivos CSV encontrados: {len(csv_files)}")
        
        for csv_file in csv_files:
            print(f"  - {csv_file.name}")
            
            # Tentar carregar o arquivo
            try:
                df = pd.read_csv(csv_file)
                print(f"    ✅ Carregado: {len(df)} registros, {len(df.columns)} colunas")
                
                # Mostrar algumas colunas
                if len(df.columns) > 0:
                    print(f"    📋 Colunas: {', '.join(df.columns[:5])}")
                
            except Exception as e:
                print(f"    ❌ Erro ao carregar: {e}")
    
    else:
        print("❌ Pasta data não encontrada!")
    
    # Testar priorização
    datasets_prioritarios = [
        'veterinary_complete_real_dataset.csv',
        'veterinary_master_dataset.csv', 
        'veterinary_realistic_dataset.csv',
        'clinical_veterinary_data.csv',
        'laboratory_complete_panel.csv'
    ]
    
    print("\n🎯 Testando priorização de datasets...")
    dataset_escolhido = None
    
    for dataset in datasets_prioritarios:
        dataset_path = data_path / dataset
        if dataset_path.exists():
            dataset_escolhido = dataset_path
            print(f"✅ Dataset prioritário encontrado: {dataset}")
            break
    
    if dataset_escolhido:
        df = pd.read_csv(dataset_escolhido)
        print(f"📊 Dataset final: {dataset_escolhido.name}")
        print(f"📈 Registros: {len(df)}")
        print(f"📋 Colunas: {len(df.columns)}")
        print(f"🏥 Diagnósticos únicos: {df['diagnostico'].nunique() if 'diagnostico' in df.columns else 'N/A'}")
        print(f"🐾 Espécies únicas: {df['especie'].nunique() if 'especie' in df.columns else 'N/A'}")
    else:
        print("❌ Nenhum dataset prioritário encontrado!")

if __name__ == "__main__":
    test_datasets()
