#!/usr/bin/env python3
"""
Ejemplo de uso del Agente ReAct de Oficial de Cumplimiento

Este script demuestra cómo usar el agente para realizar investigaciones de cumplimiento
usando la API real de OFAC para screening de sanciones.

CONFIGURACIÓN REQUERIDA:
1. Obtén una API key en https://www.ofac-api.com/
2. Configura la variable de entorno: export OFAC_API_KEY="tu_api_key"
3. También necesitas configurar: ANTHROPIC_API_KEY y TAVILY_API_KEY
"""

import os
from my_agent.agent import graph
from langchain_core.messages import HumanMessage

# Verificar configuración de APIs
def verificar_configuracion():
    """Verifica que las APIs estén configuradas correctamente"""
    apis_requeridas = {
        'OFAC_API_KEY': 'API de OFAC para screening de sanciones',
        'GROQ_API_KEY': 'API de Groq para el modelo de lenguaje',
        'TAVILY_API_KEY': 'API de Tavily para búsquedas web'
    }
    
    print("=== VERIFICACIÓN DE CONFIGURACIÓN ===")
    configuracion_completa = True
    
    for api_key, descripcion in apis_requeridas.items():
        if os.getenv(api_key):
            print(f"✅ {api_key}: Configurada")
        else:
            print(f"❌ {api_key}: NO configurada - {descripcion}")
            configuracion_completa = False
    
    if not configuracion_completa:
        print("\n⚠️  NOTA: El agente funcionará en modo simulación sin las APIs reales")
    
    print("=" * 50)

def ejemplo_investigacion_cumplimiento():
    """Ejemplo de investigación de cumplimiento usando el agente ReAct con OFAC API"""
    
    # Configuración del agente - usando Groq
    config = {"configurable": {"model_name": "groq"}}
    
    # Estado inicial
    estado_inicial = {
        "messages": [
            HumanMessage(content="""
            Como oficial de cumplimiento, necesito investigar la empresa 'TechCorp Inc.' 
            para verificar su estado de cumplimiento normativo. Por favor:
            
            1. Usa la API de OFAC para verificar si está en listas de sanciones
            2. Realiza una búsqueda amplia en bases de datos internacionales (OFAC, EU, UN)
            3. Revisa su estado de cumplimiento general
            4. Busca información adicional en internet usando Tavily si es necesario
            5. Genera un reporte formal con tus hallazgos
            
            Nota: Si no tienes acceso a la API real de OFAC, usa el modo simulación.
            """)
        ]
    }
    
    print("=== INICIANDO INVESTIGACIÓN DE CUMPLIMIENTO ===\n")
    
    # Ejecutar el agente
    resultado = graph.invoke(estado_inicial, config=config)
    
    print("=== RESULTADO DE LA INVESTIGACIÓN ===")
    print(f"Mensajes finales: {len(resultado['messages'])}")
    print(f"Memoria de cumplimiento: {resultado.get('memoria_cumplimiento', {})}")
    print(f"Entidades verificadas: {resultado.get('entidades_verificadas', {})}")
    
    # Mostrar la respuesta final del agente
    if resultado['messages']:
        respuesta_final = resultado['messages'][-1]
        print(f"\n=== RESPUESTA DEL OFICIAL DE CUMPLIMIENTO ===")
        print(respuesta_final.content)

def ejemplo_consulta_memoria():
    """Ejemplo de cómo el agente usa su memoria y OFAC API"""
    
    config = {"configurable": {"model_name": "groq"}}
    
    estado_inicial = {
        "messages": [
            HumanMessage(content="""
            Consulta tu memoria sobre investigaciones previas y luego 
            verifica el cumplimiento de 'GlobalBank Ltd' enfocándote en:
            
            1. Screening OFAC para verificar sanciones
            2. Búsqueda en bases de datos internacionales
            3. Regulaciones AML (Anti-Money Laundering)
            4. Genera reporte con toda la información recopilada
            """)
        ]
    }
    
    print("\n=== EJEMPLO DE USO DE MEMORIA ===\n")
    
    resultado = graph.invoke(estado_inicial, config=config)
    
    if resultado['messages']:
        respuesta_final = resultado['messages'][-1]
        print(f"=== RESPUESTA CON MEMORIA ===")
        print(respuesta_final.content)

if __name__ == "__main__":
    # Verificar configuración antes de ejecutar
    verificar_configuracion()
    
    # Ejecutar ejemplos
    ejemplo_investigacion_cumplimiento()
    ejemplo_consulta_memoria()
    
    print("\n=== AGENTE REACT DE OFICIAL DE CUMPLIMIENTO LISTO ===")
    print("El agente está configurado con:")
    print("✅ API real de OFAC para screening de sanciones")
    print("✅ Búsqueda en bases de datos internacionales (OFAC, EU, UN, PEP)")
    print("✅ Screening masivo para múltiples entidades")
    print("✅ Herramienta Tavily para búsquedas web")
    print("✅ Sistema de memoria persistente")
    print("✅ Capacidad de generar reportes formales")
    print("✅ Patrón ReAct (Reasoning + Acting)")
    print("\n🎯 Visualiza el agente en LangGraph Studio: http://localhost:8123")
