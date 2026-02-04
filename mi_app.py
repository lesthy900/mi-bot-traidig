import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
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

# --- 2. MOTOR DE APRENDIZAJE DIARIO ---
def calcular_niveles_optimos(activo):
    # Descargamos datos históricos para que el bot "estudie" el comportamiento
    # period="7d" permite aprender cómo se ha movido la divisa la última semana
    hist = yf.download(activo, period="7d", interval="15m", progress=False)
    if hist.empty: return None, None
    
    # Limpiar columnas
    hist.columns = [c[0] if isinstance(c, tuple) else c for c in hist.columns]
    
    # 1. Aprender la Volatilidad Real (ATR)
    high_low = hist['High'] - hist['Low']
    atr = high_low.rolling(14).mean().iloc[-1]
    
    # 2. Aprender la "Fuerza de Empuje" (Eficiencia)
    # Calculamos cuánto se mueve el precio en promedio antes de una corrección
    movimiento_promedio = (hist['High'] - hist['Low']).mean()
    
    # Configuramos el SL basado en la volatilidad actual (para que no te saque el ruido)
    sl_dinamico = atr * 1.8 
    
    # Configuramos el TP basado en el comportamiento de la semana
    # Si el mercado está muy activo, el TP es más largo; si no, más corto.
    tp_dinamico = movimiento_promedio * 2.5 
    
    return sl_dinamico, tp_dinamico

# --- 3. GENERACIÓN DE SEÑAL MEJORADA ---
def generar_alerta_ia(activo, precio, sl_dist, tp_dist, rsi):
    tp_final = precio + tp_dist
    sl_final = precio - sl_dist
    
    # Ratio Riesgo:Beneficio real
    ratio = tp_dist / sl_dist
    
    mensaje = (
        f"🤖 **LESTHY_BOT: APRENDIZAJE COMPLETADO**\n\n"
        f"📈 **Activo:** {activo}\n"
        f"🎯 **PUNTO DE ENTRADA:** {precio:,.4f}\n"
        f"📊 **RSI Actual:** {rsi:.2f}\n\n"
        f"🧠 **NIVELES OPTIMIZADOS (Basado en 7 días):**\n"
        f"✅ **Take Profit:** {tp_final:,.4f} (+{tp_dist:,.4f})\n"
        f"❌ **Stop Loss:** {sl_final:,.4f} (-{sl_dist:,.4f})\n"
        f"⚖️ **Ratio R:B:** 1:{ratio:.2f}\n\n"
        f"📢 *El bot ha ajustado estos niveles según el comportamiento reciente del mercado.*"
    )
    enviar_a_telegram(mensaje)

# --- 4. INTERFAZ ---
st.set_page_config(page_title="Lesthy_bot Intelligence", layout="wide")
st_autorefresh(interval=60000, key="bot_refresh")

st.title("🛡️ Lesthy_bot: Sistema de Aprendizaje de Divisas")

activos_interes = st.multiselect(
    "Selecciona Divisas para que el bot analice:",
    ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "BTC-USD", "GC=F"],
    default=["EURUSD=X", "GBPUSD=X", "GC=F"]
)

if st.toggle("Activar Escáner Inteligente", value=True):
    st.write("🔎 **Estudiando comportamientos y buscando entradas...**")
    
    for a in activos_interes:
        # El bot "estudia" el comportamiento antes de analizar el precio actual
        sl_optimo, tp_optimo = calcular_niveles_optimos(a)
        
        # Analizar precio actual (1 minuto)
        df_now = yf.download(a, period="1d", interval="1m", progress=False)
        if not df_now.empty and sl_optimo:
            df_now.columns = [c[0] if isinstance(c, tuple) else c for c in df_now.columns]
            
            # Cálculo de RSI
            delta = df_now['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
            
            precio_actual = df_now['Close'].iloc[-1]
            
            # Condición de entrada (Ejemplo: Sobreventa + Aprendizaje de Niveles)
            if rsi < 32:
                generar_alerta_ia(a, precio_actual, sl_optimo, tp_optimo, rsi)
                st.success(f"🚀 Señal optimizada enviada para {a}")
            
            # Mostrar datos en la App
            st.write(f"**{a}**: Precio: {precio_actual:,.4f} | RSI: {rsi:.2f}")
