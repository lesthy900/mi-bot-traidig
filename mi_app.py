import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIGURACIÓN DE COMUNICACIÓN (ID: 1703425585) ---
def enviar_a_telegram(mensaje):
    token = "8553805048:AAFNtIznh3boHALXYxcMDFmFnnQkyTX4ado"
    chat_id = "1703425585"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except:
        pass

# --- 2. LÓGICA DE SEÑALES AUTOMÁTICAS ---
def ejecutar_escaneo_pro():
    # Lista de activos para buscar la mejor oportunidad
    activos = ["BTC-USD", "ETH-USD", "SOL-USD", "NVDA", "AAPL"]
    for a in activos:
        df = yf.download(a, period="1d", interval="1m", progress=False)
        if not df.empty:
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            
            # Cálculo de RSI para detectar la oportunidad
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
            
            # CRITERIO DE SEÑAL AUTOMÁTICA (RSI < 30)
            if rsi < 30:
                precio = df['Close'].iloc[-1]
                tp, sl = precio * 1.03, precio * 0.985
                msg = (
                    f"🔥 SEÑAL AUTOMÁTICA DETECTADA\n\n"
                    f"📈 Activo: {a}\n"
                    f"💰 Precio: ${precio:,.2f}\n"
                    f"🎯 TP (+3%): ${tp:,.2f}\n"
                    f"🛑 SL (-1.5%): ${sl:,.2f}"
                )
                enviar_a_telegram(msg)
                return [a, precio]
    return None

# --- 3. INTERFAZ Y AUTO-ARRANQUE ---
st.set_page_config(page_title="Lesthy_bot Auto-Pilot", layout="wide")
st_autorefresh(interval=60000, key="auto_pilot_refresh") # Escanea cada 1 minuto

# FUNCIÓN DE PRUEBA AUTOMÁTICA (Se ejecuta sola al abrir la app)
if 'inicio_confirmado' not in st.session_state:
    enviar_a_telegram("🤖 Lesthy_bot: Sistema iniciado y escaneando el mercado automáticamente...")
    st.session_state.inicio_confirmado = True

st.title("🛡️ Terminal Lesthy_bot: Modo Piloto Automático")

st.info("🛰️ El escáner está funcionando en segundo plano. Recibirás las señales directamente en tu Telegram.")

# Ejecución constante del escáner
resultado = ejecutar_escaneo_pro()
if resultado:
    st.success(f"✅ Señal enviada para {resultado[0]} automáticamente.")
else:
    st.write("🔎 Analizando mercado... No se requiere acción manual.")
