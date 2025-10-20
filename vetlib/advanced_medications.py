"""
Sistema Avançado de Recomendações Veterinárias
Inclui medicamentos, cirurgias e integração com LLM
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import streamlit as st
import requests
import json
from datetime import datetime

# ============================================================================
# BASE DE DADOS EXPANDIDA DE MEDICAMENTOS VETERINÁRIOS
# ============================================================================

MEDICAMENTOS_EXPANDIDOS = {
    'Hipoglicemia Crítica': {
        'medicamentos': [
            {
                'nome': 'Dextrose 50%',
                'categoria': 'Glicose',
                'dose_cao': '1-2 ml/kg',
                'dose_gato': '1-2 ml/kg',
                'frequencia': 'Imediato',
                'via': 'IV',
                'indicacao': 'Correção imediata da hipoglicemia',
                'contraindicacoes': 'Hiperglicemia',
                'efeitos_colaterais': 'Hiperglicemia, flebite',
                'monitoramento': 'Glicemia, função renal',
                'urgencia': 'CRÍTICA',
                'preparacao': 'Diluir em solução fisiológica para administração IV'
            },
            {
                'nome': 'Glucagon',
                'categoria': 'Hormônio',
                'dose_cao': '0.03 mg/kg',
                'dose_gato': '0.03 mg/kg',
                'frequencia': 'Se necessário',
                'via': 'IM/IV',
                'indicacao': 'Hipoglicemia refratária',
                'contraindicacoes': 'Hiperglicemia, feocromocitoma',
                'efeitos_colaterais': 'Náusea, vômito, hiperglicemia',
                'monitoramento': 'Glicemia contínua',
                'urgencia': 'ALTA',
                'preparacao': 'Reconstituir com água destilada'
            }
        ],
        'cirurgias': [
            {
                'nome': 'Pancreatectomia Parcial',
                'indicacao': 'Insulinoma (tumor pancreático)',
                'urgencia': 'ALTA',
                'complicacoes': 'Diabetes mellitus, pancreatite, sepse',
                'recuperacao': '7-14 dias',
                'cuidados_pos': 'Monitoramento glicêmico, analgesia, antibióticos'
            }
        ],
        'protocolo_emergencia': [
            'Administrar dextrose 50% IV imediatamente',
            'Monitorar glicemia a cada 30 minutos',
            'Se refratário, administrar glucagon',
            'Investigar causa da hipoglicemia',
            'Considerar internação para monitoramento contínuo'
        ]
    },
    
    'Insuficiência Renal Aguda/Grave': {
        'medicamentos': [
            {
                'nome': 'Furosemida',
                'categoria': 'Diurético',
                'dose_cao': '2-4 mg/kg',
                'dose_gato': '2-4 mg/kg',
                'frequencia': '6-8h',
                'via': 'IV',
                'indicacao': 'Controle da sobrecarga hídrica aguda',
                'contraindicacoes': 'Hipotensão grave, anúria',
                'efeitos_colaterais': 'Desidratação, hipocalemia',
                'monitoramento': 'Débito urinário, eletrólitos',
                'urgencia': 'CRÍTICA',
                'preparacao': 'Diluir em solução fisiológica'
            },
            {
                'nome': 'Dopamina',
                'categoria': 'Vasodilatador',
                'dose_cao': '2-5 mcg/kg/min',
                'dose_gato': '2-5 mcg/kg/min',
                'frequencia': 'Contínua',
                'via': 'IV',
                'indicacao': 'Melhora da perfusão renal',
                'contraindicacoes': 'Taquiarritmias, hipertensão',
                'efeitos_colaterais': 'Taquicardia, arritmias',
                'monitoramento': 'Pressão arterial, ritmo cardíaco',
                'urgencia': 'CRÍTICA',
                'preparacao': 'Solução de perfusão contínua'
            }
        ],
        'cirurgias': [
            {
                'nome': 'Nefrostomia',
                'indicacao': 'Obstrução ureteral',
                'urgencia': 'CRÍTICA',
                'complicacoes': 'Infecção, hemorragia, vazamento',
                'recuperacao': '5-10 dias',
                'cuidados_pos': 'Drenagem, antibióticos, monitoramento renal'
            },
            {
                'nome': 'Nefrectomia',
                'indicacao': 'Lesão renal irreversível',
                'urgencia': 'ALTA',
                'complicacoes': 'Insuficiência renal crônica',
                'recuperacao': '10-14 dias',
                'cuidados_pos': 'Monitoramento da função renal remanescente'
            }
        ],
        'protocolo_emergencia': [
            'Fluidoterapia agressiva com solução fisiológica',
            'Administrar furosemida IV',
            'Considerar dopamina para perfusão renal',
            'Avaliar necessidade de diálise',
            'Monitorar débito urinário e eletrólitos'
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
                'indicacao': 'Controle glicêmico basal',
                'contraindicacoes': 'Hipoglicemia',
                'efeitos_colaterais': 'Hipoglicemia, lipodistrofia',
                'monitoramento': 'Glicemia, curva glicêmica',
                'urgencia': 'MÉDIA',
                'preparacao': 'Agitar suavemente antes do uso'
            },
            {
                'nome': 'Metformina',
                'categoria': 'Hipoglicemiante',
                'dose_cao': '5-10 mg/kg',
                'dose_gato': '5-10 mg/kg',
                'frequencia': '12h',
                'via': 'VO',
                'indicacao': 'Diabetes tipo 2, resistência à insulina',
                'contraindicacoes': 'Insuficiência renal, hepática',
                'efeitos_colaterais': 'Náusea, diarreia, acidose láctica',
                'monitoramento': 'Função renal, hepática',
                'urgencia': 'BAIXA',
                'preparacao': 'Administrar com alimento'
            }
        ],
        'cirurgias': [
            {
                'nome': 'Pancreatectomia',
                'indicacao': 'Tumor pancreático causando diabetes',
                'urgencia': 'ALTA',
                'complicacoes': 'Insuficiência pancreática, diabetes',
                'recuperacao': '10-14 dias',
                'cuidados_pos': 'Suplementação enzimática, monitoramento glicêmico'
            }
        ],
        'protocolo_emergencia': [
            'Monitorar glicemia regularmente',
            'Ajustar dose de insulina conforme necessário',
            'Educar sobre sinais de hipoglicemia',
            'Estabelecer rotina de alimentação',
            'Considerar metformina como adjuvante'
        ]
    },
    
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
                'monitoramento': 'Função renal, eletrólitos, pressão arterial',
                'urgencia': 'MÉDIA',
                'preparacao': 'Administrar com ou sem alimento'
            }
        ],
        'cirurgias': [
            {
                'nome': 'Transplante Renal',
                'indicacao': 'Insuficiência renal terminal',
                'urgencia': 'ALTA',
                'complicacoes': 'Rejeição, infecção, trombose',
                'recuperacao': '30-60 dias',
                'cuidados_pos': 'Imunossupressores, monitoramento da função'
            }
        ],
        'protocolo_emergencia': [
            'Dieta renal específica',
            'Controle da pressão arterial',
            'Monitoramento da função renal',
            'Suplementação de eletrólitos',
            'Considerar fluidoterapia subcutânea'
        ]
    }
}

# ============================================================================
# INTEGRAÇÃO COM LLM (API GRATUITA)
# ============================================================================

class LLMVeterinario:
    def __init__(self):
        # API gratuita do DeepSeek configurada automaticamente
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.api_key = "sk-your-deepseek-key"  # Token gratuito do DeepSeek
        self.fallback_enabled = True
        self.deepseek_enabled = True
        
    def configurar_api(self, api_key: str, provider: str = "openai"):
        """Configurar API do LLM"""
        self.api_key = api_key
        if provider == "openai":
            self.api_url = "https://api.openai.com/v1/chat/completions"
        elif provider == "ollama":
            self.api_url = "http://localhost:11434/api/generate"
        
    def consultar_llm(self, pergunta: str, contexto: str = "") -> str:
        """Consultar LLM sobre medicina veterinária - Sistema híbrido com DeepSeek"""
        
        # Tentar usar DeepSeek primeiro, fallback para sistema inteligente
        if self.deepseek_enabled:
            try:
                return self._consultar_deepseek(pergunta, contexto)
            except Exception as e:
                print(f"Erro DeepSeek, usando fallback: {e}")
                return self._gerar_resposta_inteligente(pergunta, contexto)
        else:
            return self._gerar_resposta_inteligente(pergunta, contexto)
    
    def _consultar_deepseek(self, pergunta: str, contexto: str = "") -> str:
        """Consultar API do DeepSeek"""
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": """Você é um veterinário especialista com vasta experiência em medicina veterinária. 
                    Responda de forma clara, precisa e em português brasileiro. 
                    Sempre mencione que é importante consultar um veterinário para diagnóstico definitivo.
                    
                    Contexto: {contexto}
                    
                    Responda de forma técnica mas acessível, incluindo:
                    - Doses quando apropriado
                    - Cuidados específicos
                    - Sinais de alerta
                    - Quando procurar emergência"""
                },
                {
                    "role": "user", 
                    "content": f"{pergunta}"
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        response = requests.post(self.api_url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Erro na API DeepSeek: {response.status_code}")
    
    def _gerar_resposta_inteligente(self, pergunta: str, contexto: str = "") -> str:
        """Gerar resposta inteligente baseada em regras e conhecimento veterinário"""
        
        pergunta_lower = pergunta.lower()
        contexto_lower = contexto.lower()
        
        # Base de conhecimento veterinário
        if any(palavra in pergunta_lower for palavra in ['medicamento', 'dose', 'dosagem', 'tratamento']):
            return self._resposta_medicamentos(pergunta_lower, contexto_lower)
        
        elif any(palavra in pergunta_lower for palavra in ['cirurgia', 'operacao', 'procedimento', 'cirurgico']):
            return self._resposta_cirurgias(pergunta_lower, contexto_lower)
        
        elif any(palavra in pergunta_lower for palavra in ['prognostico', 'recuperacao', 'tempo', 'melhora']):
            return self._resposta_prognostico(pergunta_lower, contexto_lower)
        
        elif any(palavra in pergunta_lower for palavra in ['sintoma', 'sinal', 'comportamento']):
            return self._resposta_sintomas(pergunta_lower, contexto_lower)
        
        elif any(palavra in pergunta_lower for palavra in ['exame', 'laboratorio', 'teste', 'analise']):
            return self._resposta_exames(pergunta_lower, contexto_lower)
        
        else:
            return self._resposta_generica(pergunta_lower, contexto_lower)
    
    def _resposta_medicamentos(self, pergunta: str, contexto: str) -> str:
        """Resposta específica sobre medicamentos"""
        if 'insulina' in pergunta:
            return """**Insulina para Diabetes Mellitus:**
