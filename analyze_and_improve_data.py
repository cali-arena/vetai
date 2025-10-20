"""
Análise e melhoria da qualidade dos dados veterinários
Tornar os dados mais realistas e as hipóteses mais precisas
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("=" * 70)
print("🔍 ANÁLISE E MELHORIA DOS DADOS VETERINÁRIOS")
print("=" * 70)

# Carregar dados atuais
df = pd.read_csv('data/veterinary_complete_real_dataset.csv')

print(f"\n📊 DADOS ATUAIS:")
print(f"   Registros: {len(df)}")
print(f"   Colunas: {len(df.columns)}")

# Análise da qualidade dos dados
print(f"\n🔍 ANÁLISE DE QUALIDADE:")

# Verificar casos de doença renal
drc = df[df['diagnostico'] == 'Doença Renal Crônica']
print(f"\n🏥 DOENÇA RENAL CRÔNICA ({len(drc)} casos):")
print(f"   Creatinina média: {drc['creatinina'].mean():.2f} (normal: 0.5-1.6)")
print(f"   Ureia média: {drc['ureia'].mean():.2f} (normal: 20-50)")
print(f"   Apatia: {drc['apatia'].mean():.1%}")
print(f"   Poliúria: {drc['poliuria'].mean():.1%}")
print(f"   Polidipsia: {drc['polidipsia'].mean():.1%}")

# Verificar casos de diabetes
diabetes = df[df['diagnostico'] == 'Diabetes Mellitus']
print(f"\n🍯 DIABETES MELLITUS ({len(diabetes)} casos):")
print(f"   Glicose média: {diabetes['glicose'].mean():.2f} (normal: 70-120)")
print(f"   Poliúria: {diabetes['poliuria'].mean():.1%}")
print(f"   Polidipsia: {diabetes['polidipsia'].mean():.1%}")
print(f"   Perda de peso: {diabetes['perda_peso'].mean():.1%}")

# Verificar casos saudáveis
saudavel = df[df['diagnostico'] == 'Saudável']
print(f"\n✅ ANIMAIS SAUDÁVEIS ({len(saudavel)} casos):")
print(f"   Creatinina média: {saudavel['creatinina'].mean():.2f}")
print(f"   Glicose média: {saudavel['glicose'].mean():.2f}")
print(f"   Apatia: {saudavel['apatia'].mean():.1%}")
print(f"   Febre: {saudavel['febre'].mean():.1%}")

# Identificar problemas
print(f"\n⚠️ PROBLEMAS IDENTIFICADOS:")

# 1. Valores de creatinina muito altos para casos saudáveis
creat_saudavel_alta = saudavel[saudavel['creatinina'] > 1.6]
if len(creat_saudavel_alta) > 0:
    print(f"   - {len(creat_saudavel_alta)} animais 'saudáveis' com creatinina > 1.6")

# 2. Valores de glicose muito altos para casos saudáveis
glic_saudavel_alta = saudavel[saudavel['glicose'] > 120]
if len(glic_saudavel_alta) > 0:
    print(f"   - {len(glic_saudavel_alta)} animais 'saudáveis' com glicose > 120")

# 3. Casos de doença renal com valores normais
drc_normal = drc[(drc['creatinina'] <= 1.6) & (drc['ureia'] <= 50)]
if len(drc_normal) > 0:
    print(f"   - {len(drc_normal)} casos de DRC com valores laboratoriais normais")

# 4. Casos de diabetes com glicose normal
diab_normal = diabetes[diabetes['glicose'] <= 120]
if len(diab_normal) > 0:
    print(f"   - {len(diab_normal)} casos de diabetes com glicose normal")

print(f"\n🔧 CRIANDO DADOS MAIS REALISTAS...")

# Criar dataset melhorado
np.random.seed(42)  # Para reprodutibilidade

# Função para gerar valores mais realistas
def gerar_valores_realistas(diagnostico, especie, n_casos):
    """Gera valores mais realistas baseados no diagnóstico"""
    
    dados = []
    
    for i in range(n_casos):
        # Valores base normais
        if especie == 'Canina':
            hemoglobina_base = np.random.normal(15, 1.5)
            hematocrito_base = np.random.normal(45, 4)
            leucocitos_base = np.random.normal(12, 3)
            glicose_base = np.random.normal(95, 15)
            ureia_base = np.random.normal(35, 8)
            creatinina_base = np.random.normal(1.0, 0.3)
            alt_base = np.random.normal(50, 20)
            albumina_base = np.random.normal(3.2, 0.3)
        else:  # Felina
            hemoglobina_base = np.random.normal(12, 1.5)
            hematocrito_base = np.random.normal(37, 3)
            leucocitos_base = np.random.normal(12, 4)
            glicose_base = np.random.normal(110, 20)
            ureia_base = np.random.normal(45, 10)
            creatinina_base = np.random.normal(1.4, 0.4)
            alt_base = np.random.normal(45, 15)
            albumina_base = np.random.normal(3.4, 0.4)
        
        # Sintomas base (baixa prevalência para saudáveis)
        sintomas_base = {
            'febre': 0.05, 'apatia': 0.10, 'perda_peso': 0.02, 'vomito': 0.05,
            'diarreia': 0.03, 'tosse': 0.02, 'letargia': 0.08, 'feridas_cutaneas': 0.01,
            'poliuria': 0.02, 'polidipsia': 0.03
        }
        
        # Ajustar valores baseado no diagnóstico
        if diagnostico == 'Saudável':
            # Manter valores normais
            pass
            
        elif diagnostico == 'Doença Renal Crônica':
            creatinina_base *= np.random.uniform(2.5, 4.5)  # 2.5-4.5x normal
            ureia_base *= np.random.uniform(2.0, 3.5)       # 2-3.5x normal
            albumina_base *= np.random.uniform(0.6, 0.8)    # Baixa albumina
            hemoglobina_base *= np.random.uniform(0.7, 0.9) # Anemia
            
            sintomas_base = {
                'febre': 0.10, 'apatia': 0.85, 'perda_peso': 0.70, 'vomito': 0.60,
                'diarreia': 0.30, 'tosse': 0.05, 'letargia': 0.75, 'feridas_cutaneas': 0.10,
                'poliuria': 0.90, 'polidipsia': 0.90
            }
            
        elif diagnostico == 'Diabetes Mellitus':
            glicose_base *= np.random.uniform(2.5, 4.0)     # 2.5-4x normal
            
            sintomas_base = {
                'febre': 0.05, 'apatia': 0.50, 'perda_peso': 0.70, 'vomito': 0.30,
                'diarreia': 0.10, 'tosse': 0.05, 'letargia': 0.60, 'feridas_cutaneas': 0.30,
                'poliuria': 0.95, 'polidipsia': 0.95
            }
            
        elif diagnostico == 'Doença Periodontal':
            leucocitos_base *= np.random.uniform(1.3, 2.0)  # Leucocitose
            
            sintomas_base = {
                'febre': 0.20, 'apatia': 0.40, 'perda_peso': 0.30, 'vomito': 0.20,
                'diarreia': 0.10, 'tosse': 0.05, 'letargia': 0.30, 'feridas_cutaneas': 0.05,
                'poliuria': 0.02, 'polidipsia': 0.05
            }
            
        elif diagnostico == 'Otite':
            leucocitos_base *= np.random.uniform(1.2, 1.8)  # Leucocitose leve
            
            sintomas_base = {
                'febre': 0.30, 'apatia': 0.60, 'perda_peso': 0.20, 'vomito': 0.10,
                'diarreia': 0.05, 'tosse': 0.05, 'letargia': 0.50, 'feridas_cutaneas': 0.05,
                'poliuria': 0.02, 'polidipsia': 0.02
            }
            
        elif diagnostico == 'Dermatite':
            leucocitos_base *= np.random.uniform(1.1, 1.5)  # Leucocitose leve
            
            sintomas_base = {
                'febre': 0.10, 'apatia': 0.40, 'perda_peso': 0.10, 'vomito': 0.05,
                'diarreia': 0.05, 'tosse': 0.02, 'letargia': 0.30, 'feridas_cutaneas': 0.95,
                'poliuria': 0.02, 'polidipsia': 0.02
            }
        
        # Gerar sintomas
        sintomas = {}
        for sintoma, prob in sintomas_base.items():
            sintomas[sintoma] = np.random.choice([0, 1], p=[1-prob, prob])
        
        # Criar registro
        registro = {
            'id': f'VET{i+1:04d}',
            'especie': especie,
            'raca': np.random.choice(['SRD', 'Labrador', 'Persa', 'Siamês', 'Poodle', 'Maine Coon']),
            'idade_anos': round(np.random.gamma(3, 3), 1),
            'sexo': np.random.choice(['M', 'F']),
            'hemoglobina': round(max(hemoglobina_base, 5), 2),
            'hematocrito': round(max(hematocrito_base, 20), 2),
            'leucocitos': round(max(leucocitos_base, 2), 2),
            'glicose': round(max(glicose_base, 50), 2),
            'ureia': round(max(ureia_base, 10), 2),
            'creatinina': round(max(creatinina_base, 0.2), 2),
            'alt': round(max(alt_base, 5), 2),
            'albumina': round(max(albumina_base, 1.0), 2),
            **sintomas,
            'diagnostico': diagnostico
        }
        
        dados.append(registro)
    
    return dados

# Gerar dataset melhorado
print(f"\n📊 Gerando dataset melhorado...")

dados_melhorados = []

# Distribuição mais realista
distribuicao = {
    'Saudável': 200,
    'Doença Renal Crônica': 120,
    'Diabetes Mellitus': 100,
    'Doença Periodontal': 90,
    'Otite': 80,
    'Dermatite': 70,
    'Obesidade': 60,
    'Artrose': 50,
    'Neoplasia': 20,
    'Doença Cardíaca': 10
}

# Gerar casos por espécie
especies = ['Canina', 'Felina']
for especie in especies:
    for diagnostico, n_casos in distribuicao.items():
        # Ajustar número de casos por espécie
        if especie == 'Felina':
            n_casos = int(n_casos * 0.6)  # 60% dos casos são felinos
        
        casos_especie = gerar_valores_realistas(diagnostico, especie, n_casos)
        dados_melhorados.extend(casos_especie)

# Criar DataFrame
df_melhorado = pd.DataFrame(dados_melhorados)

# Salvar dataset melhorado
output_path = Path('data/veterinary_realistic_dataset.csv')
df_melhorado.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"\n✅ DATASET MELHORADO CRIADO!")
print(f"   📊 Total: {len(df_melhorado)} registros")
print(f"   🐾 Canina: {len(df_melhorado[df_melhorado['especie'] == 'Canina'])} casos")
print(f"   🐱 Felina: {len(df_melhorado[df_melhorado['especie'] == 'Felina'])} casos")
print(f"   💾 Salvo em: {output_path}")

# Análise do dataset melhorado
print(f"\n🔍 ANÁLISE DO DATASET MELHORADO:")

# Verificar doença renal
drc_melhorado = df_melhorado[df_melhorado['diagnostico'] == 'Doença Renal Crônica']
print(f"\n🏥 DOENÇA RENAL CRÔNICA ({len(drc_melhorado)} casos):")
print(f"   Creatinina média: {drc_melhorado['creatinina'].mean():.2f}")
print(f"   Ureia média: {drc_melhorado['ureia'].mean():.2f}")
print(f"   Apatia: {drc_melhorado['apatia'].mean():.1%}")
print(f"   Poliúria: {drc_melhorado['poliuria'].mean():.1%}")

# Verificar diabetes
diab_melhorado = df_melhorado[df_melhorado['diagnostico'] == 'Diabetes Mellitus']
print(f"\n🍯 DIABETES MELLITUS ({len(diab_melhorado)} casos):")
print(f"   Glicose média: {diab_melhorado['glicose'].mean():.2f}")
print(f"   Poliúria: {diab_melhorado['poliuria'].mean():.1%}")
print(f"   Polidipsia: {diab_melhorado['polidipsia'].mean():.1%}")

# Verificar saudáveis
saud_melhorado = df_melhorado[df_melhorado['diagnostico'] == 'Saudável']
print(f"\n✅ ANIMAIS SAUDÁVEIS ({len(saud_melhorado)} casos):")
print(f"   Creatinina média: {saud_melhorado['creatinina'].mean():.2f}")
print(f"   Glicose média: {saud_melhorado['glicose'].mean():.2f}")
print(f"   Apatia: {saud_melhorado['apatia'].mean():.1%}")

print(f"\n📈 DISTRIBUIÇÃO FINAL:")
print(df_melhorado['diagnostico'].value_counts())

print(f"\n" + "=" * 70)
print("✅ DADOS MELHORADOS CRIADOS COM SUCESSO!")
print("=" * 70)
