from typing import TypedDict, Literal

from langgraph.graph import StateGraph, END
from my_agent.utils.nodes import call_model, should_continue, tool_node
from my_agent.utils.state import AgentState


# Define the config - solo Groq
class GraphConfig(TypedDict):
    model_name: Literal["groq"]


# Función para inicializar el estado del agente con memoria
def inicializar_estado(state):
    """Inicializa el estado del agente con estructuras de memoria vacías"""
    if "memoria_cumplimiento" not in state:
        state["memoria_cumplimiento"] = {}
    if "contexto_investigacion" not in state:
        state["contexto_investigacion"] = {
            "casos_activos": [],
            "entidades_en_revision": []
        }
    if "entidades_verificadas" not in state:
        state["entidades_verificadas"] = {}
    
    return state

# Define a new graph para el Agente ReAct de Oficial de Cumplimiento
workflow = StateGraph(AgentState, config_schema=GraphConfig)

# Agregar nodo de inicialización
workflow.add_node("inicializar", inicializar_estado)

# Define los nodos principales del ciclo ReAct
workflow.add_node("agent", call_model)  # Nodo de razonamiento
workflow.add_node("action", tool_node)  # Nodo de acción (herramientas)

# Set the entrypoint como inicialización
workflow.set_entry_point("inicializar")

# Conectar inicialización con el agente
workflow.add_edge("inicializar", "agent")

# Agregar conditional edges para el ciclo ReAct
workflow.add_conditional_edges(
    # Comenzamos desde el nodo 'agent' (razonamiento)
    "agent",
    # Función que determina si continuar con herramientas o terminar
    should_continue,
    # Mapeo de decisiones:
    {
        # Si necesita usar herramientas, va al nodo de acción
        "continue": "action",
        # Si no necesita herramientas, termina
        "end": END,
    },
)

# Después de usar herramientas, regresa al agente para razonar sobre los resultados
workflow.add_edge("action", "agent")

# Compilar el grafo del Agente ReAct de Oficial de Cumplimiento
# Este agente implementa el patrón ReAct: Reasoning, Acting, Observing
graph = workflow.compile()
