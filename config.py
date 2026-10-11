import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from tavily import TavilyClient

# Cargar variables del .env
load_dotenv()

# Configuración usando el modelo oficial disponible en Nebius Studio
llm = ChatOpenAI(
    base_url="https://api.studio.nebius.com/v1",
    api_key=os.getenv("NEBIUS_API_KEY"),
    model="nvidia/Nemotron-3_5-Lightning",
    temperature=0.1,
)

# Inicializar cliente de Tavily
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

print("⚙️ Configuración con NVIDIA Nemotron lista.")