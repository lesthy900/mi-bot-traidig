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

# --- 2. GENERACIÓN DE SEÑAL CON ESPECIFICACIONES ---
def generar_alerta_pro(activo, precio, rsi, capital):
    # Diferenciales técnicos (especificaciones de salida)
    pts_tp = precio * 0.03   # Ejemplo para +3%
    pts_sl = precio * 0.015  # Ejemplo para -1.5%
    
    tp_final = precio + pts_tp
    sl_final = precio - pts_sl
    lote = capital / precio  # Lote basado en tu riesgo configurado
    
    mensaje = (
        f"🔥 SEÑAL CON ESPECIFICACIONES\n\n"
        f"📈 Activo: {activo}\n"
        f"💰 PUNTO DE ENTRADA: {precio:,.4f}\n"
        f"📦 Lote sugerido: {lote:.4f}\n\n"
        f"📊 ESPECIFICACIONES DE SALIDA:\n"
        f"✅ Take Profit: +{pts_tp:,.4f} (Objetivo: {tp_final:,.4f})\n"
        f"❌ Stop Loss: -{pts_sl:,.4f} (Límite: {sl_final:,.4f})\n\n"
        f"⚡ Acción requerida inmediata."
    )
    enviar_a_telegram(mensaje)

# --- 3. INTERFAZ Y ESCÁNER ---
st.set_page_config(page_title="Lesthy_bot Terminal Pro", layout="wide")
st_autorefresh(interval=60000, key="pilot")

st.title("🛡️ Lesthy_bot: Señales y Gestión de Lotes")

# Interruptor de activación
estado = st.toggle("🛰️ Activar Escáner de Señales VIP", value=True)
capital_op = st.sidebar.number_input("Capital por operación (USD):", min_value=10.0, value=100.0)

if estado:
    st.info("🔎 Analizando mercado en tiempo real...")
    activos = ["BTC-USD", "ETH-USD", "SOL-USD", "GC=F"] # Incluye Oro (GC=F) como en tus capturas
    
    for a in activos:
        df = yf.download(a, period="1d", interval="1m", progress=False)
        if not df.empty:
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            
            # Cálculo de RSI para entrada
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
            
            if rsi < 30: # Punto de sobreventa detectado
                generar_alerta_pro(a, df['Close'].iloc[-1], rsi, capital_op)
                st.success(f"✅ Señal enviada para {a}")
else:
    st.warning("⚠️ Escáner desactivado manualmente.")
