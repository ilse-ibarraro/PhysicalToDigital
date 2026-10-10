import os
import json
import re
from langchain_core.tools import tool
from config import tavily_client
from extractor import procesar_texto_recibo
from deep_translator import GoogleTranslator

# Inicializar traductor automático
translator = GoogleTranslator(source="auto", target="en")

# Mapeos estáticos directos para categorías y métodos habituales
CATEGORY_MAP = {
    "Alimentación": "Food & Groceries",
    "Salud": "Health & Medical",
    "Entretenimiento": "Entertainment",
    "Transporte": "Transportation",
    "Servicios": "Utilities & Services",
    "Hogar": "Home & Living",
    "Otros": "Others"
}

PAYMENT_MAP = {
    "efectivo": "Cash",
    "tarjeta de débito": "Debit Card",
    "tarjeta de crédito": "Credit Card",
    "transferencia": "Bank Transfer",
    "no especificado": "Not Specified"
}

ARCHIVO_GASTOS = "compras.json"

PRESUPUESTOS_MENSUALES = {
    "Food & Groceries": 2000.0,
    "Health & Medical": 1000.0,
    "Entertainment": 800.0,
    "Transportation": 1200.0,
    "Utilities & Services": 1500.0,
    "Home & Living": 1500.0
}

# --- HERRAMIENTAS DE FINANZAS DIGITALES, SEGURIDAD E INVERSIÓN ---

@tool
def analizar_posible_fraude(texto_mensaje: str) -> str:
    """
    Analiza un mensaje de texto (SMS), correo electrónico o alerta bancaria sospechosa 
    para detectar banderas rojas de fraude, phishing o ingeniería social (urgencia, enlaces externos, 
    solicitud de claves o datos confidenciales) y ofrece recomendaciones de seguridad.
    """
    texto_lower = texto_mensaje.lower()
    banderas_rojas = []
    
    # Detección de patrones comunes de fraude y phishing
    if any(palabra in texto_lower for palabra in ["urgente", "bloquead", "suspendid", "inmediato", "24 horas", "alerta de seguridad", "desactivad"]):
        banderas_rojas.append("Urgencia o alarma artificial para generar pánico y obligar a actuar rápido.")
        
    if any(palabra in texto_lower for palabra in ["nip", "cvv", "contraseña", "token", "clave", "código de verificación", "password"]):
        banderas_rojas.append("Solicitud de claves confidenciales, NIP o códigos de verificación.")
        
    if any(palabra in texto_lower for palabra in ["http", "bit.ly", "tinyurl", "click", "enlace", "link", "ingresa a", "valida aquí"]):
        banderas_rojas.append("Inclusión de enlaces web externos o acortados para redirigir a un sitio no oficial.")
        
    if any(palabra in texto_lower for palabra in ["ganador", "premio", "bono", "recompensa", "sorteo", "transferencia recibida"]):
        banderas_rojas.append("Promesa de premios o incentivos monetarios no solicitados.")

    nivel_riesgo = "ALTO" if len(banderas_rojas) >= 2 else ("MEDIO" if len(banderas_rojas) == 1 else "BAJO")
    
    analisis = {
        "risk_level": nivel_riesgo,
        "detected_red_flags": banderas_rojas if banderas_rojas else ["No se detectaron patrones explícitos de fraude habitual."],
        "safety_recommendations": [
            "Nunca hagas clic en enlaces recibidos por SMS o correo no solicitado.",
            "Recuerda que ningún banco te pedirá NIP, claves dinámicas o token por mensaje o llamada.",
            "Si tienes dudas, no utilices los enlaces del mensaje. Ingresa directamente desde la app oficial de tu banco o llama al número en el reverso de tu tarjeta."
        ]
    }
    return json.dumps(analisis, ensure_ascii=False, indent=2)

@tool
def calcular_simulacion_inversion(monto_inicial: float, tasa_anual_porcentaje: float, plazo_meses: int) -> str:
    """
    Calculates investment growth over a given number of months using compound interest.
    Useful for projecting returns on fixed-income instruments (e.g., Cetes, SOFIPOs, money market funds).
    """
    if monto_inicial <= 0 or tasa_anual_porcentaje <= 0 or plazo_meses <= 0:
        return "Error: Initial amount, interest rate, and term must be greater than zero."
        
    tasa_mensual = (tasa_anual_porcentaje / 100.0) / 12.0
    monto_final = monto_inicial * ((1 + tasa_mensual) ** plazo_meses)
    ganancia_total = monto_final - monto_inicial
    
    resumen = {
        "initial_investment": round(monto_inicial, 2),
        "annual_rate_percent": tasa_anual_porcentaje,
        "term_months": plazo_meses,
        "total_interest_earned": round(ganancia_total, 2),
        "projected_final_balance": round(monto_final, 2)
    }
    return json.dumps(resumen, ensure_ascii=False, indent=2)

@tool
def validar_datos_transferencia(clabe_o_cuenta: str, banco_destino: str, monto: float) -> str:
    """
    Validates transfer details such as CLABE number length (18 digits) or card number length (16 digits),
    calculates estimated SPEI transfer fees, and provides safety checks before transferring funds.
    """
    limpio = re.sub(r"\D", "", clabe_o_cuenta)
    es_clabe_valida = len(limpio) == 18
    es_tarjeta_valida = len(limpio) == 16
    
    if not (es_clabe_valida or es_tarjeta_valida):
        estado_cuenta = "Invalid format (CLABE must have 18 digits; debit card must have 16 digits)."
    else:
        estado_cuenta = "Valid account length."

    # Estimated interbank SPEI fees
    comision_estimada = 0.0 if monto < 5000 else 5.0

    analisis = {
        "destination_bank": banco_destino,
        "amount_to_transfer": round(monto, 2),
        "account_status": estado_cuenta,
        "estimated_spei_fee": round(comision_estimada, 2),
        "safety_recommendation": "Always verify recipient name on the preview screen before authorizing the SPEI transaction."
    }
    return json.dumps(analisis, ensure_ascii=False, indent=2)

