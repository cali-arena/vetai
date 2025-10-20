"""
Sistema de Regras Clínicas para Geração de Hipóteses Diagnósticas
Baseado em critérios clínicos reais e literatura veterinária
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

# ============================================================================
# REGRAS CLÍNICAS PARA DIAGNÓSTICO DIFERENCIAL
# ============================================================================

def gerar_hipoteses_clinicas(sintomas: Dict, exames: Dict, especie: str) -> List[Dict]:
    """
    Gera hipóteses diagnósticas baseadas em regras clínicas
    
    Args:
        sintomas: Dict com sintomas (0/1)
        exames: Dict com valores laboratoriais
        especie: "Canina" ou "Felina"
    
    Returns:
        Lista de hipóteses com scores e critérios
    """
    
    hipoteses = []
    
    # Faixas de referência por espécie
    if especie == "Canina":
        refs = {
            'creatinina': (0.5, 1.6),
            'ureia': (20, 50),
            'glicose': (70, 120),
            'hemoglobina': (12, 18),
            'hematocrito': (37, 55),
            'leucocitos': (6, 17),
            'alt': (10, 100),
            'albumina': (2.5, 3.8)
        }
    else:  # Felina
        refs = {
            'creatinina': (0.8, 2.0),
            'ureia': (30, 60),
            'glicose': (70, 150),
            'hemoglobina': (9, 15),
            'hematocrito': (30, 45),
            'leucocitos': (5.5, 19.5),
            'alt': (10, 80),
            'albumina': (2.5, 3.9)
        }
    
    # ============================================================================
    # REGRAS PARA DOENÇA RENAL CRÔNICA
    # ============================================================================
    if _avaliar_doenca_renal(sintomas, exames, refs):
        score = _calcular_score_renal(sintomas, exames, refs)
        hipoteses.append({
            'diagnostico': 'Doença Renal Crônica',
            'score': score,
            'criteria': _get_criteria_renal(sintomas, exames, refs),
            'prioridade': 'ALTA' if score > 0.7 else 'MÉDIA'
        })
    
    # ============================================================================
    # REGRAS PARA DIABETES MELLITUS
    # ============================================================================
    if _avaliar_diabetes(sintomas, exames, refs):
        score = _calcular_score_diabetes(sintomas, exames, refs)
        hipoteses.append({
            'diagnostico': 'Diabetes Mellitus',
            'score': score,
            'criteria': _get_criteria_diabetes(sintomas, exames, refs),
            'prioridade': 'ALTA' if score > 0.7 else 'MÉDIA'
        })
    
    # ============================================================================
    # REGRAS PARA DOENÇA PERIODONTAL
    # ============================================================================
    if _avaliar_periodontal(sintomas, exames, refs):
        score = _calcular_score_periodontal(sintomas, exames, refs)
        hipoteses.append({
            'diagnostico': 'Doença Periodontal',
            'score': score,
            'criteria': _get_criteria_periodontal(sintomas, exames, refs),
            'prioridade': 'MÉDIA' if score > 0.5 else 'BAIXA'
        })
    
    # ============================================================================
    # REGRAS PARA OTITE
    # ============================================================================
    if _avaliar_otite(sintomas, exames, refs):
        score = _calcular_score_otite(sintomas, exames, refs)
        hipoteses.append({
            'diagnostico': 'Otite',
            'score': score,
            'criteria': _get_criteria_otite(sintomas, exames, refs),
            'prioridade': 'MÉDIA' if score > 0.6 else 'BAIXA'
        })
    
    # ============================================================================
    # REGRAS PARA DERMATITE
    # ============================================================================
    if _avaliar_dermatite(sintomas, exames, refs):
        score = _calcular_score_dermatite(sintomas, exames, refs)
        hipoteses.append({
            'diagnostico': 'Dermatite',
            'score': score,
            'criteria': _get_criteria_dermatite(sintomas, exames, refs),
            'prioridade': 'MÉDIA' if score > 0.7 else 'BAIXA'
        })
    
    # ============================================================================
    # REGRAS PARA DOENÇA CARDÍACA
    # ============================================================================
    if _avaliar_cardiopatia(sintomas, exames, refs):
        score = _calcular_score_cardiopatia(sintomas, exames, refs)
        hipoteses.append({
            'diagnostico': 'Doença Cardíaca',
            'score': score,
            'criteria': _get_criteria_cardiopatia(sintomas, exames, refs),
            'prioridade': 'ALTA' if score > 0.6 else 'MÉDIA'
        })
    
    # ============================================================================
    # REGRAS PARA NEOPLASIA
    # ============================================================================
    if _avaliar_neoplasia(sintomas, exames, refs):
        score = _calcular_score_neoplasia(sintomas, exames, refs)
        hipoteses.append({
            'diagnostico': 'Neoplasia',
            'score': score,
            'criteria': _get_criteria_neoplasia(sintomas, exames, refs),
            'prioridade': 'ALTA' if score > 0.5 else 'MÉDIA'
        })
    
    # ============================================================================
    # REGRAS PARA OBESIDADE
    # ============================================================================
    if _avaliar_obesidade(sintomas, exames, refs):
        score = _calcular_score_obesidade(sintomas, exames, refs)
        hipoteses.append({
            'diagnostico': 'Obesidade',
            'score': score,
            'criteria': _get_criteria_obesidade(sintomas, exames, refs),
            'prioridade': 'BAIXA'
        })
    
    # ============================================================================
    # REGRAS PARA ARTROSE
    # ============================================================================
    if _avaliar_artrose(sintomas, exames, refs):
        score = _calcular_score_artrose(sintomas, exames, refs)
        hipoteses.append({
            'diagnostico': 'Artrose',
            'score': score,
            'criteria': _get_criteria_artrose(sintomas, exames, refs),
            'prioridade': 'BAIXA'
        })
    
    # Se não há hipóteses, verificar se há sintomas específicos
    if not hipoteses:
        hipoteses = _gerar_hipoteses_sintomas_especificos(sintomas, exames, especie, refs)
    
    # Ordenar por score e prioridade
    hipoteses.sort(key=lambda x: (x['prioridade'], x['score']), reverse=True)
    
    return hipoteses[:5]  # Top 5 hipóteses

# ============================================================================
# FUNÇÕES DE AVALIAÇÃO POR DOENÇA
# ============================================================================

def _avaliar_doenca_renal(sintomas: Dict, exames: Dict, refs: Dict) -> bool:
    """Avalia se há evidências de doença renal"""
    creatinina = exames.get('creatinina', 0)
    ureia = exames.get('ureia', 0)
    
    # Critérios principais
    creatinina_alta = creatinina > refs['creatinina'][1] * 1.5
    ureia_alta = ureia > refs['ureia'][1] * 1.5
    
    # Sintomas característicos
    poliuria = sintomas.get('poliuria', 0) == 1
    polidipsia = sintomas.get('polidipsia', 0) == 1
    apatia = sintomas.get('apatia', 0) == 1
    perda_peso = sintomas.get('perda_peso', 0) == 1
    
    # Critérios mais sensíveis
    # 1. Laboratório alterado OU
    # 2. Poliúria + Polidipsia (síndrome PU/PD) OU
    # 3. Qualquer sintoma + laboratório limítrofe
    criterios_lab = creatinina_alta + ureia_alta
    pu_pd = poliuria and polidipsia
    laboratorio_limitrofe = (creatinina > refs['creatinina'][1] * 1.2) or (ureia > refs['ureia'][1] * 1.2)
    
    return criterios_lab >= 1 or pu_pd or (laboratorio_limitrofe and (apatia or perda_peso))

def _calcular_score_renal(sintomas: Dict, exames: Dict, refs: Dict) -> float:
    """Calcula score para doença renal"""
    score = 0.0
    
    # Laboratório (peso 0.6)
    creatinina = exames.get('creatinina', 0)
    ureia = exames.get('ureia', 0)
    
    if creatinina > refs['creatinina'][1] * 2:
        score += 0.3
    elif creatinina > refs['creatinina'][1] * 1.5:
        score += 0.2
    
    if ureia > refs['ureia'][1] * 2:
        score += 0.3
    elif ureia > refs['ureia'][1] * 1.5:
        score += 0.2
    
    # Sintomas (peso 0.4)
    if sintomas.get('poliuria', 0) == 1:
        score += 0.15
    if sintomas.get('polidipsia', 0) == 1:
        score += 0.15
    if sintomas.get('apatia', 0) == 1:
        score += 0.1
    
    return min(score, 1.0)

def _get_criteria_renal(sintomas: Dict, exames: Dict, refs: Dict) -> List[str]:
    """Retorna critérios para doença renal"""
    criteria = []
    
    creatinina = exames.get('creatinina', 0)
    ureia = exames.get('ureia', 0)
    
    if creatinina > refs['creatinina'][1] * 1.5:
        criteria.append(f"Creatinina elevada ({creatinina:.1f} - normal: {refs['creatinina'][1]})")
    
    if ureia > refs['ureia'][1] * 1.5:
        criteria.append(f"Ureia elevada ({ureia:.1f} - normal: {refs['ureia'][1]})")
    
    if sintomas.get('poliuria', 0) == 1:
        criteria.append("Poliúria (aumento da frequência urinária)")
    
    if sintomas.get('polidipsia', 0) == 1:
        criteria.append("Polidipsia (aumento da sede)")
    
    if sintomas.get('apatia', 0) == 1:
        criteria.append("Apatia/letargia")
    
    return criteria

def _avaliar_diabetes(sintomas: Dict, exames: Dict, refs: Dict) -> bool:
    """Avalia se há evidências de diabetes"""
    glicose = exames.get('glicose', 0)
    
    # Critérios principais
    glicose_alta = glicose > refs['glicose'][1] * 1.5
    glicose_limitrofe = glicose > refs['glicose'][1] * 1.2
    
    # Sintomas característicos
    poliuria = sintomas.get('poliuria', 0) == 1
    polidipsia = sintomas.get('polidipsia', 0) == 1
    perda_peso = sintomas.get('perda_peso', 0) == 1
    apatia = sintomas.get('apatia', 0) == 1
    
    # Critérios mais sensíveis
    # 1. Glicose alta OU
    # 2. Poliúria + Polidipsia (síndrome PU/PD) OU
    # 3. Glicose limítrofe + perda de peso OU
    # 4. Qualquer 2 sintomas característicos
    pu_pd = poliuria and polidipsia
    glicose_sintomas = glicose_limitrofe and perda_peso
    dois_sintomas = (poliuria + polidipsia + perda_peso + apatia) >= 2
    
    return glicose_alta or pu_pd or glicose_sintomas or dois_sintomas

def _calcular_score_diabetes(sintomas: Dict, exames: Dict, refs: Dict) -> float:
    """Calcula score para diabetes"""
    score = 0.0
    
    # Laboratório (peso 0.7)
    glicose = exames.get('glicose', 0)
    
    if glicose > refs['glicose'][1] * 3:
        score += 0.7
    elif glicose > refs['glicose'][1] * 2:
        score += 0.5
    elif glicose > refs['glicose'][1] * 1.5:
        score += 0.3
    
    # Sintomas (peso 0.3)
    if sintomas.get('poliuria', 0) == 1:
        score += 0.1
    if sintomas.get('polidipsia', 0) == 1:
        score += 0.1
    if sintomas.get('perda_peso', 0) == 1:
        score += 0.1
    
    return min(score, 1.0)

def _get_criteria_diabetes(sintomas: Dict, exames: Dict, refs: Dict) -> List[str]:
    """Retorna critérios para diabetes"""
    criteria = []
    
    glicose = exames.get('glicose', 0)
    
    if glicose > refs['glicose'][1] * 1.5:
        criteria.append(f"Glicose elevada ({glicose:.1f} - normal: {refs['glicose'][1]})")
    
    if sintomas.get('poliuria', 0) == 1:
        criteria.append("Poliúria (aumento da frequência urinária)")
    
    if sintomas.get('polidipsia', 0) == 1:
        criteria.append("Polidipsia (aumento da sede)")
    
    if sintomas.get('perda_peso', 0) == 1:
        criteria.append("Perda de peso")
    
    return criteria

# ============================================================================
# FUNÇÕES PARA OUTRAS DOENÇAS
# ============================================================================

def _avaliar_periodontal(sintomas: Dict, exames: Dict, refs: Dict) -> bool:
    """Avalia doença periodontal"""
    leucocitos = exames.get('leucocitos', 0)
    leucocitose = leucocitos > refs['leucocitos'][1] * 1.2
    
    apatia = sintomas.get('apatia', 0) == 1
    perda_peso = sintomas.get('perda_peso', 0) == 1
    febre = sintomas.get('febre', 0) == 1
    
    return leucocitose or (apatia and perda_peso) or febre

def _calcular_score_periodontal(sintomas: Dict, exames: Dict, refs: Dict) -> float:
    """Calcula score para doença periodontal"""
    score = 0.0
    
    leucocitos = exames.get('leucocitos', 0)
    if leucocitos > refs['leucocitos'][1] * 1.2:
        score += 0.4
    
    if sintomas.get('febre', 0) == 1:
        score += 0.3
    if sintomas.get('apatia', 0) == 1:
        score += 0.2
    if sintomas.get('perda_peso', 0) == 1:
        score += 0.1
    
    return min(score, 1.0)

def _get_criteria_periodontal(sintomas: Dict, exames: Dict, refs: Dict) -> List[str]:
    """Critérios para doença periodontal"""
    criteria = []
    
    leucocitos = exames.get('leucocitos', 0)
    if leucocitos > refs['leucocitos'][1] * 1.2:
        criteria.append(f"Leucocitose ({leucocitos:.1f} - normal: {refs['leucocitos'][1]})")
    
    if sintomas.get('febre', 0) == 1:
        criteria.append("Febre")
    if sintomas.get('apatia', 0) == 1:
        criteria.append("Apatia")
    if sintomas.get('perda_peso', 0) == 1:
        criteria.append("Perda de peso")
    
    return criteria

def _avaliar_otite(sintomas: Dict, exames: Dict, refs: Dict) -> bool:
    """Avalia otite"""
    leucocitos = exames.get('leucocitos', 0)
    leucocitose = leucocitos > refs['leucocitos'][1] * 1.1
    
    febre = sintomas.get('febre', 0) == 1
    apatia = sintomas.get('apatia', 0) == 1
    letargia = sintomas.get('letargia', 0) == 1
    
    return (leucocitose and (febre or apatia)) or letargia

def _calcular_score_otite(sintomas: Dict, exames: Dict, refs: Dict) -> float:
    """Calcula score para otite"""
    score = 0.0
    
    if sintomas.get('febre', 0) == 1:
        score += 0.4
    if sintomas.get('apatia', 0) == 1:
        score += 0.3
    if sintomas.get('letargia', 0) == 1:
        score += 0.3
    
    leucocitos = exames.get('leucocitos', 0)
    if leucocitos > refs['leucocitos'][1] * 1.1:
        score += 0.2
    
    return min(score, 1.0)

def _get_criteria_otite(sintomas: Dict, exames: Dict, refs: Dict) -> List[str]:
    """Critérios para otite"""
    criteria = []
    
    if sintomas.get('febre', 0) == 1:
        criteria.append("Febre")
    if sintomas.get('apatia', 0) == 1:
        criteria.append("Apatia")
    if sintomas.get('letargia', 0) == 1:
        criteria.append("Letargia")
    
    leucocitos = exames.get('leucocitos', 0)
    if leucocitos > refs['leucocitos'][1] * 1.1:
        criteria.append(f"Leucocitose leve ({leucocitos:.1f})")
    
    return criteria

def _avaliar_dermatite(sintomas: Dict, exames: Dict, refs: Dict) -> bool:
    """Avalia dermatite"""
    feridas = sintomas.get('feridas_cutaneas', 0) == 1
    apatia = sintomas.get('apatia', 0) == 1
    
    return feridas or (apatia and sintomas.get('perda_peso', 0) == 1)

def _calcular_score_dermatite(sintomas: Dict, exames: Dict, refs: Dict) -> float:
    """Calcula score para dermatite"""
    score = 0.0
    
    if sintomas.get('feridas_cutaneas', 0) == 1:
        score += 0.8
    if sintomas.get('apatia', 0) == 1:
        score += 0.2
    
    return min(score, 1.0)

def _get_criteria_dermatite(sintomas: Dict, exames: Dict, refs: Dict) -> List[str]:
    """Critérios para dermatite"""
    criteria = []
    
    if sintomas.get('feridas_cutaneas', 0) == 1:
        criteria.append("Lesões cutâneas/feridas")
    if sintomas.get('apatia', 0) == 1:
        criteria.append("Apatia")
    
    return criteria

# Funções placeholder para outras doenças
def _avaliar_cardiopatia(sintomas: Dict, exames: Dict, refs: Dict) -> bool:
    return sintomas.get('tosse', 0) == 1 and sintomas.get('apatia', 0) == 1

def _calcular_score_cardiopatia(sintomas: Dict, exames: Dict, refs: Dict) -> float:
    score = 0.0
    if sintomas.get('tosse', 0) == 1:
        score += 0.6
    if sintomas.get('apatia', 0) == 1:
        score += 0.4
    return score

def _get_criteria_cardiopatia(sintomas: Dict, exames: Dict, refs: Dict) -> List[str]:
    criteria = []
    if sintomas.get('tosse', 0) == 1:
        criteria.append("Tosse")
    if sintomas.get('apatia', 0) == 1:
        criteria.append("Apatia")
    return criteria

def _avaliar_neoplasia(sintomas: Dict, exames: Dict, refs: Dict) -> bool:
    return (sintomas.get('perda_peso', 0) == 1 and sintomas.get('apatia', 0) == 1 and 
            sintomas.get('febre', 0) == 1)

def _calcular_score_neoplasia(sintomas: Dict, exames: Dict, refs: Dict) -> float:
    score = 0.0
    if sintomas.get('perda_peso', 0) == 1:
        score += 0.4
    if sintomas.get('apatia', 0) == 1:
        score += 0.3
    if sintomas.get('febre', 0) == 1:
        score += 0.3
    return score

def _get_criteria_neoplasia(sintomas: Dict, exames: Dict, refs: Dict) -> List[str]:
    criteria = []
    if sintomas.get('perda_peso', 0) == 1:
        criteria.append("Perda de peso")
    if sintomas.get('apatia', 0) == 1:
        criteria.append("Apatia")
    if sintomas.get('febre', 0) == 1:
        criteria.append("Febre")
    return criteria

def _avaliar_obesidade(sintomas: Dict, exames: Dict, refs: Dict) -> bool:
    return sintomas.get('apatia', 0) == 1 and sintomas.get('letargia', 0) == 1

def _calcular_score_obesidade(sintomas: Dict, exames: Dict, refs: Dict) -> float:
    score = 0.0
    if sintomas.get('apatia', 0) == 1:
        score += 0.5
    if sintomas.get('letargia', 0) == 1:
        score += 0.5
    return score

def _get_criteria_obesidade(sintomas: Dict, exames: Dict, refs: Dict) -> List[str]:
    criteria = []
    if sintomas.get('apatia', 0) == 1:
        criteria.append("Apatia")
    if sintomas.get('letargia', 0) == 1:
        criteria.append("Letargia")
    return criteria

def _avaliar_artrose(sintomas: Dict, exames: Dict, refs: Dict) -> bool:
    return sintomas.get('apatia', 0) == 1 and sintomas.get('letargia', 0) == 1

def _calcular_score_artrose(sintomas: Dict, exames: Dict, refs: Dict) -> float:
    score = 0.0
    if sintomas.get('apatia', 0) == 1:
        score += 0.5
    if sintomas.get('letargia', 0) == 1:
        score += 0.5
    return score

def _get_criteria_artrose(sintomas: Dict, exames: Dict, refs: Dict) -> List[str]:
    criteria = []
    if sintomas.get('apatia', 0) == 1:
        criteria.append("Apatia")
    if sintomas.get('letargia', 0) == 1:
        criteria.append("Letargia")
    return criteria
