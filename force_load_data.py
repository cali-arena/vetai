"""
Script para forçar carregamento do dataset
Executa automaticamente quando necessário
"""

import sys
from pathlib import Path

# Adicionar path da biblioteca
sys.path.insert(0, str(Path(__file__).parent))

def carregar_dataset_force():
    """Força o carregamento do dataset"""
    try:
        from vetlib.data_io import carregar_dataset_exemplo
        df = carregar_dataset_exemplo()
        
        if df is not None:
            print(f"✅ Dataset carregado com sucesso: {len(df)} registros")
            print(f"📋 Colunas: {len(df.columns)}")
            if 'diagnostico' in df.columns:
                print(f"🏥 Diagnósticos: {df['diagnostico'].nunique()}")
            if 'especie' in df.columns:
                print(f"🐾 Espécies: {df['especie'].nunique()}")
            return df
        else:
            print("❌ Erro: Dataset não pôde ser carregado")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao carregar dataset: {str(e)}")
        return None

if __name__ == "__main__":
    print("🔄 Forçando carregamento do dataset...")
    df = carregar_dataset_force()
    
    if df is not None:
        print("✅ Dataset carregado e pronto para uso!")
    else:
        print("❌ Falha no carregamento do dataset")