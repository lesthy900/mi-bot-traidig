import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh # Nueva librería

# Configuración de la página
st.set_page_config(page_title="Bot en Tiempo Real", layout="wide")

# ESTA LÍNEA HACE LA MAGIA: Se actualiza cada 30000 milisegundos (30 segundos)
st_autorefresh(interval=30000, key="datarefresh")

st.title("🤖 Bot de Trading en Tiempo Real (Auto-update)")
st.caption("La página se actualiza automáticamente cada 30 segundos")

# Panel lateral
st.sidebar.header("Configuración")
ticker = st.sidebar.text_input("Símbolo (Ticker)", value="AAPL")
inicio = st.sidebar.date_input("Fecha inicio", value=pd.to_datetime("2024-01-01"))

# Botón para activar/desactivar el modo automático
if st.sidebar.checkbox("Ejecutar Análisis", value=True):
    # Descarga los datos más recientes hasta el segundo actual
    data = yf.download(ticker, start=inicio)
    
    if not data.empty:
        data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
        
        # Cálculo del RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        data['RSI'] = 100 - (100 / (1 + (gain/loss)))

        # Lógica de señales
        capital = 10000
        position = 0
        buy_signals = []
        sell_signals = []

        for i in range(len(data)):
            rsi = data['RSI'].iloc[i]
            precio = data['Close'].iloc[i]
            if rsi < 30 and position == 0:
                position = capital / precio
                capital = 0
                buy_signals.append(precio)
                sell_signals.append(np.nan)
            elif rsi > 70 and position > 0:
                capital = position * precio
                position = 0
                buy_signals.append(np.nan)
                sell_signals.append(precio)
            else:
                buy_signals.append(np.nan)
                sell_signals.append(np.nan)

        data['Buy_Sig'] = buy_signals
        data['Sell_Sig'] = sell_signals

        # Métricas en vivo
        ultimo_precio = data['Close'].iloc[-1]
        final_val = capital if capital > 0 else position * ultimo_precio
        
        col1, col2 = st.columns(2)
        col1.metric(f"Precio {ticker}", f"${ultimo_precio:.2f}", f"{data['Close'].diff().iloc[-1]:.2f}")
        col2.metric("Ganancia Estimada", f"${final_val - 10000:.2f}")

        # Gráfico
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(data.index, data['Close'], alpha=0.5, label="Precio")
        ax.scatter(data.index, data['Buy_Sig'], color='green', marker='^', s=80, label="COMPRA")
        ax.scatter(data.index, data['Sell_Sig'], color='red', marker='v', s=80, label="VENTA")
        ax.legend()
        st.pyplot(fig)
        
        st.write(f"Última actualización: {pd.Timestamp.now().strftime('%H:%M:%S')}")
    else:
        st.error("Esperando datos...")