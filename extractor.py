from pydantic import BaseModel, Field
from typing import List, Optional
from config import llm

# 1. Definición del modelo de datos para cada artículo individual
class ItemGasto(BaseModel):
    concepto: str = Field(description="Nombre o descripción corta del producto o servicio comprado")
    monto: float = Field(description="Precio o costo del producto/servicio en número flotante")
    categoria: str = Field(description="Categoría sugerida (ej. Alimentación, Transporte, Servicios, Entretenimiento, Salud, Hogar)")

# 2. Definición del modelo de datos principal del recibo o ticket
class TicketGasto(BaseModel):
    comercio: str = Field(description="Nombre del establecimiento, comercio o vendedor")
    fecha: Optional[str] = Field(description="Fecha de la compra en formato YYYY-MM-DD o texto si está explícita")
    metodo_pago: Optional[str] = Field(description="Método de pago (ej. Efectivo, Tarjeta de Crédito, Tarjeta de Débito, Transferencia)")
    total: float = Field(description="Monto total pagado de la compra")
    items: List[ItemGasto] = Field(description="Lista de los productos o servicios desglosados")

# Configurar el LLM para forzar la salida estructurada usando el modelo Pydantic
structured_llm = llm.with_structured_output(TicketGasto)

def procesar_texto_recibo(texto_recibo: str) -> TicketGasto:
    """Transforma texto no estructurado de tickets o notas de compra en un esquema Pydantic."""
    prompt = f"""Analiza el siguiente texto de un ticket, recibo o nota de compra física.
Extrae la información relevante y estructura el resultado cumpliendo estrictamente con el formato solicitado.

Texto del recibo/nota:
{texto_recibo}"""
    
    return structured_llm.invoke(prompt)

if __name__ == "__main__":
    print("=" * 65)
    print("🧾 Módulo Extractor de Recibos y Gastos Físicos (PhysicalToDigital)")
    print("=" * 65)
    
    # Ejemplo de prueba con una nota de compra informal/física
    nota_ejemplo = """
    Ticket de Chedraui Culiacán - Fecha: 05/10/2026
    Pago con tarjeta de débito.
    Compré 1 Leche LALA de $28.50, un paquete de tortillas de $24.00, y 2 jabones corporales por $45.00.
    Total pagado: $97.50
    """
    
    print("\n📄 Procesando texto de compra física...")
    resultado = procesar_texto_recibo(nota_ejemplo)
    
    print("\n✅ Datos estructurados en JSON de forma exitosa:")
    print(resultado.model_dump_json(indent=2))