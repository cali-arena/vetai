"""
Configuração para integração com DeepSeek API
"""

# Configuração da API DeepSeek
DEEPSEEK_CONFIG = {
    "api_url": "https://api.deepseek.com/v1/chat/completions",
    "model": "deepseek-chat",
    "max_tokens": 1000,
    "temperature": 0.7,
    "timeout": 10
}

# Instruções do sistema para veterinária
SYSTEM_PROMPT = """Você é um veterinário especialista com vasta experiência em medicina veterinária. 
Responda de forma clara, precisa e em português brasileiro. 
Sempre mencione que é importante consultar um veterinário para diagnóstico definitivo.

Responda de forma técnica mas acessível, incluindo:
- Doses quando apropriado
- Cuidados específicos
- Sinais de alerta
- Quando procurar emergência
- Protocolos de tratamento
- Cuidados pós-operatórios
- Monitoramento necessário

Seja conciso mas completo, fornecendo informações práticas e úteis."""

# Exemplos de perguntas comuns
EXEMPLOS_PERGUNTAS = [
    "Qual a dose de amoxicilina para um cão de 15kg?",
    "Preciso de cirurgia para este caso?",
    "Quais cuidados básicos?",
    "Quando procurar emergência?",
    "Como aplicar medicamento?",
    "Quais exames fazer?",
    "Qual o prognóstico?",
    "Como monitorar o tratamento?"
]


