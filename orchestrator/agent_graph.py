"""
Orquestación de agentes usando el patrón "Agents as Tools".
Implementa topologías de grafo de agentes con comunicación estructurada.
"""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import uuid
from strands import Agent, tool
from strands_tools import use_aws, shell, file_read, file_write

# Configurar logger
logger = logging.getLogger(__name__)


@dataclass
class AgentNode:
    """Representa un nodo (agente) en el grafo de agentes."""
    id: str
    role: str
    agent: Agent
    tools: List[Any] = None
    message_queue: List[Dict] = None
    
    def __post_init__(self):
        if self.tools is None:
            self.tools = []
        if self.message_queue is None:
            self.message_queue = []


@dataclass
class AgentEdge:
    """Representa una conexión entre agentes."""
    from_agent: str
    to_agent: str
    relationship: str = "peer"
    bidirectional: bool = False


class AgentGraph:
    """
    Grafo de agentes implementando el patrón "Agents as Tools".
    
    Soporta múltiples topologías:
    - Star: Coordinador central con especialistas
    - Hierarchical: Estructura de árbol con niveles
    - Mesh: Red completamente conectada
    """
    
    def __init__(self, graph_id: str):
        self.graph_id = graph_id
        self.nodes: Dict[str, AgentNode] = {}
        self.edges: List[AgentEdge] = []
        self.topology_type: Optional[str] = None
        self.active = False
    
    def add_existing_agent(self, agent_id: str, role: str, agent: Agent) -> AgentNode:
        """Añade un agente existente al grafo."""
        node = AgentNode(
            id=agent_id,
            role=role,
            agent=agent
        )
        
        self.nodes[agent_id] = node
        return node
    
    def add_edge(self, from_agent: str, to_agent: str, relationship: str = "peer", bidirectional: bool = False):
        """Añade una conexión entre dos agentes."""
        if from_agent not in self.nodes or to_agent not in self.nodes:
            raise ValueError(f"Ambos agentes deben existir en el grafo antes de crear la conexión")
        
        edge = AgentEdge(from_agent, to_agent, relationship, bidirectional)
        self.edges.append(edge)
        
        if bidirectional:
            reverse_edge = AgentEdge(to_agent, from_agent, relationship, False)
            self.edges.append(reverse_edge)
    
    def create_star_topology_from_existing(self, coordinator_id: str, specialist_ids: List[str]):
        """Crea una topología estrella usando agentes existentes."""
        self.topology_type = "star"
        
        if coordinator_id not in self.nodes:
            raise ValueError(f"Coordinador '{coordinator_id}' no encontrado en el grafo")
        
        coordinator_node = self.nodes[coordinator_id]
        
        # Crear herramientas para cada especialista
        specialist_tools = []
        for spec_id in specialist_ids:
            if spec_id not in self.nodes:
                logger.warning(f"Especialista '{spec_id}' no encontrado, omitiendo...")
                continue
                
            specialist_node = self.nodes[spec_id]
            specialist_tool = self._create_agent_tool(specialist_node)
            specialist_tools.append(specialist_tool)
            
            # Añadir conexiones bidireccionales
            self.add_edge(coordinator_id, spec_id, "supervisor", True)
        
        # Actualizar el coordinador con las herramientas de especialistas
        coordinator_node.tools = specialist_tools
        coordinator_node.tools.append(use_aws)
        coordinator_node.tools.append(shell)
        coordinator_node.tools.append(file_read)
        coordinator_node.tools.append(file_write)
        
        # Recrear el agente coordinador con las nuevas herramientas
        original_prompt = self._extract_system_prompt(coordinator_node.agent)
        enhanced_prompt = self._enhance_coordinator_prompt(original_prompt, specialist_ids)
        
        # Preservar el callback handler original
        original_callback = coordinator_node.agent.callback_handler
        
        coordinator_node.agent = Agent(
            system_prompt=enhanced_prompt,
            tools=specialist_tools,
            callback_handler=original_callback
        )
        
        logger.info(f"Topología estrella creada con coordinador '{coordinator_id}' y {len(specialist_tools)} especialistas")
    
    def create_hierarchical_topology_from_existing(self, hierarchy_config: Dict):
        """Crea una topología jerárquica usando agentes existentes."""
        self.topology_type = "hierarchical"
        
        # Procesar niveles de abajo hacia arriba para asegurar que las herramientas estén disponibles
        levels = sorted(hierarchy_config["levels"], key=lambda x: x["level"], reverse=True)
        
        for level_config in levels:
            for node_config in level_config["nodes"]:
                node_id = node_config["id"]
                
                if node_id not in self.nodes:
                    logger.warning(f"Agente '{node_id}' no encontrado en el nivel {level_config['level']}, omitiendo...")
                    continue
                
                node = self.nodes[node_id]
                
                # Recopilar herramientas de subordinados
                subordinate_tools = []
                if "subordinates" in node_config:
                    for sub_id in node_config["subordinates"]:
                        if sub_id in self.nodes:
                            sub_tool = self._create_agent_tool(self.nodes[sub_id])
                            subordinate_tools.append(sub_tool)
                            
                            # Añadir conexión jerárquica
                            self.add_edge(node_id, sub_id, "supervisor")
                
                # Actualizar el agente con herramientas de subordinados
                if subordinate_tools:
                    node.tools = subordinate_tools
                    
                    # Recrear el agente con las nuevas herramientas
                    original_prompt = self._extract_system_prompt(node.agent)
                    enhanced_prompt = self._enhance_manager_prompt(
                        original_prompt, 
                        node_config.get("subordinates", [])
                    )
                    
                    # Preservar el callback handler original
                    original_callback = node.agent.callback_handler
                    
                    node.agent = Agent(
                        system_prompt=enhanced_prompt,
                        tools=subordinate_tools,
                        callback_handler=original_callback
                    )
        
        logger.info(f"Topología jerárquica creada con {len(self.nodes)} agentes")
    
    def _create_agent_tool(self, agent_node: AgentNode):
        """Crea una función herramienta para un nodo de agente."""
        def agent_tool_func(query: str) -> str:
            """Herramienta creada dinámicamente para comunicación entre agentes."""
            logger.info(f"🤖 {agent_node.role} ({agent_node.id}) procesando consulta...")
            
            # Validar que la consulta no esté vacía
            if not query or not query.strip():
                logger.warning(f"Consulta vacía recibida por {agent_node.role}")
                return f"No se recibió consulta válida para {agent_node.role}"
            
            # Añadir mensaje a la cola
            message = {
                "content": query,
                "timestamp": str(uuid.uuid4()),
                "processed": False
            }
            agent_node.message_queue.append(message)
            
            # Procesar con el agente
            try:
                response = agent_node.agent(query)
                
                # Extraer el resultado de manera más robusta
                if hasattr(response, 'message'):
                    result = response.message
                elif hasattr(response, 'content'):
                    result = response.content
                else:
                    result = str(response)
                
                # Asegurar que result sea una cadena de texto
                if not isinstance(result, str):
                    result = str(result)
                
                # Validar que el resultado no esté vacío
                if not result or not result.strip():
                    result = f"El {agent_node.role} procesó la consulta pero no generó respuesta visible."
                
                message["processed"] = True
                logger.info(f"✅ {agent_node.role} completó el procesamiento")
                return result.strip()
                
            except Exception as e:
                logger.error(f"❌ Error en {agent_node.role}: {str(e)}")
                message["error"] = str(e)
                return f"Error al procesar con {agent_node.role}: {str(e)}"
        
        # Configurar metadatos de la función
        agent_tool_func.__name__ = f"{agent_node.id}_tool"
        agent_tool_func.__doc__ = f"Consultar al {agent_node.role} para tareas relacionadas con {agent_node.id}."
        
        # Convertir a herramienta de Strands
        return tool(agent_tool_func)
    
    def _extract_system_prompt(self, agent: Agent) -> str:
        """Extrae el system prompt de un agente existente."""
        # Intentar acceder al system prompt del agente
        if hasattr(agent, 'system_prompt'):
            return agent.system_prompt
        elif hasattr(agent, '_system_prompt'):
            return agent._system_prompt
        else:
            # Prompt por defecto si no se puede extraer
            return "Eres un agente especializado. Ayuda con las consultas de tu dominio de expertise."
    
    def _enhance_coordinator_prompt(self, original_prompt: str, specialist_ids: List[str]) -> str:
        """Mejora el prompt del coordinador con información sobre especialistas disponibles."""
        specialist_info = []
        for spec_id in specialist_ids:
            if spec_id in self.nodes:
                node = self.nodes[spec_id]
                specialist_info.append(f"- {node.role} ({spec_id}): Usa la herramienta {spec_id}_tool")
        
        # Solo añadir información de especialistas si hay alguno disponible
        if not specialist_info:
            return original_prompt
        
        enhanced_prompt = f"""{original_prompt}

HERRAMIENTAS DE ESPECIALISTAS DISPONIBLES:
{chr(10).join(specialist_info)}

INSTRUCCIONES DE USO DE HERRAMIENTAS:
1. Analiza la consulta para determinar qué especialistas necesitas
2. Usa las herramientas apropiadas con consultas claras y específicas
3. Proporciona contexto suficiente en cada consulta a los especialistas
4. Sintetiza las respuestas en una respuesta coherente y completa
5. Si una herramienta no responde adecuadamente, proporciona una respuesta basada en tu conocimiento

IMPORTANTE: Siempre proporciona una respuesta útil, incluso si las herramientas no funcionan como se espera."""
        
        return enhanced_prompt
    
    def _enhance_manager_prompt(self, original_prompt: str, subordinate_ids: List[str]) -> str:
        """Mejora el prompt de un manager con información sobre subordinados."""
        subordinate_info = []
        for sub_id in subordinate_ids:
            if sub_id in self.nodes:
                node = self.nodes[sub_id]
                subordinate_info.append(f"- {node.role} ({sub_id}): Usa la herramienta {sub_id}_tool")
        
        enhanced_prompt = f"""{original_prompt}

EQUIPO DISPONIBLE:
{chr(10).join(subordinate_info)}

INSTRUCCIONES DE GESTIÓN:
1. Delega tareas específicas a los miembros apropiados de tu equipo
2. Coordina el trabajo entre diferentes especialistas cuando sea necesario
3. Sintetiza los resultados de tu equipo en respuestas coherentes
4. Asegúrate de que todas las perspectivas relevantes sean consideradas"""
        
        return enhanced_prompt
    
    def send_message(self, target_agent_id: str, message: str) -> str:
        """Envía un mensaje a un agente específico en el grafo."""
        if target_agent_id not in self.nodes:
            raise ValueError(f"Agente {target_agent_id} no encontrado en el grafo")
        
        # Validar que el mensaje no esté vacío
        if not message or not message.strip():
            logger.warning(f"Mensaje vacío enviado a {target_agent_id}")
            return "No se puede procesar un mensaje vacío"
        
        target_node = self.nodes[target_agent_id]
        logger.info(f"📨 Enviando mensaje a {target_node.role} ({target_agent_id})")
        
        # Añadir a la cola de mensajes
        msg_obj = {
            "content": message,
            "timestamp": str(uuid.uuid4()),
            "processed": False
        }
        target_node.message_queue.append(msg_obj)
        
        # Procesar mensaje
        try:
            response = target_node.agent(message)
            
            # Extraer el resultado de manera más robusta
            if hasattr(response, 'message'):
                result = response.message
            elif hasattr(response, 'content'):
                result = response.content
            else:
                result = str(response)
            
            # Asegurar que result sea una cadena de texto
            if not isinstance(result, str):
                result = str(result)
            
            # Validar que el resultado no esté vacío
            if not result or not result.strip():
                result = f"El agente {target_agent_id} procesó el mensaje pero no generó respuesta visible."
            
            msg_obj["processed"] = True
            return result.strip()
            
        except Exception as e:
            logger.error(f"Error al procesar mensaje en {target_agent_id}: {str(e)}")
            msg_obj["error"] = str(e)
            raise
    
    def get_status(self) -> Dict:
        """Obtiene el estado actual del grafo de agentes."""
        return {
            "graph_id": self.graph_id,
            "topology_type": self.topology_type,
            "active": self.active,
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "nodes": {
                node_id: {
                    "role": node.role,
                    "message_queue_size": len(node.message_queue),
                    "tools_count": len(node.tools)
                }
                for node_id, node in self.nodes.items()
            }
        }
    
    def activate(self):
        """Activa el grafo de agentes."""
        self.active = True
        logger.info(f"Grafo de agentes '{self.graph_id}' activado")
    
    def deactivate(self):
        """Desactiva el grafo de agentes."""
        self.active = False
        logger.info(f"Grafo de agentes '{self.graph_id}' desactivado")


