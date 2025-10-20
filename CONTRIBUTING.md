# 🤝 Guia de Contribuição - DIAGVET IA

Obrigado por considerar contribuir para o DIAGVET IA! Este documento fornece diretrizes para contribuir com o projeto.

## 📋 Como Contribuir

### 1. Fork do Projeto
1. Faça um fork do repositório no GitHub
2. Clone seu fork localmente:
   ```bash
   git clone https://github.com/SEU_USUARIO/vetai.git
   cd vetai
   ```

### 2. Configuração do Ambiente
```bash
# Navegue para o diretório VET
cd VET

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### 3. Criar uma Branch
```bash
git checkout -b feature/nova-funcionalidade
# ou
git checkout -b fix/correcao-bug
```

### 4. Fazer as Alterações
- Faça suas alterações no código
- Teste localmente executando:
  ```bash
  python -m streamlit run backup.py
  ```
- Certifique-se de que não há erros

### 5. Commit e Push
```bash
git add .
git commit -m "feat: adiciona nova funcionalidade X"
git push origin feature/nova-funcionalidade
```

### 6. Pull Request
1. Vá para o repositório original no GitHub
2. Clique em "New Pull Request"
3. Selecione sua branch
4. Descreva suas alterações
5. Submeta o PR

## 📝 Padrões de Código

### Python
- Use PEP 8 para estilo de código
- Máximo de 88 caracteres por linha
- Use type hints quando possível
- Documente funções com docstrings

### Streamlit
- Use `st.cache_data` para cache de dados
- Organize o código em funções
- Use componentes reutilizáveis
- Mantenha a interface limpa

### Commits
Use o padrão Conventional Commits:
- `feat:` nova funcionalidade
- `fix:` correção de bug
- `docs:` documentação
- `style:` formatação
- `refactor:` refatoração
- `test:` testes
- `chore:` tarefas de manutenção

## 🧪 Testes

### Executar Testes
```bash
# Teste básico
python test_basic.py

# Teste de predição
python test_prediction.py

# Teste de datasets
python test_datasets.py
```

### Criar Novos Testes
- Crie arquivos `test_*.py`
- Teste funcionalidades críticas
- Inclua casos de erro

## 📚 Documentação

### Atualizar Documentação
- README.md para mudanças principais
- QUICKSTART.md para novos passos
- DEPLOY.md para mudanças de deploy
- Comentários no código para funções complexas

### Adicionar Novos Recursos
1. Documente no README
2. Atualize o QUICKSTART se necessário
3. Adicione exemplos de uso
4. Inclua screenshots se aplicável

## 🐛 Reportar Bugs

### Template de Bug Report
```markdown
**Descrição do Bug**
Descrição clara do problema.

**Passos para Reproduzir**
1. Vá para '...'
2. Clique em '...'
3. Veja o erro

**Comportamento Esperado**
O que deveria acontecer.

**Screenshots**
Se aplicável, adicione screenshots.

**Ambiente**
- OS: [ex: Windows 10]
- Python: [ex: 3.9.0]
- Streamlit: [ex: 1.28.0]

**Logs**
Cole os logs de erro aqui.
```

## ✨ Sugerir Funcionalidades

### Template de Feature Request
```markdown
**Funcionalidade**
Descrição clara da funcionalidade desejada.

**Problema que Resolve**
Qual problema esta funcionalidade resolveria?

**Solução Proposta**
Como você imagina que deveria funcionar?

**Alternativas Consideradas**
Outras soluções que você considerou.

**Contexto Adicional**
Qualquer outro contexto sobre a funcionalidade.
```

## 🏷️ Labels

Usamos as seguintes labels:
- `bug` - Algo não está funcionando
- `enhancement` - Nova funcionalidade
- `documentation` - Melhorias na documentação
- `good first issue` - Bom para iniciantes
- `help wanted` - Precisa de ajuda
- `question` - Pergunta ou discussão

## 📞 Comunicação

### Canais
- **Issues**: Para bugs e feature requests
- **Discussions**: Para perguntas e discussões
- **Pull Requests**: Para código

### Código de Conduta
- Seja respeitoso
- Seja construtivo
- Seja paciente
- Ajude outros contribuidores

## 🎯 Áreas que Precisam de Contribuição

### Prioridade Alta
- [ ] Melhorar sistema de autenticação
- [ ] Adicionar mais testes
- [ ] Otimizar performance
- [ ] Melhorar documentação

### Prioridade Média
- [ ] Adicionar novos modelos de ML
- [ ] Melhorar interface mobile
- [ ] Adicionar mais visualizações
- [ ] Internacionalização

### Prioridade Baixa
- [ ] Temas personalizados
- [ ] Plugins adicionais
- [ ] Integração com APIs externas

## 🏆 Reconhecimento

Contribuidores serão reconhecidos:
- No README.md
- Nos releases
- No arquivo CONTRIBUTORS.md

## ❓ Dúvidas?

Se tiver dúvidas sobre como contribuir:
1. Abra uma issue com label `question`
2. Use as discussions do GitHub
3. Entre em contato via email

---

**Obrigado por contribuir para o DIAGVET IA! 🐾**
