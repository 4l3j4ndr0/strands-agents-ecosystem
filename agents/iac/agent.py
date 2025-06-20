"""
Agente experto en IaC (Terraform, CloudFormation).
"""
from strands import Agent, tool
from strands_tools import file_read, file_write, shell, python_repl
import sys
import os

# Añadir el directorio raíz al path para importar módulos comunes
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import DEFAULT_MODEL
from agents.iac.prompts import IAC_EXPERT_SYSTEM_PROMPT
# Definir el agente experto en IaC
iac_agent = Agent(
    model=DEFAULT_MODEL,
    tools=[
        file_read, 
        file_write, 
        shell, 
        python_repl
    ],
    system_prompt=IAC_EXPERT_SYSTEM_PROMPT
)

# Función para usar el agente directamente
def query_iac_expert(question: str) -> str:
    """
    Consulta al agente experto en IaC.
    
    Args:
        question (str): Pregunta para el agente
        
    Returns:
        str: Respuesta del agente
    """
    response = iac_agent(question)
    return response.message

if __name__ == "__main__":
    # Código para probar el agente de forma independiente
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("Agente Experto en IaC - Modo de prueba")
    print("Escribe 'salir' para terminar")
    
    while True:
        question = input("\nPregunta: ")
        if question.lower() == "salir":
            break
        
        try:
            response = query_iac_expert(question)
            print("\nRespuesta:")
            print(response)
        except Exception as e:
            print(f"Error: {str(e)}")
