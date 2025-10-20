# 🐾 VetDiagnosisAI - Nova Arquitetura

## 📋 Visão Geral

O sistema agora está dividido em **duas aplicações separadas** para melhor performance e organização:

### 🎯 **App de Predição (Veterinários)**
- **Arquivo**: `app_simples_vet.py`
- **Objetivo**: Interface simples e rápida para veterinários fazerem predições
- **Características**:
  - ✅ Interface limpa e focada
  - ✅ Carregamento rápido (apenas modelo pré-treinado)
  - ✅ Formulário intuitivo para dados do animal
  - ✅ Resultados com confiança e probabilidades
  - ✅ Sem treinamento de modelo (evita demora)

### 📊 **App Gerencial (Administradores)**
- **Arquivo**: `app_gerencial.py`
- **Objetivo**: Dashboard completo para monitorar e gerenciar o modelo
- **Características**:
  - ✅ Monitoramento de performance
  - ✅ Treinamento de novos modelos
  - ✅ Analytics de uso
  - ✅ Configurações do sistema
  - ✅ Logs de predições

### 🤖 **Script de Treinamento**
- **Arquivo**: `train_model.py`
- **Objetivo**: Treinar modelos separadamente via Python
- **Características**:
  - ✅ Treinamento completo e otimizado
  - ✅ Feature engineering avançado
  - ✅ Otimização de hiperparâmetros
  - ✅ Salva modelo pronto para uso

---

## 🚀 Como Usar

### 1. **Treinar o Modelo (Primeira vez)**
```bash
cd VET
python train_model.py
```

**O que acontece:**
- 🔄 Carrega dados reais da pasta `data/`
- 🔧 Cria features avançadas
- ⚙️ Otimiza hiperparâmetros automaticamente
- 🎯 Treina modelo Gradient Boosting
- 💾 Salva modelo em `models/gb_optimized_model.pkl`

### 2. **Usar App de Predição (Veterinários)**
```bash
streamlit run app_simples_vet.py
```

**Interface para veterinários:**
- 📋 Formulário simples com dados do animal
- 🧪 Campos para exames laboratoriais
- 🏥 Checkboxes para sintomas
- 🔍 Botão "Realizar Predição"
- 📊 Resultados com diagnóstico e confiança

### 3. **Usar App Gerencial (Administradores)**
```bash
streamlit run app_gerencial.py
```

**Funcionalidades:**
- 📈 **Visão Geral**: Métricas do sistema
- 🤖 **Treinar Modelo**: Retreinar com novos dados
- 📊 **Analytics**: Monitorar uso e performance
- ⚙️ **Configurações**: Ajustar parâmetros do sistema

---

## 📁 Estrutura de Arquivos

```
VET/
├── app_simples_vet.py          # App de predição para veterinários
├── app_gerencial.py            # Dashboard gerencial
├── train_model.py              # Script de treinamento
├── app.py                      # App original (não usar)
├── models/                     # Pasta dos modelos treinados
│   ├── gb_optimized_model.pkl  # Modelo principal
│   └── model_info.txt          # Informações do modelo
├── data/                       # Dados reais
│   ├── veterinary_complete_real_dataset.csv
│   ├── veterinary_master_dataset.csv
│   └── ...outros datasets
├── logs/                       # Logs de predições
│   └── predictions.json
└── README_NOVA_ARQUITETURA.md  # Este arquivo
```

---

## 🎯 Fluxo de Trabalho

### **Para Veterinários:**
1. Abrir `app_simples_vet.py`
2. Preencher dados do animal
3. Clicar em "Realizar Predição"
4. Ver diagnóstico e confiança

### **Para Administradores:**
1. **Monitorar**: Usar `app_gerencial.py` → Visão Geral
2. **Treinar**: Usar `train_model.py` ou app gerencial
3. **Analisar**: Usar `app_gerencial.py` → Analytics
4. **Configurar**: Usar `app_gerencial.py` → Configurações

---

## 🔧 Configuração

### **Requisitos:**
```bash
pip install streamlit pandas numpy scikit-learn plotly joblib
```

### **Deploy no Streamlit Cloud:**
1. **App de Predição**: Deploy de `app_simples_vet.py`
2. **App Gerencial**: Deploy de `app_gerencial.py`
3. **Dados**: Garantir que pasta `data/` e `models/` estão no repositório

---

## 📊 Vantagens da Nova Arquitetura

### ✅ **Performance:**
- App de predição carrega em segundos
- Sem demora de treinamento para veterinários
- Modelo otimizado separadamente

### ✅ **Usabilidade:**
- Interface focada para cada tipo de usuário
- Veterinários: Interface simples e rápida
- Administradores: Controle completo

### ✅ **Manutenção:**
- Treinamento de modelo isolado
- Fácil atualização do modelo
- Logs e analytics separados

### ✅ **Escalabilidade:**
- Pode ter múltiplos modelos
- Sistema de logs para análise
- Fácil adição de novos recursos

---

## 🎯 Próximos Passos

1. **✅ Implementado**: Arquitetura básica
2. **🔄 Em desenvolvimento**: Sistema de logs automático
3. **📋 Planejado**: Retreinamento automático
4. **📋 Planejado**: Alertas por email
5. **📋 Planejado**: Múltiplos modelos

---

## 🆘 Suporte

- **Problemas com dados**: Verificar pasta `data/`
- **Problemas com modelo**: Executar `train_model.py`
- **Problemas de interface**: Verificar logs do Streamlit
- **Dúvidas**: Consultar este README

---

**🎉 Sistema otimizado para veterinários e administradores!**
