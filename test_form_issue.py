#!/usr/bin/env python3
"""
Teste para verificar se o problema está no formulário Streamlit
"""

import streamlit as st
from vetlib.simple_diagnosis import gerar_hipoteses_simples

st.set_page_config(page_title="Teste Formulário", page_icon="🧪")

st.title("🧪 Teste de Formulário")

# Teste 1: Botão simples (fora do formulário)
st.markdown("### Teste 1: Botão Simples")
if st.button("✅ Teste Simples"):
    st.success("Botão simples funcionando!")
    
    # Teste do sistema
    sintomas = {'poliuria': 1, 'polidipsia': 1}
    exames = {'creatinina': 3.0, 'glicose': 20}
    especie = 'Canina'
    
    resultados = gerar_hipoteses_simples(sintomas, exames, especie)
    st.write(f"Sistema funcionando: {len(resultados)} resultados")

# Teste 2: Formulário simples
st.markdown("### Teste 2: Formulário Simples")
with st.form("teste_form"):
    nome = st.text_input("Nome do animal:")
    submit = st.form_submit_button("🔍 Testar Formulário")

if submit:
    st.success(f"Formulário funcionando! Nome: {nome}")
    
    # Teste do sistema dentro do submit
    sintomas = {'poliuria': 1, 'polidipsia': 1}
    exames = {'creatinina': 3.0, 'glicose': 20}
    especie = 'Canina'
    
    resultados = gerar_hipoteses_simples(sintomas, exames, especie)
    st.write(f"Sistema funcionando no formulário: {len(resultados)} resultados")

st.markdown("### Resultado do Teste:")
st.info("Se ambos os testes funcionarem, o problema não está no formulário básico do Streamlit.")


