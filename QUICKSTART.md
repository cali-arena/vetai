# 🚀 Guia de Início Rápido - DIAGVET IA

## ⚡ Execução em 3 Passos

### 1️⃣ **Clone o Repositório**
```bash
git clone https://github.com/cali-arena/vetai.git
cd vetai/VET
```

### 2️⃣ **Instale as Dependências**
```bash
pip install -r requirements.txt
```

### 3️⃣ **Execute a Aplicação**
```bash
# Aplicação principal
python -m streamlit run app.py

# OU aplicação backup (mais estável)
python -m streamlit run backup.py --server.port 8598
```

## 🌐 Acesso

Abra seu navegador em: **http://localhost:8501** ou **http://localhost:8598**

## 📱 Aplicações Disponíveis

| Aplicação | Arquivo | Porta | Descrição |
|-----------|---------|-------|-----------|
| **Principal** | `app.py` | 8501 | Interface completa |
| **Backup** | `backup.py` | 8598 | Versão estável |
| **Simples** | `app_simples_vet.py` | 8506 | Versão simplificada |

## 🔧 Solução de Problemas

### ❌ Erro: "Port already in use"
```bash
# Use uma porta diferente
python -m streamlit run backup.py --server.port 8599
```

### ❌ Erro: "File does not exist"
```bash
# Certifique-se de estar no diretório correto
cd VET
ls app.py  # Verificar se o arquivo existe
```

### ❌ Erro: "Module not found"
```bash
# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

## 📊 Primeiros Passos

1. **Visão Geral** - Explore o dashboard principal
2. **Upload de Dados** - Carregue seus dados veterinários
3. **Predição** - Teste o sistema de diagnóstico
4. **Insights** - Veja as regras clínicas implementadas

## 🎯 Funcionalidades Principais

- ✅ **Dashboard Interativo** - Visualizações em tempo real
- ✅ **Predição de Diagnósticos** - IA para auxiliar veterinários
- ✅ **Upload de Dados** - Suporte a CSV e Excel
- ✅ **Análise Exploratória** - EDA completo dos dados
- ✅ **Sistema de Medicamentos** - Recomendações baseadas em dados

## 📞 Suporte

Se encontrar problemas:
1. Verifique se todas as dependências estão instaladas
2. Confirme que está no diretório correto (`VET/`)
3. Tente usar a aplicação backup (`backup.py`)
4. Abra uma issue no GitHub

---

**🎉 Pronto! Seu sistema DIAGVET IA está funcionando!**
