import streamlit as st
import app_futbol
import trading_beta1

def main():
    st.set_page_config(page_title="Fútbol y Trading", layout="wide")
    st.title("Análisis Deportivo y Trading")
    pagina = st.sidebar.selectbox('Selecciona la página', ['Fútbol', 'Trading'])

    if pagina == 'Fútbol':
        app_futbol.mostrar_app_futbol()
        st.stop()
    elif pagina == 'Trading':
        if hasattr(trading_beta1, 'mostrar_app_trading'):
            trading_beta1.mostrar_app_trading()
        else:
            st.info('La función de trading se encuentra en trading_beta1.py. Si quieres una interfaz visual, agrega una función mostrar_app_trading() en ese archivo.')

if __name__ == "__main__":
    main()
