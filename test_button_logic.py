#!/usr/bin/env python3
"""
Teste simples para verificar se os botões estão funcionando
"""

import streamlit as st
from vetlib.simple_diagnosis import gerar_hipoteses_simples

st.set_page_config(page_title="Teste Botões", page_icon="🧪")

st.title("🧪 Teste de Lógica de Botões")

# Teste 1: Botão simples
st.markdown("### Teste 1: Botão Simples")
if st.button("✅ Teste Simples"):
    st.success("Botão simples funcionando!")
    
    # Teste do sistema
    sintomas = {'poliuria': 1, 'polidipsia': 1}
    exames = {'creatinina': 3.0, 'glicose': 20}
    especie = 'Canina'
    
    resultados = gerar_hipoteses_simples(sintomas, exames, especie)
    st.write(f"Sistema funcionando: {len(resultados)} resultados")
    
    for i, res in enumerate(resultados[:2], 1):
        st.write(f"{i}. {res['diagnostico']} - Score: {res['score']:.2f}")

# Teste 2: Múltiplos botões
st.markdown("### Teste 2: Múltiplos Botões")
col1, col2, col3 = st.columns(3)

with col1:
    btn1 = st.button("Botão 1", key="btn1")

with col2:
    btn2 = st.button("Botão 2", key="btn2")

with col3:
    btn3 = st.button("Botão 3", key="btn3")

if btn1:
    st.info("Botão 1 clicado!")
    sintomas = {'poliuria': 1, 'polidipsia': 1}
    exames = {'creatinina': 3.0, 'glicose': 20}
    especie = 'Canina'
    resultados = gerar_hipoteses_simples(sintomas, exames, especie)
    st.write(f"Resultados: {len(resultados)}")

if btn2:
    st.warning("Botão 2 clicado!")

if btn3:
    st.error("Botão 3 clicado!")

st.markdown("### Resultado:")
st.info("Se os botões funcionarem aqui, o problema não está na lógica básica do Streamlit.")


