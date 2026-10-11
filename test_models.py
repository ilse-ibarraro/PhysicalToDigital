import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://api.studio.nebius.com/v1",
    api_key=os.getenv("NEBIUS_API_KEY"),
)

print("🔍 Consultando modelos disponibles en Nebius...")
try:
    models = client.models.list()
    for model in models:
        print(f"- {model.id}")
except Exception as e:
    print(f"❌ Error al listar modelos: {e}")