def create_agent_graph(agents_dict):
    """
    Crea un grafo de agentes usando el patrón "Agents as Tools".
    
    Args:
        agents_dict (dict): Diccionario de agentes disponibles
        
    Returns:
        AgentGraph: Grafo de agentes configurado
    """
    logger.info("Creando grafo de agentes con patrón 'Agents as Tools'")
    
    # Crear el grafo
    graph = AgentGraph("main_ecosystem")
    
    # Mapeo de roles para los agentes
    agent_roles = {
        "coordinator": "Coordinador Principal",
        "aws_expert": "Experto en AWS",
        "networking": "Experto en Networking",
        "cicd": "Experto en CI/CD",
        "iac": "Experto en Infrastructure as Code",
        "kubernetes": "Experto en Kubernetes"
    }
    
    # Añadir todos los agentes existentes al grafo
    for agent_id, agent in agents_dict.items():
        role = agent_roles.get(agent_id, f"Agente {agent_id.title()}")
        graph.add_existing_agent(agent_id, role, agent)
        logger.info(f"Añadido agente: {role} ({agent_id})")
    
    # Crear topología estrella con el coordinador como centro
    specialist_ids = [aid for aid in agents_dict.keys() if aid != "coordinator"]
    
    if "coordinator" in agents_dict:
        graph.create_star_topology_from_existing("coordinator", specialist_ids)
    else:
        logger.warning("No se encontró coordinador, creando topología mesh")
        # Si no hay coordinador, crear topología mesh
        graph.topology_type = "mesh"
        # Implementar lógica mesh si es necesario
    
    graph.activate()
    logger.info(f"Grafo de agentes creado exitosamente con topología {graph.topology_type}")
    
    return graph


