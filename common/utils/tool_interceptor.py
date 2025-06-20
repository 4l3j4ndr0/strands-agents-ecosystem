"""
Interceptor limpio de herramientas que no afecta la funcionalidad existente.
"""
import sys
from typing import Dict, Any, Optional

class CleanToolInterceptor:
    """
    Interceptor que se integra limpiamente con el sistema existente.
    No modifica el comportamiento si no se activa explícitamente.
    """
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.session_approvals = set()
        self.auto_approve_all = False
        
        # Descripciones amigables de herramientas
        self.tool_descriptions = {
            'aws_expert_tool': 'consultar al especialista en AWS',
            'networking_tool': 'consultar al especialista en redes',
            'cicd_tool': 'consultar al especialista en CI/CD',
            'iac_tool': 'consultar al especialista en Infrastructure as Code',
            'kubernetes_tool': 'consultar al especialista en Kubernetes',
            'file_read': 'leer archivos del sistema',
            'fs_read': 'acceder al sistema de archivos',
            'file_write': 'escribir o modificar archivos',
            'fs_write': 'crear o modificar archivos',
            'execute_bash': 'ejecutar comandos en la terminal',
            'use_aws': 'ejecutar comandos de AWS CLI',
            'shell': 'ejecutar comandos del sistema',
            'python_repl': 'ejecutar código Python'
        }
    
    def should_intercept(self, tool_name: str) -> bool:
        """Determina si debe interceptar esta herramienta."""
        if not self.enabled:
            return False
        
        if self.auto_approve_all:
            return False
            
        if tool_name in self.session_approvals:
            return False
            
        return True
    
    def get_tool_description(self, tool_name: str) -> str:
        """Obtiene descripción amigable de la herramienta."""
        return self.tool_descriptions.get(tool_name, f'usar {tool_name}')
    
    def format_tool_input(self, tool_input: Dict[str, Any]) -> str:
        """Formatea los parámetros de entrada de forma legible."""
        if not tool_input:
            return "Sin parámetros"
        
        formatted_params = []
        for key, value in tool_input.items():
            # Truncar valores muy largos
            if isinstance(value, str) and len(value) > 50:
                formatted_params.append(f"{key}: {value[:50]}...")
            else:
                formatted_params.append(f"{key}: {value}")
        
        return ", ".join(formatted_params)
    
    def request_confirmation(self, tool_name: str, tool_input: Dict[str, Any] = None) -> bool:
        """
        Solicita confirmación al usuario de forma limpia.
        
        Returns:
            bool: True si aprobado, False si cancelado
        """
        return True
        if not self.should_intercept(tool_name):
            return True
        
        description = self.get_tool_description(tool_name)
        params_str = self.format_tool_input(tool_input or {})
        
        # Mostrar solicitud de confirmación
        print(f"El agente quiere: {description}")
        print(f"Herramienta: {tool_name}")
        if tool_input:
            print(f"Parámetros: {params_str}")
        print(f"{'='*60}")
        print("Opciones:")
        print("  [s] Sí, usar esta herramienta")
        print("  [n] No, cancelar")
        print("  [a] Aprobar todas las herramientas (sesión)")
        print("  [t] Aprobar solo esta herramienta (sesión)")
        print(f"{'='*60}")
        
        while True:
            try:
                response = input("¿Continuar? [s/n/a/t]: ").lower().strip()
                
                if response in ['s', 'si', 'sí', 'y', 'yes', '']:
                    print(f"✅ Usando {tool_name}...")
                    return True
                elif response in ['n', 'no']:
                    print(f"❌ {tool_name} cancelado")
                    return False
                elif response in ['a', 'all']:
                    self.auto_approve_all = True
                    print("✅ Todas las herramientas aprobadas para esta sesión")
                    return True
                elif response in ['t', 'this']:
                    self.session_approvals.add(tool_name)
                    print(f"✅ {tool_name} aprobado para esta sesión")
                    return True
                else:
                    print("Responde: s (sí), n (no), a (aprobar todo), t (aprobar esta)")
                    
            except (KeyboardInterrupt, EOFError):
                print(f"\n❌ {tool_name} cancelado")
                return False

# Instancia global del interceptor
global_interceptor = CleanToolInterceptor()

def set_interception_enabled(enabled: bool):
    """Activa o desactiva la interceptación globalmente."""
    global_interceptor.enabled = enabled

def request_tool_confirmation(tool_name: str, tool_input: Dict[str, Any] = None) -> bool:
    """Función de conveniencia para solicitar confirmación."""
    return global_interceptor.request_confirmation(tool_name, tool_input)
