"""
Script para carregar automaticamente o dataset master no Streamlit
"""

import streamlit as st
import pandas as pd
from pathlib import Path

def carregar_dataset_master():
    """Carrega automaticamente o dataset master"""
    
    # Caminho do dataset master
    caminho = Path('data/veterinary_master_dataset.csv')
    
    if caminho.exists():
        df = pd.read_csv(caminho)
        
        # Salvar no session_state
        st.session_state.df_main = df
        
        return df
    else:
        return None

if __name__ == "__main__":
    # Se executado diretamente, mostrar informações
    caminho = Path('data/veterinary_master_dataset.csv')
    
    if caminho.exists():
        df = pd.read_csv(caminho)
        print(f"✅ Dataset Master carregado: {len(df)} registros")
        print(f"📊 Colunas: {len(df.columns)}")
        print(f"🐾 Espécies: {df['especie'].value_counts().to_dict()}")
        print(f"🏥 Diagnósticos: {len(df['diagnostico'].unique())}")
    else:
        print("❌ Dataset Master não encontrado")


