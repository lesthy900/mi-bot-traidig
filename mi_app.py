import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIGURACIÓN DE TELEGRAM ---
def enviar_a_telegram(mensaje):
    token = "8553805048:AAFNtIznh3boHALXYxcMDFmFnnQkyTX4ado"
    chat_id = "1703425585"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
    try: requests.post(url, data=payload)
    except: pass

# --- 2. LÓGICA DE SEÑAL Y CÁLCULO DE LOTES ---
def generar_señal_maestra(activo, precio, rsi, capital_riesgo):
    # Cálculos de precios (no solo porcentajes)
    tp_precio = precio * 1.03
    sl_precio = precio * 0.985
    
    # Cálculo de Lote (Unidades a comprar según tu capital)
    lote_unidades = capital_riesgo / precio
    ganancia_estimada = capital_riesgo * 0.03
    
    mensaje = (
        f"🔥 SEÑAL MAESTRA DETECTADA\n\n"
        f"📈 Activo: {activo}\n"
        f"💰 Precio Entrada: ${precio:,.2f}\n"
        f"📊 RSI: {rsi:.1f}\n"
        f"📦 Lote sugerido: {lote_unidades:.4f} unidades\n\n"
        f"🎯 TAKE PROFIT: ${tp_precio:,.2f} (+${ganancia_estimada:.2f})\n"
        f"🛑 STOP LOSS: ${sl_precio:,.2f}\n\n"
        f"⚡ Ejecuta ahora en tu broker."
    )
    enviar_a_telegram(mensaje)

# --- 3. INTERFAZ DE LA APP ---
st.set_page_config(page_title="Terminal Trading VIP", layout="wide")
st_autorefresh(interval=60000, key="auto_pilot")

st.title("🤖 Lesthy_bot: Gestión de Lotes y Señales")

# Panel lateral para definir tu capital
st.sidebar.header("⚙️ Configuración de Riesgo")
mi_capital = st.sidebar.number_input("Capital por operación (USD):", min_value=10.0, value=100.0)

st.info(f"🛰️ Escaneando mercado. Riesgo configurado: *${mi_capital} USD* por señal.")

# Ejecución del escáner
activos = ["BTC-USD", "ETH-USD", "SOL-USD", "NVDA", "AAPL"]
for a in activos:
    df = yf.download(a, period="1d", interval="1m", progress=False)
    if not df.empty:
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
        
        # Disparador de señal (RSI < 30)
        if rsi < 30:
            precio_ahora = df['Close'].iloc[-1]
            generar_señal_maestra(a, precio_ahora, rsi, mi_capital)
            st.success(f"✅ Señal enviada para {a}")