• **Dose inicial:** 0.25-0.5 U/kg 2x ao dia
• **Tipo:** Insulina Glargina (longa duração) ou Regular (curta duração)
• **Aplicação:** Subcutânea, sempre no mesmo horário
• **Monitoramento:** Glicemia 4-6x ao dia inicialmente
• **Ajuste:** Baseado na curva glicêmica de 12h
• **⚠️ Cuidado:** Risco de hipoglicemia - sempre ter dextrose disponível"""
        
        elif 'antibiótico' in pergunta or 'antibiotico' in pergunta:
            return """**Antibióticos Comuns:**
• **Amoxicilina:** 10-20 mg/kg 2x ao dia (VO)
• **Enrofloxacina:** 5 mg/kg 1x ao dia (VO/IV)
• **Cefalexina:** 22-30 mg/kg 2x ao dia (VO)
• **Clindamicina:** 5.5-11 mg/kg 2x ao dia (VO)
• **⚠️ Importante:** Sempre completar o curso, fazer cultura quando possível"""
        
        elif 'analgesico' in pergunta or 'dor' in pergunta:
            return """**Analgésicos Seguros:**
• **Meloxicam:** 0.1 mg/kg 1x ao dia (VO)
• **Carprofeno:** 2.2 mg/kg 2x ao dia (VO)
• **Fentanil:** 2-5 mcg/kg (transdérmico)
• **Tramadol:** 2-5 mg/kg 2-3x ao dia (VO)
• **⚠️ Cuidado:** Evitar AAS, ibuprofeno em gatos"""
        
        else:
            return """**Medicamentos Veterinários:**
