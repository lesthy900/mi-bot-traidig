import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIGURACIÓN DE TELEGRAM (ID VERIFICADO) ---
def enviar_a_telegram(mensaje):
    token = "8553805048:AAFNtIznh3boHALXYxcMDFmFnnQkyTX4ado"
    chat_id = "1703425585"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, data=payload)
    except: pass

# --- 2. LÓGICA DE SEÑAL CON ESPECIFICACIONES TÉCNICAS ---
def generar_señal_maestra(activo, precio, rsi, capital_riesgo):
    # Definición de especificaciones (diferenciales de precio)
    puntos_tp = precio * 0.03   # Ejemplo: el 0.002 que mencionas
    puntos_sl = precio * 0.015  # Ejemplo: el 0.001 que mencionas
    
    tp_final = precio + puntos_tp
    sl_final = precio - puntos_sl
    
    # Cálculo de Lote (Unidades a comprar según tu capital)
    lote_unidades = capital_riesgo / precio
    
    mensaje = (
        f"🔥 SEÑAL CON ESPECIFICACIONES TÉCNICAS\n\n"
        f"📈 Activo: {activo}\n"
        f"💰 PUNTO DE ENTRADA: {precio:,.4f}\n"
        f"📦 Lote sugerido: {lote_unidades:.4f} unidades\n\n"
        f"📊 ESPECIFICACIONES DE SALIDA:\n"
        f"✅ Take Profit: +{puntos_tp:,.4f} (Objetivo: {tp_final:,.4f})\n"
        f"❌ Stop Loss: -{puntos_sl:,.4f} (Límite: {sl_final:,.4f})\n\n"
        f"📉 RSI Actual: {rsi:.1f}\n"
        f"⚡ Ejecuta con estos niveles exactos."
    )
    enviar_a_telegram(mensaje)

# --- 3. INTERFAZ DE LA APP ---
st.set_page_config(page_title="Terminal Trading VIP", layout="wide")
st_autorefresh(interval=60000, key="auto_pilot")

# Mensaje de inicio automático
if 'inicio' not in st.session_state:
    enviar_a_telegram("🤖 Lesthy_bot: Sistema de Especificaciones y Lotes Online.")
    st.session_state.inicio = True

st.title("🤖 Lesthy_bot: Gestión de Lotes y Especificaciones")

# Panel lateral para definir tu capital
st.sidebar.header("⚙️ Configuración de Riesgo")
mi_capital = st.sidebar.number_input("Capital por operación (USD):", min_value=10.0, value=100.0)

st.info(f"🛰️ Escaneando mercado. Riesgo: *${mi_capital} USD* | Buscando el punto de entrada justo.")

# Ejecución del escáner
activos = ["BTC-USD", "ETH-USD", "SOL-USD", "NVDA", "AAPL"]
for a in activos:
    df = yf.download(a, period="1d", interval="1m", progress=False)
    if not df.empty:
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        
        # Cálculo de RSI para el tiempo de entrada
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
        
        # Disparador de señal (RSI < 30)
        if rsi < 30:
            precio_ahora = df['Close'].iloc[-1]
            generar_señal_maestra(a, precio_ahora, rsi, mi_capital)
            st.success(f"✅ Especificaciones enviadas para {a}")
