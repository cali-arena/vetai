"""
Sistema Simples de Diagnóstico
Versão simplificada e funcional para geração de hipóteses
"""

import pandas as pd
import numpy as np
from typing import Dict, List

def gerar_hipoteses_simples(sintomas: Dict, exames: Dict, especie: str) -> List[Dict]:
    """
    Gera hipóteses diagnósticas de forma simples e funcional
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
    # DETECÇÃO DE VALORES CRÍTICOS
    # ============================================================================
    
    # Creatinina crítica
    creatinina = exames.get('creatinina', 0)
    if creatinina > 3.0:
        hipoteses.append({
            'diagnostico': 'Insuficiência Renal Aguda/Grave',
            'score': 0.95,
            'criteria': [
                f"Creatinina CRÍTICA: {creatinina:.1f} (normal: {refs['creatinina'][1]})",
                "Valor 2x acima do limite superior",
                "ATENÇÃO IMEDIATA NECESSÁRIA"
            ],
            'prioridade': 'CRÍTICA',
            'tipo': 'valor_critico'
        })
    elif creatinina > refs['creatinina'][1] * 1.5:
        hipoteses.append({
            'diagnostico': 'Doença Renal Crônica',
            'score': 0.85,
            'criteria': [
                f"Creatinina elevada: {creatinina:.1f} (normal: {refs['creatinina'][1]})",
                "Função renal comprometida"
            ],
            'prioridade': 'ALTA',
            'tipo': 'valor_alterado'
        })
    
    # Glicose crítica
    glicose = exames.get('glicose', 0)
    if glicose < 40:
        hipoteses.append({
            'diagnostico': 'Hipoglicemia Crítica',
            'score': 0.95,
            'criteria': [
                f"Glicose CRÍTICA: {glicose:.1f} (normal: {refs['glicose'][1]})",
                "Valor muito baixo - risco de coma",
                "ATENÇÃO IMEDIATA NECESSÁRIA"
            ],
            'prioridade': 'CRÍTICA',
            'tipo': 'valor_critico'
        })
    elif glicose > 300:
        hipoteses.append({
            'diagnostico': 'Hiperglicemia Crítica/Diabetes Grave',
            'score': 0.95,
            'criteria': [
                f"Glicose CRÍTICA: {glicose:.1f} (normal: {refs['glicose'][1]})",
                "Valor muito alto - risco de cetoacidose",
                "ATENÇÃO IMEDIATA NECESSÁRIA"
            ],
            'prioridade': 'CRÍTICA',
            'tipo': 'valor_critico'
        })
    elif glicose > refs['glicose'][1] * 1.5:
        hipoteses.append({
            'diagnostico': 'Diabetes Mellitus',
            'score': 0.8,
            'criteria': [
                f"Glicose elevada: {glicose:.1f} (normal: {refs['glicose'][1]})",
                "Sugestivo de diabetes"
            ],
            'prioridade': 'ALTA',
            'tipo': 'valor_alterado'
        })
    
    # Ureia elevada
    ureia = exames.get('ureia', 0)
    if ureia > refs['ureia'][1] * 2:
        hipoteses.append({
            'diagnostico': 'Insuficiência Renal',
            'score': 0.8,
            'criteria': [
                f"Ureia elevada: {ureia:.1f} (normal: {refs['ureia'][1]})",
                "Função renal comprometida"
            ],
            'prioridade': 'ALTA',
            'tipo': 'valor_alterado'
        })
    
    # ============================================================================
    # SÍNDROMES CLÍNICAS
    # ============================================================================
    
    # Síndrome PU/PD (Poliúria + Polidipsia)
    if sintomas.get('poliuria', 0) == 1 and sintomas.get('polidipsia', 0) == 1:
        score = 0.7
        criteria = ["Síndrome PU/PD (Poliúria + Polidipsia)"]
        
        # Adicionar sintomas extras
        if sintomas.get('perda_peso', 0) == 1:
            score += 0.1
            criteria.append("Perda de peso")
        
        if sintomas.get('apatia', 0) == 1:
            score += 0.1
            criteria.append("Apatia")
        
        # Determinar diagnóstico mais provável
        if glicose > refs['glicose'][1] * 1.2:
            diagnostico = 'Diabetes Mellitus'
            score += 0.2
            criteria.append(f"Glicose elevada: {glicose:.1f}")
        elif creatinina > refs['creatinina'][1] * 1.2:
            diagnostico = 'Doença Renal Crônica'
            score += 0.2
            criteria.append(f"Creatinina elevada: {creatinina:.1f}")
        else:
            diagnostico = 'Síndrome PU/PD'
            criteria.append("Investigar diabetes, doença renal, hiperadrenocorticismo")
        
        hipoteses.append({
            'diagnostico': diagnostico,
            'score': min(score, 1.0),
            'criteria': criteria,
            'prioridade': 'ALTA' if score > 0.8 else 'MÉDIA',
            'tipo': 'sindrome_clinica'
        })
    
    # Síndrome consumptiva (Perda de peso + Apatia)
    elif sintomas.get('perda_peso', 0) == 1 and sintomas.get('apatia', 0) == 1:
        hipoteses.append({
            'diagnostico': 'Síndrome Consumptiva',
            'score': 0.6,
            'criteria': [
                "Perda de peso + Apatia",
                "Investigar causas metabólicas, neoplásicas ou infecciosas"
            ],
            'prioridade': 'MÉDIA',
            'tipo': 'sindrome_clinica'
        })
    
    # ============================================================================
    # OUTRAS ALTERAÇÕES LABORATORIAIS
    # ============================================================================
    
    # Leucocitose com febre
    leucocitos = exames.get('leucocitos', 0)
    if leucocitos > refs['leucocitos'][1] * 1.5 and sintomas.get('febre', 0) == 1:
        hipoteses.append({
            'diagnostico': 'Processo Inflamatório/Infeccioso',
            'score': 0.7,
            'criteria': [
                f"Leucocitose: {leucocitos:.1f} (normal: {refs['leucocitos'][1]})",
                "Febre",
                "Investigar foco infeccioso"
            ],
            'prioridade': 'MÉDIA',
            'tipo': 'alteracao_lab'
        })
    
    # Anemia
    hemoglobina = exames.get('hemoglobina', 0)
    if hemoglobina < refs['hemoglobina'][0]:
        hipoteses.append({
            'diagnostico': 'Anemia',
            'score': 0.6,
            'criteria': [
                f"Hemoglobina baixa: {hemoglobina:.1f} (normal: {refs['hemoglobina'][0]}-{refs['hemoglobina'][1]})",
                "Investigar causa da anemia"
            ],
            'prioridade': 'MÉDIA',
            'tipo': 'alteracao_lab'
        })
    
    # ============================================================================
    # FALLBACK - CASO SEM HIPÓTESES ESPECÍFICAS
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
                    "Recomenda-se investigação adicional"
                ],
                'prioridade': 'BAIXA',
                'tipo': 'investigacao'
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
                'prioridade': 'BAIXA',
                'tipo': 'rotina'
            })
    
    # Ordenar por prioridade e score
    prioridade_order = {'CRÍTICA': 4, 'ALTA': 3, 'MÉDIA': 2, 'BAIXA': 1}
    hipoteses.sort(key=lambda x: (prioridade_order.get(x['prioridade'], 0), x['score']), reverse=True)
    
    return hipoteses[:5]  # Top 5 hipóteses