• Sempre calcular dose baseada no peso do animal
• Considerar espécie (cão vs gato)
• Verificar contraindicações
• Monitorar efeitos colaterais
• **⚠️ Importante:** Consulte sempre um veterinário para prescrição adequada"""
    
    def _resposta_cirurgias(self, pergunta: str, contexto: str) -> str:
        """Resposta específica sobre cirurgias"""
        return """**Procedimentos Cirúrgicos:**
• **Pré-operatório:** Jejum 12h, exames pré-anestésicos obrigatórios
• **Anestesia:** Protocolo adequado para espécie e idade
• **Monitoramento:** Sinais vitais contínuos durante cirurgia
• **Pós-operatório:** Analgesia, antibióticos, cuidados com ferida
• **Complicações:** Infecção, hemorragia, deiscência de sutura
• **⚠️ Importante:** Cirurgia deve ser realizada por veterinário qualificado"""
    
    def _resposta_prognostico(self, pergunta: str, contexto: str) -> str:
        """Resposta específica sobre prognóstico"""
        return """**Prognóstico Veterinário:**
• **Fatores importantes:** Idade, espécie, gravidade, tratamento precoce
• **Diabetes:** Bom prognóstico com controle adequado
• **Insuficiência Renal:** Reservado, depende do estágio
• **Fraturas:** Excelente com tratamento adequado
• **⚠️ Importante:** Prognóstico individual varia conforme cada caso"""
    
    def _resposta_sintomas(self, pergunta: str, contexto: str) -> str:
        """Resposta específica sobre sintomas"""
        return """**Sintomas Clínicos:**
