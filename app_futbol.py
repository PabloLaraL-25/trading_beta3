import streamlit as st
import requests
import pandas as pd

def mostrar_app_futbol():
    import pandas as pd
    st.subheader('Scraping de partidos desde la web de Liga MX')
    url_tabla = st.text_input('URL de la tabla de clasificación (ejemplo: https://www.ligamx.net/cancha/tablas/tablaGeneralClasificacion/sp/544f5bc44c6944)', value='https://www.ligamx.net/cancha/tablas/tablaGeneralClasificacion/sp/544f5bc44c6944')
    if 'tablas_ligamx' not in st.session_state:
        st.session_state['tablas_ligamx'] = None
    if st.button('Obtener partidos de la web') or st.session_state['tablas_ligamx'] is not None:
        if st.session_state['tablas_ligamx'] is None:
            try:
                tablas = pd.read_html(url_tabla)
                st.session_state['tablas_ligamx'] = tablas
            except Exception as e:
                st.error(f'Error al leer la tabla: {e}')
                return
        tablas = st.session_state['tablas_ligamx']
        st.success('Tabla(s) encontrada(s) en la página:')
        equipos_global = []
        tablas_validas = []
        jugadores_global = []
        tablas_jugadores = []
        # Diccionario de normalización de nombres de equipos y jugadores
        normalizar_equipo = {
            'America': 'Club América',
            'Atlético de San Luis': 'Atlético San Luis',
            'Pumas': 'Pumas UNAM',
            'Cruz Azul': 'Cruz Azul',
            'Guadalajara': 'Chivas',
            'Toluca': 'Toluca',
            'Monterrey': 'Rayados',
            'Tigres': 'Tigres UANL',
            'Santos': 'Santos Laguna',
            'León': 'León',
            'Puebla': 'Puebla',
            'Mazatlán': 'Mazatlán',
            'Juárez': 'FC Juárez',
            'Querétaro': 'Querétaro',
            'Tijuana': 'Xolos',
            'Necaxa': 'Necaxa',
            # Agrega más equivalencias si lo deseas
        }
        normalizar_jugador = {
            # Puedes agregar equivalencias de nombres de jugadores si lo deseas
        }

        import unicodedata
        def limpiar_nombre(nombre):
            if not isinstance(nombre, str):
                return nombre
            nombre = unicodedata.normalize('NFKD', nombre)
            nombre = nombre.encode('ascii', 'ignore').decode('ascii')
            return nombre.lower().replace('fc ', '').replace('club ', '').replace('unam', 'pumas unam').replace('america', 'club america').replace('san luis', 'atletico san luis').strip()

        def normaliza_nombre(nombre, dicc):
            nombre_limpio = limpiar_nombre(nombre)
            for k, v in dicc.items():
                if limpiar_nombre(k) == nombre_limpio:
                    return v
            return nombre

        for i, tabla in enumerate(tablas):
            if isinstance(tabla.columns, pd.MultiIndex):
                tabla.columns = [c[-1] if isinstance(c, tuple) else c for c in tabla.columns]
            tabla = tabla.rename(columns={
                'Club': 'Equipo', 'Visitante': 'Equipo', 'Local': 'Equipo',
                'PTS': 'Puntos', 'pts': 'Puntos', 'Puntos': 'Puntos',
                'Dif': 'Diferencia', 'dif': 'Diferencia', 'DIF': 'Diferencia',
                'Jugador': 'Jugador', 'Nombre': 'Jugador', 'Player': 'Jugador',
                'Goles': 'Goles', 'GF': 'Goles', 'Goals': 'Goles',
                'Equipo': 'Equipo', 'Team': 'Equipo'
            })
            tabla = tabla.loc[:, ~tabla.columns.duplicated()]
            # Normalizar nombres de equipos
            if 'Equipo' in tabla.columns:
                tabla['Equipo'] = tabla['Equipo'].apply(lambda x: normaliza_nombre(x, normalizar_equipo))
            # Normalizar nombres de jugadores
            if 'Jugador' in tabla.columns:
                tabla['Jugador'] = tabla['Jugador'].apply(lambda x: normaliza_nombre(x, normalizar_jugador))
            st.write(f'Tabla {i+1}:')
            st.dataframe(tabla)
            cols = [str(c).lower() if isinstance(c, str) else '' for c in tabla.columns]
            # Detectar tabla de equipos
            if 'equipo' in cols and 'puntos' in cols:
                equipos = tabla['Equipo'].astype(str).tolist()
                equipos_global.extend(equipos)
                tablas_validas.append((i, tabla))
            # Detectar tabla de jugadores
            if 'jugador' in cols and 'goles' in cols:
                jugadores = tabla['Jugador'].astype(str).tolist()
                jugadores_global.extend(jugadores)
                tablas_jugadores.append((i, tabla))

        # Opción: modo de entrada (automático desde tabla o manual)
        modo_entrada = st.radio('Modo de entrada', ['Auto (leer tabla web)', 'Manual (ingresar estadísticas)'], index=0)

        # Modo manual: formularios para ingresar estadísticas de dos equipos
        if modo_entrada == 'Manual':
            st.markdown('### Entrada manual de estadísticas')
            with st.form('manual_form'):
                col1, col2 = st.columns(2)
                with col1:
                    m_equipo1 = st.text_input('Equipo 1', value='Equipo A')
                    m_puntos1 = st.number_input('Puntos (Equipo 1)', min_value=0, value=0)
                    m_dif1 = st.number_input('Diferencia de goles (Equipo 1)', value=0)
                    m_gf1 = st.number_input('Goles a favor (Equipo 1)', min_value=0, value=0)
                    m_gc1 = st.number_input('Goles en contra (Equipo 1)', min_value=0, value=0)
                    m_gan1 = st.number_input('Ganados (Equipo 1)', min_value=0, value=0)
                    m_per1 = st.number_input('Perdidos (Equipo 1)', min_value=0, value=0)
                    m_sb1 = st.number_input('Saques de banda (Equipo 1)', min_value=0, value=0)
                with col2:
                    m_equipo2 = st.text_input('Equipo 2', value='Equipo B')
                    m_puntos2 = st.number_input('Puntos (Equipo 2)', min_value=0, value=0)
                    m_dif2 = st.number_input('Diferencia de goles (Equipo 2)', value=0)
                    m_gf2 = st.number_input('Goles a favor (Equipo 2)', min_value=0, value=0)
                    m_gc2 = st.number_input('Goles en contra (Equipo 2)', min_value=0, value=0)
                    m_gan2 = st.number_input('Ganados (Equipo 2)', min_value=0, value=0)
                    m_per2 = st.number_input('Perdidos (Equipo 2)', min_value=0, value=0)
                    m_sb2 = st.number_input('Saques de banda (Equipo 2)', min_value=0, value=0)
                enviar = st.form_submit_button('Analizar manualmente')
            if enviar:
                # Construir comparativa y score similar al automático
                st.markdown(f"""
                ### Comparativa (Manual)
                | Equipo | Puntos | Dif. Goles | Goles a favor | Goles en contra | Ganados | Perdidos | Saques de banda |
                |--------|--------|------------|---------------|-----------------|---------|----------|-----------------|
                | {m_equipo1} | {m_puntos1} | {m_dif1} | {m_gf1} | {m_gc1} | {m_gan1} | {m_per1} | {m_sb1} |
                | {m_equipo2} | {m_puntos2} | {m_dif2} | {m_gf2} | {m_gc2} | {m_gan2} | {m_per2} | {m_sb2} |
                """)

                score = 0
                total_score = 6.0
                if m_puntos1 > m_puntos2:
                    score += 2
                elif m_puntos2 > m_puntos1:
                    score -= 2
                if m_dif1 > m_dif2:
                    score += 1
                elif m_dif2 > m_dif1:
                    score -= 1
                if m_gf1 > m_gf2:
                    score += 0.5
                elif m_gf2 > m_gf1:
                    score -= 0.5
                if m_gan1 > m_gan2:
                    score += 0.5
                elif m_gan2 > m_gan1:
                    score -= 0.5
                if m_per1 < m_per2:
                    score += 0.5
                elif m_per2 < m_per1:
                    score -= 0.5
                # incluir saques de banda como indicador adicional (más saques -> más ataque)
                if m_sb1 > m_sb2:
                    score += 0.5
                elif m_sb2 > m_sb1:
                    score -= 0.5

                prob1 = max(0, min(100, round(50 + (score/total_score)*50, 1)))
                prob2 = 100 - prob1
                if score > 0:
                    st.success(f"{m_equipo1} tiene mejores estadísticas. Probabilidad: {m_equipo1} ({prob1}%) vs {m_equipo2} ({prob2}%)")
                elif score < 0:
                    st.success(f"{m_equipo2} tiene mejores estadísticas. Probabilidad: {m_equipo2} ({prob2}%) vs {m_equipo1} ({prob1}%)")
                else:
                    st.warning(f'El partido está muy parejo. Probabilidad: {m_equipo1} ({prob1}%) vs {m_equipo2} ({prob2}%)')

            # Si el usuario elige manual, no mostrar la UI automática
            return
        if equipos_global:
            equipo1 = st.selectbox('Equipo 1 (todas las tablas)', equipos_global, key='eq1_global')
            equipo2 = st.selectbox('Equipo 2 (todas las tablas)', equipos_global, key='eq2_global')
            if st.button('Analizar enfrentamiento', key='btn_global'):
                fila1, fila2 = None, None
                for _, tabla in tablas_validas:
                    if fila1 is None:
                        f1 = tabla[tabla['Equipo'] == equipo1]
                        if not f1.empty:
                            fila1 = f1
                    if fila2 is None:
                        f2 = tabla[tabla['Equipo'] == equipo2]
                        if not f2.empty:
                            fila2 = f2
                if fila1 is not None and fila2 is not None:
                    def get_val(fila, colnames, default=0):
                        # busca varias variantes y devuelve un número cuando es posible
                        for c in colnames:
                            if c in fila.columns:
                                val = fila[c].values[0]
                                try:
                                    # convertir a número si es posible
                                    if pd.isna(val):
                                        return default
                                    if isinstance(val, str):
                                        valn = val.replace(',', '').strip()
                                        return float(valn) if ('.' in valn) else int(valn)
                                    return float(val)
                                except Exception:
                                    return default
                        return default

                    puntos1 = get_val(fila1, ['Puntos', 'PTS', 'pts'])
                    puntos2 = get_val(fila2, ['Puntos', 'PTS', 'pts'])
                    dif1 = get_val(fila1, ['Diferencia', 'Dif', 'DIF'])
                    dif2 = get_val(fila2, ['Diferencia', 'Dif', 'DIF'])
                    gf1 = get_val(fila1, ['Goles', 'GF', 'Goles a favor', 'Goles Favor', 'GFavor'])
                    gf2 = get_val(fila2, ['Goles', 'GF', 'Goles a favor', 'Goles Favor', 'GFavor'])
                    gc1 = get_val(fila1, ['GC', 'Goles en contra', 'Goles Contra', 'GContra'])
                    gc2 = get_val(fila2, ['GC', 'Goles en contra', 'Goles Contra', 'GContra'])
                    gan1 = get_val(fila1, ['JG', 'G', 'Ganados', 'PG', 'Partidos Ganados'])
                    gan2 = get_val(fila2, ['JG', 'G', 'Ganados', 'PG', 'Partidos Ganados'])
                    per1 = get_val(fila1, ['JP', 'P', 'Perdidos', 'PP', 'Partidos Perdidos'])
                    per2 = get_val(fila2, ['JP', 'P', 'Perdidos', 'PP', 'Partidos Perdidos'])

                    st.markdown(f"""
                    ### Comparativa
                    | Equipo | Puntos | Dif. Goles | Goles a favor | Goles en contra | Ganados | Perdidos |
                    |--------|--------|------------|---------------|-----------------|---------|----------|
                    | {equipo1} | {puntos1} | {dif1} | {gf1} | {gc1} | {gan1} | {per1} |
                    | {equipo2} | {puntos2} | {dif2} | {gf2} | {gc2} | {gan2} | {per2} |
                    """)

                    score = 0
                    total_score = 5.0  # Suma máxima absoluta de los criterios
                    if puntos1 > puntos2:
                        score += 2
                    elif puntos2 > puntos1:
                        score -= 2
                    if dif1 > dif2:
                        score += 1
                    elif dif2 > dif1:
                        score -= 1
                    if gf1 > gf2:
                        score += 0.5
                    elif gf2 > gf1:
                        score -= 0.5
                    if gan1 > gan2:
                        score += 0.5
                    elif gan2 > gan1:
                        score -= 0.5
                    if per1 < per2:
                        score += 0.5
                    elif per2 < per1:
                        score -= 0.5

                    # Calcular porcentaje de probabilidad
                    prob1 = max(0, min(100, round(50 + (score/total_score)*50, 1)))
                    prob2 = 100 - prob1

                    if score > 0:
                        st.success(f"{equipo1} tiene mejores estadísticas globales. Probabilidad de ganar: {equipo1} ({prob1}%) vs {equipo2} ({prob2}%)")
                    elif score < 0:
                        st.success(f"{equipo2} tiene mejores estadísticas globales. Probabilidad de ganar: {equipo2} ({prob2}%) vs {equipo1} ({prob1}%)")
                    else:
                        st.warning(f'El partido está muy parejo según los datos analizados. Probabilidad: {equipo1} ({prob1}%) vs {equipo2} ({prob2}%)')

        # Análisis de jugadores si hay tablas de jugadores
        if jugadores_global:
            jugador1 = st.selectbox('Jugador 1', jugadores_global, key='jug1_global')
            jugador2 = st.selectbox('Jugador 2', jugadores_global, key='jug2_global')
            if st.button('Comparar jugadores', key='btn_jugadores'):
                fila_j1, fila_j2 = None, None
                for _, tabla in tablas_jugadores:
                    if fila_j1 is None:
                        f1 = tabla[tabla['Jugador'] == jugador1]
                        if not f1.empty:
                            fila_j1 = f1
                    if fila_j2 is None:
                        f2 = tabla[tabla['Jugador'] == jugador2]
                        if not f2.empty:
                            fila_j2 = f2
                if fila_j1 is not None and fila_j2 is not None:
                    def get_val_j(fila, colnames, default=0):
                        for c in colnames:
                            if c in fila.columns:
                                return fila[c].values[0]
                        return default
                    goles1 = get_val_j(fila_j1, ['Goles'])
                    goles2 = get_val_j(fila_j2, ['Goles'])
                    equipo1 = get_val_j(fila_j1, ['Equipo'])
                    equipo2 = get_val_j(fila_j2, ['Equipo'])
                    pj1 = get_val_j(fila_j1, ['PJ', 'Partidos Jugados', 'J'])
                    pj2 = get_val_j(fila_j2, ['PJ', 'Partidos Jugados', 'J'])

                    st.markdown(f"""
                    ### Comparativa de Jugadores
                    | Jugador | Equipo | Goles | Partidos Jugados |
                    |---------|--------|-------|------------------|
                    | {jugador1} | {equipo1} | {goles1} | {pj1} |
                    | {jugador2} | {equipo2} | {goles2} | {pj2} |
                    """)

                    if goles1 > goles2:
                        st.success(f"{jugador1} ha anotado más goles que {jugador2}.")
                    elif goles2 > goles1:
                        st.success(f"{jugador2} ha anotado más goles que {jugador1}.")
                    else:
                        st.info('Ambos jugadores tienen la misma cantidad de goles.')
    st.title('Apuestas Deportivas - Liga MX')
    st.markdown('''Esta página muestra los últimos partidos jugados en la Liga MX usando datos reales de la API-Football.''')

    season = st.selectbox('Temporada', ['2023', '2024', '2025'])
    jornada = st.number_input('Jornada (1-17)', min_value=1, max_value=17, value=1, step=1)
    API_KEY = st.text_input('API Key de API-Football', type='password')

    if API_KEY:
        if st.button('Buscar partidos de la jornada seleccionada'):
            url = f"https://v3.football.api-sports.io/fixtures?league=262&season={season}&round=Regular%20Season%20-%20{int(jornada)}"
            headers = {"x-apisports-key": API_KEY}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                partidos = data.get("response", [])
                if partidos:
                    st.subheader(f'Partidos de la Jornada {jornada} en Liga MX ({season})')
                    for match in partidos:
                        fecha = match["fixture"]["date"][:10]
                        home = match["teams"]["home"]["name"]
                        away = match["teams"]["away"]["name"]
                        score = match["goals"]["home"], match["goals"]["away"]
                        st.write(f"{fecha}: {home} {score[0]} - {score[1]} {away}")
                else:
                    st.warning("La API respondió correctamente pero no hay partidos para la jornada seleccionada. Esto puede deberse a que tu API key no tiene acceso a la Liga MX o a partidos históricos. Prueba con otra liga (por ejemplo, Premier League) o considera adquirir el plan premium de la API.")
                    st.code(data)
            else:
                st.error(f"Error {response.status_code}: No se pudieron obtener los partidos. Respuesta de la API:")
                st.code(response.text)
    else:
        st.info("Ingresa tu API key para ver los partidos reales de la Liga MX.")
