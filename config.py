import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from tavily import TavilyClient

# Cargar variables del .env
load_dotenv()

# Configuración usando el modelo oficial de NVIDIA Nemotron en Nebius Studio
llm = ChatOpenAI(
    base_url="https://api.studio.nebius.com/v1",
    api_key=os.getenv("NEBIUS_API_KEY"),
    model="nvidia/Llama-3.1-Nemotron-70B-Instruct",
    temperature=0.1,
)

# Inicializar cliente de Tavily
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

print("⚙️ Configuración e inicialización con NVIDIA Llama-3.1-Nemotron-70B-Instruct en Nebius lista.")