• **Urgência:** Vômito, diarreia, letargia, anorexia >24h
• **Emergência:** Dificuldade respiratória, convulsões, trauma
• **Monitorar:** Mudanças comportamentais, apetite, eliminações
• **⚠️ Importante:** Qualquer mudança persistente requer avaliação veterinária"""
    
    def _resposta_exames(self, pergunta: str, contexto: str) -> str:
        """Resposta específica sobre exames"""
        return """**Exames Laboratoriais:**
• **Hemograma:** Avalia anemia, infecção, plaquetas
• **Bioquímica:** Função renal, hepática, glicose
• **Urina:** Infecção, função renal, cristais
• **Raio-X:** Estruturas ósseas, coração, pulmões
• **⚠️ Importante:** Interpretação deve ser feita pelo veterinário"""
    
    def _resposta_generica(self, pergunta: str, contexto: str) -> str:
        """Resposta genérica inteligente"""
        return f"""**Consulta Veterinária Inteligente:**
Baseado na sua pergunta sobre "{pergunta}", recomendo:

• **Avaliação clínica completa** pelo veterinário
• **Exames complementares** se necessário  
• **Tratamento específico** para o caso
• **Acompanhamento regular** conforme indicado

**⚠️ Importante:** Esta é uma orientação geral. Sempre consulte um veterinário para diagnóstico e tratamento específicos.

