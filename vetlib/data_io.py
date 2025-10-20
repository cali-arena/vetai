"""
Módulo de entrada/saída e validação de dados
"""

import pandas as pd
import streamlit as st
from pathlib import Path
import io


# Colunas esperadas no schema
SCHEMA_COLUNAS = {
    'identificacao': ['id', 'data', 'especie', 'raca', 'idade_anos', 'sexo'],
    'exames': [
        'hemoglobina', 'hematocrito', 'leucocitos', 'plaquetas',
        'glicose', 'ureia', 'creatinina', 'alt', 'ast', 'fosfatase_alcalina',
        'proteinas_totais', 'albumina', 'colesterol', 'triglicerideos',
        # Exames adicionais
        'eritrocitos', 'neutrofilos', 'linfocitos', 'monocitos', 'eosinofilos',
        'fa', 'ggt', 'bilirrubina_total', 'globulinas', 'calcio', 'fosforo',
        'sodio', 'potassio', 'temperatura_retal', 'pulso', 'freq_respiratoria'
    ],
    'sintomas': [
        'febre', 'apatia', 'perda_peso', 'vomito', 'diarreia',
        'tosse', 'letargia', 'feridas_cutaneas', 'poliuria', 'polidipsia',
        'dor', 'cirurgia'
    ],
    'alvo': ['diagnostico']
}

# Mapeamentos alternativos de nomes de colunas
MAPEAMENTOS_COLUNAS = {
    # Identificação
    'ID': 'id',
    'Id': 'id',
    'codigo': 'id',
    'Data': 'data',
    'date': 'data',
    'Especie': 'especie',
    'Species': 'especie',
    'species': 'especie',
    'Raca': 'raca',
    'Raça': 'raca',
    'Breed': 'raca',
    'breed': 'raca',
    'Idade': 'idade_anos',
    'Age': 'idade_anos',
    'age': 'idade_anos',
    'idade': 'idade_anos',
    'Sexo': 'sexo',
    'Sex': 'sexo',
    'sex': 'sexo',
    'gender': 'sexo',
    
    # Exames
    'Hemoglobina': 'hemoglobina',
    'Hb': 'hemoglobina',
    'hemoglobin': 'hemoglobina',
    'Hematocrito': 'hematocrito',
    'Ht': 'hematocrito',
    'hematocrit': 'hematocrito',
    'Leucocitos': 'leucocitos',
    'Leucócitos': 'leucocitos',
    'WBC': 'leucocitos',
    'wbc': 'leucocitos',
    'Plaquetas': 'plaquetas',
    'PLT': 'plaquetas',
    'plt': 'plaquetas',
    'platelets': 'plaquetas',
    'Glicose': 'glicose',
    'glucose': 'glicose',
    'Glucose': 'glicose',
    'Ureia': 'ureia',
    'BUN': 'ureia',
    'bun': 'ureia',
    'Creatinina': 'creatinina',
    'creatinine': 'creatinina',
    'Creatinine': 'creatinina',
    'ALT': 'alt',
    'AST': 'ast',
    'Fosfatase_Alcalina': 'fosfatase_alcalina',
    'FA': 'fa',
    'ALP': 'fosfatase_alcalina',
    'alp': 'fosfatase_alcalina',
    'Proteinas_Totais': 'proteinas_totais',
    'Proteínas_Totais': 'proteinas_totais',
    'TP': 'proteinas_totais',
    'total_protein': 'proteinas_totais',
    'Albumina': 'albumina',
    'albumin': 'albumina',
    'Colesterol': 'colesterol',
    'cholesterol': 'colesterol',
    'Triglicerideos': 'triglicerideos',
    'Triglicerídeos': 'triglicerideos',
    'triglycerides': 'triglicerideos',
    
    # Sintomas
    'Febre': 'febre',
    'fever': 'febre',
    'Apatia': 'apatia',
    'apathy': 'apatia',
    'Perda_Peso': 'perda_peso',
    'weight_loss': 'perda_peso',
    'Vomito': 'vomito',
    'Vômito': 'vomito',
    'vomiting': 'vomito',
    'Diarreia': 'diarreia',
    'diarrhea': 'diarreia',
    'Tosse': 'tosse',
    'cough': 'tosse',
    'Letargia': 'letargia',
    'lethargy': 'letargia',
    'Feridas_Cutaneas': 'feridas_cutaneas',
    'skin_lesions': 'feridas_cutaneas',
    'Poliuria': 'poliuria',
    'polyuria': 'poliuria',
    'Polidipsia': 'polidipsia',
    'polydipsia': 'polidipsia',
    
    # Alvo
    'Diagnostico': 'diagnostico',
    'Diagnóstico': 'diagnostico',
    'diagnosis': 'diagnostico',
    'Diagnosis': 'diagnostico',
    'disease': 'diagnostico',
    'Disease': 'diagnostico',
    'outcome': 'diagnostico'
}


