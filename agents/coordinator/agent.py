"""
Agente coordinador para orquestar los agentes especializados.
"""
from strands import Agent
import sys
import os
import logging

# Configurar logger
logger = logging.getLogger(__name__)

# Añadir el directorio raíz al path para importar módulos comunes
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import DEFAULT_MODEL
from agents.coordinator.prompts import COORDINATOR_SYSTEM_PROMPT

# Importar los agentes especializados
from agents.aws_expert.agent import aws_expert_agent, query_aws_expert
from agents.networking.agent import networking_agent, query_networking_expert
from agents.cicd.agent import cicd_agent, query_cicd_expert
from agents.iac.agent import iac_agent, query_iac_expert
from agents.kubernetes.agent import kubernetes_agent, query_kubernetes_expert

# Definir el agente coordinador
coordinator_agent = Agent(
    model=DEFAULT_MODEL,
    system_prompt=COORDINATOR_SYSTEM_PROMPT
)

# Función para manejar solicitudes
def handle_request(user_query: str) -> str:
    """
    Maneja una solicitud del usuario y la dirige al agente especializado adecuado.
    
    Args:
        user_query (str): Consulta del usuario
        
    Returns:
        str: Respuesta al usuario
    """
    # Usar el agente coordinador para determinar qué agentes especializados utilizar
    planning_response = coordinator_agent(user_query)
    
    # Asegurarse de que planning_result sea una cadena de texto
    if hasattr(planning_response, 'message'):
        planning_result = planning_response.message
    else:
        planning_result = str(planning_response)
    
    # Analizar el resultado para determinar qué agente usar
    agent_mapping = {
        "aws expert": query_aws_expert,
        "networking expert": query_networking_expert,
        "ci/cd expert": query_cicd_expert,
        "iac expert": query_iac_expert,
        "kubernetes expert": query_kubernetes_expert
    }
    
    # Determinar el agente principal a usar
    selected_agent = None
    
    # Asegurarse de que planning_result sea una cadena de texto
    if not isinstance(planning_result, str):
        planning_result = str(planning_result)
    
    for agent_name, agent_func in agent_mapping.items():
        if agent_name.lower() in planning_result.lower():
            selected_agent = agent_func
            break
    
    # Si no se identificó ningún agente específico, usar el coordinador
    if selected_agent is None:
        response = coordinator_agent(f"""
        No pude determinar un agente especializado para tu consulta. 
        Por favor, intenta ser más específico o reformula tu pregunta.
        
        Tu consulta original fue:
        {user_query}
        """)
        return response.message
    
    # Usar el agente seleccionado para responder
    try:
        result = selected_agent(f"""
        {user_query}
        
        Contexto adicional del coordinador:
        {planning_result}
        """)
        
        # Asegurarse de que el resultado sea una cadena de texto
        if not isinstance(result, str):
            if hasattr(result, 'message'):
                result = result.message
            else:
                result = str(result)
        
        return result
    except Exception as e:
        # En caso de error, usar el coordinador como fallback
        logger.error(f"Error al usar el agente especializado: {str(e)}")
        response = coordinator_agent(f"""
        Hubo un problema al procesar tu consulta con el agente especializado.
        Por favor, reformula tu pregunta o proporciona más detalles.
        
        Tu consulta original fue:
        {user_query}
        """)
        return response.message

# Función para usar el agente directamente
def query_coordinator(question: str) -> str:
    """
    Consulta al agente coordinador.
    
    Args:
        question (str): Pregunta para el agente
        
    Returns:
        str: Respuesta del agente
    """
    response = handle_request(question)
    return response

if __name__ == "__main__":
    # Código para probar el agente de forma independiente
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("Agente Coordinador - Modo de prueba")
    print("Escribe 'salir' para terminar")
    
    while True:
        question = input("\nPregunta: ")
        if question.lower() == "salir":
            break
        
        try:
            response = query_coordinator(question)
            print("\nRespuesta:")
            print(response)
        except Exception as e:
            print(f"Error: {str(e)}")