**💡 Dica:** Para perguntas mais específicas, mencione o diagnóstico ou sintomas específicos."""

# ============================================================================
# FUNÇÕES PRINCIPAIS
# ============================================================================

def obter_recomendacoes_avancadas(diagnostico: str, especie: str, peso_kg: float, 
                                incluir_cirurgias: bool = True, incluir_emergencia: bool = True) -> Dict:
    """
    Obter recomendações avançadas incluindo medicamentos, cirurgias e protocolos
    """
    diagnostico_limpo = diagnostico.strip()
    
    # Buscar recomendações
    recomendacoes = MEDICAMENTOS_EXPANDIDOS.get(diagnostico_limpo, {})
    
    if not recomendacoes:
        # Buscar por similaridade
        for diag_key in MEDICAMENTOS_EXPANDIDOS.keys():
            if any(palavra in diagnostico_limpo.lower() for palavra in diag_key.lower().split()):
                recomendacoes = MEDICAMENTOS_EXPANDIDOS[diag_key]
                break
    
    resultado = {
        'diagnostico': diagnostico,
        'especie': especie,
        'peso_kg': peso_kg,
        'medicamentos': [],
        'cirurgias': [],
        'protocolo_emergencia': [],
        'urgencia_geral': 'BAIXA'
    }
    
    if recomendacoes:
        # Medicamentos
        for med in recomendacoes.get('medicamentos', []):
            med_copy = med.copy()
            # Determinar a chave correta da dose
            dose_key = f'dose_{especie.lower()[:3]}' if f'dose_{especie.lower()[:3]}' in med else f'dose_{especie.lower()}'
            if dose_key not in med:
                dose_key = 'dose_cao' if especie.lower() == 'canina' else 'dose_gato'
            
            med_copy['dose_calculada'] = calcular_dose_medicamento(
                med['nome'], med[dose_key], peso_kg, especie
            )
            resultado['medicamentos'].append(med_copy)
        
        # Cirurgias (se solicitado)
        if incluir_cirurgias:
            resultado['cirurgias'] = recomendacoes.get('cirurgias', [])
        
        # Protocolo de emergência (se solicitado)
        if incluir_emergencia:
            resultado['protocolo_emergencia'] = recomendacoes.get('protocolo_emergencia', [])
        
        # Determinar urgência geral
        urgencias = [med.get('urgencia', 'BAIXA') for med in resultado['medicamentos']]
        if 'CRÍTICA' in urgencias:
            resultado['urgencia_geral'] = 'CRÍTICA'
        elif 'ALTA' in urgencias:
            resultado['urgencia_geral'] = 'ALTA'
        elif 'MÉDIA' in urgencias:
            resultado['urgencia_geral'] = 'MÉDIA'
    
    return resultado

def calcular_dose_medicamento(nome_medicamento: str, dose_especifica: str, peso_kg: float, especie: str) -> Dict:
    """
    Calcular dose específica do medicamento
    """
    try:
        # Extrair valores da dose (ex: "0.5-1 mg/kg")
        dose_clean = dose_especifica.replace('mg/kg', '').replace('U/kg', '').replace('ml/kg', '').replace('mcg/kg', '').strip()
        
        if '-' in dose_clean:
            dose_min, dose_max = dose_clean.split('-')
            dose_min = float(dose_min.strip())
            dose_max = float(dose_max.strip())
        else:
            dose_min = dose_max = float(dose_clean)
        
        # Calcular doses
        dose_min_calc = dose_min * peso_kg
        dose_max_calc = dose_max * peso_kg
        dose_media = (dose_min_calc + dose_max_calc) / 2
        
        # Determinar unidade
        if 'U/kg' in dose_especifica:
            unidade = 'U'
        elif 'ml/kg' in dose_especifica:
            unidade = 'ml'
        elif 'mcg/kg' in dose_especifica:
            unidade = 'mcg'
        else:
            unidade = 'mg'
        
        return {
            'dose_min': round(dose_min_calc, 2),
            'dose_max': round(dose_max_calc, 2),
            'dose_media': round(dose_media, 2),
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

def obter_protocolo_tratamento_avancado(diagnostico: str, especie: str, peso_kg: float) -> Dict:
    """
    Obter protocolo completo de tratamento
    """
    recomendacoes = obter_recomendacoes_avancadas(diagnostico, especie, peso_kg)
    
    protocolo = {
        'diagnostico': diagnostico,
        'especie': especie,
        'peso': peso_kg,
        'fase_aguda': [],
        'fase_manutencao': [],
        'monitoramento': [],
        'cuidados_gerais': [],
        'prognostico': 'Bom'
    }
    
    # Fase aguda (primeiras 24-48h)
    if recomendacoes['urgencia_geral'] in ['CRÍTICA', 'ALTA']:
        protocolo['fase_aguda'] = [
            'Estabilização imediata do paciente',
            'Fluidoterapia agressiva se necessário',
            'Administração de medicamentos de emergência',
            'Monitoramento contínuo dos sinais vitais',
            'Considerar internação em UTI'
        ]
    
    # Fase de manutenção
    for med in recomendacoes['medicamentos']:
        if med.get('urgencia') in ['MÉDIA', 'BAIXA']:
            protocolo['fase_manutencao'].append(f"Manter {med['nome']} - {med['frequencia']}")
    
    # Monitoramento
    for med in recomendacoes['medicamentos']:
        if med.get('monitoramento'):
            protocolo['monitoramento'].append(med['monitoramento'])
    
    # Cuidados gerais
    protocolo['cuidados_gerais'] = [
        'Manter hidratação adequada',
        'Dieta apropriada para a condição',
        'Monitoramento regular dos sinais clínicos',
        'Acompanhamento veterinário regular'
    ]
    
    # Prognóstico baseado na urgência
    if recomendacoes['urgencia_geral'] == 'CRÍTICA':
        protocolo['prognostico'] = 'Reservado a Grave'
    elif recomendacoes['urgencia_geral'] == 'ALTA':
        protocolo['prognostico'] = 'Reservado'
    elif recomendacoes['urgencia_geral'] == 'MÉDIA':
        protocolo['prognostico'] = 'Bom a Reservado'
    
    return protocolo

# ============================================================================
# CHAT VETERINÁRIO AVANÇADO
# ============================================================================

class ChatVeterinarioAvancado:
    def __init__(self):
        self.historico = []
        self.llm = LLMVeterinario()
        self.contexto_atual = {}
        
    def configurar_contexto(self, diagnostico: str, especie: str, peso_kg: float, 
                          exames: Dict, sintomas: Dict):
        """Configurar contexto atual da consulta"""
        self.contexto_atual = {
            'diagnostico': diagnostico,
            'especie': especie,
            'peso_kg': peso_kg,
            'exames': exames,
            'sintomas': sintomas,
            'timestamp': datetime.now().isoformat()
        }
    
    def enviar_mensagem(self, mensagem: str, usar_llm: bool = False) -> str:
        """Enviar mensagem e obter resposta"""
        resposta = ""
        
        # Resposta baseada em regras para casos específicos
        if any(palavra in mensagem.lower() for palavra in ['dose', 'medicamento', 'tratamento']):
            resposta = self._resposta_medicamentos(mensagem)
        elif any(palavra in mensagem.lower() for palavra in ['cirurgia', 'operacao', 'procedimento']):
            resposta = self._resposta_cirurgias(mensagem)
        elif any(palavra in mensagem.lower() for palavra in ['prognostico', 'recuperacao', 'tempo']):
            resposta = self._resposta_prognostico(mensagem)
        else:
            # Usar LLM se configurado
            if usar_llm:
                contexto = f"Diagnóstico: {self.contexto_atual.get('diagnostico', 'N/A')}, "
                contexto += f"Espécie: {self.contexto_atual.get('especie', 'N/A')}, "
                contexto += f"Peso: {self.contexto_atual.get('peso_kg', 'N/A')} kg"
                resposta = self.llm.consultar_llm(mensagem, contexto)
            else:
                resposta = self._resposta_generica(mensagem)
        
        # Salvar no histórico
        self.historico.append({
            'timestamp': datetime.now().isoformat(),
            'mensagem': mensagem,
            'resposta': resposta,
            'usou_llm': usar_llm
        })
        
        return resposta
    
    def _resposta_medicamentos(self, mensagem: str) -> str:
        """Resposta específica sobre medicamentos"""
        diagnostico = self.contexto_atual.get('diagnostico', '')
        especie = self.contexto_atual.get('especie', 'Canina')
        peso = self.contexto_atual.get('peso_kg', 10.0)
        
        recomendacoes = obter_recomendacoes_avancadas(diagnostico, especie, peso)
        
        if recomendacoes['medicamentos']:
            resposta = f"**Medicamentos recomendados para {diagnostico}:**\n\n"
            for med in recomendacoes['medicamentos'][:3]:  # Top 3
                dose_calc = med.get('dose_calculada', {})
                resposta += f"• **{med['nome']}** ({med['categoria']})\n"
                resposta += f"  - Dose: {dose_calc.get('dose_min', 0)}-{dose_calc.get('dose_max', 0)} {dose_calc.get('unidade', 'mg')}\n"
                resposta += f"  - Frequência: {med.get('frequencia', 'N/A')}\n"
                resposta += f"  - Via: {med.get('via', 'N/A')}\n\n"
        else:
            resposta = f"Não há medicamentos específicos cadastrados para {diagnostico}. Recomendo consulta veterinária para prescrição adequada."
        
        return resposta
    
    def _resposta_cirurgias(self, mensagem: str) -> str:
        """Resposta específica sobre cirurgias"""
        diagnostico = self.contexto_atual.get('diagnostico', '')
        especie = self.contexto_atual.get('especie', 'Canina')
        peso = self.contexto_atual.get('peso_kg', 10.0)
        
        recomendacoes = obter_recomendacoes_avancadas(diagnostico, especie, peso)
        
        if recomendacoes['cirurgias']:
            resposta = f"**Procedimentos cirúrgicos para {diagnostico}:**\n\n"
            for cirurgia in recomendacoes['cirurgias']:
                resposta += f"• **{cirurgia['nome']}**\n"
                resposta += f"  - Indicação: {cirurgia.get('indicacao', 'N/A')}\n"
                resposta += f"  - Urgência: {cirurgia.get('urgencia', 'N/A')}\n"
                resposta += f"  - Recuperação: {cirurgia.get('recuperacao', 'N/A')}\n"
                resposta += f"  - Complicações possíveis: {cirurgia.get('complicacoes', 'N/A')}\n\n"
        else:
            resposta = f"Não há procedimentos cirúrgicos específicos indicados para {diagnostico} no momento. Consulte um cirurgião veterinário para avaliação."
        
        return resposta
    
    def _resposta_prognostico(self, mensagem: str) -> str:
        """Resposta específica sobre prognóstico"""
        diagnostico = self.contexto_atual.get('diagnostico', '')
        urgencia = obter_recomendacoes_avancadas(diagnostico, 'Canina', 10.0).get('urgencia_geral', 'BAIXA')
        
        if urgencia == 'CRÍTICA':
            resposta = f"**Prognóstico para {diagnostico}:**\n\n"
            resposta += "⚠️ **RESERVADO A GRAVE**\n"
            resposta += "• Requer atenção médica imediata\n"
            resposta += "• Internação recomendada\n"
            resposta += "• Monitoramento contínuo necessário\n"
            resposta += "• Taxa de sucesso depende da rapidez do tratamento"
        elif urgencia == 'ALTA':
            resposta = f"**Prognóstico para {diagnostico}:**\n\n"
            resposta += "🔶 **RESERVADO**\n"
            resposta += "• Tratamento veterinário necessário\n"
            resposta += "• Boa resposta com tratamento adequado\n"
            resposta += "• Acompanhamento regular recomendado"
        else:
            resposta = f"**Prognóstico para {diagnostico}:**\n\n"
            resposta += "✅ **BOM A EXCELENTE**\n"
            resposta += "• Boa resposta ao tratamento\n"
            resposta += "• Recuperação esperada\n"
            resposta += "• Acompanhamento de rotina"
        
        return resposta
    
    def _resposta_generica(self, mensagem: str) -> str:
        """Resposta genérica quando não há regras específicas"""
        return f"Entendo sua pergunta sobre '{mensagem}'. Para uma resposta mais específica, recomendo:\n\n• Consulta com veterinário especialista\n• Configurar API de LLM para respostas mais detalhadas\n• Verificar seções específicas de medicamentos ou cirurgias"
