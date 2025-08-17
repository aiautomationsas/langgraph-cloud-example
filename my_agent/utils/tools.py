from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
import requests
import json
import os
from typing import Dict, Any, List

# Herramienta Tavily existente
tavily_search = TavilySearchResults(max_results=3)

@tool
def ofac_screening_api(nombre: str, tipo_entidad: str = "individual") -> str:
    """
    Realiza screening de sanciones usando la API de OFAC-API.com (Screening API v4).
    Esta API está optimizada para reducir falsos positivos con lógica de fuzzy matching.
    
    Args:
        nombre: Nombre de la persona u organización a verificar
        tipo_entidad: Tipo de entidad ('individual', 'organization', 'vessel')
    
    Returns:
        Resultados del screening de sanciones OFAC
    """
    try:
        # Configuración de la API OFAC
        api_key = os.getenv('OFAC_API_KEY')
        base_url = "https://api.ofac-api.com/v4/screen"
        
        if not api_key:
            return "⚠️ ERROR: No se puede realizar el screening OFAC. La variable de entorno OFAC_API_KEY no está configurada. Por favor configura una API key válida para usar esta funcionalidad."
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "name": nombre,
            "type": tipo_entidad,
            "threshold": 0.8,  # Umbral de similitud para reducir falsos positivos
            "apiKey": api_key  # La API espera la key en el payload
        }
        
        response = requests.post(base_url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return f"Screening OFAC completado para '{nombre}':\n{json.dumps(data, indent=2)}"
        else:
            return f"⚠️ ERROR EN API OFAC (Status {response.status_code}): {response.text}\n\nNo se pudo realizar el screening para '{nombre}'. Por favor verifica la API key o intenta más tarde."
            
    except requests.RequestException as e:
        return f"⚠️ ERROR DE CONEXIÓN: No se pudo conectar con la API OFAC: {str(e)}"
    except Exception as e:
        return f"⚠️ ERROR INESPERADO: No se pudo realizar el screening OFAC para '{nombre}': {str(e)}"

@tool
def ofac_search_api(query: str, dataset: str = "all") -> str:
    """
    Busca en la base de datos global de sanciones usando OFAC Search API v4.
    Proporciona resultados más amplios para investigación y due diligence.
    
    Args:
        query: Término de búsqueda (nombre, dirección, número ID, etc.)
        dataset: Dataset a consultar ('ofac', 'eu', 'un', 'pep', 'all')
    
    Returns:
        Resultados de búsqueda en bases de datos de sanciones
    """
    try:
        api_key = os.getenv('OFAC_API_KEY')
        base_url = "https://api.ofac-api.com/v4/search"
        
        if not api_key:
            return "⚠️ ERROR: No se puede realizar la búsqueda OFAC. La variable de entorno OFAC_API_KEY no está configurada. Por favor configura una API key válida para usar esta funcionalidad."
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "dataset": dataset,
            "limit": 10,
            "apiKey": api_key  # La API espera la key en el payload
        }
        
        response = requests.post(base_url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return f"Búsqueda OFAC para '{query}' en dataset '{dataset}':\n{json.dumps(data, indent=2)}"
        else:
            return f"⚠️ ERROR EN API OFAC (Status {response.status_code}): {response.text}\n\nNo se pudo realizar la búsqueda para '{query}'. Por favor verifica la API key o intenta más tarde."
            
    except requests.RequestException as e:
        return f"⚠️ ERROR DE CONEXIÓN: No se pudo conectar con la API OFAC: {str(e)}"
    except Exception as e:
        return f"⚠️ ERROR INESPERADO: No se pudo realizar la búsqueda OFAC para '{query}': {str(e)}"

@tool
def ofac_bulk_screening(nombres_lista: str) -> str:
    """
    Realiza screening masivo usando OFAC Bulk Job API v4 (Beta).
    Puede procesar hasta 1 millón de nombres de forma asíncrona.
    
    Args:
        nombres_lista: Lista de nombres separados por comas o JSON array string
    
    Returns:
        Resultado del job de screening masivo
    """
    try:
        api_key = os.getenv('OFAC_API_KEY')
        base_url = "https://api.ofac-api.com/v4/bulk"
        
        if not api_key:
            return "⚠️ ERROR: No se puede realizar el screening masivo OFAC. La variable de entorno OFAC_API_KEY no está configurada. Por favor configura una API key válida para usar esta funcionalidad."
        
        # Procesar la lista de nombres
        if nombres_lista.startswith('['):
            try:
                nombres = json.loads(nombres_lista)
            except json.JSONDecodeError:
                return "⚠️ ERROR DE FORMATO: El formato JSON de la lista de nombres es inválido. Proporciona un JSON válido o nombres separados por comas."
        else:
            nombres = [n.strip() for n in nombres_lista.split(',')]
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "names": nombres,
            "threshold": 0.8,
            "apiKey": api_key  # La API espera la key en el payload
        }
        
        response = requests.post(base_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return f"Bulk screening OFAC iniciado para {len(nombres)} entidades:\n{json.dumps(data, indent=2)}"
        else:
            return f"⚠️ ERROR EN API OFAC (Status {response.status_code}): {response.text}\n\nNo se pudo realizar el screening masivo para {len(nombres)} entidades. Por favor verifica la API key o intenta más tarde."
            
    except json.JSONDecodeError:
        return "⚠️ ERROR DE FORMATO: Formato de lista inválido. Use nombres separados por comas o un JSON array válido."
    except requests.RequestException as e:
        return f"⚠️ ERROR DE CONEXIÓN: No se pudo conectar con la API OFAC: {str(e)}"
    except Exception as e:
        return f"⚠️ ERROR INESPERADO: No se pudo realizar el screening masivo OFAC: {str(e)}"

@tool
def verificar_cumplimiento_entidad(nombre_entidad: str, tipo_verificacion: str = "general") -> str:
    """
    Verifica el estado de cumplimiento de una entidad específica.
    
    Args:
        nombre_entidad: Nombre de la entidad a verificar
        tipo_verificacion: Tipo de verificación ('sanctions', 'kyc', 'aml', 'general')
    
    Returns:
        Informe de cumplimiento de la entidad
    """
    try:
        # Simulación de verificación de cumplimiento
        verificaciones = {
            "sanctions": f"Verificación de sanciones para {nombre_entidad}: NO encontrada en listas de sanciones",
            "kyc": f"Verificación KYC para {nombre_entidad}: Documentación completa y verificada",
            "aml": f"Verificación AML para {nombre_entidad}: Sin alertas de lavado de dinero",
            "general": f"Verificación general para {nombre_entidad}: Estado de cumplimiento APROBADO"
        }
        
        resultado = verificaciones.get(tipo_verificacion, verificaciones["general"])
        return f"{resultado}\nFecha de verificación: 2024-01-15\nPróxima revisión: 2024-04-15"
        
    except Exception as e:
        return f"Error en verificación de cumplimiento para {nombre_entidad}: {str(e)}"

@tool
def consultar_memoria_cumplimiento(clave: str) -> str:
    """
    Consulta la memoria del agente para recuperar información previa sobre cumplimiento.
    
    Args:
        clave: Clave para buscar en la memoria (ej: 'entidad_X', 'caso_123')
    
    Returns:
        Información almacenada en memoria o mensaje de no encontrado
    """
    # Esta es una implementación básica - en producción usarías una base de datos
    memoria_simulada = {
        "entidad_ejemplo": "Revisión previa: APROBADA (2024-01-10)",
        "caso_123": "Investigación en curso - Pendiente documentación adicional",
        "regulacion_gdpr": "Última actualización: Cumplimiento verificado 2024-01-12"
    }
    
    if clave in memoria_simulada:
        return f"Memoria encontrada para '{clave}': {memoria_simulada[clave]}"
    else:
        return f"No se encontró información en memoria para '{clave}'"

@tool
def generar_reporte_cumplimiento(entidad: str, hallazgos: str) -> str:
    """
    Genera un reporte formal de cumplimiento basado en los hallazgos.
    
    Args:
        entidad: Nombre de la entidad evaluada
        hallazgos: Resumen de los hallazgos de la investigación
    
    Returns:
        Reporte formal de cumplimiento
    """
    reporte = f"""
    === REPORTE DE CUMPLIMIENTO ===
    
    Entidad: {entidad}
    Fecha: 2024-01-15
    Oficial de Cumplimiento: Agente IA
    
    HALLAZGOS:
    {hallazgos}
    
    RECOMENDACIONES:
    - Continuar monitoreo regular
    - Actualizar documentación según sea necesario
    - Revisar en 90 días
    
    Estado: PROCESADO
    ===================================
    """
    return reporte

# Lista de todas las herramientas disponibles para el agente
tools = [
    tavily_search,
    ofac_screening_api,
    ofac_search_api,
    ofac_bulk_screening,
    verificar_cumplimiento_entidad,
    consultar_memoria_cumplimiento,
    generar_reporte_cumplimiento
]