"""
Sistema de Regras Clínicas Melhorado para Geração de Hipóteses Diagnósticas
Versão mais sensível que gera hipóteses mesmo com poucos sintomas
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

def gerar_hipoteses_clinicas_melhoradas(sintomas: Dict, exames: Dict, especie: str) -> List[Dict]:
    """
    Gera hipóteses diagnósticas baseadas em regras clínicas melhoradas
    Versão mais sensível que funciona mesmo com poucos sintomas
    """
    
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
    
    hipoteses = []
    
    # ============================================================================
    # SÍNDROME PU/PD (Poliúria + Polidipsia) - MUITO IMPORTANTE
    # ============================================================================
    if sintomas.get('poliuria', 0) == 1 and sintomas.get('polidipsia', 0) == 1:
        score = 0.7  # Score alto para PU/PD
        
        # Verificar alterações laboratoriais
        glicose = exames.get('glicose', 0)
        creatinina = exames.get('creatinina', 0)
        ureia = exames.get('ureia', 0)
        
        # Adicionar sintomas extras
        if sintomas.get('perda_peso', 0) == 1:
            score += 0.15
        if sintomas.get('apatia', 0) == 1:
            score += 0.1
        
        criteria = ["Síndrome PU/PD (Poliúria + Polidipsia)"]
        
        # Determinar diagnóstico mais provável
        if glicose > refs['glicose'][1] * 1.2:
            score += 0.2
            diagnostico = 'Diabetes Mellitus'
            criteria.extend([
                f"Glicose elevada ({glicose:.1f} - normal: {refs['glicose'][1]})",
                "Perda de peso" if sintomas.get('perda_peso', 0) == 1 else None,
                "Apatia" if sintomas.get('apatia', 0) == 1 else None
            ])
        elif creatinina > refs['creatinina'][1] * 1.2 or ureia > refs['ureia'][1] * 1.2:
            score += 0.2
            diagnostico = 'Doença Renal Crônica'
            criteria.extend([
                f"Creatinina elevada ({creatinina:.1f})" if creatinina > refs['creatinina'][1] * 1.2 else None,
                f"Ureia elevada ({ureia:.1f})" if ureia > refs['ureia'][1] * 1.2 else None,
                "Perda de peso" if sintomas.get('perda_peso', 0) == 1 else None,
                "Apatia" if sintomas.get('apatia', 0) == 1 else None
            ])
        else:
            # PU/PD sem alterações laboratoriais específicas
            diagnostico = 'Síndrome PU/PD'
            criteria.extend([
                "Valores laboratoriais dentro da normalidade",
                "Investigar diabetes, doença renal, hiperadrenocorticismo",
                "Perda de peso" if sintomas.get('perda_peso', 0) == 1 else None,
                "Apatia" if sintomas.get('apatia', 0) == 1 else None
            ])
        
        # Remover None da lista
        criteria = [c for c in criteria if c is not None]
        
        hipoteses.append({
            'diagnostico': diagnostico,
            'score': min(score, 1.0),
            'criteria': criteria,
            'prioridade': 'ALTA' if score > 0.8 else 'MÉDIA'
        })
    
    # ============================================================================
    # SÍNDROME CONSUMPTIVA (Perda de peso + Apatia)
    # ============================================================================
    elif sintomas.get('perda_peso', 0) == 1 and sintomas.get('apatia', 0) == 1:
        score = 0.6
        criteria = [
            "Síndrome consumptiva (Perda de peso + Apatia)",
            "Investigar causas metabólicas, neoplásicas ou infecciosas"
        ]
        
        # Adicionar outros sintomas
        if sintomas.get('febre', 0) == 1:
            score += 0.2
            criteria.append("Febre")
        
        if sintomas.get('vomito', 0) == 1:
            score += 0.1
            criteria.append("Vômitos")
        
        hipoteses.append({
            'diagnostico': 'Síndrome Consumptiva',
            'score': min(score, 1.0),
            'criteria': criteria,
            'prioridade': 'MÉDIA'
        })
    
    # ============================================================================
    # SINTOMAS ISOLADOS COM ALTERAÇÕES LABORATORIAIS
    # ============================================================================
    
    # Glicose elevada
    glicose = exames.get('glicose', 0)
    if glicose > refs['glicose'][1] * 1.5:
        score = 0.8
        criteria = [f"Glicose significativamente elevada ({glicose:.1f} - normal: {refs['glicose'][1]})"]
        
        if sintomas.get('perda_peso', 0) == 1:
            score += 0.1
            criteria.append("Perda de peso")
        
        hipoteses.append({
            'diagnostico': 'Diabetes Mellitus',
            'score': min(score, 1.0),
            'criteria': criteria,
            'prioridade': 'ALTA'
        })
    
    # Creatinina elevada
    creatinina = exames.get('creatinina', 0)
    if creatinina > refs['creatinina'][1] * 1.5:
        score = 0.8
        criteria = [f"Creatinina significativamente elevada ({creatinina:.1f} - normal: {refs['creatinina'][1]})"]
        
        if sintomas.get('apatia', 0) == 1:
            score += 0.1
            criteria.append("Apatia")
        
        hipoteses.append({
            'diagnostico': 'Doença Renal Crônica',
            'score': min(score, 1.0),
            'criteria': criteria,
            'prioridade': 'ALTA'
        })
    
    # Leucocitose com febre
    leucocitos = exames.get('leucocitos', 0)
    if leucocitos > refs['leucocitos'][1] * 1.5 and sintomas.get('febre', 0) == 1:
        hipoteses.append({
            'diagnostico': 'Processo Inflamatório/Infeccioso',
            'score': 0.7,
            'criteria': [
                f"Leucocitose ({leucocitos:.1f} - normal: {refs['leucocitos'][1]})",
                "Febre",
                "Investigar foco infeccioso ou inflamatório"
            ],
            'prioridade': 'MÉDIA'
        })
    
    # ============================================================================
    # SINTOMAS ESPECÍFICOS
    # ============================================================================
    
    # Febre isolada
    if sintomas.get('febre', 0) == 1 and not any(sintomas.get(k, 0) == 1 for k in ['poliuria', 'polidipsia', 'perda_peso', 'apatia']):
        hipoteses.append({
            'diagnostico': 'Síndrome Febril',
            'score': 0.5,
            'criteria': [
                "Febre",
                "Investigar causa infecciosa ou inflamatória",
                "Considerar exames complementares"
            ],
            'prioridade': 'BAIXA'
        })
    
    # Vômitos + Diarreia
    if sintomas.get('vomito', 0) == 1 and sintomas.get('diarreia', 0) == 1:
        hipoteses.append({
            'diagnostico': 'Gastroenterite',
            'score': 0.6,
            'criteria': [
                "Vômitos e diarreia",
                "Investigar causa viral, bacteriana ou parasitária",
                "Monitorar hidratação"
            ],
            'prioridade': 'MÉDIA'
        })
    
    # ============================================================================
    # CASO SEM HIPÓTESES ESPECÍFICAS
    # ============================================================================
    if not hipoteses:
        sintomas_presentes = [k for k, v in sintomas.items() if v == 1]
        if sintomas_presentes:
            hipoteses.append({
                'diagnostico': 'Investigação Necessária',
                'score': 0.4,
                'criteria': [
                    f"Sintomas presentes: {', '.join([s.replace('_', ' ').title() for s in sintomas_presentes])}",
                    "Valores laboratoriais dentro da normalidade",
                    "Recomenda-se investigação adicional e acompanhamento"
                ],
                'prioridade': 'BAIXA'
            })
        else:
            hipoteses.append({
                'diagnostico': 'Exame de Rotina',
                'score': 0.1,
                'criteria': [
                    "Nenhum sintoma específico relatado",
                    "Valores laboratoriais dentro da normalidade",
                    "Manter acompanhamento de rotina"
                ],
                'prioridade': 'BAIXA'
            })
    
    # Ordenar por score e prioridade
    hipoteses.sort(key=lambda x: (x['prioridade'], x['score']), reverse=True)
    
    return hipoteses[:5]  # Top 5 hipóteses


