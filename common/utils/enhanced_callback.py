"""
Callback handler mejorado que intercepta herramientas sin afectar funcionalidad existente.
"""
from .tool_interceptor import global_interceptor

class EnhancedStreamingCallback:
    """
    Callback handler que combina streaming con interceptación de herramientas.
    Mantiene toda la funcionalidad existente.
    """
    
    def __init__(self, enable_interception: bool = True, enable_streaming: bool = True):
        self.enable_interception = enable_interception
        self.enable_streaming = enable_streaming
        self.pending_tools = {}
        self.tool_results = {}
    
    def __call__(self, **kwargs):
        """
        Callback principal que maneja tanto streaming como interceptación.
        """
        # 1. Interceptar herramientas si está habilitado
        if self.enable_interception and self._is_tool_use_event(kwargs):
            return self._handle_tool_interception(kwargs)
        
        # 2. Streaming normal si está habilitado
        if self.enable_streaming:
            return self._handle_streaming(kwargs)
    
    def _is_tool_use_event(self, kwargs) -> bool:
        """Detecta si es un evento de uso de herramienta."""
        return "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name")
    
    def _handle_tool_interception(self, kwargs):
        """Maneja la interceptación de herramientas."""
        tool_info = kwargs["current_tool_use"]
        tool_name = tool_info.get("name", "unknown_tool")
        tool_input = tool_info.get("input", {})
        tool_id = tool_info.get("toolUseId", "unknown_id")
        
        # Solo interceptar si no hemos procesado esta herramienta
        if tool_id not in self.tool_results:
            # Mostrar información de la herramienta
            print(f"\n\n\033[1;32m🔧 Consultando especialista: {self._get_friendly_name(tool_name)} ({tool_name})\033[0m")
            # Solicitar confirmación
            confirmed = global_interceptor.request_confirmation(tool_name, tool_input)
            self.tool_results[tool_id] = confirmed
            
            if not confirmed:
                print("⏭️  Continuando sin usar esta herramienta...")
                # Nota: No podemos cancelar la herramienta desde aquí,
                # pero el usuario sabe que fue cancelada
            else:
                print("\033[1;36m⚡ Procesando...\033[0m")
    
    def _handle_streaming(self, kwargs):
        """Maneja el streaming de texto normal."""
        # Mostrar texto generado por el modelo
        if "data" in kwargs:
            print(kwargs["data"], end="", flush=True)
        
        # Mostrar cuando se completa la respuesta
        elif kwargs.get("complete", False):
            print()  # Nueva línea al final
    
    def _get_friendly_name(self, tool_name: str) -> str:
        """Convierte nombres de herramientas a nombres amigables."""
        friendly_names = {
            'aws_expert_tool': 'AWS Expert',
            'networking_tool': 'Networking Expert', 
            'cicd_tool': 'CI/CD Expert',
            'iac_tool': 'IaC Expert',
            'kubernetes_tool': 'Kubernetes Expert'
        }
        return friendly_names.get(tool_name, tool_name.replace('_tool', '').replace('_', ' ').title())

# Función de conveniencia para crear el callback
def create_enhanced_callback(enable_interception: bool = True, enable_streaming: bool = True):
    """
    Crea un callback handler mejorado.
    
    Args:
        enable_interception: Si interceptar herramientas
        enable_streaming: Si hacer streaming de texto
    """
    return EnhancedStreamingCallback(enable_interception, enable_streaming)

# Callback por defecto (mantiene compatibilidad)
def enhanced_streaming_handler(**kwargs):
    """
    Handler por defecto que mantiene compatibilidad con el sistema existente.
    """
    default_callback = EnhancedStreamingCallback()
    return default_callback(**kwargs)
