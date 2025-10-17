import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import ta
import streamlit as st

# 1. Descargar datos históricos
data = yf.download("AAPL", start="2024-01-01", end="2024-12-31")

# Asegurarse de que close_prices sea una Serie 1D
close_prices = data["Close"].squeeze()

# 2. Calcular indicadores técnicos
data["RSI"] = ta.momentum.RSIIndicator(close_prices).rsi()
macd = ta.trend.MACD(close_prices)
data["MACD"] = macd.macd()
data["Signal"] = macd.macd_signal()
data["EMA"] = ta.trend.EMAIndicator(close_prices, window=20).ema_indicator()

# 3. Mostrar primeras filas
print(data.head())

# 4. Graficar precios + EMA
plt.figure(figsize=(12,6))
plt.plot(close_prices, label="Precio")
plt.plot(data["EMA"], label="EMA 20", linestyle="--")
plt.title("Precio y EMA")
plt.legend()
plt.show()

# 5. Inicializar columnas para señales
data["Senal_Compra"] = None
data["Senal_Venta"] = None

# 6. Lógica de decisión
for i in range(1, len(data)):
    # Señal de compra: RSI < 30 y cruce MACD arriba de Signal
    if (
        data["RSI"].iloc[i] < 30 and
        data["MACD"].iloc[i] > data["Signal"].iloc[i] and
        data["MACD"].iloc[i-1] <= data["Signal"].iloc[i-1]
    ):
        data["Senal_Compra"].iloc[i] = data["Close"].iloc[i]
    # Señal de venta: RSI > 70 y cruce MACD abajo de Signal
    elif (
        data["RSI"].iloc[i] > 70 and
        data["MACD"].iloc[i] < data["Signal"].iloc[i] and
        data["MACD"].iloc[i-1] >= data["Signal"].iloc[i-1]
    ):
        data["Senal_Venta"].iloc[i] = data["Close"].iloc[i]

# 7. Graficar resultados con señales
plt.figure(figsize=(12,6))
plt.plot(data["Close"], label="Precio", color="blue")
plt.plot(data["EMA"], label="EMA 20", linestyle="--", color="orange")
plt.scatter(data.index, data["Senal_Compra"], label="Compra", marker="^", color="green", alpha=1)
plt.scatter(data.index, data["Senal_Venta"], label="Venta", marker="v", color="red", alpha=1)
plt.title("Precio, EMA y Señales de trading")
plt.xlabel("Fecha")
plt.ylabel("Precio")
plt.legend()
plt.show()

def mostrar_app_trading():
    st.title('Trading Plus')
    symbols = st.text_input('Símbolos (acciones o criptomonedas, separados por coma)', 'AAPL,MSFT,BTC-USD,ETH-USD')
    st.caption('Ejemplo: AAPL, MSFT, BTC-USD, ETH-USD')
    import datetime
    today = datetime.date.today()
    default_start = st.date_input('Fecha inicio', datetime.date(today.year, 1, 1))
    default_end = st.date_input('Fecha fin', today)
    ema_window = st.slider('Ventana EMA', 5, 50, 20)
    rsi_period = st.slider('Periodo RSI', 5, 30, 14)

    if st.button('Descargar y analizar'):
        import yfinance as yf
        import pandas as pd
        import matplotlib.pyplot as plt
        import ta
        for symbol in [s.strip().upper() for s in symbols.split(',') if s.strip()]:
            st.header(f'Análisis para {symbol}')
            data = yf.download(symbol, start=default_start, end=default_end)
            close_prices = data['Close'].squeeze()
            data['RSI'] = ta.momentum.RSIIndicator(close_prices, window=rsi_period).rsi()
            macd = ta.trend.MACD(close_prices)
            data['MACD'] = macd.macd()
            data['Signal'] = macd.macd_signal()
            data['EMA'] = ta.trend.EMAIndicator(close_prices, window=ema_window).ema_indicator()
            data['Senal_Compra'] = None
            data['Senal_Venta'] = None
            for i in range(1, len(data)):
                if (
                    data['RSI'].iloc[i] < 30 and
                    data['MACD'].iloc[i] > data['Signal'].iloc[i] and
                    data['MACD'].iloc[i-1] <= data['Signal'].iloc[i-1]
                ):
                    data['Senal_Compra'].iloc[i] = data['Close'].iloc[i]
                elif (
                    data['RSI'].iloc[i] > 70 and
                    data['MACD'].iloc[i] < data['Signal'].iloc[i] and
                    data['MACD'].iloc[i-1] >= data['Signal'].iloc[i-1]
                ):
                    data['Senal_Venta'].iloc[i] = data['Close'].iloc[i]
            st.dataframe(data)
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(data.index, data['Close'], label='Precio')
            ax.plot(data.index, data['EMA'], label='EMA')
            ax.scatter(data.index, data['Senal_Compra'], color='green', label='Compra', marker='^')
            ax.scatter(data.index, data['Senal_Venta'], color='red', label='Venta', marker='v')
            ax.legend()
            st.pyplot(fig)

