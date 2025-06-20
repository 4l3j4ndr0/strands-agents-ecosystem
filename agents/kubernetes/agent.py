"""
Agente experto en Kubernetes/EKS.
"""
from strands import Agent, tool
from strands_tools import file_read, file_write, shell, use_aws
import sys
import os


# Añadir el directorio raíz al path para importar módulos comunes
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import DEFAULT_MODEL
from agents.kubernetes.prompts import KUBERNETES_EXPERT_SYSTEM_PROMPT

# Definir el agente experto en Kubernetes/EKS
kubernetes_agent = Agent(
    model=DEFAULT_MODEL,
    tools=[
        file_read, 
        file_write, 
        shell, 
        use_aws
    ],
    system_prompt=KUBERNETES_EXPERT_SYSTEM_PROMPT
)

# Función para usar el agente directamente
def query_kubernetes_expert(question: str) -> str:
    """
    Consulta al agente experto en Kubernetes/EKS.
    
    Args:
        question (str): Pregunta para el agente
        
    Returns:
        str: Respuesta del agente
    """
    response = kubernetes_agent(question)
    return response.message

if __name__ == "__main__":
    # Código para probar el agente de forma independiente
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("Agente Experto en Kubernetes/EKS - Modo de prueba")
    print("Escribe 'salir' para terminar")
    
    while True:
        question = input("\nPregunta: ")
        if question.lower() == "salir":
            break
        
        try:
            response = query_kubernetes_expert(question)
            print("\nRespuesta:")
            print(response)
        except Exception as e:
            print(f"Error: {str(e)}")
