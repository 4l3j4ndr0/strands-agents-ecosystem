"""
Agente experto en AWS.
"""
from strands import Agent, tool
from strands_tools import use_aws, shell, python_repl, file_read, file_write
import sys
import os

# Añadir el directorio raíz al path para importar módulos comunes
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.tools.aws_tools import list_aws_resources, analyze_aws_costs
from config.settings import DEFAULT_MODEL
from agents.aws_expert.prompts import AWS_EXPERT_SYSTEM_PROMPT
def custom_callback_handler(**kwargs):
    if "data" in kwargs:
        print(f"MODEL OUTPUT: {kwargs['data']}")
    elif "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
        print(f"\nUSING TOOL: {kwargs['current_tool_use']['name']}")
# Definir el agente experto en AWS
aws_expert_agent = Agent(
    model=DEFAULT_MODEL,
    tools=[
        use_aws, 
        shell, 
        python_repl, 
        file_read,
        file_write
    ],
    system_prompt=AWS_EXPERT_SYSTEM_PROMPT
)

# Función para usar el agente directamente
def query_aws_expert(question: str) -> str:
    """
    Consulta al agente experto en AWS.
    
    Args:
        question (str): Pregunta para el agente
        
    Returns:
        str: Respuesta del agente
    """
    response = aws_expert_agent(question)
    return response.message

if __name__ == "__main__":
    # Código para probar el agente de forma independiente
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("Agente Experto en AWS - Modo de prueba")
    print("Escribe 'salir' para terminar")
    
    while True:
        question = input("\nPregunta: ")
        if question.lower() == "salir":
            break
        
        try:
            response = query_aws_expert(question)
            print("\nRespuesta:")
            print(response)
        except Exception as e:
            print(f"Error: {str(e)}")
