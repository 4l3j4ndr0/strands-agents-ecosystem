"""
Agente experto en CI/CD (GitHub Actions).
"""
from strands import Agent, tool
from strands_tools import file_read, file_write, shell
import sys
import os

# Añadir el directorio raíz al path para importar módulos comunes
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import DEFAULT_MODEL
from agents.cicd.prompts import CICD_EXPERT_SYSTEM_PROMPT

# Definir el agente experto en CI/CD
cicd_agent = Agent(
    model=DEFAULT_MODEL,
    tools=[
        file_read, 
        file_write, 
        shell
    ],
    system_prompt=CICD_EXPERT_SYSTEM_PROMPT
)

# Función para usar el agente directamente
def query_cicd_expert(question: str) -> str:
    """
    Consulta al agente experto en CI/CD.
    
    Args:
        question (str): Pregunta para el agente
        
    Returns:
        str: Respuesta del agente
    """
    response = cicd_agent(question)
    return response.message

if __name__ == "__main__":
    # Código para probar el agente de forma independiente
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("Agente Experto en CI/CD - Modo de prueba")
    print("Escribe 'salir' para terminar")
    
    while True:
        question = input("\nPregunta: ")
        if question.lower() == "salir":
            break
        
        try:
            response = query_cicd_expert(question)
            print("\nRespuesta:")
            print(response)
        except Exception as e:
            print(f"Error: {str(e)}")
