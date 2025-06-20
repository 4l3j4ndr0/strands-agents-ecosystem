"""
Configuraciones globales para el ecosistema de agentes Strands.
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env si existe
load_dotenv()

# Configuración de AWS
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_PROFILE = os.getenv("AWS_PROFILE", "default")

# Configuración de modelos
DEFAULT_MODEL = os.getenv("MODEL_ID", "us.anthropic.claude-3-7-sonnet-20250219-v1:0")
MODEL_TEMPERATURE = 0.3

# Configuración de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Configuración de agentes
ENABLE_AGENT_GRAPH = True
ENABLE_STREAMING = True

# Rutas de archivos
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
