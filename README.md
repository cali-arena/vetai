# 🐾 DIAGVET IA - Sistema Inteligente de Diagnóstico Veterinário

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)

## 📋 Visão Geral

O **DIAGVET IA** é um sistema completo de diagnóstico veterinário baseado em inteligência artificial, desenvolvido com Streamlit para análise de dados clínicos, laboratoriais e predição de diagnósticos em animais. O sistema oferece uma interface intuitiva para veterinários analisarem dados de pacientes e obterem insights baseados em machine learning.

## 🚀 Aplicações Disponíveis

### 🔧 Aplicação Principal
- **Arquivo:** `app.py`
- **URL Local:** http://localhost:8501
- **Descrição:** Interface principal com todas as funcionalidades completas

### 💾 Aplicação Backup
- **Arquivo:** `app_backup.py` / `backup.py`
- **URL geral:** http://localhost:8598
- **URL compilada:** https://diagvetai.streamlit.app/


### 📱 Aplicação Simples
- **Arquivo:** `app_simples_vet.py`
- **Descrição:** Versão simplificada focada em predições rápidas

## 📊 Funcionalidades

### 🏠 **Visão Geral**
- Dashboard com estatísticas gerais
- Distribuição de idade e gênero dos pacientes
- Raças mais comuns (caninos e felinos)
- Métricas de resumo dos dados

### 🧪 **Laboratório & Sintomas (EDA)**
- Análise exploratória de dados
- Visualizações interativas
- Correlações entre variáveis
- Distribuições estatísticas

### 🤖 **Treinar Modelo**
- Treinamento de modelos de Machine Learning
- Validação cruzada
- Métricas de performance
- Comparação de algoritmos

### 🔍 **Predição**
- Sistema de predição de diagnósticos
- Interface intuitiva para entrada de dados
- Probabilidades de diagnóstico
- Explicabilidade dos resultados

### 📥 **Upload de Dados**
- Importação de dados veterinários
- Suporte a múltiplos formatos (CSV, Excel)
- Validação de dados
- Pré-processamento automático

### 🧠 **Insights & Regras**
- Regras clínicas implementadas
- Insights baseados em dados
- Recomendações de tratamento
- Sistema de medicamentos

## 📁 Estrutura do Projeto

```
VET/
├── 📱 Aplicações
│   ├── app.py                 # Aplicação principal
│   ├── app_backup.py          # Aplicação backup
│   ├── app_simples_vet.py     # Aplicação simplificada
│   └── backup.py              # Versão alternativa
├── 📄 Páginas
│   ├── pages/
│   │   ├── 1_📊_Visão_Geral.py
│   │   ├── 2_🧪_Laboratório_&_Sintomas_(EDA).py
│   │   ├── 3_🤖_Treinar_Modelo.py
│   │   ├── 4_🔍_Predição.py
│   │   ├── 5_📥_Upload_de_Dados.py
│   │   └── 6_🧠_Insights_&_Regras.py
├── 📊 Dados
│   ├── data/
│   │   ├── clinical_veterinary_data.csv
│   │   ├── laboratory_complete_panel.csv
│   │   ├── veterinary_complete_real_dataset.csv
│   │   └── veterinary_master_dataset.csv
├── 🤖 Modelos
│   ├── models/
│   │   ├── gb_model_optimized.pkl
│   │   ├── model_minimal.pkl
│   │   └── model_info_781.txt
├── 📚 Biblioteca
│   ├── vetlib/
│   │   ├── __init__.py
│   │   ├── modeling.py
│   │   ├── preprocessing.py
│   │   ├── medications.py
│   │   ├── clinical_rules.py
│   │   └── insights.py
└── 📋 Configuração
    ├── requirements.txt
    ├── README.md
    └── DEPLOY.md
```

## 🔧 Tecnologias Utilizadas

- **🐍 Python 3.8+** - Linguagem principal
- **📊 Streamlit** - Interface web interativa
- **🐼 Pandas** - Manipulação e análise de dados
- **🔢 NumPy** - Computação numérica
- **🤖 Scikit-learn** - Machine Learning
- **📈 Plotly** - Visualizações interativas
- **📊 Matplotlib/Seaborn** - Gráficos estáticos
- **📄 OpenPyXL** - Manipulação de arquivos Excel
- **🖼️ Pillow** - Processamento de imagens

## 📊 Datasets Incluídos

- **Dados Clínicos Veterinários** - Informações de consultas e diagnósticos
- **Painel Laboratorial Completo** - Resultados de exames laboratoriais
- **Dataset Realista** - Dados sintéticos baseados em casos reais
- **Dataset Mestre** - Consolidação de todas as fontes de dados

## 🚀 Deploy

### Deploy Local
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run app.py
```

### Deploy em Produção
Consulte o arquivo `DEPLOY.md` para instruções detalhadas de deploy em produção.

## 📝 Status do Sistema

✅ **Aplicação Backup:** Funcionando em http://localhost:8598  
✅ **Dependências:** Todas instaladas e funcionais  
✅ **Modelos:** Carregados e operacionais  
✅ **Datasets:** Carregados e validados  
⚠️ **Avisos:** Alguns warnings sobre `use_container_width` (não críticos)

## 🌐 URLs de Acesso

### Local
- **Principal:** http://localhost:8501


## 📚 Documentação Adicional

- **[QUICKSTART.md](QUICKSTART.md)** - Guia de início rápido
- **[DEPLOY.md](DEPLOY.md)** - Instruções de deploy
- **[PROJETO_COMPLETO.md](PROJETO_COMPLETO.md)** - Documentação completa do projeto
- **[SISTEMA_MEDICAMENTOS.md](SISTEMA_MEDICAMENTOS.md)** - Sistema de medicamentos

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👥 Autores

- **Lucas Cabral, Klauber Barros, Amanda Rodrigues, Marry, Fernando** - *Desenvolvimento Principal* - [@cali-arena](https://github.com/cali-arena)

## 🙏 Agradecimentos

- Comunidade Streamlit
- Scikit-learn team
- Pandas development team
- Veterinários que contribuíram com dados e feedback

---

*Sistema desenvolvido para auxiliar veterinários no diagnóstico e análise de dados clínicos de animais, utilizando inteligência artificial para melhorar a precisão e eficiência dos diagnósticos veterinários.*

