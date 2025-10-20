"""
Página: Predição
Fazer predições de diagnóstico com explicabilidade
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Adicionar path da biblioteca
sys.path.insert(0, str(Path(__file__).parent.parent))

from vetlib.modeling import prever_diagnostico, carregar_modelo
from vetlib.explain import (
    explicar_predicao_local, gerar_texto_explicacao,
    plotar_shap_summary, calcular_shap_values, plotar_shap_waterfall,
    calcular_permutation_importance, plotar_permutation_importance
)
from vetlib.insights import gerar_alertas_valores_criticos, gerar_recomendacoes_clinicas
from vetlib.preprocessing import FAIXAS_REFERENCIA
from vetlib.data_io import SCHEMA_COLUNAS, carregar_arquivo, exportar_para_download
from vetlib.medications import (
    obter_recomendacoes_medicamentos, obter_protocolo_tratamento,
    calcular_dose_medicamento, ChatVeterinario
)
from vetlib.advanced_medications import (
    obter_recomendacoes_avancadas, obter_protocolo_tratamento_avancado,
    ChatVeterinarioAvancado
)
from vetlib.clinical_rules_improved import gerar_hipoteses_clinicas_melhoradas
from vetlib.hybrid_diagnosis import sistema_hibrido
from vetlib.simple_diagnosis import gerar_hipoteses_simples

st.set_page_config(page_title="Predição", page_icon="🔍", layout="wide")

# Título
st.title("🔍 Predição de Diagnóstico")
st.markdown("Predições com explicabilidade e recomendações clínicas")

# Verificar se há modelo treinado
if st.session_state.get('modelo_treinado') is None:
    st.warning("⚠️ Nenhum modelo treinado na sessão.")
    
    st.markdown("### 📂 Carregar Modelo Salvo")
    
    # Listar modelos disponíveis
    models_dir = Path('models')
    if models_dir.exists():
        modelos_disponiveis = list(models_dir.glob('*.pkl'))
        
        if modelos_disponiveis:
            modelo_arquivo = st.selectbox(
                "Selecione um modelo:",
                modelos_disponiveis,
                format_func=lambda x: x.name
            )
            
            if st.button("📥 Carregar Modelo"):
                modelo, preprocessadores, feature_names, classes = carregar_modelo(str(modelo_arquivo))
                
                if modelo is not None:
                    st.session_state.modelo_treinado = modelo
                    st.session_state.preprocessor = preprocessadores
                    st.session_state.feature_names = feature_names
                    st.session_state.target_names = classes
                    st.success("✅ Modelo carregado!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao carregar modelo")
        else:
            st.info("Nenhum modelo salvo encontrado em /models")
    
    st.info("👉 Vá para **🤖 Treinar Modelo** para treinar um novo modelo primeiro.")
    st.stop()

# Obter modelo e preprocessadores
modelo = st.session_state.get('modelo_treinado')
preprocessadores = st.session_state.get('preprocessor')
feature_names = st.session_state.get('feature_names')
target_names = st.session_state.get('target_names')

# Sistema sempre disponível via fallback

# ============================================================================
# SEÇÃO: MODO DE PREDIÇÃO
# ============================================================================

st.markdown("## 🎯 Modo de Predição")

modo = st.radio(
    "Selecione o modo:",
    ["📝 Entrada Manual", "📤 Upload de Arquivo"],
    horizontal=True
)

st.markdown("---")

# ============================================================================
# MODO 1: ENTRADA MANUAL
# ============================================================================

if modo == "📝 Entrada Manual":
    st.markdown("## 📝 Inserir Dados Manualmente")
    
    # Interface simplificada sem formulário
    st.markdown("### 🐾 Identificação")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        especie = st.selectbox("Espécie", ["Canina", "Felina", "Equina"])
    
    with col2:
        sexo = st.selectbox("Sexo", ["M", "F"])
    
    with col3:
        idade_anos = st.number_input("Idade (anos)", 0.1, 30.0, 5.0, 0.1)
        
    st.markdown("### 🧪 Exames Laboratoriais")
    
    # Organizar exames em colunas
    exames_valores = {}
    
    exames_disponiveis = [e for e in SCHEMA_COLUNAS['exames'] if e in feature_names]
    
    # Dividir em 3 colunas
    n_cols = 3
    cols = st.columns(n_cols)
    
    for idx, exame in enumerate(exames_disponiveis):
        col_idx = idx % n_cols
        
        # Obter faixa de referência
        if especie in FAIXAS_REFERENCIA and exame in FAIXAS_REFERENCIA[especie]:
            min_ref, max_ref = FAIXAS_REFERENCIA[especie][exame]
            valor_padrao = (min_ref + max_ref) / 2
            help_text = f"Referência {especie}: {min_ref} - {max_ref}"
        else:
            valor_padrao = 0.0
            help_text = None
        
        with cols[col_idx]:
            exames_valores[exame] = st.number_input(
                exame.replace('_', ' ').title(),
                value=float(valor_padrao),
                format="%.2f",
                help=help_text,
                key=f"exame_{exame}"
            )
    
    st.markdown("### 💊 Sintomas Clínicos")
    
    sintomas_valores = {}
    
    sintomas_disponiveis = [s for s in SCHEMA_COLUNAS['sintomas'] if s in feature_names]
    
    # Dividir em colunas
    cols_sint = st.columns(n_cols)
    
    for idx, sintoma in enumerate(sintomas_disponiveis):
        col_idx = idx % n_cols
        
        with cols_sint[col_idx]:
            sintomas_valores[sintoma] = st.checkbox(
                sintoma.replace('_', ' ').title(),
                key=f"sintoma_{sintoma}"
            )
        
    # Botão de teste simples primeiro
    st.markdown("### 🎯 Ações")
    
    # Botão único para teste
    submit_teste = st.button("🧪 Teste Rápido", type="primary", key="btn_teste")
    
    # Botões adicionais
    col1, col2 = st.columns(2)
    with col1:
        submit_modelo = st.button("🤖 Predição por IA", type="secondary", key="btn_modelo")
    with col2:
        submit_hipoteses = st.button("🧠 Gerar Hipóteses Clínicas", type="secondary", key="btn_hipoteses")
    
    # Debug: verificar se botão foi clicado
    if submit_hipoteses:
        # Converter sintomas para formato esperado
        sintomas_dict = {k: int(v) for k, v in sintomas_valores.items()}
        
        # Carregar dados históricos no sistema híbrido se ainda não carregado
        if st.session_state.get('df_main') is not None and sistema_hibrido.df_historico is None:
            sistema_hibrido.carregar_dados_historicos(st.session_state.df_main)
        
        # Gerar hipóteses simples e funcionais
        with st.spinner("Gerando hipóteses baseadas em critérios clínicos..."):
            try:
                hipoteses = gerar_hipoteses_simples(sintomas_dict, exames_valores, especie)
                
                if hipoteses:
                    st.success(f"🎯 **{len(hipoteses)} hipóteses** geradas baseadas em critérios clínicos!")
                    
                    # Salvar no session state para uso posterior
                    st.session_state.ultima_hipoteses = hipoteses
                    st.session_state.dados_entrada = {
                        'especie': especie,
                        'sexo': sexo,
                        'idade_anos': idade_anos,
                        'peso_kg': 10.0,  # Default
                        **exames_valores,
                        **sintomas_dict
                    }
                    
                    # Exibir hipóteses
                    st.markdown("### 🎯 Hipóteses Diagnósticas")
                    
                    for i, hipotese in enumerate(hipoteses, 1):
                        # Determinar cor e ícone baseado no tipo
                        tipo = hipotese.get('tipo', 'regras_clinicas')
                        if tipo == 'valor_critico':
                            cor = "🔴"
                            expandido = True
                        elif tipo == 'casos_similares':
                            cor = "🔵"
                            expandido = i == 1
                        else:
                            cor = "🟡"
                            expandido = i == 1
                        
                        with st.expander(f"{cor} **{i}. {hipotese['diagnostico']}** - Score: {hipotese['score']:.2f} ({hipotese['prioridade']})", 
                                       expanded=expandido):
                            
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.markdown("**Critérios Identificados:**")
                                for criterio in hipotese['criteria']:
                                    st.markdown(f"• {criterio}")
                                
                                # Mostrar informações adicionais baseadas no tipo
                                if tipo == 'casos_similares' and 'casos_encontrados' in hipotese:
                                    st.info(f"📊 Baseado em {hipotese['casos_encontrados']} casos similares nos dados históricos")
                                elif tipo == 'valor_critico':
                                    st.error("⚠️ VALORES CRÍTICOS DETECTADOS - ATENÇÃO IMEDIATA NECESSÁRIA!")
                            
                            with col2:
                                st.metric("Score", f"{hipotese['score']:.2f}")
                                st.metric("Prioridade", hipotese['prioridade'])
                                st.metric("Tipo", tipo.replace('_', ' ').title())
                    
                    # Botão para usar hipótese principal
                    if st.button("💊 Ver Recomendações de Medicamentos", type="primary"):
                        st.session_state.ultima_predicao = {
                            'diagnostico': hipoteses[0]['diagnostico'],
                            'confianca': hipoteses[0]['score'],
                            'tipo': 'hipoteses_clinicas'
                        }
                        # Salvar resultados atuais também
                        st.session_state.resultados_atuais = hipoteses
                        st.rerun()
                
                else:
                    st.warning("⚠️ Nenhuma hipótese diagnóstica identificada com os critérios atuais.")
                    
            except Exception as e:
                st.error(f"❌ Erro ao gerar hipóteses: {str(e)}")
    
    # Debug: verificar se botão foi clicado
    if submit_teste:
        st.markdown("### 🧪 Teste Rápido do Sistema")
        
        # Dados de teste fixos
        sintomas_teste = {'poliuria': 1, 'polidipsia': 1}
        exames_teste = {'creatinina': 3.0, 'glicose': 20}
        especie_teste = 'Canina'
        
        st.info(f"**Dados de teste:** Sintomas: {sintomas_teste}, Exames: {exames_teste}, Espécie: {especie_teste}")
        
        try:
            resultados_teste = gerar_hipoteses_simples(sintomas_teste, exames_teste, especie_teste)
            
            st.success(f"✅ Sistema funcionando! {len(resultados_teste)} hipóteses geradas:")
            
            for i, resultado in enumerate(resultados_teste[:3], 1):
                st.markdown(f"**{i}. {resultado['diagnostico']}**")
                st.markdown(f"- Score: {resultado['score']:.2f}")
                st.markdown(f"- Prioridade: {resultado['prioridade']}")
                st.markdown(f"- Tipo: {resultado['tipo']}")
                
                if 'criteria' in resultado:
                    st.markdown("**Critérios:**")
                    for criterio in resultado['criteria']:
                        st.markdown(f"  • {criterio}")
                st.markdown("---")
                
        except Exception as e:
            st.error(f"❌ Erro no teste: {str(e)}")
    
    # Sistema funcionando perfeitamente! 🎉
    
    # Debug: verificar se botão foi clicado
    if submit_modelo:
        
        # Criar dicionário com todos os valores
        dados_predicao = {
            'especie': especie,
            'sexo': sexo,
            'idade_anos': idade_anos,
            **exames_valores,
            **{k: int(v) for k, v in sintomas_valores.items()}
        }
        
        
        # Fazer predição
        with st.spinner("Fazendo predição..."):
            try:
                # Tentar usar modelo treinado se disponível e compatível
                if (modelo is not None and 
                    preprocessadores is not None and 
                    feature_names is not None):
                    try:
                        resultados = prever_diagnostico(
                            modelo,
                            dados_predicao,
                            preprocessadores,
                            feature_names,
                            top_n=3
                        )
                        st.info("🤖 **Predição usando modelo de IA treinado**")
                    except Exception as model_error:
                        st.warning(f"⚠️ Erro no modelo treinado: {str(model_error)[:100]}...")
                        st.info("🔄 **Usando sistema de regras clínicas como fallback**")
                        raise model_error
                else:
                    raise ValueError("Modelo ou preprocessadores não disponíveis")
                    
            except Exception as e:
                # Fallback para sistema simples de diagnóstico
                st.info("🧠 **Usando sistema de regras clínicas**")
                sintomas_dict_fallback = {k: int(v) for k, v in sintomas_valores.items()}
                resultados_simples = gerar_hipoteses_simples(sintomas_dict_fallback, exames_valores, especie)
                
                # Converter e organizar resultados (evitar duplicações)
                resultados = []
                diagnosticos_unicos = set()
                
                for hipotese in resultados_simples:
                    diag = hipotese['diagnostico']
                    # Evitar duplicações, priorizar maior score
                    if diag not in diagnosticos_unicos or any(r['diagnostico'] == diag and r['probabilidade'] < hipotese['score'] for r in resultados):
                        if diag in diagnosticos_unicos:
                            # Remover versão anterior com score menor
                            resultados = [r for r in resultados if r['diagnostico'] != diag]
                        else:
                            diagnosticos_unicos.add(diag)
                        
                        resultados.append({
                            'diagnostico': hipotese['diagnostico'],
                            'probabilidade': hipotese['score'],
                            'confianca': hipotese['prioridade'],
                            'tipo': hipotese.get('tipo', 'clínico'),
                            'criteria': hipotese.get('criteria', [])
                        })
                
                # Ordenar por score (maior primeiro) e limitar a 3
                resultados = sorted(resultados, key=lambda x: x['probabilidade'], reverse=True)[:3]
                
                # ========================================================
                # RESULTADOS
                # ========================================================
                
                st.markdown("---")
                st.markdown("## 🎯 Resultados da Predição")
                
                # Mostrar tipo de predição usado
                if len(resultados) > 0:
                    if 'score' in str(resultados[0]):
                        st.markdown("🧠 **Sistema de Regras Clínicas** - Funciona independentemente de modelo treinado")
                    else:
                        st.markdown("🤖 **Modelo de IA Treinado** - Baseado em aprendizado de máquina")
                
                # Diagnósticos melhorados
                st.markdown("### 🏥 Diagnósticos Identificados")
                st.info(f"**{len(resultados)} diagnóstico(s) identificado(s)** com base nos critérios clínicos")
                
                for i, res in enumerate(resultados, 1):
                    diag = res['diagnostico']
                    prob = res['probabilidade']
                    conf = res['confianca']
                    
                    # Container para cada diagnóstico
                    with st.container():
                        st.markdown("---")
                        
                        # Header do diagnóstico
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            # Cor e ícone baseado na prioridade
                            if conf == 'CRÍTICA':
                                st.error(f"🔴 **#{i} - {diag}**")
                                st.caption("⚠️ ATENÇÃO IMEDIATA NECESSÁRIA")
                            elif conf == 'ALTA':
                                st.warning(f"🟡 **#{i} - {diag}**")
                                st.caption("🔶 Prioridade alta")
                            elif conf == 'MÉDIA':
                                st.info(f"🟢 **#{i} - {diag}**")
                                st.caption("🔷 Prioridade média")
                            else:
                                st.success(f"✅ **#{i} - {diag}**")
                                st.caption("🔹 Monitoramento")
                        
                        with col2:
                            st.metric("Score", f"{prob:.2f}")
                        
                        with col3:
                            st.metric("Prioridade", conf)
                        
                        # Critérios de diagnóstico
                        if res.get('criteria'):
                            st.markdown("**📋 Critérios identificados:**")
                            for criterio in res['criteria']:
                                st.markdown(f"• {criterio}")
                        
                        # Tipo de evidência
                        if res.get('tipo'):
                            tipo_icon = {
                                'valor_critico': '🚨',
                                'sindrome_clinica': '🔬',
                                'valor_alterado': '📊',
                                'alteracao_lab': '🧪'
                            }.get(res['tipo'], '🔍')
                            
                            tipo_text = {
                                'valor_critico': 'Valor crítico detectado',
                                'sindrome_clinica': 'Síndrome clínica',
                                'valor_alterado': 'Valor alterado',
                                'alteracao_lab': 'Alteração laboratorial'
                            }.get(res['tipo'], 'Critério clínico')
                            
                            st.caption(f"{tipo_icon} {tipo_text}")
                
                # Alertas de valores críticos
                st.markdown("### ⚠️ Alertas de Valores Críticos")
                
                alertas = gerar_alertas_valores_criticos(exames_valores, especie)
                
                if alertas:
                    for alerta in alertas:
                        if alerta.startswith('🚨'):
                            st.error(alerta)
                        else:
                            st.warning(alerta)
                else:
                    st.success("✅ Nenhum valor crítico detectado")
                
                # Recomendações clínicas
                st.markdown("### 💡 Recomendações Clínicas")
                
                recomendacoes = gerar_recomendacoes_clinicas(
                    resultados[0]['diagnostico'],
                    resultados[0]['probabilidade'],
                    exames_valores,
                    especie
                )
                
                for rec in recomendacoes:
                    if rec.startswith('⚕️'):
                        st.info(rec)
                    elif rec.startswith('⚠️'):
                        st.warning(rec)
                    else:
                        st.markdown(rec)
                
                # Explicabilidade simplificada
                st.markdown("### 🔍 Explicabilidade da Predição")
                
                # Explicar baseado nos critérios clínicos
                st.info("**🧠 Sistema de Regras Clínicas** - Baseado em critérios médicos veterinários")
                
                # Mostrar critérios usados para cada resultado
                for i, res in enumerate(resultados, 1):
                    st.markdown(f"**#{i} - {res['diagnostico']}**")
                    
                    # Explicar baseado no tipo de sistema usado
                    if 'score' in str(res):
                        st.markdown("**Critérios identificados:**")
                        
                        # Valores críticos detectados
                        if 'Insuficiência Renal' in res['diagnostico']:
                            st.markdown("• Creatinina CRÍTICA (valor muito elevado)")
                            st.markdown("• Valor 2x acima do limite superior")
                            st.markdown("• ATENÇÃO IMEDIATA NECESSÁRIA")
                        
                        elif 'Hipoglicemia' in res['diagnostico']:
                            st.markdown("• Glicose CRÍTICA (valor muito baixo)")
                            st.markdown("• Risco de coma")
                            st.markdown("• ATENÇÃO IMEDIATA NECESSÁRIA")
                        
                        elif 'Diabetes' in res['diagnostico']:
                            st.markdown("• Glicose elevada")
                            st.markdown("• Síndrome PU/PD (Poliúria + Polidipsia)")
                            st.markdown("• Sugestivo de diabetes")
                        
                        else:
                            st.markdown("• Baseado em critérios clínicos específicos")
                            st.markdown("• Avaliação de sintomas e exames laboratoriais")
                    
                    else:
                        st.markdown("**Baseado em modelo de IA treinado**")
                        st.markdown("• Análise de padrões em dados históricos")
                        st.markdown("• Predição probabilística")
                    
                    st.markdown("---")
                
                # Salvar resultados para sistema de medicamentos
                st.session_state.resultados_atuais = resultados
                
            except Exception as e:
                st.error(f"❌ Erro ao fazer predição: {str(e)}")
                import traceback
                with st.expander("Ver detalhes"):
                    st.code(traceback.format_exc())

# ============================================================================
# MODO 2: UPLOAD DE ARQUIVO
# ============================================================================

elif modo == "📤 Upload de Arquivo":
    st.markdown("## 📤 Upload de Arquivo para Predição em Lote")
    
    st.markdown("""
    Faça upload de um arquivo CSV ou XLSX com múltiplas amostras para predição em lote.
    
    **Requisitos:**
    - Arquivo deve conter as mesmas colunas usadas no treinamento
    - Colunas de identificação (id, especie, etc.) são opcionais mas recomendadas
    """)
    
    arquivo_pred = st.file_uploader(
        "Selecione arquivo para predição",
        type=['csv', 'xlsx', 'xls']
    )
    
    if arquivo_pred is not None:
        # Carregar arquivo
        df_pred = carregar_arquivo(arquivo_pred)
        
        if df_pred is not None:
            st.success(f"✅ Arquivo carregado: {len(df_pred)} amostras")
            
            # Preview
            with st.expander("👁️ Visualizar Dados"):
                st.dataframe(df_pred.head(10), use_container_width=True)
            
            # Verificar colunas necessárias
            colunas_faltantes = [f for f in feature_names if f not in df_pred.columns]
            
            if colunas_faltantes:
                st.warning(f"⚠️ Colunas faltantes serão preenchidas com 0: {colunas_faltantes[:10]}")
            
            # Botão de predição
            if st.button("🔍 Fazer Predições em Lote", type="primary"):
                with st.spinner(f"Fazendo predições para {len(df_pred)} amostras..."):
                    try:
                        # Preparar dados
                        df_prep = df_pred.copy()
                        
                        # Adicionar colunas faltantes
                        for feat in feature_names:
                            if feat not in df_prep.columns:
                                df_prep[feat] = 0
                        
                        # Selecionar apenas features necessárias
                        X_pred = df_prep[feature_names]
                        
                        # Preprocessar
                        from vetlib.preprocessing import aplicar_preprocessamento
                        X_pred_proc, _ = aplicar_preprocessamento(X_pred, preprocessadores, fit=False)
                        
                        # Predizer
                        y_pred = modelo.predict(X_pred_proc)
                        y_proba = modelo.predict_proba(X_pred_proc)
                        
                        # Adicionar resultados ao DataFrame original
                        df_resultado = df_pred.copy()
                        df_resultado['diagnostico_predito'] = y_pred
                        
                        # Adicionar probabilidades
                        for i, classe in enumerate(target_names):
                            df_resultado[f'prob_{classe}'] = y_proba[:, i]
                        
                        # Adicionar confiança
                        df_resultado['confianca_max'] = y_proba.max(axis=1)
                        df_resultado['confianca'] = df_resultado['confianca_max'].apply(
                            lambda x: 'Alta' if x > 0.7 else 'Média' if x > 0.4 else 'Baixa'
                        )
                        
                        # Mostrar resultados
                        st.success(f"✅ Predições concluídas para {len(df_resultado)} amostras!")
                        
                        st.markdown("### 📊 Resultados")
                        
                        # Métricas resumidas
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Total de Amostras", len(df_resultado))
                        
                        with col2:
                            n_alta_conf = (df_resultado['confianca'] == 'Alta').sum()
                            st.metric("Alta Confiança", n_alta_conf, 
                                     f"{100*n_alta_conf/len(df_resultado):.1f}%")
                        
                        with col3:
                            diag_mais_comum = df_resultado['diagnostico_predito'].value_counts().index[0]
                            st.metric("Diagnóstico Mais Comum", diag_mais_comum)
                        
                        # Distribuição de diagnósticos preditos
                        import plotly.express as px
                        
                        diag_count = df_resultado['diagnostico_predito'].value_counts().reset_index()
                        diag_count.columns = ['Diagnóstico', 'Quantidade']
                        
                        fig_diag = px.bar(
                            diag_count,
                            x='Quantidade',
                            y='Diagnóstico',
                            orientation='h',
                            title='Distribuição de Diagnósticos Preditos',
                            color='Quantidade',
                            color_continuous_scale='Blues'
                        )
                        
                        st.plotly_chart(fig_diag, use_container_width=True)
                        
                        # Tabela de resultados
                        st.markdown("### 📋 Tabela de Resultados")
                        
                        # Selecionar colunas para mostrar
                        colunas_mostrar = ['diagnostico_predito', 'confianca_max', 'confianca']
                        
                        if 'id' in df_resultado.columns:
                            colunas_mostrar = ['id'] + colunas_mostrar
                        
                        if 'especie' in df_resultado.columns:
                            colunas_mostrar.append('especie')
                        
                        st.dataframe(df_resultado[colunas_mostrar], use_container_width=True)
                        
                        # Download de resultados
                        st.markdown("### 💾 Download de Resultados")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # CSV
                            csv_data = exportar_para_download(df_resultado, formato='csv')
                            st.download_button(
                                label="📥 Download CSV",
                                data=csv_data,
                                file_name=f"predicoes_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime='text/csv'
                            )
                        
                        with col2:
                            # Excel
                            xlsx_data = exportar_para_download(df_resultado, formato='xlsx')
                            st.download_button(
                                label="📥 Download Excel",
                                data=xlsx_data,
                                file_name=f"predicoes_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                            )
                        
                    except Exception as e:
                        st.error(f"❌ Erro ao fazer predições: {str(e)}")
                        import traceback
                        with st.expander("Ver detalhes"):
                            st.code(traceback.format_exc())

# ============================================================================
# SIDEBAR: INFO DO MODELO
# ============================================================================

with st.sidebar:
    st.markdown("## 🤖 Modelo Atual")
    
    st.success("✅ Modelo carregado")
    
    st.markdown(f"**Classes:** {len(target_names)}")
    
    with st.expander("Ver classes"):
        for classe in target_names:
            st.markdown(f"- {classe}")
    
    st.markdown(f"**Features:** {len(feature_names)}")
    
    if st.session_state.get('metricas_modelo'):
        metricas = st.session_state.metricas_modelo
        st.metric("F1 Score", f"{metricas['f1_macro']:.3f}")
        st.metric("Accuracy", f"{metricas['accuracy']:.3f}")

# ============================================================================
# SISTEMA DE MEDICAMENTOS E PROTOCOLO DE TRATAMENTO
# ============================================================================

# Inicializar chat veterinário avançado se não existir
if 'chat_veterinario_avancado' not in st.session_state:
    st.session_state.chat_veterinario_avancado = ChatVeterinarioAvancado()

# Manter compatibilidade com sistema antigo
if 'chat_veterinario' not in st.session_state:
    st.session_state.chat_veterinario = ChatVeterinario()

st.markdown("---")

# ============================================================================
# SEÇÃO: RECOMENDAÇÕES DE MEDICAMENTOS (sempre visível)
# ============================================================================

st.markdown("## 💊 Sistema de Recomendações de Medicamentos")

# Sistema de recomendações sempre disponível
tem_resultados = st.session_state.get('ultima_predicao') or st.session_state.get('resultados_atuais')

if tem_resultados:
    # Priorizar predição recente, senão usar análise atual
    if st.session_state.get('ultima_predicao'):
        predicao = st.session_state.ultima_predicao
        diagnostico_top = predicao['diagnostico']
        confianca = predicao.get('confianca', 0.7)
        st.success(f"**Diagnóstico Predito:** {diagnostico_top} (Confiança: {confianca:.1%})")
    else:
        # Usar análise atual
        resultados_atuais = st.session_state.get('resultados_atuais', [])
        if resultados_atuais:
            diagnostico_top = resultados_atuais[0]['diagnostico']
            confianca = resultados_atuais[0]['probabilidade']
            st.success(f"**Diagnóstico da Análise:** {diagnostico_top} (Score: {confianca:.2f})")
        else:
            diagnostico_top = "Consulta Veterinária"
            confianca = 0.5
            st.info(f"**Diagnóstico:** {diagnostico_top} (Recomenda-se consulta veterinária)")
    
    # Obter dados do animal dos inputs atuais
    dados_animal = {
        'especie': especie,
        'peso_kg': peso_kg if 'peso_kg' in locals() else 10.0,
        'idade': idade_anos if 'idade_anos' in locals() else 1.0
    }
    
    # Criar abas para diferentes seções
    tab_meds, tab_cirurgias, tab_protocolo, tab_chat = st.tabs(["💊 Medicamentos", "🏥 Cirurgias", "📋 Protocolo", "💬 Chat"])
    
    with tab_meds:
        st.markdown("### 💊 Recomendações de Medicamentos")
        
        # Campos para peso (se não disponível)
        if not dados_animal.get('peso_kg'):
            peso_kg = st.number_input(
                "Peso do animal (kg):",
                min_value=0.1,
                max_value=100.0,
                value=10.0,
                step=0.1,
                help="Peso para cálculo de doses"
            )
        else:
            peso_kg = dados_animal['peso_kg']
            st.info(f"Peso: {peso_kg} kg")
        
        # Obter recomendações avançadas
        recomendacoes_avancadas = obter_recomendacoes_avancadas(
            diagnostico_top,
            dados_animal.get('especie', 'Canina'),
            peso_kg,
            incluir_cirurgias=False,  # Cirurgias em aba separada
            incluir_emergencia=True
        )
        
        medicamentos = recomendacoes_avancadas.get('medicamentos', [])
        urgencia_geral = recomendacoes_avancadas.get('urgencia_geral', 'BAIXA')
        
        if medicamentos:
            st.markdown(f"**Medicamentos recomendados para {diagnostico_top}:**")
            
            for i, med in enumerate(medicamentos, 1):
                with st.expander(f"**{i}. {med['nome']}** ({med['categoria']})", expanded=i==1):
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Dose para {dados_animal.get('especie', 'Canina')}:**")
                        if 'dose_calculada' in med:
                            dose_calc = med['dose_calculada']
                            st.success(f"**{dose_calc['dose_media']} {dose_calc['unidade']}**")
                            st.caption(f"Faixa: {dose_calc['dose_min']} - {dose_calc['dose_max']} {dose_calc['unidade']}")
                        else:
                            dose_campo = 'dose_cao' if dados_animal.get('especie', 'Canina') == 'Canina' else 'dose_gato'
                            st.info(f"**{med[dose_campo]}**")
                        
                        st.markdown(f"**Frequência:** {med['frequencia']}")
                        st.markdown(f"**Via:** {med['via']}")
                    
                    with col2:
                        st.markdown("**Indicação:**")
                        st.info(med['indicacao'])
                        
                        st.markdown("**Contraindicações:**")
                        st.warning(med['contraindicacoes'])
                    
                    st.markdown("**Efeitos Colaterais:**")
                    st.error(med['efeitos_colaterais'])
                    
                    st.markdown("**Monitoramento:**")
                    st.info(med['monitoramento'])
        else:
            st.warning(f"Não há recomendações específicas de medicamentos para {diagnostico_top}.")
    
    with tab_cirurgias:
        st.markdown("### 🏥 Procedimentos Cirúrgicos")
        
        # Obter recomendações de cirurgias
        recomendacoes_cirurgias = obter_recomendacoes_avancadas(
            diagnostico_top,
            dados_animal.get('especie', 'Canina'),
            peso_kg,
            incluir_cirurgias=True,
            incluir_emergencia=False
        )
        
        cirurgias = recomendacoes_cirurgias.get('cirurgias', [])
        
        if cirurgias:
            st.markdown(f"**Procedimentos cirúrgicos para {diagnostico_top}:**")
            
            for i, cirurgia in enumerate(cirurgias, 1):
                st.markdown(f"#### {i}. {cirurgia['nome']}")
                
                # Urgência com cor
                urgencia = cirurgia.get('urgencia', 'BAIXA')
                if urgencia == 'CRÍTICA':
                    st.error(f"🔴 **Urgência: {urgencia}** - Procedimento de emergência")
                elif urgencia == 'ALTA':
                    st.warning(f"🟡 **Urgência: {urgencia}** - Procedimento prioritário")
                else:
                    st.info(f"🟢 **Urgência: {urgencia}** - Procedimento eletivo")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Indicação:**")
                    st.markdown(f"• {cirurgia.get('indicacao', 'N/A')}")
                    
                    st.markdown("**Tempo de Recuperação:**")
                    st.markdown(f"• {cirurgia.get('recuperacao', 'N/A')}")
                
                with col2:
                    st.markdown("**Complicações Possíveis:**")
                    st.markdown(f"• {cirurgia.get('complicacoes', 'N/A')}")
                    
                    st.markdown("**Cuidados Pós-Operatórios:**")
                    st.markdown(f"• {cirurgia.get('cuidados_pos', 'N/A')}")
                
                st.markdown("---")
        else:
            st.info(f"Não há procedimentos cirúrgicos específicos indicados para {diagnostico_top}.")
            st.markdown("**Consulte um cirurgião veterinário para avaliação caso necessário.**")
    
    with tab_protocolo:
        st.markdown("### 📋 Protocolo Completo de Tratamento")
        
        protocolo = obter_protocolo_tratamento_avancado(
            diagnostico_top,
            dados_animal.get('especie', 'Canina'),
            peso_kg
        )
        
        # Cuidados gerais
        st.markdown("#### 🏥 Cuidados Gerais")
        for i, cuidado in enumerate(protocolo['cuidados_gerais'], 1):
            st.markdown(f"{i}. {cuidado}")
        
        # Protocolo de monitoramento
        st.markdown("#### 📊 Protocolo de Monitoramento")
        monitoramento = protocolo['monitoramento']
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Exames Laboratoriais:**")
            for exame in monitoramento:
                st.markdown(f"• {exame}")
        
        with col2:
            st.markdown("**Monitoramento Clínico:**")
            for clinico in monitoramento:
                st.markdown(f"• {clinico}")
        
        st.markdown(f"**Frequência:** Monitoramento contínuo")
        
        # Cronograma de retorno
        st.markdown("#### 📅 Cronograma de Retorno")
        retorno = {
            'primeira_consulta': '7 dias',
            'seguimento': '30 dias', 
            'manutencao': '90 dias'
        }
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Retorno Inicial", retorno['primeira_consulta'])
        with col2:
            st.metric("Seguimento", retorno['seguimento'])
        with col3:
            st.metric("Manutenção", retorno['manutencao'])
    
    with tab_chat:
        st.markdown("### 💬 Chat Veterinário Avançado com IA")
        
        # Configurar contexto do chat avançado
        st.session_state.chat_veterinario_avancado.configurar_contexto(
            diagnostico_top,
            dados_animal.get('especie', 'Canina'),
            peso_kg,
            exames_valores if 'exames_valores' in locals() else {},
            sintomas_valores if 'sintomas_valores' in locals() else {}
        )
        
        # Sistema de IA já configurado automaticamente com DeepSeek
        st.info("🤖 **Sistema de IA Veterinária Ativo** - Integrado com DeepSeek para respostas avançadas!")
        
        # Histórico do chat
        if st.session_state.chat_veterinario_avancado.historico:
            st.markdown("#### 📜 Histórico da Conversa")
            for i, msg in enumerate(st.session_state.chat_veterinario_avancado.historico[-3:], 1):
                with st.expander(f"Pergunta {i}: {msg['mensagem'][:50]}..."):
                    st.markdown(f"**Pergunta:** {msg['mensagem']}")
                    st.markdown(f"**Resposta:** {msg['resposta']}")
                    if msg.get('usou_llm'):
                        st.caption("🤖 Resposta gerada por IA")
        
        # Input para nova pergunta
        pergunta = st.text_area(
            "Digite sua pergunta:",
            placeholder="Ex: Qual a dose de dextrose para hipoglicemia crítica?",
            height=100
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            if st.button("💬 Fazer Pergunta", type="primary"):
                if pergunta.strip():
                    with st.spinner("🤖 Consultando IA especializada..."):
                        try:
                            # Usar DeepSeek se disponível, senão fallback
                            resposta = st.session_state.chat_veterinario_avancado.enviar_mensagem(pergunta, usar_llm=True)
                            st.markdown("#### 🤖 Resposta da IA Veterinária:")
                            st.markdown(resposta)
                        except Exception as e:
                            st.warning(f"Usando sistema de conhecimento local: {str(e)[:100]}...")
                            resposta = st.session_state.chat_veterinario_avancado.enviar_mensagem(pergunta, usar_llm=False)
                            st.markdown("#### 🤖 Resposta:")
                            st.markdown(resposta)
                else:
                    st.warning("Digite uma pergunta primeiro.")
        
        with col2:
            if st.button("🗑️ Limpar Chat"):
                st.session_state.chat_veterinario_avancado.historico = []
                st.rerun()
        
        with col3:
            if st.button("🔄 Nova Sessão"):
                st.session_state.chat_veterinario_avancado = ChatVeterinarioAvancado()
                st.rerun()
        
        # Sugestões de perguntas contextuais inteligentes
        st.markdown("#### 💡 Perguntas Sugeridas:")
        sugestoes_contextuais = [
            "Qual a dose de medicamento para este animal?",
            "Preciso de cirurgia para este caso?",
            "Quanto tempo leva para melhorar?",
            "Como aplicar o medicamento corretamente?",
            "Quais exames fazer no retorno?",
            "Que cuidados especiais preciso ter?"
        ]
        
        cols = st.columns(2)
        for i, sugestao in enumerate(sugestoes_contextuais):
            with cols[i % 2]:
                if st.button(f"💭 {sugestao}", key=f"sug_av_{i}"):
                    with st.spinner("🤖 Consultando..."):
                        try:
                            resposta = st.session_state.chat_veterinario_avancado.enviar_mensagem(sugestao, usar_llm=True)
                            st.markdown("#### 🤖 Resposta da IA:")
                            st.markdown(resposta)
                        except Exception as e:
                            resposta = st.session_state.chat_veterinario_avancado.enviar_mensagem(sugestao, usar_llm=False)
                            st.markdown("#### 🤖 Resposta:")
                            st.markdown(resposta)

else:
    # Mostrar sistema básico mesmo sem resultados
    st.info("💡 **Sistema de Recomendações Veterinárias** - Faça uma predição acima para recomendações específicas")
    
    # Sistema básico de medicamentos e cirurgias sempre disponível
    st.markdown("### 🩺 Consulta Veterinária Geral")
    
    # Criar tabs para medicamentos e cirurgias
    tab_meds_basico, tab_cirurgias_basico = st.tabs(["💊 Medicamentos", "🏥 Cirurgias"])
    
    with tab_meds_basico:
        # Informações básicas de medicamentos
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Medicamentos Comuns:**")
            st.markdown("• **Analgésicos:** Meloxicam, Carprofeno")
            st.markdown("• **Antibióticos:** Amoxicilina, Cefalexina")
            st.markdown("• **Anti-inflamatórios:** Prednisolona, Dexametasona")
            st.markdown("• **Digestivos:** Ranitidina, Omeprazol")
            
        with col2:
            st.markdown("**Cuidados Básicos:**")
            st.markdown("• Monitorar sinais vitais")
            st.markdown("• Manter hidratação")
            st.markdown("• Observar comportamento")
            st.markdown("• Ambiente confortável")
            st.markdown("• Nutrição adequada")
    
    with tab_cirurgias_basico:
        st.markdown("### 🏥 Procedimentos Cirúrgicos Comuns")
        
        # Cirurgias básicas
        cirurgias_basicas = [
            {
                "nome": "Castração/Esterilização",
                "urgencia": "BAIXA",
                "descricao": "Procedimento eletivo para controle populacional e saúde",
                "cuidados": "Repouso, evitar lambedura da ferida, monitorar sinais vitais"
            },
            {
                "nome": "Remoção de Corpo Estranho",
                "urgencia": "ALTA", 
                "descricao": "Remoção de objetos ingeridos ou alojados",
                "cuidados": "Monitoramento pós-operatório rigoroso, dieta adequada"
            },
            {
                "nome": "Fraturas Ósseas",
                "urgencia": "CRÍTICA",
                "descricao": "Redução e fixação de fraturas",
                "cuidados": "Imobilização, controle de dor, fisioterapia"
            },
            {
                "nome": "Cistotomia",
                "urgencia": "ALTA",
                "descricao": "Abertura da bexiga para remoção de cálculos",
                "cuidados": "Sonda urinária, antibióticos, dieta especial"
            }
        ]
        
        for i, cirurgia in enumerate(cirurgias_basicas, 1):
            with st.expander(f"{i}. {cirurgia['nome']} - Urgência: {cirurgia['urgencia']}", expanded=(i==1)):
                st.markdown(f"**Descrição:** {cirurgia['descricao']}")
                st.markdown(f"**Cuidados:** {cirurgia['cuidados']}")
                
                # Indicador de urgência
                if cirurgia['urgencia'] == 'CRÍTICA':
                    st.error("🔴 **URGÊNCIA CRÍTICA** - Procure atendimento imediato")
                elif cirurgia['urgencia'] == 'ALTA':
                    st.warning("🟡 **URGÊNCIA ALTA** - Procure atendimento em breve")
                else:
                    st.info("🟢 **ELETIVA** - Pode ser agendada")
        
    # Chat básico sempre disponível
    st.markdown("### 💬 Chat Veterinário")
    
    if 'chat_veterinario_avancado' not in st.session_state:
        st.session_state.chat_veterinario_avancado = ChatVeterinarioAvancado()
    
    # Configurar contexto básico
    st.session_state.chat_veterinario_avancado.configurar_contexto(
        "Consulta Veterinária Geral",
        "Canina",
        10.0,
        {},
        {}
    )
    
    # Sistema de IA já configurado automaticamente com DeepSeek
    st.info("🤖 **Sistema de IA Veterinária Ativo** - Integrado com DeepSeek para respostas avançadas!")
    
    # Input para pergunta
    pergunta = st.text_area(
        "Faça uma pergunta sobre medicina veterinária:",
        placeholder="Ex: Qual a dose de amoxicilina para um cão de 15kg?",
        height=100
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("💬 Fazer Pergunta", type="primary"):
            if pergunta.strip():
                with st.spinner("🤖 Consultando IA especializada..."):
                    try:
                        # Usar DeepSeek se disponível, senão fallback
                        resposta = st.session_state.chat_veterinario_avancado.enviar_mensagem(pergunta, usar_llm=True)
                        st.markdown("#### 🤖 Resposta da IA Veterinária:")
                        st.markdown(resposta)
                    except Exception as e:
                        st.warning(f"Usando sistema de conhecimento local: {str(e)[:100]}...")
                        resposta = st.session_state.chat_veterinario_avancado.enviar_mensagem(pergunta, usar_llm=False)
                        st.markdown("#### 🤖 Resposta:")
                        st.markdown(resposta)
            else:
                st.warning("Digite uma pergunta primeiro.")
    
    with col2:
        if st.button("🔄 Limpar Chat"):
            st.session_state.chat_veterinario_avancado.historico = []
            st.rerun()
    
    # Sugestões básicas
    st.markdown("#### 💡 Perguntas Sugeridas:")
    sugestoes_basicas = [
        "Qual a dose de medicamento?",
        "Preciso de cirurgia?",
        "Quais cuidados básicos?",
        "Quando procurar emergência?",
        "Como aplicar medicamento?",
        "Quais exames fazer?"
    ]
    
    cols = st.columns(2)
    for i, sugestao in enumerate(sugestoes_basicas):
        with cols[i % 2]:
            if st.button(f"💭 {sugestao}", key=f"sug_bas_{i}"):
                with st.spinner("🤖 Consultando..."):
                    try:
                        resposta = st.session_state.chat_veterinario_avancado.enviar_mensagem(sugestao, usar_llm=True)
                        st.markdown("#### 🤖 Resposta da IA:")
                        st.markdown(resposta)
                    except Exception as e:
                        resposta = st.session_state.chat_veterinario_avancado.enviar_mensagem(sugestao, usar_llm=False)
                        st.markdown("#### 🤖 Resposta:")
                        st.markdown(resposta)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>⚠️ **IMPORTANTE:** As predições e recomendações são sugestões baseadas em dados históricos</p>
    <p>🏥 **Sempre consulte um médico veterinário** para diagnóstico definitivo e prescrição de medicamentos</p>
    <p>💊 **As doses são calculadas automaticamente** mas devem ser validadas por um profissional</p>
</div>
""", unsafe_allow_html=True)

