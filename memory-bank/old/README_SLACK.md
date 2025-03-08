# Integración de Agentes con Slack

Este módulo proporciona la infraestructura necesaria para conectar los agentes de Autonomos Lab con Slack, permitiendo interacciones en tiempo real a través de la plataforma de mensajería.

## Características

- Conexión a Slack mediante Socket Mode
- Soporte para múltiples agentes
- Manejo de conversaciones con contexto
- Registro de interacciones
- Configuración flexible

## Requisitos

- Python 3.9+
- slack-bolt
- dotenv
- Tokens de Slack (Bot Token y App Token)

## Configuración

1. Crea una aplicación en [api.slack.com](https://api.slack.com/apps)
2. Configura los siguientes permisos de bot:
   - `chat:write`
   - `im:history`
   - `channels:history`
   - `app_mentions:read`
3. Habilita Socket Mode y obtén un App Token
4. Instala la app en tu workspace y obtén el Bot Token
5. Añade los tokens al archivo `.env`:

```
SLACK_BOT_TOKEN=xoxb-tu-bot-token
SLACK_APP_TOKEN=xapp-tu-app-token
```

## Uso Básico

Para ejecutar un solo agente (Lucius Fox):

```bash
python slack_main.py
```

Para ejecutar múltiples agentes:

```bash
python slack/multi_agent_main.py
```

## Estructura

- `slack/base_adapter.py`: Adaptador base para conectar agentes a Slack
- `slack/agent_registry.py`: Registro para gestionar múltiples agentes
- `slack_main.py`: Punto de entrada para ejecutar Lucius Fox en Slack
- `slack/multi_agent_main.py`: Punto de entrada para ejecutar múltiples agentes

## Personalización

### Añadir un Nuevo Agente

1. Crea una instancia de tu agente basado en `BaseAgent`
2. Registra el agente con el `AgentRegistry`

```python
from agents.base_agent import BaseAgent
from slack.agent_registry import AgentRegistry

# Crear agente
my_agent = BaseAgent(
    name="MiAgente",
    personality="características de personalidad",
    primary_objective="objetivo principal",
    llm_model="llama-3.3-70b-versatile",
    temperature=0.7
)

# Registrar con el registro
registry = AgentRegistry()
registry.register_agent(my_agent, mention_only=True)

# Iniciar todos los agentes
registry.start_all()
```

### Configuración Avanzada

Para configuraciones más avanzadas, puedes modificar directamente el adaptador de Slack:

```python
from slack.base_adapter import SlackAdapter

adapter = SlackAdapter(
    agent=my_agent,
    mention_only=True,  # Solo responder a menciones
    bot_token="token-personalizado",  # Usar token específico
    app_token="token-personalizado"   # Usar token específico
)

adapter.start()
```

## Solución de Problemas

### Errores Comunes

- **Error de Autenticación**: Verifica que los tokens en `.env` sean correctos y tengan los permisos adecuados.
- **Error de Conexión**: Asegúrate de que Socket Mode esté habilitado en la configuración de la app de Slack.
- **Respuestas Duplicadas**: Verifica que no haya múltiples instancias del bot ejecutándose.

### Logs

Los logs se guardan en:
- `slack_bot.log` para el bot simple
- `slack_multi_agent.log` para múltiples agentes

Revisa estos archivos para obtener información detallada sobre errores o problemas.
