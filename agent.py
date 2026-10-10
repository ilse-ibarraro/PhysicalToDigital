import warnings
warnings.filterwarnings("ignore", category=UserWarning)

from config import llm
from tools import (
    buscar_informacion_financiera, 
    extraer_datos_de_ticket, 
    consultar_resumen_gastos,
    verificar_estado_presupuesto,
    calcular_simulacion_inversion,
    validar_datos_transferencia,
    analizar_posible_fraude
)
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

# Lista completa de herramientas registradas en el agente
tools = [
    analizar_posible_fraude,
    calcular_simulacion_inversion,
    validar_datos_transferencia,
    buscar_informacion_financiera, 
    extraer_datos_de_ticket, 
    consultar_resumen_gastos,
    verificar_estado_presupuesto
]

llm_with_tools = llm.bind_tools(tools)
tools_by_name = {tool.name: tool for tool in tools}

SYSTEM_PROMPT = """You are PhysicalToDigital, a comprehensive financial mentor and co-pilot.
Your core mission is to empower users with digital finance guidance, bridging the gap between physical money and digital ecosystems.

Key Responsibilities:
1. Detect potential fraud, phishing, or scam attempts using 'analizar_posible_fraude' when users share suspicious messages, emails, or links.
2. Explain and guide digital payments, account validation, and money transfers using universal financial concepts (e.g., routing numbers, settlement IDs, interbank fees) alongside local payment rails.
3. Simulate and advise on investment strategies (fixed-income instruments, interest rates, compound growth, risk management) using globally understandable financial analogies and examples.
4. Convert physical receipts, invoices, or cash expenses into structured digital JSON records using your extraction tool.
5. Analyze budgets, expense limits, and proactively warn users if a category exceeds 80% or 100% of its monthly budget.
6. Provide clear, safe, encouraging, and actionable financial insights accessible to an international audience.
7. ALWAYS respond in English. Translate concepts and transaction terms into clear, standard financial English."""

def ejecutar_agente(consulta_usuario: str):
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=consulta_usuario)
    ]
    
    print(f"\n👤 Usuario: {consulta_usuario}")
    print("🤖 Co-piloto pensando...")
    
    ai_msg = llm_with_tools.invoke(messages)
    messages.append(ai_msg)
    
    if ai_msg.tool_calls:
        for tool_call in ai_msg.tool_calls:
            nombre_herramienta = tool_call["name"]
            print(f"\n🔎 Ejecutando herramienta integrada: {nombre_herramienta}...")
            
            tool_a_ejecutar = tools_by_name[nombre_herramienta]
            tool_output = tool_a_ejecutar.invoke(tool_call["args"])
            
            messages.append(ToolMessage(content=str(tool_output), tool_call_id=tool_call["id"]))
        
        respuesta_final = llm_with_tools.invoke(messages)
        print(f"\n🤖 Co-piloto: {respuesta_final.content}")
    else:
        print(f"\n🤖 Co-piloto: {ai_msg.content}")

if __name__ == "__main__":
    print("=" * 65)
    print("🤖 PhysicalToDigital Co-Pilot activo (Seguridad, Inversiones, Transferencias y Gastos).")
    print("Escribe tu consulta sobre fraudes, transferencias, inversiones, registra un ticket o revisa presupuesto (o 'salir').")
    print("=" * 65)
    
    while True:
        try:
            entrada = input("\n👤 Tu consulta: ").strip()
            if entrada.lower() in ["salir", "exit", "quit"]:
                print("👋 ¡Hasta luego!")
                break
            if not entrada:
                continue
            ejecutar_agente(entrada)
        except KeyboardInterrupt:
            print("\n👋 Sesión interrumpida.")
            break