def listar_datasets_disponiveis():
    """
    Lista todos os datasets disponíveis na pasta data/
    
    Returns:
        dict: {nome: caminho}
    """
    data_dir = Path('data')
    datasets = {}
    
    if data_dir.exists():
        # Datasets REAIS baixados
        arquivos_reais = {
            'veterinary_realistic_dataset.csv': '🎯 Dataset Realista (1280 casos - Dados Clínicos Melhorados)',
            'veterinary_complete_real_dataset.csv': '🌟 Dataset Completo REAL (800 casos - Exames + Sintomas)',
            'veterinary_master_dataset.csv': '📊 Master Dataset (500 casos - Dados Clínicos Reais)',
            'clinical_veterinary_data.csv': '🏥 Clinical Veterinary Data (500 casos)',
            'laboratory_complete_panel.csv': '🧪 Laboratory Complete Panel (300 casos)',
            'uci_horse_colic.csv': '🐴 UCI Horse Colic (368 casos - Equinos)',
            'exemplo_vet.csv': '📚 Dataset Sintético Educacional (300 casos)'
        }
        
        for arquivo, descricao in arquivos_reais.items():
            caminho = data_dir / arquivo
            if caminho.exists():
                datasets[descricao] = caminho
    
    return datasets


def carregar_dataset_selecionado(caminho):
    """
    Carrega dataset selecionado
    
    Args:
        caminho: Path do arquivo
        
    Returns:
        pd.DataFrame ou None
    """
    try:
        return pd.read_csv(caminho)
    except Exception as e:
        st.error(f"Erro ao carregar dataset: {e}")
        return None


def carregar_arquivo(arquivo_upload):
    """
    Carrega arquivo CSV ou XLSX enviado pelo usuário
    
    Args:
        arquivo_upload: Objeto de upload do Streamlit
        
    Returns:
        pd.DataFrame ou dict de DataFrames (para XLSX com múltiplas abas)
    """
    try:
        nome_arquivo = arquivo_upload.name.lower()
        
        if nome_arquivo.endswith('.csv'):
            # Tentar diferentes encodings
            try:
                df = pd.read_csv(arquivo_upload, encoding='utf-8-sig')
            except:
                arquivo_upload.seek(0)
                try:
                    df = pd.read_csv(arquivo_upload, encoding='latin-1')
                except:
                    arquivo_upload.seek(0)
                    df = pd.read_csv(arquivo_upload, encoding='iso-8859-1')
            
            return df
        
        elif nome_arquivo.endswith(('.xlsx', '.xls')):
            # Carregar todas as abas
            df_dict = pd.read_excel(arquivo_upload, sheet_name=None, engine='openpyxl')
            
            # Se houver apenas uma aba, retornar DataFrame diretamente
            if len(df_dict) == 1:
                return list(df_dict.values())[0]
            
            return df_dict
        
        else:
            st.error("❌ Formato de arquivo não suportado. Use CSV ou XLSX.")
            return None
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar arquivo: {str(e)}")
        return None


