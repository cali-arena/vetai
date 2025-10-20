"""
Script para gerar dataset sintético realista de dados veterinários
Simula exames laboratoriais, sintomas e diagnósticos para cães e gatos
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Seed para reprodutibilidade
np.random.seed(42)
random.seed(42)

# Configurações
N_SAMPLES = 300

# Listas de opções
ESPECIES = ['Canina', 'Felina']
RACAS_CANINAS = ['SRD', 'Labrador', 'Golden Retriever', 'Pastor Alemão', 'Poodle', 'Bulldog', 'Beagle', 'Yorkshire']
RACAS_FELINAS = ['SRD', 'Persa', 'Siamês', 'Maine Coon', 'Bengal', 'Ragdoll', 'Sphynx']
SEXOS = ['M', 'F']

# Diagnósticos possíveis
DIAGNOSTICOS = [
    'Saudável',
    'Doença Renal Crônica',
    'Diabetes Mellitus',
    'Hepatopatia',
    'Anemia',
    'Leishmaniose',
    'Cinomose',
    'Pancreatite',
    'Hipertireoidismo',
    'Dermatite',
    'Gastroenterite'
]

# Faixas de referência normais por espécie
REFERENCIAS = {
    'Canina': {
        'hemoglobina': (12, 18),
        'hematocrito': (37, 55),
        'leucocitos': (6, 17),
        'plaquetas': (200, 500),
        'glicose': (70, 120),
        'ureia': (20, 50),
        'creatinina': (0.5, 1.6),
        'alt': (10, 100),
        'ast': (15, 50),
        'fosfatase_alcalina': (20, 150),
        'proteinas_totais': (5.4, 7.5),
        'albumina': (2.5, 3.8),
        'colesterol': (130, 270),
        'triglicerideos': (20, 150)
    },
    'Felina': {
        'hemoglobina': (9, 15),
        'hematocrito': (30, 45),
        'leucocitos': (5.5, 19.5),
        'plaquetas': (300, 700),
        'glicose': (70, 150),
        'ureia': (30, 60),
        'creatinina': (0.8, 2.0),
        'alt': (10, 80),
        'ast': (10, 50),
        'fosfatase_alcalina': (10, 80),
        'proteinas_totais': (6.0, 8.5),
        'albumina': (2.5, 3.9),
        'colesterol': (90, 200),
        'triglicerideos': (25, 100)
    }
}

def gerar_valor_normal(especie, exame, variacao=0.15):
    """Gera valor dentro da faixa normal com pequena variação"""
    min_val, max_val = REFERENCIAS[especie][exame]
    media = (min_val + max_val) / 2
    return np.random.normal(media, (max_val - min_val) * variacao)

def gerar_valor_anormal(especie, exame, tipo='alto', intensidade=1.5):
    """Gera valor fora da faixa normal"""
    min_val, max_val = REFERENCIAS[especie][exame]
    if tipo == 'alto':
        return max_val * np.random.uniform(intensidade, intensidade + 0.5)
    else:
        return min_val * np.random.uniform(0.3, 0.7)

def gerar_caso_saudavel(especie):
    """Gera caso saudável com valores normais"""
    caso = {}
    for exame in REFERENCIAS[especie].keys():
        caso[exame] = gerar_valor_normal(especie, exame)
    
    # Sintomas mínimos ou ausentes
    caso.update({
        'febre': 0,
        'apatia': np.random.choice([0, 0, 0, 1], p=[0.9, 0.05, 0.05, 0.0]),
        'perda_peso': 0,
        'vomito': 0,
        'diarreia': 0,
        'tosse': 0,
        'letargia': 0,
        'feridas_cutaneas': 0,
        'poliuria': 0,
        'polidipsia': 0
    })
    
    return caso

def gerar_caso_doenca_renal(especie):
    """Gera caso de doença renal crônica"""
    caso = {}
    
    # Valores alterados característicos
    caso['creatinina'] = gerar_valor_anormal(especie, 'creatinina', 'alto', 2.0)
    caso['ureia'] = gerar_valor_anormal(especie, 'ureia', 'alto', 1.8)
    caso['fosfatase_alcalina'] = gerar_valor_anormal(especie, 'fosfatase_alcalina', 'alto', 1.3)
    
    # Anemia associada
    caso['hemoglobina'] = gerar_valor_anormal(especie, 'hemoglobina', 'baixo')
    caso['hematocrito'] = gerar_valor_anormal(especie, 'hematocrito', 'baixo')
    
    # Demais valores normais ou levemente alterados
    for exame in ['leucocitos', 'plaquetas', 'glicose', 'alt', 'ast', 
                  'proteinas_totais', 'albumina', 'colesterol', 'triglicerideos']:
        caso[exame] = gerar_valor_normal(especie, exame, 0.2)
    
    # Sintomas característicos
    caso.update({
        'febre': 0,
        'apatia': np.random.choice([0, 1], p=[0.2, 0.8]),
        'perda_peso': np.random.choice([0, 1], p=[0.3, 0.7]),
        'vomito': np.random.choice([0, 1], p=[0.4, 0.6]),
        'diarreia': np.random.choice([0, 1], p=[0.7, 0.3]),
        'tosse': 0,
        'letargia': np.random.choice([0, 1], p=[0.3, 0.7]),
        'feridas_cutaneas': 0,
        'poliuria': np.random.choice([0, 1], p=[0.2, 0.8]),
        'polidipsia': np.random.choice([0, 1], p=[0.2, 0.8])
    })
    
    return caso

def gerar_caso_diabetes(especie):
    """Gera caso de diabetes mellitus"""
    caso = {}
    
    # Hiperglicemia
    caso['glicose'] = gerar_valor_anormal(especie, 'glicose', 'alto', 2.5)
    caso['triglicerideos'] = gerar_valor_anormal(especie, 'triglicerideos', 'alto', 1.5)
    caso['colesterol'] = gerar_valor_anormal(especie, 'colesterol', 'alto', 1.3)
    
    # Possível elevação de enzimas hepáticas
    caso['alt'] = gerar_valor_normal(especie, 'alt', 0.3)
    caso['ast'] = gerar_valor_normal(especie, 'ast', 0.3)
    
    # Demais normais
    for exame in ['hemoglobina', 'hematocrito', 'leucocitos', 'plaquetas', 
                  'ureia', 'creatinina', 'fosfatase_alcalina', 
                  'proteinas_totais', 'albumina']:
        caso[exame] = gerar_valor_normal(especie, exame)
    
    caso.update({
        'febre': 0,
        'apatia': np.random.choice([0, 1], p=[0.5, 0.5]),
        'perda_peso': np.random.choice([0, 1], p=[0.3, 0.7]),
        'vomito': np.random.choice([0, 1], p=[0.7, 0.3]),
        'diarreia': 0,
        'tosse': 0,
        'letargia': np.random.choice([0, 1], p=[0.4, 0.6]),
        'feridas_cutaneas': np.random.choice([0, 1], p=[0.7, 0.3]),
        'poliuria': np.random.choice([0, 1], p=[0.1, 0.9]),
        'polidipsia': np.random.choice([0, 1], p=[0.1, 0.9])
    })
    
    return caso

def gerar_caso_hepatopatia(especie):
    """Gera caso de doença hepática"""
    caso = {}
    
    # Enzimas hepáticas elevadas
    caso['alt'] = gerar_valor_anormal(especie, 'alt', 'alto', 3.0)
    caso['ast'] = gerar_valor_anormal(especie, 'ast', 'alto', 2.5)
    caso['fosfatase_alcalina'] = gerar_valor_anormal(especie, 'fosfatase_alcalina', 'alto', 2.0)
    
    # Hipoalbuminemia
    caso['albumina'] = gerar_valor_anormal(especie, 'albumina', 'baixo')
    caso['proteinas_totais'] = gerar_valor_anormal(especie, 'proteinas_totais', 'baixo')
    
    # Colesterol pode estar alterado
    caso['colesterol'] = gerar_valor_normal(especie, 'colesterol', 0.4)
    
    # Demais normais ou levemente alterados
    for exame in ['hemoglobina', 'hematocrito', 'leucocitos', 'plaquetas', 
                  'glicose', 'ureia', 'creatinina', 'triglicerideos']:
        caso[exame] = gerar_valor_normal(especie, exame, 0.2)
    
    caso.update({
        'febre': np.random.choice([0, 1], p=[0.7, 0.3]),
        'apatia': np.random.choice([0, 1], p=[0.3, 0.7]),
        'perda_peso': np.random.choice([0, 1], p=[0.4, 0.6]),
        'vomito': np.random.choice([0, 1], p=[0.3, 0.7]),
        'diarreia': np.random.choice([0, 1], p=[0.5, 0.5]),
        'tosse': 0,
        'letargia': np.random.choice([0, 1], p=[0.3, 0.7]),
        'feridas_cutaneas': 0,
        'poliuria': 0,
        'polidipsia': 0
    })
    
    return caso

def gerar_caso_anemia(especie):
    """Gera caso de anemia"""
    caso = {}
    
    # Hemograma alterado
    caso['hemoglobina'] = gerar_valor_anormal(especie, 'hemoglobina', 'baixo')
    caso['hematocrito'] = gerar_valor_anormal(especie, 'hematocrito', 'baixo')
    
    # Demais normais
    for exame in ['leucocitos', 'plaquetas', 'glicose', 'ureia', 'creatinina', 
                  'alt', 'ast', 'fosfatase_alcalina', 
                  'proteinas_totais', 'albumina', 'colesterol', 'triglicerideos']:
        caso[exame] = gerar_valor_normal(especie, exame)
    
    caso.update({
        'febre': 0,
        'apatia': np.random.choice([0, 1], p=[0.3, 0.7]),
        'perda_peso': np.random.choice([0, 1], p=[0.5, 0.5]),
        'vomito': 0,
        'diarreia': 0,
        'tosse': 0,
        'letargia': np.random.choice([0, 1], p=[0.2, 0.8]),
        'feridas_cutaneas': 0,
        'poliuria': 0,
        'polidipsia': 0
    })
    
    return caso

def gerar_caso_leishmaniose(especie):
    """Gera caso de leishmaniose (mais comum em caninos)"""
    caso = {}
    
    # Alterações características
    caso['proteinas_totais'] = gerar_valor_anormal(especie, 'proteinas_totais', 'alto', 1.3)
    caso['albumina'] = gerar_valor_anormal(especie, 'albumina', 'baixo')
    caso['creatinina'] = gerar_valor_normal(especie, 'creatinina', 0.4)
    caso['ureia'] = gerar_valor_normal(especie, 'ureia', 0.4)
    
    # Anemia leve
    caso['hemoglobina'] = gerar_valor_anormal(especie, 'hemoglobina', 'baixo')
    caso['hematocrito'] = gerar_valor_anormal(especie, 'hematocrito', 'baixo')
    
    # Demais normais
    for exame in ['leucocitos', 'plaquetas', 'glicose', 
                  'alt', 'ast', 'fosfatase_alcalina', 
                  'colesterol', 'triglicerideos']:
        caso[exame] = gerar_valor_normal(especie, exame, 0.2)
    
    caso.update({
        'febre': np.random.choice([0, 1], p=[0.5, 0.5]),
        'apatia': np.random.choice([0, 1], p=[0.3, 0.7]),
        'perda_peso': np.random.choice([0, 1], p=[0.2, 0.8]),
        'vomito': 0,
        'diarreia': 0,
        'tosse': 0,
        'letargia': np.random.choice([0, 1], p=[0.4, 0.6]),
        'feridas_cutaneas': np.random.choice([0, 1], p=[0.2, 0.8]),
        'poliuria': 0,
        'polidipsia': 0
    })
    
    return caso

def gerar_caso_generico(especie, diagnostico):
    """Gera caso genérico para outras doenças"""
    caso = {}
    
    # Valores com mais variação
    for exame in REFERENCIAS[especie].keys():
        caso[exame] = gerar_valor_normal(especie, exame, 0.3)
    
    # Sintomas aleatórios
    caso.update({
        'febre': np.random.choice([0, 1], p=[0.6, 0.4]),
        'apatia': np.random.choice([0, 1], p=[0.5, 0.5]),
        'perda_peso': np.random.choice([0, 1], p=[0.6, 0.4]),
        'vomito': np.random.choice([0, 1], p=[0.6, 0.4]),
        'diarreia': np.random.choice([0, 1], p=[0.6, 0.4]),
        'tosse': np.random.choice([0, 1], p=[0.7, 0.3]),
        'letargia': np.random.choice([0, 1], p=[0.5, 0.5]),
        'feridas_cutaneas': np.random.choice([0, 1], p=[0.7, 0.3]),
        'poliuria': np.random.choice([0, 1], p=[0.8, 0.2]),
        'polidipsia': np.random.choice([0, 1], p=[0.8, 0.2])
    })
    
    return caso

# Geração de casos
dados = []

# Distribuição de diagnósticos (mais saudáveis, menos doenças raras)
dist_diagnosticos = [0.30, 0.15, 0.12, 0.10, 0.08, 0.08, 0.05, 0.04, 0.03, 0.03, 0.02]

for i in range(N_SAMPLES):
    # Selecionar diagnóstico
    diagnostico = np.random.choice(DIAGNOSTICOS, p=dist_diagnosticos)
    
    # Selecionar espécie
    especie = random.choice(ESPECIES)
    
    # Selecionar raça
    if especie == 'Canina':
        raca = random.choice(RACAS_CANINAS)
    else:
        raca = random.choice(RACAS_FELINAS)
    
    # Gerar caso baseado no diagnóstico
    if diagnostico == 'Saudável':
        caso = gerar_caso_saudavel(especie)
    elif diagnostico == 'Doença Renal Crônica':
        caso = gerar_caso_doenca_renal(especie)
    elif diagnostico == 'Diabetes Mellitus':
        caso = gerar_caso_diabetes(especie)
    elif diagnostico == 'Hepatopatia':
        caso = gerar_caso_hepatopatia(especie)
    elif diagnostico == 'Anemia':
        caso = gerar_caso_anemia(especie)
    elif diagnostico == 'Leishmaniose':
        caso = gerar_caso_leishmaniose(especie)
    else:
        caso = gerar_caso_generico(especie, diagnostico)
    
    # Adicionar metadados
    caso['id'] = f'VET{i+1:04d}'
    caso['data'] = (datetime.now() - timedelta(days=random.randint(0, 730))).strftime('%Y-%m-%d')
    caso['especie'] = especie
    caso['raca'] = raca
    caso['sexo'] = random.choice(SEXOS)
    caso['idade_anos'] = np.random.uniform(0.5, 15)
    caso['diagnostico'] = diagnostico
    
    dados.append(caso)

# Criar DataFrame
df = pd.DataFrame(dados)

# Reordenar colunas
colunas_ordem = ['id', 'data', 'especie', 'raca', 'sexo', 'idade_anos',
                 'hemoglobina', 'hematocrito', 'leucocitos', 'plaquetas',
                 'glicose', 'ureia', 'creatinina',
                 'alt', 'ast', 'fosfatase_alcalina',
                 'proteinas_totais', 'albumina', 'colesterol', 'triglicerideos',
                 'febre', 'apatia', 'perda_peso', 'vomito', 'diarreia',
                 'tosse', 'letargia', 'feridas_cutaneas', 'poliuria', 'polidipsia',
                 'diagnostico']

df = df[colunas_ordem]

# Arredondar valores numéricos
colunas_numericas = ['hemoglobina', 'hematocrito', 'leucocitos', 'plaquetas',
                     'glicose', 'ureia', 'creatinina', 'alt', 'ast', 
                     'fosfatase_alcalina', 'proteinas_totais', 'albumina', 
                     'colesterol', 'triglicerideos', 'idade_anos']

for col in colunas_numericas:
    df[col] = df[col].round(2)

# Salvar
df.to_csv('data/exemplo_vet.csv', index=False, encoding='utf-8-sig')

print(f"✅ Dataset sintético gerado com sucesso!")
print(f"📊 Total de registros: {len(df)}")
print(f"\n📈 Distribuição de diagnósticos:")
print(df['diagnostico'].value_counts())
print(f"\n🐾 Distribuição de espécies:")
print(df['especie'].value_counts())
print(f"\n💾 Arquivo salvo em: data/exemplo_vet.csv")

