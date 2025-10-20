"""
Sistema de Recomendações de Medicamentos Veterinários
Base de dados de medicamentos, doses e protocolos clínicos
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import streamlit as st

# ============================================================================
# BASE DE DADOS DE MEDICAMENTOS VETERINÁRIOS
# ============================================================================

MEDICAMENTOS_VETERINARIOS = {
    'Doença Renal Crônica': {
        'medicamentos': [
            {
                'nome': 'Benazepril',
                'categoria': 'IECA',
                'dose_cao': '0.25-0.5 mg/kg',
                'dose_gato': '0.25-0.5 mg/kg',
                'frequencia': '12-24h',
                'via': 'VO',
                'indicacao': 'Controle da pressão arterial e proteinúria',
                'contraindicacoes': 'Hipotensão, estenose bilateral das artérias renais',
                'efeitos_colaterais': 'Tosse seca, hipotensão, hipercalemia',
                'monitoramento': 'Função renal, eletrólitos, pressão arterial'
            },
            {
                'nome': 'Furosemida',
                'categoria': 'Diurético',
                'dose_cao': '1-2 mg/kg',
                'dose_gato': '1-2 mg/kg',
                'frequencia': '8-12h',
                'via': 'VO/IV',
                'indicacao': 'Controle da sobrecarga hídrica',
                'contraindicacoes': 'Desidratação, hipotensão',
                'efeitos_colaterais': 'Desidratação, hipocalemia, ototoxicidade',
                'monitoramento': 'Eletrólitos, função renal, hidratação'
            },
            {
                'nome': 'Calcitriol',
                'categoria': 'Vitamina D',
                'dose_cao': '2.5-5 ng/kg',
                'dose_gato': '2.5-5 ng/kg',
                'frequencia': '24h',
                'via': 'VO',
                'indicacao': 'Controle do hiperparatireoidismo secundário',
                'contraindicacoes': 'Hipercalcemia, hiperfosfatemia',
                'efeitos_colaterais': 'Hipercalcemia, hiperfosfatemia',
                'monitoramento': 'Cálcio, fósforo, PTH'
            }
        ]
    },
    'Diabetes Mellitus': {
        'medicamentos': [
            {
                'nome': 'Insulina Glargina',
                'categoria': 'Insulina',
                'dose_cao': '0.5-1 U/kg',
                'dose_gato': '0.5-1 U/kg',
                'frequencia': '12h',
                'via': 'SC',
                'indicacao': 'Controle glicêmico',
                'contraindicacoes': 'Hipoglicemia',
                'efeitos_colaterais': 'Hipoglicemia, lipodistrofia',
                'monitoramento': 'Glicemia, curva glicêmica'
            },
            {
                'nome': 'Insulina Regular',
                'categoria': 'Insulina',
                'dose_cao': '0.25-0.5 U/kg',
                'dose_gato': '0.25-0.5 U/kg',
                'frequencia': '8-12h',
                'via': 'SC',
                'indicacao': 'Controle glicêmico pós-prandial',
                'contraindicacoes': 'Hipoglicemia',
                'efeitos_colaterais': 'Hipoglicemia',
                'monitoramento': 'Glicemia'
            },
            {
                'nome': 'Glipizida',
                'categoria': 'Hipoglicemiante Oral',
                'dose_cao': '0.5-1 mg/kg',
                'dose_gato': '0.5-1 mg/kg',
                'frequencia': '12h',
                'via': 'VO',
                'indicacao': 'Diabetes tipo 2 em gatos',
                'contraindicacoes': 'Cetoacidose, insuficiência hepática',
                'efeitos_colaterais': 'Hipoglicemia, vômitos',
                'monitoramento': 'Glicemia, função hepática'
            }
        ]
    },
    'Doença Periodontal': {
        'medicamentos': [
            {
                'nome': 'Amoxicilina + Clavulanato',
                'categoria': 'Antibiótico',
                'dose_cao': '12.5-25 mg/kg',
                'dose_gato': '12.5-25 mg/kg',
                'frequencia': '12h',
                'via': 'VO',
                'indicacao': 'Infecção bacteriana oral',
                'contraindicacoes': 'Alergia à penicilina',
                'efeitos_colaterais': 'Distúrbios gastrointestinais',
                'monitoramento': 'Sinais de alergia'
            },
            {
                'nome': 'Clindamicina',
                'categoria': 'Antibiótico',
                'dose_cao': '5-10 mg/kg',
                'dose_gato': '5-10 mg/kg',
                'frequencia': '12h',
                'via': 'VO',
                'indicacao': 'Infecção anaeróbica oral',
                'contraindicacoes': 'Alergia à clindamicina',
                'efeitos_colaterais': 'Vômitos, diarreia',
                'monitoramento': 'Função hepática'
            },
            {
                'nome': 'Meloxicam',
                'categoria': 'AINE',
                'dose_cao': '0.1 mg/kg',
                'dose_gato': '0.05 mg/kg',
                'frequencia': '24h',
                'via': 'VO',
                'indicacao': 'Controle da dor e inflamação',
                'contraindicacoes': 'Insuficiência renal/hepática',
                'efeitos_colaterais': 'Úlcera gástrica, nefrotoxicidade',
                'monitoramento': 'Função renal, sinais de úlcera'
            }
        ]
    },
    'Otite': {
        'medicamentos': [
            {
                'nome': 'Surolan',
                'categoria': 'Antimicrobiano Tópico',
                'dose_cao': '2-4 gotas',
                'dose_gato': '2-4 gotas',
                'frequencia': '12h',
                'via': 'Tópico (ouvido)',
                'indicacao': 'Otite bacteriana/fúngica',
                'contraindicacoes': 'Perfuração timpânica',
                'efeitos_colaterais': 'Irritação local',
                'monitoramento': 'Resposta clínica'
            },
            {
                'nome': 'Prednisolona',
                'categoria': 'Corticosteróide',
                'dose_cao': '0.5-1 mg/kg',
                'dose_gato': '0.5-1 mg/kg',
                'frequencia': '12-24h',
                'via': 'VO',
                'indicacao': 'Controle da inflamação',
                'contraindicacoes': 'Infecção bacteriana sistêmica',
                'efeitos_colaterais': 'Poliúria, polidipsia, imunossupressão',
                'monitoramento': 'Função hepática, glicemia'
            },
            {
                'nome': 'Ciprofloxacina',
                'categoria': 'Antibiótico',
                'dose_cao': '5-10 mg/kg',
                'dose_gato': '5-10 mg/kg',
                'frequencia': '12h',
                'via': 'VO',
                'indicacao': 'Infecção bacteriana resistente',
                'contraindicacoes': 'Gestação, crescimento',
                'efeitos_colaterais': 'Articulopatia, distúrbios gastrointestinais',
                'monitoramento': 'Função articular'
            }
        ]
    },
    'Dermatite': {
        'medicamentos': [
            {
                'nome': 'Prednisolona',
                'categoria': 'Corticosteróide',
                'dose_cao': '0.5-1 mg/kg',
                'dose_gato': '0.5-1 mg/kg',
                'frequencia': '12-24h',
                'via': 'VO',
                'indicacao': 'Controle da inflamação alérgica',
                'contraindicacoes': 'Infecção bacteriana',
                'efeitos_colaterais': 'Poliúria, polidipsia, imunossupressão',
                'monitoramento': 'Função hepática'
            },
            {
                'nome': 'Ciclosporina',
                'categoria': 'Imunossupressor',
                'dose_cao': '5 mg/kg',
                'dose_gato': '5 mg/kg',
                'frequencia': '24h',
                'via': 'VO',
                'indicacao': 'Dermatite atópica refratária',
                'contraindicacoes': 'Neoplasia, infecção',
                'efeitos_colaterais': 'Nefrotoxicidade, hepatotoxicidade',
                'monitoramento': 'Função renal e hepática'
            },
            {
                'nome': 'Cetirizina',
                'categoria': 'Antihistamínico',
                'dose_cao': '1 mg/kg',
                'dose_gato': '0.5 mg/kg',
                'frequencia': '12h',
                'via': 'VO',
                'indicacao': 'Alívio do prurido',
                'contraindicacoes': 'Insuficiência renal',
                'efeitos_colaterais': 'Sedação leve',
                'monitoramento': 'Resposta clínica'
            }
        ]
    },
    'Obesidade': {
        'medicamentos': [
            {
                'nome': 'Dieta Prescrita',
                'categoria': 'Nutricional',
                'dose_cao': 'Calculado por calorias',
                'dose_gato': 'Calculado por calorias',
                'frequencia': 'Contínua',
                'via': 'Alimentação',
                'indicacao': 'Redução de peso',
                'contraindicacoes': 'Desnutrição',
                'efeitos_colaterais': 'Perda de peso excessiva',
                'monitoramento': 'Peso corporal, condição corporal'
            },
            {
                'nome': 'Exercício Controlado',
                'categoria': 'Físico',
                'dose_cao': '15-30 min/dia',
                'dose_gato': '10-20 min/dia',
                'frequencia': 'Diária',
                'via': 'Atividade',
                'indicacao': 'Aumento do gasto calórico',
                'contraindicacoes': 'Problemas articulares',
                'efeitos_colaterais': 'Fadiga',
                'monitoramento': 'Tolerância ao exercício'
            }
        ]
    },
    'Doença Cardíaca': {
        'medicamentos': [
            {
                'nome': 'Enalapril',
                'categoria': 'IECA',
                'dose_cao': '0.25-0.5 mg/kg',
                'dose_gato': '0.25-0.5 mg/kg',
                'frequencia': '12h',
                'via': 'VO',
                'indicacao': 'Insuficiência cardíaca congestiva',
                'contraindicacoes': 'Hipotensão, estenose renal',
                'efeitos_colaterais': 'Tosse, hipotensão',
                'monitoramento': 'Função renal, pressão arterial'
            },
            {
                'nome': 'Furosemida',
                'categoria': 'Diurético',
                'dose_cao': '1-2 mg/kg',
                'dose_gato': '1-2 mg/kg',
                'frequencia': '8-12h',
                'via': 'VO/IV',
                'indicacao': 'Controle da sobrecarga hídrica',
                'contraindicacoes': 'Desidratação',
                'efeitos_colaterais': 'Desidratação, hipocalemia',
                'monitoramento': 'Eletrólitos, hidratação'
            },
            {
                'nome': 'Pimobendan',
                'categoria': 'Inodilatador',
                'dose_cao': '0.25 mg/kg',
                'dose_gato': '0.25 mg/kg',
                'frequencia': '12h',
                'via': 'VO',
                'indicacao': 'Insuficiência cardíaca',
                'contraindicacoes': 'Obstrução do trato de saída',
                'efeitos_colaterais': 'Vômitos, diarreia',
                'monitoramento': 'Função cardíaca'
            }
        ]
    },
    'Artrose': {
        'medicamentos': [
            {
                'nome': 'Meloxicam',
                'categoria': 'AINE',
                'dose_cao': '0.1 mg/kg',
                'dose_gato': '0.05 mg/kg',
                'frequencia': '24h',
                'via': 'VO',
                'indicacao': 'Controle da dor e inflamação',
                'contraindicacoes': 'Insuficiência renal/hepática',
                'efeitos_colaterais': 'Úlcera gástrica, nefrotoxicidade',
                'monitoramento': 'Função renal, sinais de úlcera'
            },
            {
                'nome': 'Gabapentina',
                'categoria': 'Analgésico',
                'dose_cao': '10-20 mg/kg',
                'dose_gato': '10-20 mg/kg',
                'frequencia': '8-12h',
                'via': 'VO',
                'indicacao': 'Dor neuropática crônica',
                'contraindicacoes': 'Insuficiência renal',
                'efeitos_colaterais': 'Sedação, ataxia',
                'monitoramento': 'Função renal, sinais neurológicos'
            },
            {
                'nome': 'Glucosamina + Condroitina',
                'categoria': 'Suplemento',
                'dose_cao': '20-40 mg/kg',
                'dose_gato': '20-40 mg/kg',
                'frequencia': '24h',
                'via': 'VO',
                'indicacao': 'Suporte articular',
                'contraindicacoes': 'Alergia aos componentes',
                'efeitos_colaterais': 'Distúrbios gastrointestinais',
                'monitoramento': 'Resposta clínica'
            }
        ]
    },
    'Neoplasia': {
        'medicamentos': [
            {
                'nome': 'Prednisolona',
                'categoria': 'Corticosteróide',
                'dose_cao': '1-2 mg/kg',
                'dose_gato': '1-2 mg/kg',
                'frequencia': '12-24h',
                'via': 'VO',
                'indicacao': 'Controle da inflamação e apetite',
                'contraindicacoes': 'Infecção bacteriana',
                'efeitos_colaterais': 'Imunossupressão, poliúria',
                'monitoramento': 'Função hepática, infecções'
            },
            {
                'nome': 'Metronidazol',
                'categoria': 'Antimicrobiano',
                'dose_cao': '10-15 mg/kg',
                'dose_gato': '10-15 mg/kg',
                'frequencia': '12h',
                'via': 'VO',
                'indicacao': 'Infecção anaeróbica',
                'contraindicacoes': 'Gravidez',
                'efeitos_colaterais': 'Neurotoxicidade',
                'monitoramento': 'Sinais neurológicos'
            },
            {
                'nome': 'Ondansetrona',
                'categoria': 'Antiemético',
                'dose_cao': '0.5 mg/kg',
                'dose_gato': '0.5 mg/kg',
                'frequencia': '8-12h',
                'via': 'VO/IV',
                'indicacao': 'Controle de náuseas e vômitos',
                'contraindicacoes': 'Alergia ao ondansetrona',
                'efeitos_colaterais': 'Cefaleia, constipação',
                'monitoramento': 'Resposta clínica'
            }
        ]
    }
}

# ============================================================================
# FUNÇÕES DE CÁLCULO DE DOSES
# ============================================================================

def calcular_dose_medicamento(peso_kg: float, dose_por_kg: str, especie: str) -> Dict:
    """
    Calcula a dose de medicamento baseada no peso
    
    Args:
        peso_kg: Peso do animal em kg
        dose_por_kg: Dose por kg (ex: "0.5-1 mg/kg")
        especie: "Canina" ou "Felina"
    
    Returns:
        Dict com dose calculada e informações
    """
    try:
        # Extrair valor numérico da dose
        if '-' in dose_por_kg:
            dose_min, dose_max = dose_por_kg.replace('mg/kg', '').replace('U/kg', '').replace('ng/kg', '').split('-')
            dose_min = float(dose_min.strip())
            dose_max = float(dose_max.strip())
            dose_media = (dose_min + dose_max) / 2
        else:
            dose_media = float(dose_por_kg.replace('mg/kg', '').replace('U/kg', '').replace('ng/kg', '').strip())
            dose_min = dose_media * 0.8
            dose_max = dose_media * 1.2
        
        # Calcular dose total
        dose_total_min = dose_min * peso_kg
        dose_total_max = dose_max * peso_kg
        dose_total_media = dose_media * peso_kg
        
        # Determinar unidade
        unidade = 'mg'
        if 'U/kg' in dose_por_kg:
            unidade = 'U'
        elif 'ng/kg' in dose_por_kg:
            unidade = 'ng'
        
        return {
            'dose_min': round(dose_total_min, 2),
            'dose_max': round(dose_total_max, 2),
            'dose_media': round(dose_total_media, 2),
            'unidade': unidade,
            'peso': peso_kg,
            'especie': especie
        }
    except:
        return {
            'dose_min': 0,
            'dose_max': 0,
            'dose_media': 0,
            'unidade': 'mg',
            'peso': peso_kg,
            'especie': especie
        }

def obter_recomendacoes_medicamentos(diagnostico: str, especie: str, peso_kg: float = None) -> List[Dict]:
    """
    Obtém recomendações de medicamentos para um diagnóstico
    
    Args:
        diagnostico: Diagnóstico do animal
        especie: "Canina" ou "Felina"
        peso_kg: Peso do animal (opcional)
    
    Returns:
        Lista de medicamentos recomendados
    """
    if diagnostico not in MEDICAMENTOS_VETERINARIOS:
        return []
    
    medicamentos = MEDICAMENTOS_VETERINARIOS[diagnostico]['medicamentos']
    
    # Calcular doses se peso fornecido
    if peso_kg:
        for med in medicamentos:
            dose_campo = 'dose_cao' if especie == 'Canina' else 'dose_gato'
            dose_info = calcular_dose_medicamento(peso_kg, med[dose_campo], especie)
            med['dose_calculada'] = dose_info
    
    return medicamentos

def obter_protocolo_tratamento(diagnostico: str, especie: str, peso_kg: float = None) -> Dict:
    """
    Obtém protocolo completo de tratamento
    
    Args:
        diagnostico: Diagnóstico do animal
        especie: "Canina" ou "Felina"
        peso_kg: Peso do animal (opcional)
    
    Returns:
        Protocolo de tratamento completo
    """
    medicamentos = obter_recomendacoes_medicamentos(diagnostico, especie, peso_kg)
    
    protocolo = {
        'diagnostico': diagnostico,
        'especie': especie,
        'peso_kg': peso_kg,
        'medicamentos': medicamentos,
        'cuidados_gerais': obter_cuidados_gerais(diagnostico),
        'monitoramento': obter_protocolo_monitoramento(diagnostico),
        'retorno': obter_cronograma_retorno(diagnostico)
    }
    
    return protocolo

def obter_cuidados_gerais(diagnostico: str) -> List[str]:
    """Retorna cuidados gerais baseados no diagnóstico"""
    cuidados = {
        'Doença Renal Crônica': [
            'Dieta renal prescrita (baixo fósforo e proteína)',
            'Acesso livre à água fresca',
            'Monitorar consumo de água',
            'Evitar exercícios intensos',
            'Controle rigoroso da pressão arterial'
        ],
        'Diabetes Mellitus': [
            'Dieta diabética prescrita',
            'Administração rigorosa de insulina',
            'Monitoramento glicêmico domiciliar',
            'Exercício regular controlado',
            'Controle de peso'
        ],
        'Doença Periodontal': [
            'Escovação dental diária',
            'Limpeza dental profissional',
            'Dieta seca para limpeza mecânica',
            'Brinquedos para mastigação',
            'Exames odontológicos regulares'
        ],
        'Otite': [
            'Limpeza cuidadosa do ouvido',
            'Evitar entrada de água',
            'Proteção contra traumas',
            'Monitoramento de sinais de dor',
            'Retorno para limpeza profissional'
        ],
        'Dermatite': [
            'Banhos com shampoo medicamentoso',
            'Controle de ectoparasitas',
            'Dieta hipoalergênica se indicado',
            'Evitar alérgenos conhecidos',
            'Monitoramento de lesões'
        ]
    }
    
    return cuidados.get(diagnostico, [
        'Acompanhamento veterinário regular',
        'Monitoramento de sinais clínicos',
        'Seguimento do protocolo medicamentoso',
        'Retorno conforme agendado'
    ])

def obter_protocolo_monitoramento(diagnostico: str) -> Dict:
    """Retorna protocolo de monitoramento baseado no diagnóstico"""
    protocolos = {
        'Doença Renal Crônica': {
            'laboratorio': ['Creatinina', 'Ureia', 'Eletrólitos', 'Fósforo', 'PTH'],
            'frequencia': 'A cada 2-4 semanas inicialmente',
            'clinico': ['Consumo de água', 'Apetite', 'Peso', 'Pressão arterial'],
            'imagens': ['Ultrassom renal (a cada 3-6 meses)']
        },
        'Diabetes Mellitus': {
            'laboratorio': ['Glicemia', 'Curva glicêmica', 'Frutosamina'],
            'frequencia': 'A cada 1-2 semanas até estabilização',
            'clinico': ['Consumo de água', 'Apetite', 'Peso', 'Sinais de hipoglicemia'],
            'imagens': ['Nenhuma rotineira']
        },
        'Doença Periodontal': {
            'laboratorio': ['Hemograma completo'],
            'frequencia': 'A cada 6 meses',
            'clinico': ['Hálito', 'Apetite', 'Dor oral'],
            'imagens': ['Radiografias dentais (anual)']
        }
    }
    
    return protocolos.get(diagnostico, {
        'laboratorio': ['Hemograma', 'Bioquímica básica'],
        'frequencia': 'Conforme necessidade clínica',
        'clinico': ['Sinais clínicos gerais'],
        'imagens': ['Conforme indicação']
    })

def obter_cronograma_retorno(diagnostico: str) -> Dict:
    """Retorna cronograma de retorno baseado no diagnóstico"""
    cronogramas = {
        'Doença Renal Crônica': {
            'inicial': '1-2 semanas',
            'seguimento': '1-3 meses',
            'manutencao': '3-6 meses'
        },
        'Diabetes Mellitus': {
            'inicial': '1 semana',
            'seguimento': '2-4 semanas',
            'manutencao': '1-3 meses'
        },
        'Doença Periodontal': {
            'inicial': '1 semana',
            'seguimento': '1 mês',
            'manutencao': '6 meses'
        }
    }
    
    return cronogramas.get(diagnostico, {
        'inicial': '1-2 semanas',
        'seguimento': '1 mês',
        'manutencao': '3-6 meses'
    })

# ============================================================================
# SISTEMA DE CHAT INTEGRADO
# ============================================================================

class ChatVeterinario:
    """Sistema de chat integrado com modelo para perguntas veterinárias"""
    
    def __init__(self):
        self.historico = []
        self.contexto_atual = {}
    
    def processar_pergunta(self, pergunta: str, diagnostico: str = None, 
                          dados_animal: Dict = None) -> str:
        """
        Processa pergunta do usuário e retorna resposta baseada no contexto
        
        Args:
            pergunta: Pergunta do usuário
            diagnostico: Diagnóstico atual (se disponível)
            dados_animal: Dados do animal (se disponível)
        
        Returns:
            Resposta baseada no contexto
        """
        # Adicionar ao histórico
        self.historico.append({
            'pergunta': pergunta,
            'diagnostico': diagnostico,
            'dados': dados_animal,
            'timestamp': pd.Timestamp.now()
        })
        
        # Processar pergunta baseada em palavras-chave
        resposta = self._gerar_resposta_contextual(pergunta, diagnostico, dados_animal)
        
        return resposta
    
    def _gerar_resposta_contextual(self, pergunta: str, diagnostico: str, dados_animal: Dict) -> str:
        """Gera resposta contextual baseada na pergunta"""
        
        pergunta_lower = pergunta.lower()
        
        # Perguntas sobre medicamentos
        if any(palavra in pergunta_lower for palavra in ['medicamento', 'dose', 'doses', 'remedio']):
            return self._resposta_medicamentos(pergunta, diagnostico, dados_animal)
        
        # Perguntas sobre prognóstico
        elif any(palavra in pergunta_lower for palavra in ['prognostico', 'prognóstico', 'evolução', 'melhora']):
            return self._resposta_prognostico(diagnostico)
        
        # Perguntas sobre monitoramento
        elif any(palavra in pergunta_lower for palavra in ['monitoramento', 'exames', 'retorno', 'acompanhamento']):
            return self._resposta_monitoramento(diagnostico)
        
        # Perguntas sobre cuidados
        elif any(palavra in pergunta_lower for palavra in ['cuidados', 'alimentação', 'exercicio', 'exercício']):
            return self._resposta_cuidados(diagnostico)
        
        # Perguntas gerais
        else:
            return self._resposta_geral(pergunta, diagnostico)
    
    def _resposta_medicamentos(self, pergunta: str, diagnostico: str, dados_animal: Dict) -> str:
        """Resposta sobre medicamentos"""
        if not diagnostico:
            return "Para recomendações de medicamentos, preciso saber o diagnóstico do animal. Você pode fazer uma predição primeiro."
        
        medicamentos = obter_recomendacoes_medicamentos(
            diagnostico, 
            dados_animal.get('especie', 'Canina') if dados_animal else 'Canina',
            dados_animal.get('peso_kg') if dados_animal else None
        )
        
        if not medicamentos:
            return f"Não tenho recomendações específicas de medicamentos para {diagnostico} no momento."
        
        resposta = f"**Recomendações de medicamentos para {diagnostico}:**\n\n"
        
        for i, med in enumerate(medicamentos[:3], 1):  # Top 3 medicamentos
            resposta += f"**{i}. {med['nome']}** ({med['categoria']})\n"
            resposta += f"   • **Dose**: {med.get('dose_calculada', {}).get('dose_media', med.get('dose_cao', 'N/A'))} {med.get('dose_calculada', {}).get('unidade', 'mg')}\n"
            resposta += f"   • **Frequência**: {med['frequencia']}\n"
            resposta += f"   • **Via**: {med['via']}\n"
            resposta += f"   • **Indicação**: {med['indicacao']}\n\n"
        
        resposta += "⚠️ **Importante**: Consulte sempre um veterinário antes de administrar medicamentos."
        
        return resposta
    
    def _resposta_prognostico(self, diagnostico: str) -> str:
        """Resposta sobre prognóstico"""
        prognosticos = {
            'Doença Renal Crônica': "O prognóstico depende do estágio da doença. Com tratamento adequado, muitos animais mantêm boa qualidade de vida por anos.",
            'Diabetes Mellitus': "Com controle adequado da glicemia, a maioria dos animais diabéticos leva vida normal e saudável.",
            'Doença Periodontal': "Com tratamento e cuidados adequados, o prognóstico é excelente. A prevenção é fundamental.",
            'Otite': "O prognóstico é geralmente bom com tratamento adequado. Casos crônicos podem requerer tratamento prolongado.",
            'Dermatite': "O prognóstico varia conforme a causa. Casos alérgicos podem ser controlados com tratamento adequado."
        }
        
        return prognosticos.get(diagnostico, 
                              "O prognóstico depende de vários fatores. Consulte seu veterinário para uma avaliação mais específica.")
    
    def _resposta_monitoramento(self, diagnostico: str) -> str:
        """Resposta sobre monitoramento"""
        if not diagnostico:
            return "Para informações sobre monitoramento, preciso saber o diagnóstico específico."
        
        protocolo = obter_protocolo_monitoramento(diagnostico)
        
        resposta = f"**Protocolo de monitoramento para {diagnostico}:**\n\n"
        resposta += f"**Exames laboratoriais:** {', '.join(protocolo['laboratorio'])}\n"
        resposta += f"**Frequência:** {protocolo['frequencia']}\n"
        resposta += f"**Monitoramento clínico:** {', '.join(protocolo['clinico'])}\n"
        
        if protocolo.get('imagens'):
            resposta += f"**Exames de imagem:** {', '.join(protocolo['imagens'])}\n"
        
        return resposta
    
    def _resposta_cuidados(self, diagnostico: str) -> str:
        """Resposta sobre cuidados"""
        if not diagnostico:
            return "Para recomendações de cuidados específicos, preciso saber o diagnóstico."
        
        cuidados = obter_cuidados_gerais(diagnostico)
        
        resposta = f"**Cuidados gerais para {diagnostico}:**\n\n"
        for i, cuidado in enumerate(cuidados, 1):
            resposta += f"{i}. {cuidado}\n"
        
        return resposta
    
    def _resposta_geral(self, pergunta: str, diagnostico: str) -> str:
        """Resposta geral"""
        if diagnostico:
            return f"Com base no diagnóstico de {diagnostico}, recomendo que você consulte seu veterinário para orientações específicas. Posso ajudar com informações sobre medicamentos, monitoramento ou cuidados gerais."
        else:
            return "Posso ajudar com informações sobre medicamentos, prognóstico, monitoramento e cuidados. Para respostas mais específicas, faça primeiro uma predição diagnóstica."
    
    def limpar_historico(self):
        """Limpa o histórico de conversas"""
        self.historico = []
    
    def obter_historico(self) -> List[Dict]:
        """Retorna histórico de conversas"""
        return self.historico