def mapear_colunas_automatico(df):
    """
    Tenta mapear colunas automaticamente usando dicionário de mapeamentos
    
    Args:
        df: DataFrame original
        
    Returns:
        DataFrame com colunas mapeadas, dicionário de mapeamentos aplicados
    """
    colunas_mapeadas = {}
    df_novo = df.copy()
    
    for col_original in df.columns:
        col_limpa = col_original.strip()
        
        # Verificar se está no mapeamento
        if col_limpa in MAPEAMENTOS_COLUNAS:
            col_nova = MAPEAMENTOS_COLUNAS[col_limpa]
            colunas_mapeadas[col_original] = col_nova
        # Verificar se já está no formato correto
        elif col_limpa.lower() in [c.lower() for categoria in SCHEMA_COLUNAS.values() for c in categoria]:
            colunas_mapeadas[col_original] = col_limpa.lower()
    
    # Aplicar mapeamentos
    if colunas_mapeadas:
        df_novo = df_novo.rename(columns=colunas_mapeadas)
    
    return df_novo, colunas_mapeadas


def validar_schema(df, requer_diagnostico=True):
    """
    Valida se o DataFrame tem as colunas mínimas necessárias
    
    Args:
        df: DataFrame a validar
        requer_diagnostico: Se True, exige coluna 'diagnostico'
        
    Returns:
        (bool, list): (é_valido, lista_de_avisos)
    """
    avisos = []
    
    # Colunas obrigatórias mínimas
    obrigatorias = ['especie']
    
    # Verificar colunas obrigatórias
    for col in obrigatorias:
        if col not in df.columns:
            avisos.append(f"❌ Coluna obrigatória ausente: '{col}'")
    
    # Verificar se tem ao menos alguns exames ou sintomas
    exames_presentes = [c for c in SCHEMA_COLUNAS['exames'] if c in df.columns]
    sintomas_presentes = [c for c in SCHEMA_COLUNAS['sintomas'] if c in df.columns]
    
    if len(exames_presentes) == 0 and len(sintomas_presentes) == 0:
        avisos.append("⚠️ Nenhum exame ou sintoma identificado. Verifique os nomes das colunas.")
    
    # Verificar diagnóstico se necessário
    if requer_diagnostico and 'diagnostico' not in df.columns:
        avisos.append("⚠️ Coluna 'diagnostico' não encontrada. Necessária para treinamento de modelo.")
    
    # Verificar valores da coluna espécie
    if 'especie' in df.columns:
        especies_validas = ['Canina', 'Felina', 'Equina', 'canina', 'felina', 'equina']
        especies_invalidas = df[~df['especie'].isin(especies_validas)]['especie'].unique()
        if len(especies_invalidas) > 0:
            avisos.append(f"⚠️ Valores inválidos em 'especie': {especies_invalidas}")
    
    # Verificar valores de sexo
    if 'sexo' in df.columns:
        sexos_validos = ['M', 'F', 'm', 'f', 'Macho', 'Fêmea', 'male', 'female']
        sexos_invalidos = df[~df['sexo'].isin(sexos_validos)]['sexo'].unique()
        if len(sexos_invalidos) > 0:
            avisos.append(f"⚠️ Valores inválidos em 'sexo': {sexos_invalidos}")
    
    # É válido se não houver erros críticos (apenas avisos começam com ⚠️)
    erros_criticos = [a for a in avisos if a.startswith('❌')]
    e_valido = len(erros_criticos) == 0
    
    return e_valido, avisos


