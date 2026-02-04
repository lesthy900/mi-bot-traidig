import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# 1. CONFIGURACIÓN PROFESIONAL
st.set_page_config(page_title="Terminal Pro Trading", layout="wide")
st_autorefresh(interval=30000, key="pro_refresh")

# Estilo para una interfaz oscura tipo terminal
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Terminal de Trading Inteligente")

# --- PANEL LATERAL (Gestión de Cartera) ---
st.sidebar.header("🕹️ Centro de Control")
ticker = st.sidebar.text_input("Activo (Ej: AAPL, BTC-USD)", value="AAPL")
capital_inicial = st.sidebar.number_input("Capital Simulado ($)", value=1000.0)

if 'balance' not in st.session_state:
    st.session_state.balance = capital_inicial

# --- PROCESAMIENTO DE DATOS ---
data = yf.download(ticker, period="1d", interval="1m")

if not data.empty:
    # Limpieza de columnas para compatibilidad
    data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
    
    # Cálculo del RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    data['RSI'] = 100 - (100 / (1 + (gain/loss)))
    
    precio_actual = data['Close'].iloc[-1]
    ultimo_rsi = data['RSI'].iloc[-1]

    # --- IA Y PREDICCIÓN (Lógica de Medias Móviles) ---
    ma20 = data['Close'].rolling(window=20).mean().iloc[-1]
    tendencia = "ALZA 📈" if precio_actual > ma20 else "BAJA 📉"
    probabilidad = "Alta" if (ultimo_rsi < 40 and tendencia == "ALZA 📈") else "Moderada"

    # --- MÉTRICAS EN TIEMPO REAL ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Precio Actual", f"${precio_actual:.2f}")
    m2.metric("RSI (14)", f"{ultimo_rsi:.1f}")
    m3.metric("Tendencia IA", tendencia)
    m4.metric("Probabilidad", probabilidad)

    # --- NOTIFICACIONES Y ALERTAS ---
    if ultimo_rsi < 30:
        st.warning(f"⚠️ ¡ALERTA DE COMPRA! RSI en {ultimo_rsi:.1f} (Sobrevendido)")
    elif ultimo_rsi > 70:
        st.error(f"⚠️ ¡ALERTA DE VENTA! RSI en {ultimo_rsi:.1f} (Sobrecomprado)")

    # --- GRÁFICO PROFESIONAL CORREGIDO ---
    st.subheader(f"Análisis Técnico: {ticker}")
    
    # Aquí corregimos el error de la foto 384b077a
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    fig.subplots_adjust(hspace=0.3) # Ajuste manual de espacio para evitar el AttributeError
    
    # Gráfica de Precios
    ax1.plot(data.index, data['Close'], color='#58a6ff', label="Precio")
    ax1.set_title("Evolución del Precio (1 min)")
    ax1.legend()
    ax1.grid(alpha=0.2)
    
    # Gráfica de RSI
    ax2.plot(data.index, data['RSI'], color='#f0883e', label="RSI")
    ax2.axhline(70, color='red', linestyle='--', alpha=0.5)
    ax2.axhline(30, color='green', linestyle='--', alpha=0.5)
    ax2.set_ylim(0, 100)
    ax2.set_title("Indicador RSI")
    ax2.legend()
    
    st.pyplot(fig)
    
    st.write(f"Última actualización: {pd.Timestamp.now().strftime('%H:%M:%S')}")

else:
    st.info("Buscando datos en vivo... Asegúrate de que el mercado esté abierto o usa un Ticker válido.")
