"""
VetDiagnosisAI - App Gerencial
Dashboard para monitorar performance, acurácia e retreinar modelo
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta
import joblib
import json
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="VetDiagnosisAI - Dashboard Gerencial",
    page_icon="📊",
    layout="wide"
)

# CSS personalizado
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .success-card {
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .warning-card {
        background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("📊 VetDiagnosisAI - Dashboard Gerencial")
st.markdown("### Monitoramento de Performance e Gestão do Modelo")

# Sidebar para navegação
st.sidebar.title("🎛️ Controles")
pagina = st.sidebar.selectbox(
    "Selecione a página:",
    ["📈 Visão Geral", "🤖 Treinar Modelo", "📊 Analytics", "⚙️ Configurações"]
)

# Função para carregar dados reais
@st.cache_data
def carregar_dados_reais():
    """Carrega dados reais da pasta data"""
    try:
        data_path = Path("data")
        if not data_path.exists():
            return None
            
        csv_files = list(data_path.glob("*.csv"))
        if not csv_files:
            return None
            
        # Priorizar datasets específicos
        datasets_prioritarios = [
            'veterinary_complete_real_dataset.csv',
            'veterinary_master_dataset.csv', 
            'veterinary_realistic_dataset.csv',
            'clinical_veterinary_data.csv',
            'laboratory_complete_panel.csv'
        ]
        
        for dataset_name in datasets_prioritarios:
            dataset_path = data_path / dataset_name
            if dataset_path.exists():
                df = pd.read_csv(dataset_path)
                if len(df) > 0:
                    return df, dataset_name
                    
        # Se não encontrar os prioritários, usar qualquer CSV
        if csv_files:
            df = pd.read_csv(csv_files[0])
            return df, csv_files[0].name
            
        return None
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

# Função para carregar logs de predições
def carregar_logs():
    """Carrega logs de predições (simulado por enquanto)"""
    logs_path = Path("logs/predictions.json")
    if logs_path.exists():
        try:
            with open(logs_path, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

# Função para salvar logs
def salvar_log(log_data):
    """Salva log de predição"""
    logs_path = Path("logs")
    logs_path.mkdir(exist_ok=True)
    
    logs = carregar_logs()
    logs.append(log_data)
    
    # Manter apenas últimos 1000 logs
    if len(logs) > 1000:
        logs = logs[-1000:]
    
    with open(logs_path / "predictions.json", 'w') as f:
        json.dump(logs, f, indent=2)

# Página: Visão Geral
if pagina == "📈 Visão Geral":
    st.header("📈 Visão Geral do Sistema")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    # Carregar dados para estatísticas
    dados_result = carregar_dados_reais()
    if dados_result:
        df, dataset_name = dados_result
        total_registros = len(df)
        total_diagnosticos = df['diagnostico'].nunique() if 'diagnostico' in df.columns else 0
    else:
        total_registros = 0
        total_diagnosticos = 0
    
    # Carregar informações do modelo atual
    model_path = Path("models/gb_optimized_model.pkl")
    if model_path.exists():
        try:
            model_data = joblib.load(model_path)
            accuracy_atual = model_data.get('accuracy', 0)
            ultima_atualizacao = model_data.get('timestamp', 'N/A')
        except:
            accuracy_atual = 0
            ultima_atualizacao = 'N/A'
    else:
        accuracy_atual = 0
        ultima_atualizacao = 'Nunca'
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📊 Total de Registros", f"{total_registros:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🏥 Diagnósticos Únicos", total_diagnosticos)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        color_class = "success-card" if accuracy_atual >= 0.85 else "warning-card"
        st.markdown(f'<div class="{color_class}">', unsafe_allow_html=True)
        st.metric("🎯 Acurácia Atual", f"{accuracy_atual:.1%}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🔄 Última Atualização", ultima_atualizacao.split('T')[0] if 'T' in ultima_atualizacao else ultima_atualizacao)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Status do modelo
    st.subheader("🎯 Status do Modelo")
    
    if accuracy_atual >= 0.85:
        st.success("✅ **Modelo em Excelente Estado!** Acurácia >= 85%")
    elif accuracy_atual >= 0.75:
        st.warning("⚠️ **Modelo Aceitável** - Considere retreinar para melhorar performance")
    else:
        st.error("❌ **Modelo Precisa de Atualização** - Acurácia abaixo de 75%")
    
    # Gráficos de performance
    if dados_result:
        df, dataset_name = dados_result
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribuição de diagnósticos
            if 'diagnostico' in df.columns:
                diag_counts = df['diagnostico'].value_counts().head(10)
                fig = px.pie(
                    values=diag_counts.values,
                    names=diag_counts.index,
                    title="Top 10 Diagnósticos Mais Frequentes"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Distribuição por espécie
            if 'especie' in df.columns:
                especie_counts = df['especie'].value_counts()
                fig = px.bar(
                    x=especie_counts.index,
                    y=especie_counts.values,
                    title="Distribuição por Espécie"
                )
                st.plotly_chart(fig, use_container_width=True)

# Página: Treinar Modelo
elif pagina == "🤖 Treinar Modelo":
    st.header("🤖 Treinamento do Modelo")
    
    dados_result = carregar_dados_reais()
    if not dados_result:
        st.error("❌ Nenhum dataset encontrado na pasta 'data/'. Adicione dados reais para treinar o modelo.")
        st.stop()
    
    df, dataset_name = dados_result
    st.success(f"✅ Dataset carregado: {dataset_name} ({len(df)} registros)")
    
    # Configurações de treinamento
    st.subheader("⚙️ Configurações de Treinamento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        use_advanced_features = st.checkbox("🔧 Feature Engineering Avançado", value=True)
        use_feature_selection = st.checkbox("🎯 Seleção de Features", value=True)
        test_size = st.slider("📊 Tamanho do Teste", 0.1, 0.4, 0.2, 0.05)
    
    with col2:
        use_hyperparameter_tuning = st.checkbox("⚙️ Otimização de Hiperparâmetros", value=True)
        cv_folds = st.slider("🔄 Validação Cruzada (folds)", 3, 10, 5)
        random_state = st.number_input("🎲 Random State", 1, 1000, 42)
    
    # Botão para treinar
    if st.button("🚀 Treinar Modelo", type="primary", use_container_width=True):
        
        with st.spinner("🔄 Preparando dados..."):
            # Preparar dados
            df_ml = df.copy()
            
            # Codificação
            le_especie = LabelEncoder()
            le_sexo = LabelEncoder()
            le_diagnostico = LabelEncoder()
            
            if 'especie' in df_ml.columns:
                df_ml['especie_encoded'] = le_especie.fit_transform(df_ml['especie'])
            if 'sexo' in df_ml.columns:
                df_ml['sexo_encoded'] = le_sexo.fit_transform(df_ml['sexo'])
            df_ml['diagnostico_encoded'] = le_diagnostico.fit_transform(df_ml['diagnostico'])
            
            # Feature engineering
            if use_advanced_features:
                # Criar features derivadas
                if 'idade_anos' in df_ml.columns:
                    df_ml['idade_categoria'] = pd.cut(df_ml['idade_anos'], bins=[0, 1, 3, 7, 12, 100], labels=[0, 1, 2, 3, 4])
                    df_ml['idade_senior'] = (df_ml['idade_anos'] > 7).astype(int)
                
                # Criar features de sintomas
                sintoma_cols = [col for col in df_ml.columns if col in ['febre', 'apatia', 'perda_peso', 'vomito', 'diarreia', 'tosse', 'letargia', 'feridas_cutaneas', 'poliuria', 'polidipsia']]
                if sintoma_cols:
                    df_ml['total_sintomas'] = df_ml[sintoma_cols].sum(axis=1)
            
            # Selecionar features numéricas
            numeric_cols = df_ml.select_dtypes(include=[np.number]).columns.tolist()
            if 'diagnostico_encoded' in numeric_cols:
                numeric_cols.remove('diagnostico_encoded')
            
            X = df_ml[numeric_cols].fillna(0)
            y = df_ml['diagnostico_encoded']
            
            # Feature selection
            if use_feature_selection:
                from sklearn.feature_selection import SelectKBest, f_classif
                k_best = min(30, X.shape[1])
                selector = SelectKBest(score_func=f_classif, k=k_best)
                X = selector.fit_transform(X, y)
        
        with st.spinner("🔄 Dividindo dados..."):
            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=y
            )
            
            # Escalar
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
        
        with st.spinner("🔄 Treinando modelo..."):
            # Configurar modelo
            gb_params = {
                'n_estimators': 1000,
                'learning_rate': 0.01,
                'max_depth': 12,
                'min_samples_split': 2,
                'min_samples_leaf': 1,
                'subsample': 0.8,
                'random_state': random_state
            }
            
            # Otimização de hiperparâmetros
            if use_hyperparameter_tuning:
                param_grid = {
                    'n_estimators': [800, 1000, 1200],
                    'learning_rate': [0.005, 0.01, 0.02],
                    'max_depth': [10, 12, 15],
                    'subsample': [0.7, 0.8, 0.9]
                }
                
                gb_base = GradientBoostingClassifier(random_state=random_state)
                random_search = RandomizedSearchCV(
                    gb_base, param_grid, n_iter=15, cv=cv_folds, 
                    scoring='accuracy', random_state=random_state, n_jobs=-1
                )
                random_search.fit(X_train_scaled, y_train)
                gb_params.update(random_search.best_params_)
            
            # Treinar modelo final
            gb_model = GradientBoostingClassifier(**gb_params)
            gb_model.fit(X_train_scaled, y_train)
            
            # Predições
            y_pred = gb_model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Validação cruzada
            cv_scores = cross_val_score(gb_model, X_train_scaled, y_train, cv=cv_folds)
            cv_mean = cv_scores.mean()
            cv_std = cv_scores.std()
        
        # Salvar modelo
        with st.spinner("💾 Salvando modelo..."):
            model_data = {
                'model': gb_model,
                'scaler': scaler,
                'le_diagnostico': le_diagnostico,
                'le_especie': le_especie,
                'le_sexo': le_sexo,
                'accuracy': accuracy,
                'cv_mean': cv_mean,
                'cv_std': cv_std,
                'timestamp': datetime.now().isoformat(),
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'features_used': numeric_cols[:X.shape[1]] if use_feature_selection else numeric_cols
            }
            
            model_path = Path("models")
            model_path.mkdir(exist_ok=True)
            joblib.dump(model_data, model_path / "gb_optimized_model.pkl")
        
        # Mostrar resultados
        st.success("✅ Modelo treinado e salvo com sucesso!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🎯 Acurácia", f"{accuracy:.1%}")
        with col2:
            st.metric("📊 CV Mean", f"{cv_mean:.3f}")
        with col3:
            st.metric("📈 CV Std", f"{cv_std:.3f}")
        
        # Status da meta
        if accuracy >= 0.85:
            st.success(f"🎉 **META ALCANÇADA!** Acurácia de {accuracy:.1%} >= 85%!")
        else:
            st.warning(f"🎯 Meta: 85% | Atual: {accuracy:.1%} | Faltam: {(0.85-accuracy)*100:.1f}%")

# Página: Analytics
elif pagina == "📊 Analytics":
    st.header("📊 Analytics e Monitoramento")
    
    # Carregar logs
    logs = carregar_logs()
    
    if not logs:
        st.info("📊 Nenhum log de predições encontrado ainda.")
        st.info("💡 Use o app de predição para gerar dados de analytics.")
    else:
        st.success(f"📊 {len(logs)} predições registradas")
        
        # Converter logs para DataFrame
        df_logs = pd.DataFrame(logs)
        df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp'])
        
        # Métricas de uso
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Total de Predições", len(df_logs))
        
        with col2:
            predicoes_hoje = len(df_logs[df_logs['timestamp'].dt.date == datetime.now().date()])
            st.metric("📅 Predições Hoje", predicoes_hoje)
        
        with col3:
            confianca_media = df_logs['confianca'].mean()
            st.metric("🎯 Confiança Média", f"{confianca_media:.1f}%")
        
        with col4:
            especies_unicas = df_logs['especie'].nunique()
            st.metric("🐾 Espécies Atendidas", especies_unicas)
        
        # Gráficos de analytics
        col1, col2 = st.columns(2)
        
        with col1:
            # Predições por dia
            df_daily = df_logs.groupby(df_logs['timestamp'].dt.date).size().reset_index(name='predicoes')
            fig = px.line(df_daily, x='timestamp', y='predicoes', title='Predições por Dia')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Distribuição de diagnósticos
            diag_counts = df_logs['diagnostico_predito'].value_counts().head(10)
            fig = px.bar(diag_counts, title='Top 10 Diagnósticos Mais Preditos')
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabela de logs recentes
        st.subheader("📋 Predições Recentes")
        df_recent = df_logs.tail(20)[['timestamp', 'especie', 'idade', 'diagnostico_predito', 'confianca']]
        st.dataframe(df_recent, use_container_width=True)

# Página: Configurações
elif pagina == "⚙️ Configurações":
    st.header("⚙️ Configurações do Sistema")
    
    # Configurações do modelo
    st.subheader("🤖 Configurações do Modelo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**Configurações Atuais:**")
        model_path = Path("models/gb_optimized_model.pkl")
        if model_path.exists():
            model_data = joblib.load(model_path)
            st.write(f"✅ Modelo carregado")
            st.write(f"📊 Acurácia: {model_data.get('accuracy', 0):.1%}")
            st.write(f"🕒 Última atualização: {model_data.get('timestamp', 'N/A')}")
        else:
            st.write("❌ Nenhum modelo encontrado")
    
    with col2:
        st.info("**Ações Disponíveis:**")
        if st.button("🔄 Retreinar Modelo", type="primary"):
            st.info("Use a aba 'Treinar Modelo' para retreinar")
        
        if st.button("📊 Verificar Performance"):
            st.info("Analisando performance atual...")
        
        if st.button("🧹 Limpar Logs"):
            logs_path = Path("logs/predictions.json")
            if logs_path.exists():
                logs_path.unlink()
                st.success("Logs limpos!")
    
    # Configurações do sistema
    st.subheader("🔧 Configurações do Sistema")
    
    auto_retrain = st.checkbox("🔄 Retreinamento Automático", value=False, help="Retreinar modelo automaticamente quando acurácia < 75%")
    log_predictions = st.checkbox("📊 Log de Predições", value=True, help="Registrar todas as predições para analytics")
    email_alerts = st.checkbox("📧 Alertas por Email", value=False, help="Enviar alertas quando acurácia cair")
    
    if st.button("💾 Salvar Configurações"):
        config = {
            'auto_retrain': auto_retrain,
            'log_predictions': log_predictions,
            'email_alerts': email_alerts
        }
        
        config_path = Path("config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        st.success("✅ Configurações salvas!")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <p>📊 VetDiagnosisAI - Dashboard Gerencial</p>
    <p><small>Sistema de monitoramento e gestão do modelo de diagnóstico veterinário</small></p>
</div>
""", unsafe_allow_html=True)
