"""
Arquivo de deploy específico para Streamlit Cloud
Este arquivo garante que o app seja executado corretamente na nuvem
"""

import streamlit as st
import sys
import os

# Adicionar o diretório VET ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar o app principal
from app_simple import *

if __name__ == "__main__":
    st.info("🚀 **VET DIAGNOSIS AI v2.0 - DEPLOY STREAMLIT CLOUD** 🚀")
    st.info("✅ Sistema de ML veterinário completo carregado!")
