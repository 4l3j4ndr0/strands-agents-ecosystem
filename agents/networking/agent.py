"""
Agente experto en redes de AWS.
"""
from strands import Agent, tool
from strands_tools import use_aws, shell, python_repl
import sys
import os

# Añadir el directorio raíz al path para importar módulos comunes
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import DEFAULT_MODEL
from agents.networking.prompts import NETWORKING_EXPERT_SYSTEM_PROMPT

# Definir el agente experto en redes de AWS
networking_agent = Agent(
    model=DEFAULT_MODEL,
    tools=[
        use_aws, 
        shell, 
        python_repl
    ],
    system_prompt=NETWORKING_EXPERT_SYSTEM_PROMPT
)

# Función para usar el agente directamente
def query_networking_expert(question: str) -> str:
    """
    Consulta al agente experto en redes de AWS.
    
    Args:
        question (str): Pregunta para el agente
        
    Returns:
        str: Respuesta del agente
    """
    response = networking_agent(question)
    return response.message

if __name__ == "__main__":
    # Código para probar el agente de forma independiente
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("Agente Experto en Redes de AWS - Modo de prueba")
    print("Escribe 'salir' para terminar")
    
    while True:
        question = input("\nPregunta: ")
        if question.lower() == "salir":
            break
        
        try:
            response = query_networking_expert(question)
            print("\nRespuesta:")
            print(response)
        except Exception as e:
            print(f"Error: {str(e)}")
