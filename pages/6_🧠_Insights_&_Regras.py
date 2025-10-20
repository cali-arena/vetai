"""
Página: Insights & Regras
Geração automática de insights clínicos e hipóteses diagnósticas
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Adicionar path da biblioteca
sys.path.insert(0, str(Path(__file__).parent.parent))

from vetlib.insights import (
    gerar_insights_dataset, gerar_insights_diagnostico,
    gerar_hipoteses_diagnosticas, gerar_recomendacoes_clinicas
)
from vetlib.preprocessing import FAIXAS_REFERENCIA
from vetlib.data_io import SCHEMA_COLUNAS

st.set_page_config(page_title="Insights & Regras", page_icon="🧠", layout="wide")

# Título
st.title("🧠 Insights & Regras Clínicas")
st.markdown("Insights automáticos e hipóteses diagnósticas baseadas em dados")

# Disclaimer
st.warning("""
⚠️ **DISCLAIMER IMPORTANTE**

Este sistema gera **sugestões automáticas** baseadas em análise de dados e NÃO substitui:
- 🏥 Julgamento clínico de um médico veterinário
- 🔬 Exames complementares necessários
- 📋 Avaliação completa do paciente
- 💊 Decisões terapêuticas

**Use apenas como ferramenta de apoio à decisão clínica por profissionais qualificados.**
""")

# Verificar dados
if st.session_state.get('df_main') is None:
    st.warning("⚠️ Nenhum dataset carregado. Vá para **📥 Upload de Dados** primeiro.")
    st.stop()

df = st.session_state.df_main.copy()

st.markdown("---")

# ============================================================================
# SEÇÃO 1: INSIGHTS GERAIS DO DATASET
# ============================================================================

st.markdown("## 📊 Insights Gerais do Dataset")

with st.spinner("Gerando insights..."):
    insights_gerais = gerar_insights_dataset(df)

if insights_gerais:
    for insight in insights_gerais:
        st.markdown(insight)
else:
    st.info("Nenhum insight geral gerado")

st.markdown("---")

# ============================================================================
# SEÇÃO 2: INSIGHTS POR DIAGNÓSTICO
# ============================================================================

st.markdown("## 🔬 Insights por Diagnóstico")

if 'diagnostico' in df.columns:
    diagnosticos_disponiveis = sorted(df['diagnostico'].unique())
    
    diagnostico_selecionado = st.selectbox(
        "Selecione um diagnóstico para análise detalhada:",
        diagnosticos_disponiveis
    )
    
    with st.spinner(f"Analisando {diagnostico_selecionado}..."):
        insights_diag = gerar_insights_diagnostico(df, diagnostico_selecionado)
    
    if insights_diag:
        st.markdown(f"### 🏥 {diagnostico_selecionado}")
        
        for insight in insights_diag:
            st.markdown(insight)
    else:
        st.info(f"Nenhum insight específico gerado para {diagnostico_selecionado}")
    
else:
    st.info("Coluna 'diagnostico' não encontrada no dataset")

st.markdown("---")

# ============================================================================
# SEÇÃO 3: GERADOR DE HIPÓTESES
# ============================================================================

st.markdown("## 🔍 Gerador de Hipóteses Diagnósticas")

st.markdown("""
Insira valores de exames e sintomas para gerar **hipóteses diagnósticas automáticas**
baseadas em padrões clínicos conhecidos.
""")

with st.form("form_hipoteses"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Identificação")
        especie_hip = st.selectbox("Espécie", ["Canina", "Felina", "Equina"], key="hip_especie")
    
    with col2:
        st.markdown("### Exames Principais")
        
        # Obter faixas de referência
        refs = FAIXAS_REFERENCIA.get(especie_hip, FAIXAS_REFERENCIA['Canina'])
        
        exames_hip = {}
        
        exames_principais = ['creatinina', 'ureia', 'glicose', 'alt', 'ast', 
                            'hemoglobina', 'hematocrito']
        
        for exame in exames_principais:
            if exame in refs:
                min_ref, max_ref = refs[exame]
                valor_padrao = (min_ref + max_ref) / 2
                
                exames_hip[exame] = st.number_input(
                    f"{exame.replace('_', ' ').title()} ({min_ref}-{max_ref})",
                    value=float(valor_padrao),
                    format="%.2f",
                    key=f"hip_{exame}"
                )
    
    st.markdown("### 💊 Sintomas")
    
    sintomas_hip = {}
    
    cols = st.columns(3)
    
    sintomas_relevantes = ['febre', 'apatia', 'perda_peso', 'vomito', 'diarreia', 
                          'letargia', 'poliuria', 'polidipsia']
    
    for idx, sintoma in enumerate(sintomas_relevantes):
        col_idx = idx % 3
        
        with cols[col_idx]:
            sintomas_hip[sintoma] = st.checkbox(
                sintoma.replace('_', ' ').title(),
                key=f"hip_{sintoma}"
            )
    
    submit_hip = st.form_submit_button("🔍 Gerar Hipóteses", type="primary")

if submit_hip:
    # Converter sintomas para 0/1
    sintomas_dict = {k: int(v) for k, v in sintomas_hip.items()}
    
    # Gerar hipóteses
    with st.spinner("Gerando hipóteses diagnósticas..."):
        hipoteses = gerar_hipoteses_diagnosticas(exames_hip, sintomas_dict, especie_hip)
    
    st.markdown("---")
    st.markdown("## 🎯 Hipóteses Diagnósticas Geradas")
    
    if hipoteses:
        for hipotese in hipoteses:
            if hipotese.startswith('✅'):
                st.success(hipotese)
            else:
                st.info(hipotese)
    else:
        st.info("Nenhuma hipótese gerada com base nos valores fornecidos")
    
    # Recomendações
    st.markdown("### 💡 Próximos Passos Sugeridos")
    
    # Se houver hipótese de doença, gerar recomendações
    if hipoteses and not any('Normalidade' in h for h in hipoteses):
        # Simular diagnóstico mais provável para recomendações
        if 'Renal' in str(hipoteses):
            diag_provavel = 'Doença Renal Crônica'
        elif 'Diabetes' in str(hipoteses):
            diag_provavel = 'Diabetes Mellitus'
        elif 'Hepat' in str(hipoteses):
            diag_provavel = 'Hepatopatia'
        elif 'Anemia' in str(hipoteses):
            diag_provavel = 'Anemia'
        else:
            diag_provavel = 'Investigação necessária'
        
        recomendacoes = gerar_recomendacoes_clinicas(
            diag_provavel, 0.6, exames_hip, especie_hip
        )
        
        for rec in recomendacoes:
            if rec.startswith('⚕️'):
                st.info(rec)
            elif rec.startswith('⚠️'):
                st.warning(rec)
            else:
                st.markdown(rec)
    else:
        st.success("""
        ✅ **Sem alterações significativas detectadas**
        
        - Manter acompanhamento de rotina
        - Reavaliar periodicamente conforme protocolo clínico
        - Monitorar sinais clínicos
        """)

st.markdown("---")

# ============================================================================
# SEÇÃO 4: REGRAS CLÍNICAS (HARDCODED)
# ============================================================================

st.markdown("## 📋 Regras Clínicas de Referência")

st.markdown("""
Regras clínicas simplificadas para auxílio diagnóstico. Estas são **orientações gerais**
e devem ser interpretadas no contexto clínico completo.
""")

tab1, tab2, tab3, tab4 = st.tabs(["Doença Renal", "Diabetes", "Hepatopatias", "Anemias"])

with tab1:
    st.markdown("### 🔬 Doença Renal Crônica")
    
    st.markdown("""
    **Critérios Diagnósticos:**
    
    1. **Azotemia:** Creatinina e/ou Ureia elevadas
       - Creatinina > 1.6 mg/dL (Canina) ou > 2.0 mg/dL (Felina)
       - Ureia > 50 mg/dL (Canina) ou > 60 mg/dL (Felina)
    
    2. **Sinais Clínicos Associados:**
       - Poliúria e polidipsia
       - Perda de peso
       - Apatia/letargia
       - Vômitos
       - Anorexia
    
    3. **Achados Laboratoriais Adicionais:**
       - Anemia (hemoglobina baixa)
       - Hiperfosfatemia
       - Acidose metabólica
       - Densidade urinária baixa (< 1.030 cães, < 1.035 gatos)
    
    **Estadiamento IRIS:**
    - Estágio 1: Creatinina < 1.4 mg/dL (Canina)
    - Estágio 2: Creatinina 1.4-2.0 mg/dL (Canina)
    - Estágio 3: Creatinina 2.1-5.0 mg/dL (Canina)
    - Estágio 4: Creatinina > 5.0 mg/dL (Canina)
    
    **Condutas:**
    - Identificar e tratar causas reversíveis
    - Fluidoterapia se indicado
    - Dieta renal
    - Controle de hipertensão
    - Suporte nutricional
    - Monitoramento regular
    """)

with tab2:
    st.markdown("### 🩸 Diabetes Mellitus")
    
    st.markdown("""
    **Critérios Diagnósticos:**
    
    1. **Hiperglicemia Persistente:**
       - Glicemia > 200 mg/dL (Canina/Felina)
       - Confirmação em múltiplas amostras
       - Descartar estresse (especialmente em gatos)
    
    2. **Sinais Clínicos Clássicos:**
       - Poliúria e polidipsia
       - Polifagia (ou anorexia em casos graves)
       - Perda de peso
       - Letargia
    
    3. **Achados Laboratoriais:**
       - Glicosúria
       - Frutosamina elevada (>350 µmol/L)
       - Cetonúria (se cetoacidose diabética)
       - Possível aumento de triglicerídeos e colesterol
    
    **Tipos:**
    - **Tipo 1** (Caninos): Destruição pancreática, dependente de insulina
    - **Tipo 2** (Felinos): Resistência à insulina, pode ser reversível
    
    **Condutas:**
    - Insulinoterapia
    - Dieta adequada (rica em fibras para cães, rica em proteínas para gatos)
    - Monitoramento glicêmico regular
    - Curva glicêmica periódica
    - Controle de peso
    - Tratamento de comorbidades
    """)

with tab3:
    st.markdown("### 🏥 Hepatopatias")
    
    st.markdown("""
    **Critérios Diagnósticos:**
    
    1. **Elevação de Enzimas Hepáticas:**
       - **ALT** (Alanina Aminotransferase): > 100 U/L
       - **AST** (Aspartato Aminotransferase): > 50 U/L
       - **FA** (Fosfatase Alcalina): > 150 U/L
    
    2. **Padrões de Lesão:**
       - **Hepatocelular:** ALT >> FA (hepatite, toxinas)
       - **Colestático:** FA >> ALT (obstrução, Cushing)
       - **Misto:** Elevação de ambas
    
    3. **Sinais de Insuficiência Hepática:**
       - Hipoalbuminemia (< 2.5 g/dL)
       - Hipoglicemia
       - Aumento de ácidos biliares
       - Amônia elevada
       - Coagulopatia (TP, TTPA prolongados)
    
    4. **Sinais Clínicos:**
       - Vômitos, diarreia
       - Icterícia
       - Ascite
       - Encefalopatia hepática
       - Anorexia, perda de peso
    
    **Investigação Adicional:**
    - Ultrassom abdominal
    - Biópsia hepática (diagnóstico definitivo)
    - Testes de função hepática
    
    **Condutas:**
    - Identificar causa específica
    - Hepatoprotetores (SAMe, silimarina)
    - Dieta hepática
    - Tratamento de encefalopatia (lactulose)
    - Suporte nutricional
    - Evitar hepatotóxicos
    """)

with tab4:
    st.markdown("### 🩸 Anemias")
    
    st.markdown("""
    **Critérios Diagnósticos:**
    
    1. **Valores de Referência:**
       - **Caninos:** Hemoglobina < 12 g/dL, Hematócrito < 37%
       - **Felinos:** Hemoglobina < 9 g/dL, Hematócrito < 30%
    
    2. **Classificação por Mecanismo:**
       - **Perda de sangue:** Aguda (trauma, cirurgia) ou crônica (parasitas, úlceras)
       - **Destruição** (Hemólise): Imunomediada, toxinas, parasitas
       - **Produção inadequada:** Deficiências, doença crônica, neoplasia
    
    3. **Classificação Morfológica:**
       - **Regenerativa:** Reticulócitos ↑, policromasia
       - **Não-regenerativa:** Reticulócitos normais/baixos
    
    4. **Sinais Clínicos:**
       - Mucosas pálidas
       - Letargia, fraqueza
       - Taquicardia, taquipneia
       - Intolerância ao exercício
       - Possível icterícia (se hemolítica)
    
    **Investigação:**
    - Hemograma completo + reticulócitos
    - Esfregaço sanguíneo
    - Testes de Coombs (se suspeita imunomediada)
    - Pesquisa de hemoparasitas
    - Avaliação de medula óssea (se indicado)
    
    **Condutas (dependem da causa):**
    - Transfusão sanguínea (se Ht < 15-20%)
    - Identificar e tratar causa base
    - Imunossupressão (se imunomediada)
    - Suplementação (ferro, B12, folato)
    - Suporte nutricional
    - Monitoramento seriado
    """)

st.markdown("---")

# ============================================================================
# SEÇÃO 5: REFERÊNCIAS E LINKS ÚTEIS
# ============================================================================

st.markdown("## 📚 Referências e Recursos")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🔗 Links Úteis
    
    - [IRIS (International Renal Interest Society)](http://www.iris-kidney.com/)
    - [ACVIM (American College of Veterinary Internal Medicine)](https://www.acvim.org/)
    - [VIN (Veterinary Information Network)](https://www.vin.com/)
    - [PubMed Veterinary](https://pubmed.ncbi.nlm.nih.gov/)
    """)

with col2:
    st.markdown("""
    ### 📖 Bibliografia Recomendada
    
    - Ettinger, S.J. & Feldman, E.C. - *Textbook of Veterinary Internal Medicine*
    - Nelson, R.W. & Couto, C.G. - *Small Animal Internal Medicine*
    - Thrall, M.A. et al. - *Veterinary Hematology and Clinical Chemistry*
    - Kaneko, J.J. et al. - *Clinical Biochemistry of Domestic Animals*
    """)

st.markdown("---")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>⚠️ <strong>AVISO LEGAL</strong></p>
    <p>As informações fornecidas são para fins educacionais e de pesquisa.</p>
    <p>NÃO substituem consulta veterinária profissional.</p>
    <p>Sempre consulte um médico veterinário licenciado para diagnóstico e tratamento.</p>
</div>
""", unsafe_allow_html=True)



