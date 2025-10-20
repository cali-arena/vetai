"""
VetDiagnosisAI - App Simples para Veterinários
Interface focada apenas em predições rápidas
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import pickle
from pathlib import Path
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="VetDiagnosisAI - Predição Rápida",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para interface limpa
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .prediction-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .metric-box {
        background-color: #e8f4f8;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown('<h1 class="main-header">🐾 VetDiagnosisAI - Predição Rápida</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666;">Sistema Inteligente de Apoio ao Diagnóstico Veterinário</p>', unsafe_allow_html=True)

# Função para carregar modelo
@st.cache_data
def carregar_modelo():
    """Carrega o modelo treinado"""
    try:
        model_path = Path("models/gb_optimized_model.pkl")
        if model_path.exists():
            model_data = joblib.load(model_path)
            return model_data
        else:
            return None
    except Exception as e:
        st.error(f"Erro ao carregar modelo: {e}")
        return None

# Carregar modelo
model_data = carregar_modelo()

if model_data is None:
    st.error("❌ Modelo não encontrado! Por favor, treine o modelo primeiro no app gerencial.")
    st.info("📧 Entre em contato com o administrador do sistema.")
    st.stop()

# Extrair componentes do modelo
modelo = model_data['model']
scaler = model_data['scaler']
le_diagnostico = model_data['le_diagnostico']
accuracy = model_data.get('accuracy', 0)
training_date = model_data.get('timestamp', 'N/A')

# Mostrar informações do modelo
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.metric("🎯 Acurácia do Modelo", f"{accuracy:.1%}")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.metric("📊 Última Atualização", training_date.split('T')[0] if 'T' in training_date else training_date)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    st.metric("🧠 Tipo de Modelo", "Gradient Boosting")
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# Formulário de predição
st.subheader("🔍 Predição de Diagnóstico")

# Dividir em colunas para melhor organização
col1, col2 = st.columns(2)

with col1:
    st.markdown("**📋 Dados Básicos do Animal**")
    
    especie = st.selectbox(
        "Espécie",
        options=["Canina", "Felina", "Equina", "Bovino", "Suíno", "Ave", "Outro"],
        help="Selecione a espécie do animal"
    )
    
    raca = st.text_input(
        "Raça",
        placeholder="Ex: Labrador, Persa, SRD...",
        help="Digite a raça do animal"
    )
    
    idade_anos = st.number_input(
        "Idade (anos)",
        min_value=0.0,
        max_value=30.0,
        value=1.0,
        step=0.1,
        help="Idade do animal em anos"
    )
    
    sexo = st.selectbox(
        "Sexo",
        options=["M", "F"],
        help="Sexo do animal"
    )

with col2:
    st.markdown("**🧪 Exames Laboratoriais**")
    
    hemoglobina = st.number_input(
        "Hemoglobina (g/dL)",
        min_value=0.0,
        max_value=30.0,
        value=12.0,
        step=0.1,
        help="Valor de hemoglobina"
    )
    
    hematocrito = st.number_input(
        "Hematócrito (%)",
        min_value=0.0,
        max_value=100.0,
        value=40.0,
        step=0.1,
        help="Valor de hematócrito"
    )
    
    leucocitos = st.number_input(
        "Leucócitos (x10³/μL)",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=0.1,
        help="Contagem de leucócitos"
    )
    
    glicose = st.number_input(
        "Glicose (mg/dL)",
        min_value=0.0,
        max_value=500.0,
        value=100.0,
        step=1.0,
        help="Nível de glicose"
    )

# Segunda linha de exames
col3, col4 = st.columns(2)

with col3:
    st.markdown("**🔬 Mais Exames**")
    
    ureia = st.number_input(
        "Ureia (mg/dL)",
        min_value=0.0,
        max_value=200.0,
        value=30.0,
        step=1.0,
        help="Nível de ureia"
    )
    
    creatinina = st.number_input(
        "Creatinina (mg/dL)",
        min_value=0.0,
        max_value=10.0,
        value=1.0,
        step=0.1,
        help="Nível de creatinina"
    )
    
    alt = st.number_input(
        "ALT (U/L)",
        min_value=0.0,
        max_value=1000.0,
        value=50.0,
        step=1.0,
        help="Alanina aminotransferase"
    )

with col4:
    st.markdown("**🏥 Sintomas Clínicos**")
    
    # Sintomas como checkboxes
    febre = st.checkbox("Febre")
    apatia = st.checkbox("Apatia")
    perda_peso = st.checkbox("Perda de Peso")
    vomito = st.checkbox("Vômito")
    diarreia = st.checkbox("Diarreia")
    tosse = st.checkbox("Tosse")
    letargia = st.checkbox("Letargia")
    feridas_cutaneas = st.checkbox("Feridas Cutâneas")
    poliuria = st.checkbox("Poliúria")
    polidipsia = st.checkbox("Polidipsia")

# Botão de predição
if st.button("🔍 Realizar Predição", type="primary", use_container_width=True):
    
    # Preparar dados para predição
    try:
        # Converter sintomas para valores binários
        sintomas = [febre, apatia, perda_peso, vomito, diarreia, tosse, letargia, feridas_cutaneas, poliuria, polidipsia]
        sintomas_values = [1 if s else 0 for s in sintomas]
        
        # Criar array com todos os dados
        dados_predicao = np.array([
            especie == "Canina", especie == "Felina",  # One-hot encoding para espécie
            idade_anos,
            sexo == "M",  # 1 para macho, 0 para fêmea
            hemoglobina, hematocrito, leucocitos, 10.0,  # Plaquetas padrão
            glicose, ureia, creatinina, alt, 50.0,  # AST padrão
            100.0, 7.0, 3.5, 200.0, 100.0, 2.0  # Valores padrão para outros exames
        ] + sintomas_values).reshape(1, -1)
        
        # Fazer predição
        predicao = modelo.predict(dados_predicao)
        probabilidades = modelo.predict_proba(dados_predicao)
        
        # Obter diagnóstico
        diagnostico_predito = le_diagnostico.inverse_transform(predicao)[0]
        confianca = max(probabilidades[0]) * 100
        
        # Mostrar resultado
        st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
        st.markdown(f"### 🎯 **Diagnóstico Predito: {diagnostico_predito}**")
        st.markdown(f"### 📊 **Confiança: {confianca:.1f}%**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Mostrar probabilidades de todos os diagnósticos
        st.subheader("📈 Probabilidades por Diagnóstico")
        
        probabilidades_df = pd.DataFrame({
            'Diagnóstico': le_diagnostico.classes_,
            'Probabilidade (%)': probabilidades[0] * 100
        }).sort_values('Probabilidade (%)', ascending=False)
        
        # Gráfico de barras das probabilidades
        import plotly.express as px
        fig = px.bar(
            probabilidades_df.head(5),
            x='Probabilidade (%)',
            y='Diagnóstico',
            orientation='h',
            title='Top 5 Diagnósticos Mais Prováveis',
            color='Probabilidade (%)',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela com todas as probabilidades
        st.dataframe(probabilidades_df, use_container_width=True)
        
        # Log da predição para análise posterior
        log_predicao = {
            'timestamp': datetime.now().isoformat(),
            'especie': especie,
            'idade': idade_anos,
            'sexo': sexo,
            'sintomas': sintomas,
            'diagnostico_predito': diagnostico_predito,
            'confianca': confianca,
            'probabilidades': probabilidades[0].tolist()
        }
        
        # Salvar log (implementar sistema de logging posteriormente)
        st.success("✅ Predição realizada com sucesso!")
        
    except Exception as e:
        st.error(f"❌ Erro na predição: {e}")
        st.info("Por favor, verifique os dados inseridos e tente novamente.")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <p>🐾 VetDiagnosisAI - Sistema Inteligente de Diagnóstico Veterinário</p>
    <p><small>Para dúvidas ou suporte, entre em contato com o administrador do sistema.</small></p>
</div>
""", unsafe_allow_html=True)
