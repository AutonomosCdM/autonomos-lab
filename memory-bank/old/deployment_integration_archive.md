# Archived Deployment and Integration Preparation

# Deployment Preparation for HackathonAgents

## Deployment Checklist

### 1. Environment Configuration ✅
- [x] Slack Bot Token configured
- [x] Slack App Token configured
- [x] Groq API Keys set up for different agents
- [ ] Rotate sensitive tokens before production deployment

### 2. Infrastructure Readiness
- [x] Dockerfile configured
- [x] Poetry dependency management in place
- [x] Persistent storage directories created
- [x] Logging configuration established

### 3. Deployment Platforms
- [ ] Railway deployment configuration verified
- [ ] GitHub Actions workflow for CI/CD checked
- [ ] Health check endpoint implemented

### 4. Security Considerations
- [ ] Remove hardcoded tokens from .env file
- [ ] Implement secure token rotation mechanism
- [ ] Verify no sensitive data is exposed in logs

### 5. Performance Optimization
- [ ] Review Poetry dependency installation
- [ ] Check vector index and embedding storage
- [ ] Validate agent communication efficiency

### 6. Monitoring and Logging
- [x] Logging level set to INFO
- [x] JSON log format configured
- [ ] Set up centralized log monitoring
- [ ] Create log rotation strategy

### 7. Deployment Workflow
1. Verify all environment variables
2. Run local tests
3. Push to main branch
4. Trigger Railway deployment
5. Verify health check endpoint
6. Monitor initial deployment logs

### Recommended Next Steps
- Implement comprehensive secret management
- Set up automated token rotation
- Create detailed deployment runbook
- Establish monitoring and alerting

### Potential Risks
- Slack token exposure
- API key management
- Persistent storage reliability
- Agent communication failures

## Deployment Notes
Project: HackathonAgents
Version: 0.1.0
Deployment Strategy: Continuous Integration via Railway
Primary Communication: Slack Integration
# Archived Deployment and Integration Preparation

# Integración Avanzada de Agentes IA con Google Workspace

## Información del Proyecto

### Detalles Generales
- **Nombre**: AgentesIA Workspace
- **Objetivo**: Integración inteligente y segura con servicios Google
- **Versión**: 0.2.0
- **Estado**: Implementación inicial completada

## Herramientas y Tecnologías

### Procesamiento Principal
- **Frameworks**:
  - LangChain
  - LlamaIndex
  - Google API Client Python

### Paquetes Especializados
- `langchain-google-*`
- `llama-index-readers-google`
- `google-api-python-client`
- `google-auth-oauthlib`

## Estrategia de Autenticación

### Método de Autenticación
- **Protocolo**: OAuth 2.0
- **Flujo**: Autorización con servidor local
- **Almacenamiento de Token**: Archivo pickle encriptado

### Alcance de Permisos
- `gmail.readonly`
- `docs.readonly`
- `spreadsheets.readonly`

### Estrategias de Seguridad
- Rotación de tokens
- Almacenamiento seguro de credenciales
- Registro de accesos
- Principio de mínimo privilegio
- Validación de credenciales en tiempo de ejecución

## Capacidades por Servicio

### Gmail
#### Funcionalidades Implementadas
- Lectura de correos electrónicos
- Clasificación de prioridad basada en análisis de asunto
- Extracción de metadatos
- Filtrado inteligente de mensajes

#### Restricciones
- Solo lectura
- No modificación de correos
- Máximo 10 correos por consulta

#### Algoritmo de Clasificación de Prioridad
- Palabras clave de alta prioridad
- Palabras clave de prioridad media
- Clasificación por defecto: Baja prioridad

### Google Docs (Pendiente)
#### Procesamiento Planificado
- Extracción de texto
- Indexación semántica
- Generación de resúmenes ejecutivos
- Identificación de estructuras documentales

### Google Sheets (Pendiente)
#### Análisis Planificado
- Lectura de datos tabulares
- Generación de insights
- Cálculos estadísticos básicos
- Visualización de tendencias

## Modelo de IA

### Procesamiento Principal
- **Modelo**: Claude Sonnet
- **Rol**: Análisis profundo y generación

### Tareas Auxiliares
- **Modelo**: Claude Haiku
- **Rol**: Procesamiento rápido y filtrado inicial

## Fases de Implementación

### 1. Preparación (Completada)
- [x] Configuración de proyecto en Google Cloud
- [x] Generación de credenciales OAuth
- [x] Pruebas de autorización
- [x] Implementación de flujo OAuth

### 2. Integración Gmail (En Progreso)
- [x] Implementar Gmail loader
- [x] Desarrollar sistema de filtrado inteligente
- [ ] Crear módulo de resumen de conversaciones
- [ ] Implementar análisis de patrones de comunicación

### 3. Procesamiento de Documentos (Pendiente)
- [ ] Integrar Google Drive document loader
- [ ] Implementar indexación con LlamaIndex
- [ ] Generar pipeline de análisis de documentos

### 4. Análisis de Sheets (Pendiente)
- [ ] Utilizar Google Sheets loader
- [ ] Desarrollar transformaciones de datos
- [ ] Crear sistema de generación de insights

## Consideraciones Técnicas

### Rendimiento
- Tiempo máximo de respuesta: 2 segundos
- Precisión de procesamiento: >85%
- Número máximo de correos por consulta: 10

### Seguridad
- Principio de mínimo privilegio
- Cifrado de credenciales
- Registro de auditoría de accesos
- Validación de permisos en tiempo de ejecución

## Métricas de Éxito

### Funcionalidad
- Cobertura de formatos de documentos
- Precisión de análisis
- Relevancia de insights generados
- Porcentaje de correos clasificados correctamente

### Experiencia de Usuario
- Facilidad de configuración
- Experiencia de uso intuitiva
- Tiempo de configuración inicial
- Claridad de los mensajes de error

## Modelo de Licenciamiento

### Estructura
- **Modelo**: Freemium

### Restricciones
- Límite de documentos procesados
- Acceso básico gratuito
- Planes premium para uso extensivo

## Próximos Pasos
- Completar integración de Google Docs
- Desarrollar módulo de análisis de Google Sheets
- Mejorar algoritmo de clasificación de prioridad
- Implementar registro de auditoría detallado
- Añadir soporte para más idiomas
# Archived Deployment and Integration Preparation

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
