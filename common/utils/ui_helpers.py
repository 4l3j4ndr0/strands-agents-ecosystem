"""
Callback handler simple para streaming de respuestas.
"""

def streaming_handler(**kwargs):
    """
    Callback handler simple que muestra el streaming de texto.
    """
    # Mostrar texto generado por el modelo
    if "data" in kwargs:
        print(kwargs["data"], end="", flush=True)
    
    # Mostrar cuando se usa una herramienta
    elif "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
        tool_name = kwargs["current_tool_use"]["name"]
        print(f"\n\n🔧 Consultando especialista: {tool_name.replace('_tool', '').replace('_', ' ').title()}")
        print("-" * 40)
    
    # Mostrar cuando se completa la respuesta
    elif kwargs.get("complete", False):
        print()  # Nueva línea al final
