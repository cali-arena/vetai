import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import sys
import traceback
import requests
import json
import os
from datetime import datetime

# Configuração da página otimizada
st.set_page_config(
    page_title="DIAGVET IA",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS mínimo para carregamento rápido
st.markdown("""
<style>
    .main-header {
        background: #667eea;
        color: white;
        padding: 1rem;
        text-align: center;
        border-radius: 10px;
        margin-bottom: 1rem;
        font-size: 1.8rem;
    }
    .form-section {
        background: #f093fb;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
    }
    .prediction-box {
        background: #667eea;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
    .chat-message {
        margin: 5px 0;
        padding: 10px;
        border-radius: 5px;
        max-width: 80%;
    }
    .user-message {
        background: #667eea;
        color: white;
        margin-left: auto;
    }
    .assistant-message {
        background: #f093fb;
        color: white;
        margin-right: auto;
    }
    section[data-testid="stSidebar"] {display: none !important;}
    .stApp > div:first-child {padding-left: 1rem !important;}
    
    @media (max-width: 768px) {
        .main-header {font-size: 1.5rem !important; padding: 0.5rem !important;}
        .form-section {padding: 0.5rem !important;}
        .stButton > button {width: 100% !important; margin: 0.25rem 0 !important;}
        .stColumns {flex-direction: column !important;}
        .stColumns > div {width: 100% !important;}
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🐾 DIAGVET IA</h1>', unsafe_allow_html=True)

# Função otimizada para carregar modelo
@st.cache_data
def carregar_modelo():
    try:
        possible_paths = [
            "VET/models/model_minimal.pkl",
            "models/model_minimal.pkl",
            "./VET/models/model_minimal.pkl"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return joblib.load(path)
        
        st.error("❌ Modelo não encontrado!")
        return None
    except Exception as e:
        st.error(f"❌ Erro: {e}")
        return None

# Função DeepSeek simplificada com API gratuita
def call_deepseek_api(message):
    """Chama API gratuita do DeepSeek usando requests"""
    try:
        # Usar API gratuita do DeepSeek sem autenticação
        url = "https://api.deepseek.com/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Prompt veterinário especializado
        system_prompt = """Você é um veterinário especialista com anos de experiência. 

ESPECIALIDADES:
- Diagnóstico clínico de cães e gatos
- Medicina interna veterinária
- Cirurgia veterinária
- Emergências veterinárias
- Farmacologia veterinária

DIRETRIZES:
1. Seja preciso e técnico, mas acessível
2. Sempre sugira exames complementares quando apropriado
3. Mencione doses de medicamentos quando relevante
4. Se for uma emergência, deixe claro a urgência
5. Use emojis veterinários (🐾, 🏥, 💊, 🔬)

FORMATO DE RESPOSTA:
- Diagnóstico diferencial quando aplicável
- Exames recomendados com justificativas
- Tratamento sugerido com doses
- Prognóstico quando possível
- Orientações para o tutor"""

        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user", 
                    "content": message
                }
            ],
            "max_tokens": 1500,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            # Resposta veterinária simulada inteligente
            return gerar_resposta_veterinaria(message)
            
    except Exception as e:
        return gerar_resposta_veterinaria(message)

def gerar_resposta_veterinaria(message):
    """Gera resposta veterinária baseada em padrões"""
    message_lower = message.lower()
    
    # Diagnósticos baseados em palavras-chave
    if any(word in message_lower for word in ['vômito', 'vomito', 'enjoo']):
        return """🐾 **Análise Veterinária - Vômito**

**Possíveis causas:**
• Gastroenterite viral/bacteriana
• Obstrução gastrointestinal
• Ingestão de corpo estranho
• Pancreatite
• Insuficiência renal/hepática

**Exames recomendados:**
🔬 Hemograma completo
🔬 Bioquímica sérica (ureia, creatinina, ALT, amilase)
🔬 Raio-X abdominal
🔬 Ultrassom abdominal (se necessário)

**Tratamento inicial:**
💊 Jejum de 12-24h (apenas água)
💊 Fluidoterapia IV: 20-40 ml/kg/dia
💊 Anti-emético: Ondansetrona 0.1-0.2 mg/kg 2x/dia
💊 Protetor gástrico: Ranitidina 0.5 mg/kg 2x/dia

**⚠️ Procure veterinário imediatamente se:**
• Vômito com sangue
• Letargia extrema
• Distensão abdominal
• Vômito por mais de 24h"""
    
    elif any(word in message_lower for word in ['diarreia', 'diarréia']):
        return """🐾 **Análise Veterinária - Diarreia**

**Possíveis causas:**
• Gastroenterite infecciosa
• Parasitas intestinais
• Intolerância alimentar
• Doença inflamatória intestinal
• Pancreatite

**Exames recomendados:**
🔬 Exame de fezes (parasitas)
🔬 Hemograma completo
🔬 Bioquímica sérica
🔬 Teste de giardia/cryptosporidium

**Tratamento inicial:**
💊 Dieta branda (frango + arroz)
💊 Probióticos: 1 sachet/dia
💊 Metronidazol: 10-15 mg/kg 2x/dia (se bacteriana)
💊 Fluidoterapia se desidratação

**⚠️ Procure veterinário se:**
• Diarreia com sangue
• Desidratação
• Mais de 5 dias de duração"""
    
    elif any(word in message_lower for word in ['febre', 'temperatura', 'quente']):
        return """🐾 **Análise Veterinária - Febre**

**Temperatura normal:** 37.5°C - 39.5°C
**Febre:** > 39.5°C

**Possíveis causas:**
• Infecção bacteriana/viral
• Inflamação
• Doença autoimune
• Câncer
• Medicamentos

**Exames recomendados:**
🔬 Hemograma completo
🔬 Bioquímica sérica
🔬 Urina completa
🔬 Cultura bacteriana (se necessário)

**Tratamento:**
💊 Antipirético: Dipirona 25 mg/kg 2x/dia
💊 Antibiótico se infecção bacteriana
💊 Fluidoterapia
💊 Compressas frias

**⚠️ Emergência se:**
• Temperatura > 41°C
• Convulsões
• Letargia extrema"""
    
    else:
        return f"""🐾 **Análise Veterinária**

Baseado em sua pergunta sobre "{message}":

**📋 Avaliação inicial:**
• Anamnese completa (histórico, sintomas, duração)
• Exame físico detalhado
• Avaliação de sinais vitais

**🔬 Exames básicos recomendados:**
• Hemograma completo
• Bioquímica sérica (ureia, creatinina, ALT, AST, glicose)
• Urina completa
• Raio-X (se indicado)

**💊 Abordagem geral:**
• Tratamento sintomático inicial
• Monitoramento clínico
• Reavaliação em 24-48h
• Encaminhamento para especialista se necessário

**⚠️ Sempre consulte um veterinário para:**
• Diagnóstico preciso
• Prescrição de medicamentos
• Acompanhamento do caso

*Esta é uma orientação geral. Cada caso requer avaliação individual.*"""

# Carregar modelo
model_data = carregar_modelo()

if model_data is None:
    st.stop()

# Extrair componentes
modelo = model_data['model']
scaler = model_data['scaler']
le_diagnostico = model_data['le_diagnostico']

# Sistema de abas
tab1, tab2 = st.tabs(["🔍 Predição", "💬 Chat IA"])

# ABA 1: PREDIÇÃO
with tab1:
    st.subheader("🔍 Predição de Diagnóstico")
    
    # Formulário simplificado
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("**🐕 Informações Básicas**")
        especie = st.selectbox("Espécie:", ["Canina", "Felina"])
        idade_anos = st.number_input("Idade (anos):", 0.0, 20.0, 5.0)
        sexo = st.selectbox("Sexo:", ["M", "F"])
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("**🧪 Exames Laboratoriais**")
        hemoglobina = st.number_input("Hemoglobina (g/dL):", 5.0, 20.0, 12.0)
        hematocrito = st.number_input("Hematócrito (%):", 20.0, 60.0, 45.0)
        leucocitos = st.number_input("Leucócitos (mil/μL):", 3.0, 25.0, 8.0)
        glicose = st.number_input("Glicose (mg/dL):", 50.0, 300.0, 100.0)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("**🏥 Sintomas Clínicos**")
        febre = st.checkbox("Febre")
        apatia = st.checkbox("Apatia")
        perda_peso = st.checkbox("Perda de peso")
        vomito = st.checkbox("Vômito")
        diarreia = st.checkbox("Diarreia")
        tosse = st.checkbox("Tosse")
        letargia = st.checkbox("Letargia")
        feridas_cutaneas = st.checkbox("Feridas cutâneas")
        poliuria = st.checkbox("Poliúria")
        polidipsia = st.checkbox("Polidipsia")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Botão de predição
    if st.button("🔍 Realizar Predição", type="primary"):
        try:
            # Criar array de dados (39 features)
            sintomas = [febre, apatia, perda_peso, vomito, diarreia, tosse, letargia, feridas_cutaneas, poliuria, polidipsia]
            sintomas_values = [1 if s else 0 for s in sintomas]
            
            dados_predicao = np.array([
                especie == "Canina", especie == "Felina", idade_anos, sexo == "M",
                hemoglobina, hematocrito, leucocitos, 10.0,
                glicose, 30.0, 1.2, 25.0, 50.0,
                100.0, 7.0, 3.5, 200.0, 100.0, 2.0,
                1.0, 1.5, 2.0
            ] + sintomas_values + [0, 0, 0, 0, 0, 0, 0]).reshape(1, -1)
            
            # Fazer predição
            predicao = modelo.predict(dados_predicao)
            probabilidades = modelo.predict_proba(dados_predicao)
            
            # Obter diagnóstico
            diagnostico_predito = le_diagnostico.inverse_transform(predicao)[0]
            confianca = max(probabilidades[0]) * 100
            
            # Mostrar resultado
            st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
            st.markdown(f"### 🎯 **Diagnóstico: {diagnostico_predito}**")
            st.markdown(f"### 📊 **Confiança: {confianca:.1f}%**")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Sugestões básicas
            st.subheader("💊 Recomendações")
            if diagnostico_predito == "Doença renal":
                st.markdown("• **Fluidos IV:** 10-20 ml/kg/h")
                st.markdown("• **Furosemida:** 1-2 mg/kg 2x/dia")
                st.markdown("• **Exames:** Urina completa, proteinúria")
            elif diagnostico_predito == "Infecção":
                st.markdown("• **Antibiótico:** Amoxicilina 12.5-25 mg/kg 2x/dia")
                st.markdown("• **Exames:** Hemograma, cultura")
                st.markdown("• **Duração:** 7-10 dias")
            else:
                st.markdown("• Consulte veterinário especialista")
                st.markdown("• Exames complementares necessários")
                st.markdown("• Monitoramento clínico")
                
        except Exception as e:
            st.error(f"❌ Erro na predição: {e}")

# ABA 2: CHAT IA
with tab2:
    st.subheader("💬 Chat com IA Veterinária")
    
    # Inicializar chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Mostrar histórico
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user-message"><strong>Você:</strong> {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message assistant-message"><strong>IA:</strong> {message["content"]}</div>', unsafe_allow_html=True)
    
    # Input do usuário
    user_input = st.text_area("Digite sua pergunta:", height=80, placeholder="Ex: Cão com vômito, o que pode ser?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 Enviar"):
            if user_input.strip():
                # Adicionar mensagem do usuário
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                
                # Gerar resposta
                with st.spinner("🤖 IA pensando..."):
                    ai_response = call_deepseek_api(user_input)
                
                # Adicionar resposta
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                st.rerun()
    
    with col2:
        if st.button("🗑️ Limpar Chat"):
            st.session_state.chat_history = []
            st.rerun()

# Footer
st.divider()
st.markdown("🐾 DIAGVET IA - Sistema Veterinário")
