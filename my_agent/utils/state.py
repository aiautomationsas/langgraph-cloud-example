from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated, Sequence, Dict, Any

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    memoria_cumplimiento: Dict[str, Any]  # Memoria persistente para casos de cumplimiento
    contexto_investigacion: Dict[str, Any]  # Contexto actual de la investigación
    entidades_verificadas: Dict[str, Any]  # Cache de entidades ya verificadas
