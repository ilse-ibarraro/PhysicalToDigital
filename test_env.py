import os
from dotenv import load_dotenv
from tavily import TavilyClient

# Cargar las variables del archivo .env
load_dotenv()

tavily_key = os.getenv("TAVILY_API_KEY")

if not tavily_key:
    print("❌ ERROR: No se encontró la variable TAVILY_API_KEY en tu archivo .env")
else:
    print("✅ Archivo .env leído correctamente.")
    print("🔄 Probando conexión con Tavily Search...")

    try:
        tavily = TavilyClient(api_key=tavily_key)
        
        # Realizar una búsqueda financiera rápida de prueba
        response = tavily.search(query="tipo de cambio USD MXN hoy", max_results=1)

        print("\n🎉 ¡Conexión exitosa con Tavily!")
        print(f"Resultado obtenido: {response['results'][0]['title']}")
        print(f"Enlace: {response['results'][0]['url']}")

    except Exception as e:
        print(f"\n❌ Error al conectar con Tavily: {e}")