# --- Funciones de detección de patrones ---
def detectar_hch(prices):
    # Simplificado: busca tres picos, el del medio más alto
    if len(prices) < 20:
        return False
    for i in range(5, len(prices)-5):
        left = prices[i-5:i]
        center = prices[i-2:i+3]
        right = prices[i+1:i+6]
        lmax = left.max().item() if hasattr(left.max(), 'item') else left.max()
        cmax = center.max().item() if hasattr(center.max(), 'item') else center.max()
        rmax = right.max().item() if hasattr(right.max(), 'item') else right.max()
        mean = prices.mean().item() if hasattr(prices.mean(), 'item') else prices.mean()
        if lmax < cmax and rmax < cmax:
            if abs(lmax - rmax) < 0.02 * mean:
                return True
    return False

def detectar_doble_techo(prices):
    # Busca dos máximos similares separados por un valle
    if len(prices) < 20:
        return False
    max1 = prices[:len(prices)//2].max().item() if hasattr(prices[:len(prices)//2].max(), 'item') else prices[:len(prices)//2].max()
    max2 = prices[len(prices)//2:].max().item() if hasattr(prices[len(prices)//2:].max(), 'item') else prices[len(prices)//2:].max()
    min_valle = prices[len(prices)//4:3*len(prices)//4].min().item() if hasattr(prices[len(prices)//4:3*len(prices)//4].min(), 'item') else prices[len(prices)//4:3*len(prices)//4].min()
    mean = prices.mean().item() if hasattr(prices.mean(), 'item') else prices.mean()
    if abs(max1 - max2) < 0.02 * mean and min_valle < max1 - 0.03 * mean:
        return True
    return False

def detectar_doble_suelo(prices):
    # Busca dos mínimos similares separados por un pico
    if len(prices) < 20:
        return False
    min1 = prices[:len(prices)//2].min().item() if hasattr(prices[:len(prices)//2].min(), 'item') else prices[:len(prices)//2].min()
    min2 = prices[len(prices)//2:].min().item() if hasattr(prices[len(prices)//2:].min(), 'item') else prices[len(prices)//2:].min()
    max_pico = prices[len(prices)//4:3*len(prices)//4].max().item() if hasattr(prices[len(prices)//4:3*len(prices)//4].max(), 'item') else prices[len(prices)//4:3*len(prices)//4].max()
    mean = prices.mean().item() if hasattr(prices.mean(), 'item') else prices.mean()
    if abs(min1 - min2) < 0.02 * mean and max_pico > min1 + 0.03 * mean:
        return True
    return False
import streamlit as st
import importlib.util
# --- Navegación entre páginas ---
pagina = st.sidebar.selectbox('Selecciona la página', ['Trading', 'Fútbol'])

if pagina == 'Fútbol':
    spec = importlib.util.spec_from_file_location('app_futbol', 'c:/Users/Admin/OneDrive/Escritorio/trading_beta 2/app_futbol.py')
    app_futbol = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app_futbol)
    app_futbol.mostrar_app_futbol()
    st.stop()
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import ta

import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import ta


# Fondo personalizado con imagen
st.markdown(
    """
    <style>
    .stApp {
        background-image: url('https://i.imgur.com/t6RNs7H.png');
        background-size: cover;
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title('Trading Plus')

# Parámetros de usuario
symbols = st.text_input('Símbolos (acciones o criptomonedas, separados por coma)', 'AAPL,MSFT,BTC-USD,ETH-USD')
st.caption('Ejemplo: AAPL, MSFT, BTC-USD, ETH-USD')
import datetime
today = datetime.date.today()
default_start = pd.to_datetime(f'{today.year}-01-01')
default_end = pd.to_datetime(today)
start_date = st.date_input('Fecha inicio', default_start)
end_date = st.date_input('Fecha fin', default_end)
ema_window = st.slider('Ventana EMA', 5, 50, 20)
rsi_period = st.slider('Periodo RSI', 5, 30, 14)

if st.button('Descargar y analizar'):
    for symbol in [s.strip().upper() for s in symbols.split(',') if s.strip()]:
        st.header(f'Análisis para {symbol}')
        data = yf.download(symbol, start=start_date, end=end_date)
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

        # Detectar patrones automáticamente
        precios = data['Close'].dropna()
        if detectar_hch(precios):
            st.warning('Patrón detectado: Hombro-Cabeza-Hombro')
        if detectar_doble_techo(precios):
            st.warning('Patrón detectado: Doble Techo')
        if detectar_doble_suelo(precios):
            st.warning('Patrón detectado: Doble Suelo')


        # Determinar la última señal
        ultima_compra = data['Senal_Compra'].last_valid_index()
        ultima_venta = data['Senal_Venta'].last_valid_index()
        if ultima_compra is not None and (ultima_venta is None or ultima_compra > ultima_venta):
            st.success('Última señal: COMPRAR')
        elif ultima_venta is not None and (ultima_compra is None or ultima_venta > ultima_compra):
            st.error('Última señal: VENDER')
        else:
            st.info('Sin señal clara de compra o venta reciente.')

        # Apartado de consejo
        consejo = ""
        close = data['Close'].dropna()
        if ultima_compra is not None and (ultima_venta is None or ultima_compra > ultima_venta):
            if len(close) > 1:
                pct_change = (close.iloc[-1] - close.iloc[0]) / close.iloc[0]
                if hasattr(pct_change, 'item'):
                    pct_change = pct_change.item()
                if pct_change > 0.05:
                    consejo = "La tendencia es alcista y la última señal es de compra. Considera comprar pronto, pero revisa otros factores antes de decidir."
                else:
                    consejo = "Hay señal de compra, pero la tendencia no es claramente alcista. Sé prudente y analiza más indicadores."
            else:
                consejo = "Señal de compra detectada, pero no hay suficiente información de tendencia."
        elif ultima_venta is not None and (ultima_compra is None or ultima_venta > ultima_compra):
            consejo = "La última señal es de venta. Considera esperar antes de comprar o evalúa vender si tienes posición."
        else:
            consejo = "No hay señales claras. Mejor esperar y observar el mercado."
        st.info(f"Consejo: {consejo}")

        # Detección de tendencia general
        close = data['Close'].dropna()
        if len(close) > 1:
            pct_change = (close.iloc[-1] - close.iloc[0]) / close.iloc[0]
            # Asegurarse de que pct_change sea escalar
            if hasattr(pct_change, 'item'):
                pct_change = pct_change.item()
            if pct_change > 0.05:
                st.success('Tendencia general: Alcista 📈')
            elif pct_change < -0.05:
                st.error('Tendencia general: Bajista 📉')
            else:
                st.info('Tendencia general: Lateral')
        st.write(data.tail())
        fig, ax = plt.subplots(figsize=(12,6))
        ax.plot(data['Close'], label='Precio', color='blue')
        ax.plot(data['EMA'], label=f'EMA {ema_window}', linestyle='--', color='orange')
        ax.scatter(data.index, data['Senal_Compra'], label='Compra', marker='^', color='green', alpha=1)
        ax.scatter(data.index, data['Senal_Venta'], label='Venta', marker='v', color='red', alpha=1)
        ax.set_title(f'Precio, EMA y Señales de trading ({symbol})')
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Precio')
        ax.legend()
        st.pyplot(fig)