def padronizar_valores(df):
    """
    Padroniza valores de colunas categóricas
    
    Args:
        df: DataFrame a padronizar
        
    Returns:
        DataFrame padronizado
    """
    df_pad = df.copy()
    
    # Padronizar espécie
    if 'especie' in df_pad.columns:
        df_pad['especie'] = df_pad['especie'].str.capitalize()
    
    # Padronizar sexo
    if 'sexo' in df_pad.columns:
        mapa_sexo = {
            'macho': 'M', 'Macho': 'M', 'male': 'M', 'Male': 'M', 'm': 'M',
            'femea': 'F', 'Fêmea': 'F', 'fêmea': 'F', 'female': 'F', 'Female': 'F', 'f': 'F'
        }
        df_pad['sexo'] = df_pad['sexo'].replace(mapa_sexo)
    
    # Converter sintomas para binário (0/1) se forem strings
    for sintoma in SCHEMA_COLUNAS['sintomas']:
        if sintoma in df_pad.columns:
            if df_pad[sintoma].dtype == 'object':
                # Converter Yes/No, Sim/Não, etc para 1/0
                mapa_sim_nao = {
                    'yes': 1, 'Yes': 1, 'YES': 1, 'sim': 1, 'Sim': 1, 'SIM': 1,
                    'no': 0, 'No': 0, 'NO': 0, 'não': 0, 'Não': 0, 'NÃO': 0,
                    'true': 1, 'True': 1, 'TRUE': 1,
                    'false': 0, 'False': 0, 'FALSE': 0
                }
                df_pad[sintoma] = df_pad[sintoma].replace(mapa_sim_nao)
                df_pad[sintoma] = pd.to_numeric(df_pad[sintoma], errors='coerce').fillna(0).astype(int)
    
    return df_pad


def salvar_dataset(df, nome_arquivo='dataset_vet.csv'):
    """
    Salva DataFrame na pasta data/
    
    Args:
        df: DataFrame a salvar
        nome_arquivo: Nome do arquivo
        
    Returns:
        Path do arquivo salvo
    """
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    caminho = data_dir / nome_arquivo
    df.to_csv(caminho, index=False, encoding='utf-8-sig')
    
    return caminho


def carregar_dataset_exemplo():
    """
    Carrega o dataset master (dados reais) ou exemplo
    
    Returns:
        pd.DataFrame ou None
    """
    # Prioridade: Dataset Realista > Completo > Master > Clinical > Exemplo sintético
    opcoes = [
        Path('data/veterinary_realistic_dataset.csv'),      # MELHORADO: Dados mais realistas
        Path('data/veterinary_complete_real_dataset.csv'),  # Com exames + sintomas
        Path('data/veterinary_master_dataset.csv'),
        Path('data/clinical_veterinary_data.csv'),
        Path('data/exemplo_vet.csv')
    ]
    
    for caminho in opcoes:
        if caminho.exists():
            st.info(f"📂 Carregando: {caminho.name}")
            return pd.read_csv(caminho)
    
    st.warning("⚠️ Nenhum dataset encontrado. Execute: python download_real_datasets.py")
    return None


def obter_info_dataset(df):
    """
    Retorna informações resumidas sobre o dataset
    
    Args:
        df: DataFrame
        
    Returns:
        dict com informações
    """
    info = {
        'n_registros': len(df),
        'n_colunas': len(df.columns),
        'especies': df['especie'].value_counts().to_dict() if 'especie' in df.columns else {},
        'diagnosticos': df['diagnostico'].value_counts().to_dict() if 'diagnostico' in df.columns else {},
        'colunas_ausentes': df.isnull().sum()[df.isnull().sum() > 0].to_dict(),
        'exames_disponiveis': [c for c in SCHEMA_COLUNAS['exames'] if c in df.columns],
        'sintomas_disponiveis': [c for c in SCHEMA_COLUNAS['sintomas'] if c in df.columns]
    }
    
    return info


def exportar_para_download(df, formato='csv'):
    """
    Prepara DataFrame para download
    
    Args:
        df: DataFrame
        formato: 'csv' ou 'xlsx'
        
    Returns:
        bytes para download
    """
    if formato == 'csv':
        return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    
    elif formato == 'xlsx':
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Dados')
        return output.getvalue()
