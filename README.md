🐾 DIAGVET IA — Sistema Inteligente de Diagnóstico Veterinário








📋 Visão Geral

O DIAGVET IA é um sistema inteligente de apoio ao diagnóstico veterinário, desenvolvido com Python e Streamlit, que aplica Machine Learning e Análise de Dados Clínicos e Laboratoriais para auxiliar profissionais veterinários na tomada de decisão.

O projeto foi desenvolvido no contexto acadêmico de MBA, com o objetivo de aplicar inteligência artificial de forma prática e ética à medicina veterinária.

🌐 Acesso às Aplicações
Tipo	Descrição	Link
🧠 Aplicação Principal (Predição e Dashboard)	Interface completa com análise de dados, predição de diagnósticos e regras clínicas.	🔗 https://diagvetai.streamlit.app/

📊 Análise de Dados (EDA e Laboratório)	Painel dedicado à análise exploratória e visualização de dados clínicos e laboratoriais.	🔗 https://vetdata.streamlit.app/
📊 Funcionalidades Principais
🏠 Visão Geral

Dashboard com estatísticas de pacientes

Distribuição de idade, gênero e raças

Métricas resumidas e indicadores clínicos

🧪 Laboratório & Sintomas (EDA)

Análise exploratória interativa

Correlação entre variáveis clínicas e laboratoriais

Visualizações com Plotly, Seaborn e Matplotlib

🤖 Treinar Modelo

Treinamento de modelos de Machine Learning

Validação cruzada e métricas de performance

Comparação de diferentes algoritmos (Random Forest, Gradient Boosting, etc.)

🔍 Predição

Entrada de dados clínicos e laboratoriais

Predição de diagnósticos com probabilidades

Explicabilidade dos resultados e regras clínicas associadas

📥 Upload de Dados

Envio de arquivos CSV/Excel

Validação automática e pré-processamento dos dados

🧠 Insights & Regras

Geração de insights clínicos baseados em IA

Sugestões e recomendações automáticas

Regras diagnósticas e terapêuticas implementadas

📁 Estrutura do Projeto
VET/
├── app.py                        # Aplicação principal (Streamlit)
├── app_backup.py / backup.py     # Versão alternativa
├── app_simples_vet.py            # Versão simplificada para predições rápidas
│
├── pages/                        # Páginas do Streamlit
│   ├── 1_📊_Visão_Geral.py
│   ├── 2_🧪_Laboratório_&_Sintomas_(EDA).py
│   ├── 3_🤖_Treinar_Modelo.py
│   ├── 4_🔍_Predição.py
│   ├── 5_📥_Upload_de_Dados.py
│   └── 6_🧠_Insights_&_Regras.py
│
├── data/                         # Bases de dados utilizadas
│   ├── clinical_veterinary_data.csv
│   ├── laboratory_complete_panel.csv
│   ├── veterinary_complete_real_dataset.csv
│   └── veterinary_master_dataset.csv
│
├── models/                       # Modelos de IA
│   ├── gb_model_optimized.pkl
│   ├── model_minimal.pkl
│   └── model_info_781.txt
│
├── vetlib/                       # Biblioteca interna
│   ├── modeling.py
│   ├── preprocessing.py
│   ├── medications.py
│   ├── clinical_rules.py
│   └── insights.py
│
└── Configuração
    ├── requirements.txt
    ├── README.md
    └── DEPLOY.md

🔧 Tecnologias Utilizadas

🐍 Python 3.8+

📊 Streamlit

🐼 Pandas / NumPy

🤖 Scikit-learn

📈 Plotly / Seaborn / Matplotlib

📄 OpenPyXL

🧠 Pickle / Joblib (para modelos)

🖼️ Pillow (para imagens)

📊 Datasets

Clinical Veterinary Data: dados clínicos gerais de pacientes

Laboratory Complete Panel: painel de exames laboratoriais

Veterinary Complete Real Dataset: base de dados realista

Veterinary Master Dataset: base consolidada para modelagem

🚀 Execução Local (opcional para desenvolvedores)
# Instalar dependências
pip install -r requirements.txt

# Rodar a aplicação
streamlit run app.py

🧩 Propósito Acadêmico

O projeto DIAGVET IA foi desenvolvido no contexto de um MBA em Data Science & Inteligência Artificial, com foco em:

Aplicação de IA em contextos reais de saúde animal

Desenvolvimento de dashboards interativos para apoio à decisão

Integração entre estatística, ciência de dados e medicina veterinária

👥 Autores

Equipe de Desenvolvimento:
Lucas Cabral, Klauber Barros, Amanda Rodrigues, Marry, Fernando
🔗 GitHub: @cali-arena

📄 Licença

Distribuído sob a Licença MIT — consulte o arquivo LICENSE para mais informações.

🙏 Agradecimentos

Comunidade Streamlit

Scikit-learn & Pandas teams

Profissionais veterinários que contribuíram com feedback e dados

Coordenação do MBA em Data Science & IA

Projeto acadêmico desenvolvido para demonstrar a aplicação prática de Inteligência Artificial em diagnósticos veterinários, unindo ciência de dados, aprendizado de máquina e saúde animal.
