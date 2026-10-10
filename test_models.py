import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("NEBIUS_API_KEY")
print(f"Buscando modelos para API Key que inicia con: {api_key[:6] if api_key else 'NO ENCONTRADA'}...")

# Endpoint oficial de Nebius AI Studio (.com)
client = OpenAI(
    api_key=api_key,
    base_url="https://api.studio.nebius.com/v1"
)

try:
    models = client.models.list()
    print("\n✅ Modelos disponibles en tu cuenta de Nebius:")
    for model in models.data:
        print(f" - {model.id}")
except Exception as e:
    print(f"\n❌ Error al consultar la API de Nebius: {e}")