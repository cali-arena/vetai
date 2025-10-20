# 🚀 Guia de Deploy - DIAGVET IA

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git (para clonagem do repositório)

## 🏠 Deploy Local

### 1. Preparação do Ambiente
```bash
# Clone o repositório
git clone https://github.com/cali-arena/vetai.git
cd vetai/VET

# Crie um ambiente virtual (recomendado)
python -m venv venv

# Ative o ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### 2. Execução
```bash
# Aplicação principal
python -m streamlit run app.py

# Aplicação backup (recomendada para produção)
python -m streamlit run backup.py --server.port 8598

# Com configurações personalizadas
streamlit run backup.py --server.port 8598 --server.address 0.0.0.0
```

## ☁️ Deploy em Produção

### Opção 1: Streamlit Cloud (Recomendado)

1. **Fork o repositório** no GitHub
2. **Acesse** [share.streamlit.io](https://share.streamlit.io)
3. **Conecte** sua conta GitHub
4. **Selecione** o repositório `vetai`
5. **Configure** o arquivo principal como `VET/backup.py`
6. **Deploy** automático

### Opção 2: Heroku

```bash
# Instale o Heroku CLI
# Crie um Procfile
echo "web: streamlit run VET/backup.py --server.port=$PORT --server.address=0.0.0.0" > Procfile

# Crie um runtime.txt
echo "python-3.9.16" > runtime.txt

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### Opção 3: Docker

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY VET/requirements.txt .
RUN pip install -r requirements.txt

COPY VET/ .

EXPOSE 8501

CMD ["streamlit", "run", "backup.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
# Build e execução
docker build -t diagvet-ia .
docker run -p 8501:8501 diagvet-ia
```

### Opção 4: VPS/Servidor

```bash
# No servidor
git clone https://github.com/cali-arena/vetai.git
cd vetai/VET

# Instalar dependências
pip install -r requirements.txt

# Executar com nohup (background)
nohup streamlit run backup.py --server.port 8501 --server.address 0.0.0.0 &

# Ou usar systemd service
sudo systemctl start diagvet-ia
```

## 🔧 Configurações de Produção

### Streamlit Config
Crie um arquivo `.streamlit/config.toml`:

```toml
[server]
port = 8501
address = "0.0.0.0"
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

### Variáveis de Ambiente
```bash
# .env
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
```

## 📊 Monitoramento

### Logs
```bash
# Ver logs em tempo real
tail -f ~/.streamlit/logs/streamlit.log

# Logs do sistema
journalctl -u diagvet-ia -f
```

### Métricas
- **CPU Usage**: Monitorar uso de CPU
- **Memory**: Verificar uso de RAM
- **Disk Space**: Espaço em disco
- **Network**: Tráfego de rede

## 🔒 Segurança

### HTTPS
```bash
# Com certificado SSL
streamlit run backup.py --server.sslCertFile=cert.pem --server.sslKeyFile=key.pem
```

### Firewall
```bash
# Abrir apenas porta necessária
sudo ufw allow 8501
sudo ufw enable
```

### Autenticação
Para adicionar autenticação, use:
```python
# No início do app
import streamlit_authenticator as stauth

# Configurar autenticação
authenticator = stauth.Authenticate(
    credentials,
    'cookie_name',
    'cookie_key',
    30
)
```

## 🚨 Troubleshooting

### Problemas Comuns

1. **Porta ocupada**
   ```bash
   # Encontrar processo usando a porta
   lsof -i :8501
   # Matar processo
   kill -9 PID
   ```

2. **Dependências faltando**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

3. **Permissões**
   ```bash
   chmod +x backup.py
   ```

4. **Memória insuficiente**
   ```bash
   # Aumentar swap
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

## 📈 Performance

### Otimizações
- Use `@st.cache_data` para cache de dados
- Implemente lazy loading
- Otimize queries de banco de dados
- Use CDN para assets estáticos

### Escalabilidade
- Load balancer para múltiplas instâncias
- Redis para cache compartilhado
- Database clustering
- Microserviços

## 📞 Suporte

Para problemas de deploy:
1. Verifique os logs
2. Confirme configurações
3. Teste localmente primeiro
4. Abra issue no GitHub

---

**🎉 Deploy realizado com sucesso!**