from functools import lru_cache
from langchain_groq import ChatGroq
from my_agent.utils.tools import tools
from langgraph.prebuilt import ToolNode
from datetime import datetime


@lru_cache(maxsize=4)
def _get_model(model_name: str = None):
    # Usar Groq con el modelo gpt-oss-20b
    model = ChatGroq(temperature=0, model_name="openai/gpt-oss-20b")
    model = model.bind_tools(tools)
    return model

# Define the function that determines whether to continue or not
def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    # If there are no tool calls, then we finish
    if not last_message.tool_calls:
        return "end"
    # Otherwise if there is, we continue
    else:
        return "continue"

# Sistema prompt especializado para oficial de cumplimiento
system_prompt = """Eres un Oficial de Cumplimiento especializado que utiliza un enfoque ReAct (Reasoning + Acting).

Tu rol es:
- Investigar y verificar el cumplimiento normativo de entidades y transacciones
- Utilizar la API real de OFAC para screening de sanciones
- Mantener memoria de investigaciones previas
- Generar reportes formales de cumplimiento
- Buscar información relevante usando Tavily cuando sea necesario

Proceso ReAct:
1. REASON (Razonar): Analiza la solicitud y determina qué información necesitas
2. ACT (Actuar): Usa las herramientas disponibles para obtener información
3. OBSERVE (Observar): Evalúa los resultados y determina si necesitas más información
4. Repite el ciclo hasta tener suficiente información para generar una respuesta completa

Herramientas disponibles:
- tavily_search: Para buscar información general en internet
- ofac_screening_api: Para screening individual de sanciones OFAC (API v4)
- ofac_search_api: Para búsqueda amplia en bases de datos de sanciones (OFAC, EU, UN, PEP)
- ofac_bulk_screening: Para screening masivo de múltiples entidades
- verificar_cumplimiento_entidad: Para verificaciones adicionales de KYC/AML
- consultar_memoria_cumplimiento: Para recuperar información de investigaciones previas
- generar_reporte_cumplimiento: Para crear reportes formales

IMPORTANTE: Para usar las APIs reales de OFAC, asegúrate de que esté configurada la variable de entorno OFAC_API_KEY.

Siempre mantén un enfoque profesional y meticuloso en tus investigaciones."""

# Define the function that calls the model
def call_model(state, config):
    messages = state["messages"]
    
    # Inicializar memoria si no existe
    if "memoria_cumplimiento" not in state:
        state["memoria_cumplimiento"] = {}
    if "contexto_investigacion" not in state:
        state["contexto_investigacion"] = {}
    if "entidades_verificadas" not in state:
        state["entidades_verificadas"] = {}
    
    # Agregar contexto de memoria al prompt si existe información relevante
    contexto_memoria = ""
    if state.get("memoria_cumplimiento"):
        contexto_memoria = f"\n\nContexto de memoria de cumplimiento: {state['memoria_cumplimiento']}"
    
    system_message = {"role": "system", "content": system_prompt + contexto_memoria}
    messages = [system_message] + messages
    
    # Usar siempre OpenAI, ignorando la configuración de modelo
    model = _get_model()
    response = model.invoke(messages)
    
    # Actualizar contexto de investigación con timestamp
    state["contexto_investigacion"]["ultimo_acceso"] = datetime.now().isoformat()
    
    # We return a list, because this will get added to the existing list
    return {
        "messages": [response],
        "memoria_cumplimiento": state.get("memoria_cumplimiento", {}),
        "contexto_investigacion": state.get("contexto_investigacion", {}),
        "entidades_verificadas": state.get("entidades_verificadas", {})
    }

# Nodo personalizado para manejar herramientas con memoria
def tool_node_with_memory(state):
    # Ejecutar las herramientas
    tool_result = ToolNode(tools).invoke(state)
    
    # Actualizar memoria basada en los resultados de las herramientas
    last_message = state["messages"][-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            tool_name = tool_call.get('name', '')
            if tool_name == 'verificar_cumplimiento_entidad':
                # Guardar resultado en cache de entidades verificadas
                args = tool_call.get('args', {})
                entidad = args.get('nombre_entidad', '')
                if entidad:
                    state["entidades_verificadas"][entidad] = {
                        "fecha_verificacion": datetime.now().isoformat(),
                        "resultado": "verificado"
                    }
    
    return tool_result

# Usar el nodo de herramientas personalizado
tool_node = tool_node_with_memory