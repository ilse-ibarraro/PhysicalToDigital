import os
import json
import re
import streamlit as st
import pandas as pd
import plotly.express as px
from deep_translator import GoogleTranslator

from agent import llm_with_tools, tools_by_name, SYSTEM_PROMPT
from tools import ARCHIVO_GASTOS, PRESUPUESTOS_MENSUALES, analizar_posible_fraude
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage

# General Page Configuration
st.set_page_config(
    page_title="PhysicalToDigital - Financial Co-Pilot",
    page_icon="📈",
    layout="wide"
)

st.title("📈 PhysicalToDigital: Digital Finance & Investment Co-Pilot")
st.caption("Your intelligent mentor for digital banking, investments, SPEI transfers, and financial tracking.")

# Instancia del traductor dinámico para conceptos de productos
translator = GoogleTranslator(source="auto", target="en")

# Dictionary mappings for standardizing Spanish entries into English
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

# --- DATA LOADING AND DYNAMIC TRANSLATION ---
def cargar_datos_compras():
    if not os.path.exists(ARCHIVO_GASTOS):
        return []
    try:
        with open(ARCHIVO_GASTOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

compras = cargar_datos_compras()

# Process items and convert terms dynamically to English for visual display
items_lista = []
for c in compras:
    comercio = c.get("comercio", "Unknown")
    metodo_raw = str(c.get("metodo_pago", "not specified")).lower()
    metodo = PAYMENT_MAP.get(metodo_raw, metodo_raw.capitalize())
    
    for item in c.get("items", []):
        cat_raw = item.get("categoria", "Otros")
        categoria = CATEGORY_MAP.get(cat_raw, cat_raw)
        
        # Traducción automática dinámica del concepto
        concepto_raw = str(item.get("concepto", "General")).strip()
        try:
            concepto = translator.translate(concepto_raw)
        except Exception:
            concepto = concepto_raw.capitalize()
        
        items_lista.append({
            "Merchant": comercio,
            "Payment Method": metodo,
            "Item Concept": concepto,
            "Amount ($)": item.get("monto", 0.0),
            "Category": categoria
        })

df_items = pd.DataFrame(items_lista)

# --- SIDEBAR (INVESTMENT QUICK SIMULATOR & BUDGET SUMMARY) ---
st.sidebar.header("💡 Investment Quick Simulator")

inv_amount = st.sidebar.number_input("Initial Amount ($)", min_value=100.0, value=5000.0, step=500.0)
inv_rate = st.sidebar.number_input("Annual Interest Rate (%)", min_value=0.5, value=11.0, step=0.5)
inv_months = st.sidebar.slider("Term (Months)", min_value=1, max_value=36, value=12)

tasa_mensual = (inv_rate / 100.0) / 12.0
final_balance = inv_amount * ((1 + tasa_mensual) ** inv_months)
interest_earned = final_balance - inv_amount

st.sidebar.metric(label="Projected Total Balance", value=f"${final_balance:,.2f}")
st.sidebar.metric(label="Estimated Interest Earned", value=f"${interest_earned:,.2f}", delta=f"+${interest_earned:,.2f}")

st.sidebar.divider()
st.sidebar.header("📊 Monthly Budget Tracker")

total_gastado = df_items["Amount ($)"].sum() if not df_items.empty else 0.0
presupuesto_total = sum(PRESUPUESTOS_MENSUALES.values())
disponible_total = presupuesto_total - total_gastado

st.sidebar.metric(label="Total Monthly Budget", value=f"${presupuesto_total:,.2f}")
st.sidebar.metric(label="Total Spent", value=f"${total_gastado:,.2f}", delta=f"-${total_gastado:,.2f}", delta_color="inverse")
st.sidebar.metric(label="Available Balance", value=f"${disponible_total:,.2f}")

# --- MAIN TABS (PRIORITIZING DIGITAL FINANCE & INVESTMENTS) ---
tab_hub, tab_mentor, tab_historial = st.tabs([
    "💸 Transfer & Investment Hub", 
    "💬 Financial Mentor Chat", 
    "📋 Expense & Receipt History"
])

# 1. TAB: TRANSFER & INVESTMENT HUB
with tab_hub:
    st.subheader("Interactive Investment Growth Projection")
    st.write("Simulate compound interest returns for fixed-income instruments, treasury bonds (Cetes), or savings accounts.")
    
    # Growth Chart based on sidebar inputs
    meses_arr = list(range(0, inv_months + 1))
    saldos_arr = [inv_amount * ((1 + tasa_mensual) ** m) for m in meses_arr]
    df_growth = pd.DataFrame({"Month": meses_arr, "Projected Balance ($)": saldos_arr})
    
    fig_growth = px.line(
        df_growth, 
        x="Month", 
        y="Projected Balance ($)", 
        title=f"Growth Projection ({inv_rate}% Annual Rate over {inv_months} Months)",
        markers=True
    )
    st.plotly_chart(fig_growth, use_container_width=True)
    
    st.divider()
    st.subheader("Transfer Safety Check & Validator")
    st.write("Verify account number formatting and estimate interbank SPEI fees before sending funds.")
    
    col1, col2 = st.columns(2)
    with col1:
        acc_input = st.text_input("CLABE Number (18 digits) or Debit Card (16 digits)", placeholder="e.g., 012180004481234567")
        bank_input = st.text_input("Destination Bank", placeholder="e.g., BBVA, Banorte, Nu")
    with col2:
        amount_input = st.number_input("Amount to Transfer ($)", min_value=1.0, value=1000.0, step=100.0)
        
        if st.button("Validate Transfer Details", type="primary"):
            limpio = re.sub(r"\D", "", acc_input)
            if len(limpio) == 18:
                st.success("✅ Valid CLABE format (18 digits).")
            elif len(limpio) == 16:
                st.success("✅ Valid Debit Card format (16 digits).")
            else:
                st.error("❌ Invalid account format. Please check length (18 digits for CLABE, 16 for card).")
            
            fee = 0.0 if amount_input < 5000 else 5.0
            st.info(f"💡 Estimated SPEI transfer fee for ${amount_input:,.2f} to {bank_input if bank_input else 'Destination Bank'}: **${fee:.2f} MXN**.")

    st.divider()
    st.subheader("🛡️ Anti-Phishing & Fraud Shield")
    st.write("Paste suspicious SMS messages, emails, or bank alerts to detect scam red flags before taking action.")
    
    sms_input = st.text_area(
        "Suspicious Message Text", 
        placeholder="e.g., 'URGENT: Your bank account is locked. Click http://bit.ly/bank-verify to enter your PIN immediately.'"
    )
    
    if st.button("Analyze Security Risk", type="secondary"):
        if sms_input.strip():
            raw_resultado = analizar_posible_fraude.invoke({"texto_mensaje": sms_input})
            resultado = json.loads(raw_resultado)
            
            risk_level = resultado.get("risk_level", "DESCONOCIDO")
            red_flags = resultado.get("detected_red_flags", [])
            recommendations = resultado.get("safety_recommendations", [])
            
            if risk_level == "ALTO":
                st.error(f"🚨 **Riesgo de Fraude: {risk_level}**")
            elif risk_level == "MEDIO":
                st.warning(f"⚠️ **Riesgo de Fraude: {risk_level}**")
            else:
                st.success(f"✅ **Riesgo de Fraude: {risk_level}**")
                
            st.markdown("### Banderas Rojas Detectadas:")
            for flag in red_flags:
                st.write(f"- 🚩 {flag}")
                
            st.markdown("### Recomendaciones de Seguridad:")
            for rec in recommendations:
                st.write(f"- 🔒 {rec}")
        else:
            st.error("Por favor, pega el texto de un mensaje sospechoso para analizar.")

# 2. TAB: FINANCIAL MENTOR CHAT
with tab_mentor:
    st.subheader("Chat with your Financial & Investment Mentor")
    st.write("Ask questions about digital banking, investment yields, SPEI transfers, or paste physical receipts.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about investments, transfers, or paste receipt text here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Mentor analyzing..."):
                langchain_msgs = [SystemMessage(content=SYSTEM_PROMPT + "\n\nALWAYS respond in English. Translate concepts and transaction terms to English in your final response.")]
                
                # Reconstrucción correcta del historial de mensajes
                for m in st.session_state.messages:
                    if m["role"] == "user":
                        langchain_msgs.append(HumanMessage(content=m["content"]))
                    elif m["role"] == "assistant":
                        langchain_msgs.append(AIMessage(content=m["content"]))

                ai_msg = llm_with_tools.invoke(langchain_msgs)
                
                # Procesamiento y ejecución de llamadas a herramientas (Tool Calling)
                if ai_msg.tool_calls:
                    tool_responses = []
                    langchain_msgs.append(ai_msg)
                    
                    for tool_call in ai_msg.tool_calls:
                        name_lower = tool_call["name"].lower()
                        
                        # Buscar herramienta tolerando variaciones de mayúsculas/minúsculas
                        tool_obj = tools_by_name.get(name_lower) or tools_by_name.get(tool_call["name"])
                        
                        if tool_obj:
                            out = tool_obj.invoke(tool_call["args"])
                            tool_responses.append(ToolMessage(content=str(out), tool_call_id=tool_call["id"]))
                            
                            # Renderizado visual en vivo de resultados de la herramienta
                            try:
                                data_out = json.loads(out) if isinstance(out, str) else out
                                
                                # Si es la herramienta de simulación de inversión, dibujar la gráfica interactiva
                                if "proyeccion_mensual" in data_out:
                                    df_sim = pd.DataFrame(data_out["proyeccion_mensual"])
                                    fig_sim = px.line(
                                        df_sim, 
                                        x="mes", 
                                        y="saldo", 
                                        title=f"Projected Investment Growth ({data_out.get('monto_final', '')})",
                                        markers=True
                                    )
                                    st.plotly_chart(fig_sim, use_container_width=True)
                                else:
                                    with st.expander(f"🛠️ Tool Output ({tool_call['name']})"):
                                        st.json(data_out)
                            except Exception:
                                pass

                    langchain_msgs.extend(tool_responses)
                    
                    # Segunda llamada para generar la respuesta final enriquecida con los datos
                    final_response = llm_with_tools.invoke(langchain_msgs)
                    respuesta_texto = final_response.content
                else:
                    respuesta_texto = ai_msg.content

                st.markdown(respuesta_texto)
                st.session_state.messages.append({"role": "assistant", "content": respuesta_texto})
        
        st.rerun()

# 3. TAB: EXPENSE & RECEIPT HISTORY
with tab_historial:
    st.subheader("Physical Receipts & Expense Breakdown")
    if not df_items.empty:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("### Expenses by Category")
            fig_pie = px.pie(
                df_items, 
                names="Category", 
                values="Amount ($)", 
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_c2:
            st.markdown("### Expenses by Merchant")
            fig_bar = px.bar(
                df_items.groupby("Merchant", as_index=False)["Amount ($)"].sum(),
                x="Merchant",
                y="Amount ($)",
                color="Merchant",
                text_auto='.2f'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
        st.divider()
        st.dataframe(df_items, use_container_width=True)
        
        csv_data = df_items.to_csv(index=False).encode("utf-8")
        st.divider()
        st.write("📥 **Export Data**")
        st.download_button(
            label="Download Transactions as CSV",
            data=csv_data,
            file_name="transactions_history.csv",
            mime="text/csv",
            type="primary"
        )
    else:
        st.info("No recorded physical receipts found.")