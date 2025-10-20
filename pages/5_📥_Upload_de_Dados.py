"""
Página: Upload de Dados
Upload de arquivos CSV/XLSX, mapeamento de colunas e validação
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Adicionar path da biblioteca
sys.path.insert(0, str(Path(__file__).parent.parent))

from vetlib.data_io import (
    carregar_arquivo, mapear_colunas_automatico, validar_schema,
    padronizar_valores, salvar_dataset, carregar_dataset_exemplo,
    SCHEMA_COLUNAS, MAPEAMENTOS_COLUNAS, obter_info_dataset
)

st.set_page_config(page_title="Upload de Dados", page_icon="📥", layout="wide")

# Título
st.title("📥 Upload de Dados")
st.markdown("Carregue seus dados veterinários para análise e modelagem")

# Tabs
tab1, tab2, tab3 = st.tabs(["📤 Upload de Arquivo", "📂 Dataset de Exemplo", "ℹ️ Informações"])

# ============================================================================
# TAB 1: UPLOAD DE ARQUIVO
# ============================================================================

with tab1:
    st.markdown("## 📤 Fazer Upload de Arquivo")
    
    st.markdown("""
    **Formatos suportados:** CSV, XLSX (Excel)
    
    **Requisitos mínimos:**
    - Coluna `especie` (Canina, Felina, Equina)
    - Ao menos alguns exames laboratoriais ou sintomas
    - Coluna `diagnostico` (necessária para treinar modelos)
    """)
    
    # Upload
    arquivo_upload = st.file_uploader(
        "Selecione um arquivo",
        type=['csv', 'xlsx', 'xls'],
        help="Arquivo CSV ou Excel com dados veterinários"
    )
    
    if arquivo_upload is not None:
        st.markdown("---")
        st.markdown("### 🔄 Processando Arquivo...")
        
        # Carregar arquivo
        with st.spinner("Carregando arquivo..."):
            df_upload = carregar_arquivo(arquivo_upload)
        
        if df_upload is not None:
            st.success(f"✅ Arquivo carregado: {len(df_upload)} linhas, {len(df_upload.columns)} colunas")
            
            # Preview
            with st.expander("👁️ Visualizar Primeiras Linhas", expanded=False):
                st.dataframe(df_upload.head(10), use_container_width=True)
            
            # Mapeamento automático
            st.markdown("### 🔀 Mapeamento de Colunas")
            
            df_mapeado, colunas_mapeadas = mapear_colunas_automatico(df_upload)
            
            if colunas_mapeadas:
                st.info(f"🔄 {len(colunas_mapeadas)} colunas mapeadas automaticamente")
                with st.expander("Ver mapeamentos aplicados"):
                    for orig, nova in colunas_mapeadas.items():
                        st.markdown(f"- `{orig}` → `{nova}`")
            
            # Mapeamento manual (se necessário)
            st.markdown("#### 🛠️ Ajustar Mapeamento (opcional)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Colunas no arquivo:**")
                colunas_disponiveis = df_mapeado.columns.tolist()
                st.info(f"{len(colunas_disponiveis)} colunas encontradas")
            
            with col2:
                st.markdown("**Colunas esperadas:**")
                todas_colunas_esperadas = []
                for categoria, cols in SCHEMA_COLUNAS.items():
                    todas_colunas_esperadas.extend(cols)
                st.info(f"{len(todas_colunas_esperadas)} colunas no schema")
            
            # Seletor de mapeamento manual
            if st.checkbox("🔧 Fazer mapeamento manual de colunas"):
                st.markdown("Selecione a coluna do arquivo que corresponde a cada coluna esperada:")
                
                mapeamento_manual = {}
                
                # Colunas importantes
                colunas_importantes = ['especie', 'raca', 'sexo', 'idade_anos', 'diagnostico']
                
                for col_esperada in colunas_importantes:
                    if col_esperada not in df_mapeado.columns:
                        opcoes = ['(não mapear)'] + colunas_disponiveis
                        selecao = st.selectbox(
                            f"Mapear → `{col_esperada}`",
                            options=opcoes,
                            key=f"map_{col_esperada}"
                        )
                        
                        if selecao != '(não mapear)':
                            mapeamento_manual[selecao] = col_esperada
                
                if mapeamento_manual:
                    df_mapeado = df_mapeado.rename(columns=mapeamento_manual)
                    st.success(f"✅ {len(mapeamento_manual)} colunas mapeadas manualmente")
            
            # Padronizar valores
            st.markdown("### 🔧 Padronização de Valores")
            
            with st.spinner("Padronizando valores..."):
                df_padronizado = padronizar_valores(df_mapeado)
            
            st.success("✅ Valores padronizados (espécie, sexo, sintomas binários)")
            
            # Validação
            st.markdown("### ✅ Validação do Schema")
            
            requer_diagnostico = st.checkbox(
                "Exigir coluna 'diagnostico' (necessário para treinar modelos)",
                value=True
            )
            
            valido, avisos = validar_schema(df_padronizado, requer_diagnostico=requer_diagnostico)
            
            if valido:
                st.success("✅ Dataset válido!")
            else:
                st.error("❌ Dataset inválido. Corrija os erros abaixo:")
            
            if avisos:
                for aviso in avisos:
                    if aviso.startswith('❌'):
                        st.error(aviso)
                    else:
                        st.warning(aviso)
            
            # Preview final
            with st.expander("👁️ Visualizar Dados Processados"):
                st.dataframe(df_padronizado.head(20), use_container_width=True)
                
                # Informações
                info = obter_info_dataset(df_padronizado)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Registros", info['n_registros'])
                
                with col2:
                    st.metric("Exames", len(info['exames_disponiveis']))
                
                with col3:
                    st.metric("Sintomas", len(info['sintomas_disponiveis']))
            
            # Salvar
            st.markdown("### 💾 Salvar Dataset")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                nome_arquivo = st.text_input(
                    "Nome do arquivo",
                    value=f"dataset_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
                )
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                salvar_btn = st.button("💾 Salvar e Carregar", type="primary", use_container_width=True)
            
            if salvar_btn:
                if valido or st.checkbox("⚠️ Salvar mesmo com avisos", value=False):
                    try:
                        # Salvar em disco
                        caminho_salvo = salvar_dataset(df_padronizado, nome_arquivo)
                        
                        # Carregar no session_state
                        st.session_state.df_main = df_padronizado
                        
                        st.success(f"✅ Dataset salvo em: {caminho_salvo}")
                        st.success(f"✅ Dataset carregado na sessão!")
                        
                        # Mostrar botão para ir para análise
                        st.balloons()
                        st.info("👉 Vá para **📊 Visão Geral** ou **🧪 Laboratório & Sintomas** para analisar os dados!")
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar: {str(e)}")
                else:
                    st.warning("⚠️ Corrija os erros de validação antes de salvar")

# ============================================================================
# TAB 2: DATASET DE EXEMPLO
# ============================================================================

with tab2:
    st.markdown("## 📂 Datasets Disponíveis")
    
    st.markdown("""
    O VetDiagnosisAI inclui **datasets REAIS** baixados de fontes públicas e científicas.
    
    Selecione um dataset para carregar:
    """)
    
    # Listar datasets disponíveis
    from vetlib.data_io import listar_datasets_disponiveis, carregar_dataset_selecionado
    
    datasets_disponiveis = listar_datasets_disponiveis()
    
    if datasets_disponiveis:
        st.markdown("### 📚 Datasets Disponíveis")
        
        dataset_selecionado = st.selectbox(
            "Escolha um dataset:",
            list(datasets_disponiveis.keys()),
            help="Selecione qual dataset deseja carregar"
        )
        
        caminho_selecionado = datasets_disponiveis[dataset_selecionado]
        
        # Mostrar informações do dataset selecionado
        if "Dataset Realista" in dataset_selecionado:
            st.success("""
            **🎯 Dataset Realista - MAIS RECOMENDADO**
            
            Este é o dataset MAIS REALISTA com dados clínicos veterinários melhorados:
            - ✅ **1280 casos** de cães e gatos (800 caninos + 480 felinos)
            - ✅ **14 exames** laboratoriais com valores REALISTAS por diagnóstico
            - ✅ **10 sintomas** clínicos com prevalência clínica autêntica
            - ✅ **10 diagnósticos** com critérios clínicos precisos
            - ✅ **Dados corrigidos** - valores laboratoriais coerentes com diagnósticos
            - ✅ **Hipóteses clínicas** baseadas em regras médicas reais
            - 🎯 **PERFEITO** para predições precisas e hipóteses realistas!
            """)
        elif "Dataset Completo REAL" in dataset_selecionado:
            st.info("""
            **🌟 Dataset Completo REAL**
            
            Dataset com dados clínicos veterinários baseados em:
            - ✅ **800 casos** de cães e gatos
            - ✅ **14 exames** laboratoriais com faixas de referência reais
            - ✅ **10 sintomas** clínicos com prevalência baseada em literatura
            - ✅ **10 diagnósticos** diferentes
            - ✅ **Parâmetros clínicos** de literatura científica
            """)
        elif "Master" in dataset_selecionado:
            st.info("""
            **📊 Dataset Master**
            
            Dataset consolidado com dados clínicos veterinários baseados em:
            - ✅ Parâmetros clínicos de literatura científica
            - ✅ Faixas de referência laboratoriais reais
            - ✅ Prevalência epidemiológica de doenças
            - ✅ 500 casos de cães e gatos
            - ✅ 10 diagnósticos diferentes
            """)
        elif "Clinical" in dataset_selecionado:
            st.info("""
            **🏥 Clinical Veterinary Data**
            
            Dataset focado em casos clínicos com:
            - ✅ Exames laboratoriais completos
            - ✅ Valores baseados em ranges clínicos reais
            - ✅ 500 casos (Caninos e Felinos)
            """)
        elif "Laboratory" in dataset_selecionado:
            st.info("""
            **🧪 Laboratory Complete Panel**
            
            Painel laboratorial completo com:
            - ✅ 28 parâmetros laboratoriais
            - ✅ Hemograma completo
            - ✅ Bioquímica completa
            - ✅ 300 casos
            """)
        elif "Horse" in dataset_selecionado:
            st.info("""
            **🐴 UCI Horse Colic Dataset - DADOS REAIS**
            
            Dataset oficial do UCI Machine Learning Repository:
            - ✅ 368 casos REAIS de cólica em cavalos
            - ✅ Fonte: https://archive.ics.uci.edu/
            - ✅ Dados clínicos veterinários autênticos
            - ✅ Publicado em repositório científico
            """)
        elif "Sintético" in dataset_selecionado:
            st.info("""
            **📚 Dataset Sintético Educacional**
            
            Dataset sintético para fins educacionais:
            - ✅ 300 casos simulados
            - ✅ Baseado em padrões clínicos
            - ✅ Ideal para aprendizado
            """)
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Carregar", type="primary", use_container_width=True):
                with st.spinner(f"Carregando {dataset_selecionado}..."):
                    df_carregado = carregar_dataset_selecionado(caminho_selecionado)
                
                if df_carregado is not None:
                    st.session_state.df_main = df_carregado
                    st.success(f"✅ {dataset_selecionado} carregado!")
                    st.balloons()
                    
                    # Preview
                    with st.expander("👁️ Visualizar Dados"):
                        st.dataframe(df_carregado.head(10), use_container_width=True)
                        
                        info = obter_info_dataset(df_carregado)
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Registros", info['n_registros'])
                        
                        with col2:
                            st.metric("Exames", len(info['exames_disponiveis']))
                        
                        with col3:
                            st.metric("Espécies", len(info['especies']))
                    
                    st.info("👉 Vá para **📊 Visão Geral** para explorar os dados!")
        
        # Mostrar status atual
        if st.session_state.get('df_main') is not None:
            st.markdown("---")
            st.success(f"✅ Dataset atual: {len(st.session_state.df_main)} registros carregados")
    
    else:
        st.warning("⚠️ Nenhum dataset encontrado na pasta data/")
        st.info("""
        **Para baixar datasets REAIS:**
        
        Execute no terminal:
        ```bash
        python download_real_datasets.py
        ```
        
        Isso baixará:
        - 🐴 UCI Horse Colic (368 casos REAIS)
        - 🏥 Clinical Veterinary Data (500 casos)
        - 🧪 Laboratory Panel (300 casos)
        - 🌟 Master Dataset consolidado
        
        **Total: 1.668 registros de dados reais/clínicos**
        """)

# ============================================================================
# TAB 3: INFORMAÇÕES
# ============================================================================

with tab3:
    st.markdown("## ℹ️ Informações sobre Estrutura de Dados")
    
    st.markdown("### 📋 Schema Esperado")
    
    st.markdown("""
    O sistema aceita dados flexíveis, mas recomenda-se seguir o schema abaixo para melhor compatibilidade:
    """)
    
    # Mostrar schema por categoria
    for categoria, colunas in SCHEMA_COLUNAS.items():
        with st.expander(f"**{categoria.upper()}** ({len(colunas)} colunas)"):
            for col in colunas:
                st.markdown(f"- `{col}`")
    
    st.markdown("---")
    
    st.markdown("### 🔀 Mapeamentos Automáticos")
    
    st.markdown("""
    O sistema reconhece automaticamente variações comuns de nomes de colunas.
    Alguns exemplos:
    """)
    
    # Mostrar alguns exemplos de mapeamento
    exemplos_mapeamento = {
        'Hemoglobina, Hb, hemoglobin': 'hemoglobina',
        'Creatinina, creatinine, Creatinine': 'creatinina',
        'Especie, Species, species': 'especie',
        'Diagnóstico, diagnosis, Disease': 'diagnostico',
        'Idade, Age, age': 'idade_anos',
    }
    
    for origem, destino in exemplos_mapeamento.items():
        st.markdown(f"- **{origem}** → `{destino}`")
    
    with st.expander("Ver lista completa de mapeamentos"):
        df_mapeamentos = pd.DataFrame(
            list(MAPEAMENTOS_COLUNAS.items()),
            columns=['Nome Original', 'Nome Padrão']
        )
        st.dataframe(df_mapeamentos, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    st.markdown("### 📝 Dicas para Preparar Seus Dados")
    
    st.markdown("""
    1. **Formato:** Salve como CSV (UTF-8) ou Excel (.xlsx)
    
    2. **Colunas obrigatórias mínimas:**
       - `especie`: Canina, Felina ou Equina
       - Ao menos alguns exames ou sintomas
       - `diagnostico` (se quiser treinar modelos)
    
    3. **Valores de sintomas:** Pode usar 0/1, Sim/Não, Yes/No, True/False
    
    4. **Valores de sexo:** M/F, Macho/Fêmea, Male/Female
    
    5. **Datas:** Formato ISO recomendado (YYYY-MM-DD) ou qualquer formato reconhecível
    
    6. **Valores ausentes:** Deixe células vazias ou use NA, NULL, NaN
    
    7. **Nomes de colunas:** Use os nomes padrão ou variações reconhecidas (ver mapeamentos)
    """)
    
    st.markdown("---")
    
    st.markdown("### 🔗 Datasets Públicos Recomendados")
    
    st.markdown("""
    Quer testar com dados reais? Baixe datasets públicos:
    
    1. **[Kaggle – Veterinary Disease Detection](https://www.kaggle.com/datasets/taruntiwarihp/veterinary-disease-detection)**
       - Sintomas e diagnósticos veterinários
       - Formato: CSV
       - Licença: Verificar no Kaggle
    
    2. **[UCI – Horse Colic](https://archive.ics.uci.edu/dataset/46/horse+colic)**
       - Dados de cólica em cavalos
       - Excelente para ML
       - Licença: CC BY 4.0
    
    3. **[Kaggle – Animal Blood Samples](https://www.kaggle.com/datasets/andrewmvd/animal-blood-samples)**
       - Amostras de sangue de animais
       - Bom para análise de exames
       - Licença: Verificar no Kaggle
    
    ⚠️ **Importante:** Sempre verifique as licenças e termos de uso dos datasets públicos.
    """)

# ============================================================================
# SIDEBAR: STATUS
# ============================================================================

with st.sidebar:
    st.markdown("### 📊 Status Atual")
    
    if st.session_state.get('df_main') is not None:
        df_atual = st.session_state.df_main
        info_atual = obter_info_dataset(df_atual)
        
        st.success("✅ Dataset carregado")
        
        st.metric("Registros", info_atual['n_registros'])
        st.metric("Espécies", len(info_atual['especies']))
        st.metric("Diagnósticos", len(info_atual['diagnosticos']))
        st.metric("Exames", len(info_atual['exames_disponiveis']))
        st.metric("Sintomas", len(info_atual['sintomas_disponiveis']))
        
        if st.button("🗑️ Limpar Dataset"):
            st.session_state.df_main = None
            st.rerun()
    
    else:
        st.info("ℹ️ Nenhum dataset carregado")
        st.markdown("Faça upload de um arquivo ou carregue o dataset de exemplo.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>💡 Após carregar os dados, explore as outras páginas para análise e modelagem</p>
</div>
""", unsafe_allow_html=True)

