import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIGURACIÓN DE LESTHY_BOT (ID VERIFICADO: 1703425585) ---
def enviar_señal_completa(activo, precio, rsi):
    token = "8553805048:AAFNtIznh3boHALXYxcMDFmFnnQkyTX4ado"
    chat_id = "1703425585" # <--- Tu ID ya está configurado aquí
    
    # Cálculo de la Modalidad de Salida (Profit y Stop)
    tp = precio * 1.03  # +3%
    sl = precio * 0.985 # -1.5%
    
    mensaje = (
        f"🚀 ¡SEÑAL DETECTADA POR LESTHY_BOT! 🚀\n\n"
        f"📈 Activo: {activo}\n"
        f"💰 Precio Entrada: ${precio:,.2f}\n"
        f"📊 RSI: {rsi:.1f}\n\n"
        f"🎯 TAKE PROFIT (+3.0%): ${tp:,.2f}\n"
        f"🛑 STOP LOSS (-1.5%): ${sl:,.2f}\n\n"
        f"⚡ Señal generada automáticamente."
    )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
    
    try:
        requests.post(url, data=payload)
    except:
        pass

# --- 2. EL ESCÁNER AUTOMÁTICO (LA MEJOR OPCIÓN) ---
def ejecutar_escaneo():
    # Lista de activos para buscar la mejor oportunidad
    activos = ["BTC-USD", "ETH-USD", "SOL-USD", "NVDA", "AAPL", "TSLA"]
    for a in activos:
        df = yf.download(a, period="1d", interval="1m", progress=False)
        if not df.empty:
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            
            # Cálculo de RSI para detectar la oportunidad
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
            
            # Si el RSI es bajo (mejor opción), envía la señal
            if rsi < 30:
                precio_actual = df['Close'].iloc[-1]
                enviar_señal_completa(a, precio_actual, rsi)
                return [a, precio_actual]
    return None

# --- 3. INTERFAZ DE LA APLICACIÓN ---
st.set_page_config(page_title="Terminal Lesthy_bot Pro", layout="wide")
st_autorefresh(interval=60000, key="f5_auto") # Escanea cada minuto

st.title("🛡️ Terminal de Señales Automáticas Lesthy_bot")

if st.toggle("🛰️ Activar Escáner de Señales VIP", value=True):
    st.info("Analizando el mercado global en busca de la mejor opción con TP/SL...")
    resultado = ejecutar_escaneo()
    
    if resultado:
        st.success(f"✅ Señal enviada para {resultado[0]} a las {pd.Timestamp.now()}")
    else:
        st.write("🔎 Buscando oportunidades... El mercado está estable.")

# Botón de prueba manual para confirmar conexión inmediata
if st.button("🔔 Enviar prueba a mi Telegram ahora"):
    enviar_señal_completa("PRUEBA", 100.0, 25.0)
    st.write("Mensaje de prueba enviado. ¡Revisa tu Telegram!")