# --- HERRAMIENTAS DE GASTOS Y BÚSQUEDA ---

def traducir_texto(texto: str) -> str:
    """Traduce cualquier texto al inglés de forma dinámica."""
    if not texto:
        return texto
    try:
        return translator.translate(texto)
    except Exception:
        return texto.capitalize()

def guardar_en_json(datos_ticket_dict: dict) -> bool:
    """Estructura y traduce los campos del ticket al inglés antes de guardarlos en JSON."""
    # Traducir método de pago
    metodo_raw = str(datos_ticket_dict.get("metodo_pago", "not specified")).strip()
    datos_ticket_dict["metodo_pago"] = PAYMENT_MAP.get(metodo_raw.lower(), traducir_texto(metodo_raw))

    # Traducir items (concepto y categoría)
    items_traducidos = []
    for item in datos_ticket_dict.get("items", []):
        cat_raw = item.get("categoria", "Otros")
        categoria_en = CATEGORY_MAP.get(cat_raw, traducir_texto(cat_raw))
        
        concepto_raw = item.get("concepto", "General")
        concepto_en = traducir_texto(concepto_raw)

        items_traducidos.append({
            "concepto": concepto_en,
            "monto": item.get("monto", 0.0),
            "categoria": categoria_en
        })

    datos_ticket_dict["items"] = items_traducidos

    gastos_acumulados = []
    if os.path.exists(ARCHIVO_GASTOS):
        try:
            with open(ARCHIVO_GASTOS, "r", encoding="utf-8") as f:
                gastos_acumulados = json.load(f)
        except json.JSONDecodeError:
            gastos_acumulados = []

    comercio_nuevo = str(datos_ticket_dict.get("comercio", "")).strip().lower()
    items_nuevos = datos_ticket_dict.get("items", [])
    monto_nuevo = sum(item.get("monto", 0.0) for item in items_nuevos)
    conceptos_nuevos = sorted([item.get("concepto", "").strip().lower() for item in items_nuevos])

    for compra in gastos_acumulados:
        comercio_existente = str(compra.get("comercio", "")).strip().lower()
        if comercio_existente == comercio_nuevo:
            items_existentes = compra.get("items", [])
            monto_existente = sum(item.get("monto", 0.0) for item in items_existentes)
            conceptos_existentes = sorted([item.get("concepto", "").strip().lower() for item in items_existentes])
            if abs(monto_existente - monto_nuevo) < 0.01 and conceptos_existentes == conceptos_nuevos:
                return False

    gastos_acumulados.append(datos_ticket_dict)
    with open(ARCHIVO_GASTOS, "w", encoding="utf-8") as f:
        json.dump(gastos_acumulados, f, ensure_ascii=False, indent=2)
    return True

@tool
def buscar_informacion_financiera(query: str) -> str:
    """Busca información financiera actualizada en la web usando Tavily."""
    try:
        results = tavily_client.search(query=query, max_results=3)
        formatted_results = []
        for item in results.get("results", []):
            formatted_results.append(
                f"Título: {item['title']}\nEnlace: {item['url']}\nContenido: {item['content']}\n"
            )
        return "\n---\n".join(formatted_results)
    except Exception as e:
        return f"Error al realizar la búsqueda: {e}"

@tool
def extraer_datos_de_ticket(texto_recibo: str) -> str:
    """Extrae y estructura datos financieros desde un ticket o recibo físico."""
    try:
        ticket_estructurado = procesar_texto_recibo(texto_recibo)
        ticket_dict = ticket_estructurado.model_dump()
        exito = guardar_en_json(ticket_dict)
        if not exito:
            return f"⚠️ Duplicate receipt detected! Transaction at '{ticket_dict.get('comercio')}' is already registered."
        return json.dumps(ticket_dict, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Error al procesar o guardar el recibo: {e}"

@tool
def consultar_resumen_gastos(categoria_filtro: str = None) -> str:
    """Consulta el historial acumulado de gastos en compras.json."""
    if not os.path.exists(ARCHIVO_GASTOS):
        return "Aún no hay compras o gastos registrados en el sistema."
    try:
        with open(ARCHIVO_GASTOS, "r", encoding="utf-8") as f:
            compras = json.load(f)
        return json.dumps(compras, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Error al leer el historial de compras: {e}"

@tool
def verificar_estado_presupuesto() -> str:
    """Calcula el acumulado gastado por categoría comparándolo contra los límites mensuales."""
    if not os.path.exists(ARCHIVO_GASTOS):
        return "Aún no hay compras registradas para comparar con el presupuesto."
    try:
        with open(ARCHIVO_GASTOS, "r", encoding="utf-8") as f:
            compras = json.load(f)
        totales_por_categoria = {}
        for compra in compras:
            for item in compra.get("items", []):
                cat = item.get("categoria", "Others")
                totales_por_categoria[cat] = totales_por_categoria.get(cat, 0.0) + item.get("monto", 0.0)
        estado_presupuesto = []
        for cat, limite in PRESUPUESTOS_MENSUALES.items():
            gastado = totales_por_categoria.get(cat, 0.0)
            estado_presupuesto.append({
                "categoria": cat,
                "gastado": gastado,
                "limite": limite,
                "disponible": limite - gastado,
                "porcentaje_usado": round((gastado / limite) * 100 if limite > 0 else 0, 1)
            })
        return json.dumps(estado_presupuesto, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Error al calcular el presupuesto: {e}"