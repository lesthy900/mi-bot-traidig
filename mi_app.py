import streamlit as st
import yfinance as yf
import requests
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIGURACIÓN DEL MENSAJERO ---
def enviar_señal_completa(activo, precio, rsi):
    token = "8553805048:AAFNtIznh3boHALXYxcMDFmFnnQkyTX4ado"
    chat_id = "TU_ID_AQUÍ" # <--- ¡PON TU ID AQUÍ PARA RECIBIR LA SEÑAL!
    
    # Cálculos Automáticos de la Señal
    take_profit = precio * 1.03  # +3%
    stop_loss = precio * 0.985   # -1.5%
    
    mensaje = (
        f"🚀 *¡SEÑAL DE ALTA PROBABILIDAD!* 🚀\n\n"
        f"📈 Activo: {activo}\n"
        f"💰 Precio de Entrada: ${precio:,.2f}\n"
        f"📊 RSI actual: {rsi:.1f}\n\n"
        f"🎯 *TAKE PROFIT (+3%): ${take_profit:,.2f}*\n"
        f"🛑 *STOP LOSS (-1.5%): ${stop_loss:,.2f}*\n\n"
        f"⚡ Ejecuta con precaución."
    )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={mensaje}&parse_mode=Markdown"
    try: requests.get(url)
    except: pass

# --- 2. EL ESCÁNER AUTOMÁTICO ---
def ejecutar_escaneo():
    # Lista de los activos más líquidos para asegurar la mejor opción
    lista_activos = ["BTC-USD", "ETH-USD", "SOL-USD", "NVDA", "AAPL", "TSLA", "GC=F", "EURUSD=X"]
    
    for activo in lista_activos:
        df = yf.download(activo, period="1d", interval="1m", progress=False)
        if not df.empty:
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            
            # Cálculo de RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
            
            # Condición de "Mejor Opción": RSI bajo 28 (Sobreventa fuerte)
            if rsi < 28:
                precio_ahora = df['Close'].iloc[-1]
                enviar_señal_completa(activo, precio_ahora, rsi)
                return activo, precio_ahora

# --- 3. INTERFAZ DE STREAMLIT ---
st.set_page_config(page_title="Lesthy_bot VIP Signals", layout="wide")
st_autorefresh(interval=60000, key="auto_signals") # Escanea cada 1 minuto

st.title("🛡️ Terminal de Señales Automáticas Lesthy_bot")

if st.toggle("🛰️ Activar Escáner de Señales VIP", value=True):
    st.info("El bot está analizando el mercado global en busca de entradas con Profit/Stop Loss...")
    resultado = ejecutar_escaneo()
    if resultado:
        st.success(f"✅ Señal enviada para {resultado[0]} a las {pd.Timestamp.now()}")
else:
    st.warning("Escáner en pausa.")
