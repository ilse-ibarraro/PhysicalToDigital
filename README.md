# 📈 PhysicalToDigital: Digital Finance & Investment Co-Pilot

**Technical Documentation & Application Guide**

PhysicalToDigital is an AI-powered financial co-pilot that helps users bridge everyday financial activities with digital financial literacy. It combines receipt digitization, expense tracking, investment growth simulations, transfer data validation, and fraud-awareness tools in an interactive application.

---

## 💡 Overview & Problem Statement

Many people rely on cash and paper receipts while lacking accessible tools to understand digital finance, track spending, and recognize potential scams.

PhysicalToDigital addresses these challenges through four core capabilities:

- **Receipt Digitization:** Extracts structured information from receipt text for expense tracking.
- **Investment Literacy:** Simulates compound growth to help users understand potential investment returns.
- **Transfer Data Validation:** Checks the format of CLABE and debit card numbers and provides estimated transfer-related information.
- **Fraud Awareness:** Analyzes suspicious financial messages for potential phishing indicators and provides educational safety recommendations.

**Disclaimer:** The application is designed as an educational tool. Financial projections are estimates, and transfer validation does not execute or independently verify bank transactions.

---

## ⚡ Tech Stack & Nebius Token Factory Integration

- **LLM Provider & Infrastructure:** Nebius Token Factory (`api.studio.nebius.com/v1`), leveraging the `nvidia/Nemotron-3_5-Lightning` model for low-latency agent reasoning and structured tool execution.
- **Agent Orchestration:** Python 3.13 with LangChain and native function calling (`tool_calls`) for multi-step execution.
- **Frontend & Visualizations:** Streamlit web interface with interactive Plotly graphs and custom dark theme styling.
- **Data Persistence & Processing:** Local JSON persistence (`compras.json`) and dynamic translation using `deep-translator` to deliver standardized English-language reporting across all interactive modules.

---

## 🧩 Key Modules Summary

| Module | Core Functionality | Primary Tools / Technologies |
|---|---|---|
| Transfer & Investment Hub | Investment simulations, SPEI validation, and anti-phishing risk analysis | Compound interest calculations, regex validation, LLM reasoning |
| Financial Mentor Chat | Natural-language financial co-pilot | LangChain, `tool_calls`, Plotly charts |
| Expense & Receipt History | Receipt categorization, data standardization, and CSV export | `deep-translator`, JSON persistence, Streamlit dataframes |

---

## 🛠️ Application Modules & Features

### 1. 💸 Transfer & Investment Hub

- Interactive compound interest simulator with customizable terms, annual rates, and visual Plotly growth projections.
- SPEI transfer format validator that checks 18-digit CLABE and 16-digit debit card formatting, with estimated fee calculations.
- Anti-phishing risk analysis module that identifies potential red flags in suspicious messages, providing risk level evaluation (`HIGH`, `MEDIUM`, `LOW`) and actionable security recommendations in English.

### 2. 💬 Financial Mentor Chat (Agentic Co-Pilot)

- Natural-language interface connected to specialized financial tools:
  - `calcular_simulacion_inversion` — Investment growth simulation.
  - `validar_datos_transferencia` — Transfer data validation.
  - `analizar_posible_fraude` — Potential fraud analysis.
  - `extraer_datos_de_ticket` — Receipt data extraction.
- Supports multi-turn conversations and generates inline charts when executing financial simulations.

### 3. 📋 Expense & Receipt History

- Visual dashboard categorizing receipt records by merchant and expense type.
- Data standardization for international presentation.
- CSV export for further analysis.

---

## 🚀 Quickstart & Local Setup

### Prerequisites

- Python 3.13 installed.
- Git installed.
- An active Nebius Token Factory API key.

### Installation Steps

#### 1. Clone the repository

```bash
git clone https://github.com/ilse-ibarraro/PhysicalToDigital.git
cd PhysicalToDigital
```

#### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux (Bash):**

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

#### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configure your Nebius API key

Set your API key as an environment variable. Replace `your_api_key_here` with your actual key. Never publish your API key in the repository.

**Windows (PowerShell):**

```powershell
$env:NEBIUS_API_KEY="your_api_key_here"
```

**macOS / Linux (Bash):**

```bash
export NEBIUS_API_KEY="your_api_key_here"
```

#### 5. Run the application

```bash
streamlit run app.py
```

Open the local URL displayed in your terminal.

---

## 🔐 Security & Limitations

- Never commit API keys, passwords, or other secrets to the repository.
- Financial simulations are educational estimates and do not guarantee investment returns.
- Transfer validation checks data formats; it does not initiate or confirm transactions.
- Fraud analysis provides potential risk indicators and should not be treated as a definitive security assessment.
- Keep your API key private and use environment variables to configure credentials.

---

## 🧠 NVIDIA & Nebius Usage

PhysicalToDigital integrates the `nvidia/Nemotron-3_5-Lightning` model through Nebius Token Factory for AI-powered financial assistance and tool execution.

The model allows users to interact with the application's financial education tools through natural-language requests.

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.