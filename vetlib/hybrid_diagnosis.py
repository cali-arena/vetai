"""
Sistema Híbrido de Diagnóstico
Combina regras clínicas com aprendizado dos dados históricos
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import streamlit as st

class SistemaDiagnosticoHibrido:
    def __init__(self):
        self.df_historico = None
        self.modelo_similaridade = None
        self.scaler = StandardScaler()
        self.feature_names = None
        
    def carregar_dados_historicos(self, df: pd.DataFrame):
        """Carrega dados históricos para aprendizado"""
        self.df_historico = df.copy()
        
        # Preparar features para similaridade
        feature_cols = [col for col in df.columns if col not in ['id', 'especie', 'raca', 'sexo', 'diagnostico', 'idade_anos']]
        self.feature_names = feature_cols
        
        # Preparar dados para treinamento
        X = df[feature_cols].fillna(df[feature_cols].median())
        
        # Treinar modelo de similaridade
        X_scaled = self.scaler.fit_transform(X)
        self.modelo_similaridade = NearestNeighbors(n_neighbors=10, metric='cosine')
        self.modelo_similaridade.fit(X_scaled)
        
        st.success(f"✅ Dados históricos carregados: {len(df)} casos, {len(feature_cols)} features")
    
    def detectar_valores_criticos(self, exames: Dict, especie: str) -> Dict:
        """Detecta valores críticos baseados em faixas de referência"""
        
        # Faixas de referência críticas
        if especie == "Canina":
            refs_criticos = {
                'creatinina': {'critico_baixo': 0.2, 'critico_alto': 3.0, 'normal': (0.5, 1.6)},
                'ureia': {'critico_baixo': 10, 'critico_alto': 100, 'normal': (20, 50)},
                'glicose': {'critico_baixo': 40, 'critico_alto': 300, 'normal': (70, 120)},
                'hemoglobina': {'critico_baixo': 6, 'critico_alto': 20, 'normal': (12, 18)},
                'hematocrito': {'critico_baixo': 20, 'critico_alto': 70, 'normal': (37, 55)},
                'leucocitos': {'critico_baixo': 2, 'critico_alto': 30, 'normal': (6, 17)},
                'alt': {'critico_baixo': 5, 'critico_alto': 200, 'normal': (10, 100)},
                'albumina': {'critico_baixo': 1.5, 'critico_alto': 5.0, 'normal': (2.5, 3.8)}
            }
        else:  # Felina
            refs_criticos = {
                'creatinina': {'critico_baixo': 0.3, 'critico_alto': 4.0, 'normal': (0.8, 2.0)},
                'ureia': {'critico_baixo': 15, 'critico_alto': 120, 'normal': (30, 60)},
                'glicose': {'critico_baixo': 40, 'critico_alto': 350, 'normal': (70, 150)},
                'hemoglobina': {'critico_baixo': 5, 'critico_alto': 18, 'normal': (9, 15)},
                'hematocrito': {'critico_baixo': 15, 'critico_alto': 60, 'normal': (30, 45)},
                'leucocitos': {'critico_baixo': 2, 'critico_alto': 35, 'normal': (5.5, 19.5)},
                'alt': {'critico_baixo': 5, 'critico_alto': 150, 'normal': (10, 80)},
                'albumina': {'critico_baixo': 1.5, 'critico_alto': 5.0, 'normal': (2.5, 3.9)}
            }
        
        alertas = {
            'criticos': [],
            'alterados': [],
            'normais': []
        }
        
        for exame, valor in exames.items():
            if exame in refs_criticos and valor > 0:
                refs = refs_criticos[exame]
                
                if valor <= refs['critico_baixo'] or valor >= refs['critico_alto']:
                    status = 'CRÍTICO'
                    if valor <= refs['critico_baixo']:
                        alertas['criticos'].append(f"{exame}: {valor:.1f} (↓ MUITO BAIXO - crítico: ≤{refs['critico_baixo']})")
                    else:
                        alertas['criticos'].append(f"{exame}: {valor:.1f} (↑ MUITO ALTO - crítico: ≥{refs['critico_alto']})")
                elif valor < refs['normal'][0] or valor > refs['normal'][1]:
                    status = 'ALTERADO'
                    if valor < refs['normal'][0]:
                        alertas['alterados'].append(f"{exame}: {valor:.1f} (↓ baixo - normal: {refs['normal'][0]}-{refs['normal'][1]})")
                    else:
                        alertas['alterados'].append(f"{exame}: {valor:.1f} (↑ alto - normal: {refs['normal'][0]}-{refs['normal'][1]})")
                else:
                    status = 'NORMAL'
                    alertas['normais'].append(f"{exame}: {valor:.1f} (✓ normal)")
        
        return alertas
    
    def encontrar_casos_similares(self, sintomas: Dict, exames: Dict, especie: str, n_casos: int = 20) -> pd.DataFrame:
        """Encontra casos similares nos dados históricos"""
        
        if self.df_historico is None or self.modelo_similaridade is None:
            return pd.DataFrame()
        
        # Preparar dados do caso atual
        caso_atual = {}
        
        # Adicionar exames
        for exame, valor in exames.items():
            if exame in self.feature_names:
                caso_atual[exame] = valor
        
        # Adicionar sintomas
        for sintoma, presente in sintomas.items():
            if sintoma in self.feature_names:
                caso_atual[sintoma] = int(presente)
        
        # Adicionar dados demográficos padrão
        for col in self.feature_names:
            if col not in caso_atual:
                if col == 'idade_anos':
                    caso_atual[col] = 5.0  # Idade padrão
                elif col in ['especie', 'sexo']:
                    continue  # Pular colunas categóricas não numéricas
                else:
                    caso_atual[col] = 0  # Valor padrão
        
        # Criar DataFrame com o caso atual
        df_caso = pd.DataFrame([caso_atual])
        
        # Garantir que todas as colunas existem
        for col in self.feature_names:
            if col not in df_caso.columns:
                df_caso[col] = 0
        
        # Filtrar por espécie se especificado
        df_filtrado = self.df_historico.copy()
        if especie and 'especie' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['especie'] == especie]
        
        # Preparar dados para similaridade
        X_caso = df_caso[self.feature_names].fillna(0)
        X_historico = df_filtrado[self.feature_names].fillna(df_filtrado[self.feature_names].median())
        
        # Escalar dados
        X_caso_scaled = self.scaler.transform(X_caso)
        X_historico_scaled = self.scaler.fit_transform(X_historico)
        
        # Encontrar casos similares
        try:
            distances, indices = self.modelo_similaridade.kneighbors(X_caso_scaled)
            
            # Retornar casos similares com diagnóstico
            casos_similares = df_filtrado.iloc[indices[0]].copy()
            casos_similares['distancia'] = distances[0]
            casos_similares['similaridade'] = 1 - distances[0]  # Converter distância em similaridade
            
            return casos_similares.head(n_casos)
        except:
            return pd.DataFrame()
    
    def gerar_hipoteses_hibridas(self, sintomas: Dict, exames: Dict, especie: str) -> List[Dict]:
        """Gera hipóteses combinando regras clínicas e dados históricos"""
        
        hipoteses = []
        
        # 1. Detectar valores críticos
        alertas = self.detectar_valores_criticos(exames, especie)
        
        # 2. Gerar hipóteses baseadas em valores críticos
        if alertas['criticos']:
            # Casos críticos - prioridade máxima
            for alerta in alertas['criticos']:
                if 'creatinina' in alerta.lower() and 'alto' in alerta.lower():
                    hipoteses.append({
                        'diagnostico': 'Insuficiência Renal Aguda/Grave',
                        'score': 0.95,
                        'criteria': [alerta, "Valores críticos detectados", "ATENÇÃO IMEDIATA NECESSÁRIA"],
                        'prioridade': 'CRÍTICA',
                        'tipo': 'valor_critico'
                    })
                elif 'glicose' in alerta.lower() and 'baixo' in alerta.lower():
                    hipoteses.append({
                        'diagnostico': 'Hipoglicemia Crítica',
                        'score': 0.95,
                        'criteria': [alerta, "Valores críticos detectados", "ATENÇÃO IMEDIATA NECESSÁRIA"],
                        'prioridade': 'CRÍTICA',
                        'tipo': 'valor_critico'
                    })
                elif 'glicose' in alerta.lower() and 'alto' in alerta.lower():
                    hipoteses.append({
                        'diagnostico': 'Hiperglicemia Crítica/Diabetes Grave',
                        'score': 0.95,
                        'criteria': [alerta, "Valores críticos detectados", "ATENÇÃO IMEDIATA NECESSÁRIA"],
                        'prioridade': 'CRÍTICA',
                        'tipo': 'valor_critico'
                    })
        
        # 3. Gerar hipóteses baseadas em casos similares
        if self.df_historico is not None:
            casos_similares = self.encontrar_casos_similares(sintomas, exames, especie, n_casos=20)
            
            if not casos_similares.empty:
                # Analisar diagnósticos dos casos similares
                diagnosticos_similares = casos_similares['diagnostico'].value_counts()
                
                for diagnostico, count in diagnosticos_similares.items():
                    # Calcular score baseado na frequência e similaridade
                    casos_com_diagnostico = casos_similares[casos_similares['diagnostico'] == diagnostico]
                    score_base = count / len(casos_similares)
                    similaridade_media = casos_com_diagnostico['similaridade'].mean()
                    
                    score_final = (score_base * 0.6) + (similaridade_media * 0.4)
                    
                    # Critérios baseados nos casos similares
                    criteria = [
                        f"Encontrados {count} casos similares com este diagnóstico",
                        f"Similaridade média: {similaridade_media:.2f}",
                        f"Frequência nos casos similares: {score_base:.1%}"
                    ]
                    
                    # Adicionar alertas relevantes
                    if alertas['alterados']:
                        criteria.extend(alertas['alterados'][:2])  # Máximo 2 alertas
                    
                    hipoteses.append({
                        'diagnostico': diagnostico,
                        'score': score_final,
                        'criteria': criteria,
                        'prioridade': 'ALTA' if score_final > 0.7 else 'MÉDIA' if score_final > 0.4 else 'BAIXA',
                        'tipo': 'casos_similares',
                        'casos_encontrados': count
                    })
        
        # 4. Gerar hipóteses baseadas em regras clínicas (fallback)
        if not hipoteses:
            hipoteses.extend(self._gerar_hipoteses_regras_clinicas(sintomas, exames, especie))
        
        # 5. Adicionar alertas como hipóteses informativas
        if alertas['alterados'] and not any(h['tipo'] == 'valor_critico' for h in hipoteses):
            hipoteses.append({
                'diagnostico': 'Alterações Laboratoriais',
                'score': 0.6,
                'criteria': alertas['alterados'],
                'prioridade': 'MÉDIA',
                'tipo': 'alteracoes_lab'
            })
        
        # Ordenar por prioridade e score
        prioridade_order = {'CRÍTICA': 4, 'ALTA': 3, 'MÉDIA': 2, 'BAIXA': 1}
        hipoteses.sort(key=lambda x: (prioridade_order.get(x['prioridade'], 0), x['score']), reverse=True)
        
        return hipoteses[:5]
    
    def _gerar_hipoteses_regras_clinicas(self, sintomas: Dict, exames: Dict, especie: str) -> List[Dict]:
        """Fallback para regras clínicas básicas"""
        hipoteses = []
        
        # Síndrome PU/PD
        if sintomas.get('poliuria', 0) == 1 and sintomas.get('polidipsia', 0) == 1:
            hipoteses.append({
                'diagnostico': 'Síndrome PU/PD',
                'score': 0.6,
                'criteria': ['Síndrome PU/PD (Poliúria + Polidipsia)'],
                'prioridade': 'MÉDIA',
                'tipo': 'regras_clinicas'
            })
        
        # Sintomas isolados
        sintomas_presentes = [k for k, v in sintomas.items() if v == 1]
        if sintomas_presentes:
            hipoteses.append({
                'diagnostico': 'Investigação Necessária',
                'score': 0.4,
                'criteria': [f"Sintomas presentes: {', '.join(sintomas_presentes)}"],
                'prioridade': 'BAIXA',
                'tipo': 'regras_clinicas'
            })
        
        return hipoteses

# Instância global do sistema
sistema_hibrido = SistemaDiagnosticoHibrido()