def execute_workflow(graph, query, start_node="coordinator"):
    """
    Ejecuta un flujo de trabajo a través del grafo de agentes.
    
    Args:
        graph (AgentGraph): Grafo de agentes
        query (str): Consulta del usuario
        start_node (str): Nodo inicial para la ejecución
        
    Returns:
        str: Resultado de la ejecución
    """
    try:
        logger.info(f"Ejecutando consulta a través del grafo de agentes, comenzando por '{start_node}'")
        
        # Verificar que el grafo esté activo
        if not graph.active:
            raise ValueError("El grafo de agentes no está activo")
        
        # Enviar mensaje al nodo inicial
        result = graph.send_message(start_node, query)
        
        logger.info("Ejecución completada con éxito")
        return result
        
    except Exception as e:
        logger.error(f"Error al ejecutar el flujo de trabajo: {str(e)}")
        raise


# Funciones de utilidad para crear configuraciones predefinidas
def create_aws_architecture_hierarchy():
    """Crea una configuración jerárquica para diseño de arquitectura AWS."""
    return {
        "levels": [
            {
                "level": 1,
                "nodes": [
                    {
                        "id": "coordinator",
                        "subordinates": ["aws_expert", "networking", "iac"]
                    }
                ]
            },
            {
                "level": 2,
                "nodes": [
                    {
                        "id": "aws_expert",
                        "subordinates": []
                    },
                    {
                        "id": "networking",
                        "subordinates": []
                    },
                    {
                        "id": "iac",
                        "subordinates": []
                    }
                ]
            }
        ]
    }


def create_devops_hierarchy():
    """Crea una configuración jerárquica para DevOps."""
    return {
        "levels": [
            {
                "level": 1,
                "nodes": [
                    {
                        "id": "coordinator",
                        "subordinates": ["cicd", "kubernetes", "iac"]
                    }
                ]
            },
            {
                "level": 2,
                "nodes": [
                    {
                        "id": "cicd",
                        "subordinates": []
                    },
                    {
                        "id": "kubernetes",
                        "subordinates": []
                    },
                    {
                        "id": "iac",
                        "subordinates": []
                    }
                ]
            }
        ]
    }
