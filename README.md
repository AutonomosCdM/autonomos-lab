# HackathonAgents

## Descripción

Sistema de agentes de IA especializados para participación efectiva en hackathones.

## Configuración del Entorno

### Requisitos Previos

- Python 3.10+
- Poetry (gestor de dependencias)

### Instalación

1. Clonar el repositorio
2. Instalar Poetry: `pip install poetry`
3. Instalar dependencias: `poetry install`
4. Activar entorno virtual: `poetry shell`

## Desarrollo

### Estructura del Proyecto

- `/agents/`: Componentes del agente
- `/core/`: Funcionalidades core compartidas
- `/cli/`: Interfaz de línea de comandos
- `/data/`: Recursos y datos necesarios
- `/tests/`: Tests automatizados

### Herramientas de Desarrollo

- Formateo: `poetry run black .`
- Linting: `poetry run flake8`
- Tests: `poetry run pytest`

## Primer Hito

Creación de agente CLI básico con personalidad definida, utilizando LangChain y LlamaIndex.

## Licencia

[Especificar licencia]
