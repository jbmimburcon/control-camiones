import streamlit as st
import datetime
import pandas as pd
import gspread

# ==============================================================================
# 1. CONFIGURACIONES GENERALES Y DICCIONARIOS (DATOS REALES JORGE)
# ==============================================================================
st.set_page_config(page_title="Control de Flota - Concepción", layout="wide", page_icon="🚛")

DICCIONARIO_CHOFERES = {
    "2447-CIN": "Pedro Fernandez",
    "1156-FER": "Ramiro Fernandez",
    "311-SLP": "Juan Ortiz",
    "472-PXA": "Chofer"
}

COSTO_LLANTA_POR_KM = 0.60
COSTO_ACEITE_POR_KM = 0.20
PRECIO_DIESEL_POR_LITRO = 18.0

# MANTENIDO EXACTAMENTE IGUAL A TU VERSIÓN CORREGIDA TRAS LOS 2 DÍAS DE TRABAJO
ID_HOJA_CALCULO = "1fNfxOGdGwwcr8Fn12u2FUIAQ9rB9TZYL5kEUrAWlYEM"

def conectar_base_datos():
    creds_dict = {
        "type": st.secrets["connections"]["gsheets"]["type"],
        "project_id": st.secrets["connections"]["gsheets"]["project_id"],
        "private_key_id": st.secrets["connections"]["gsheets"]["private_key_id"],
        "private_key": st.secrets["connections"]["gsheets"]["private_key"],
        "client_email": st.secrets["connections"]["gsheets"]["client_email"],
        "client_id": st.secrets["connections"]["gsheets"]["client_id"],
        "auth_uri": st.secrets["connections"]["gsheets"]["auth_uri"],
        "token_uri": st.secrets["connections"]["gsheets"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["connections"]["gsheets"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["connections"]["gsheets"]["client_x509_cert_url"]
    }
    client = gspread.service_account_from_dict(creds_dict)
    return client.open_by_key(ID_HOJA_CALCULO).get_worksheet(0)

# Funciones de control de estado para limpiar el formulario de forma efectiva
def limpiar_formulario():
    st.session_state.volumen = "0"
    st.session_state.distancia = "0"
    st.session_state.diesel = "0"
    st.session_state.extras = "0"
    st.session_state.precio_flete = "280"
    st.session_state.cfo = ""
    st.session_state.obs = ""

if "volumen" not in st.session_state:
    limpiar_formulario()

# ==============================================================================
# 2. CREACIÓN DEL MENÚ DE NAVEGACIÓN
# ==============================================================================
opcion_menu = st.sidebar.radio(
    "Seleccione una opción:",
    ["Panel del Dueño (Reportes)", "Formulario de la Secretaria"]
)

if opcion_menu == "Formulario de la Secretaria":
    st.markdown("# 📝 Acceso Restringido")
    contrasena = st.text_input("Ingrese la clave para registrar viajes:", type="password")
    
    if contrasena == "AdminFlota2026":
        st.markdown("# 📝 Registro de Viaje Diario")
        st.markdown("### Ingrese los datos solicitados en las casillas.")
        
        fecha_registro = st.date_input("📆 Fecha del registro:", datetime.date.today())
        lista_placas = list(DICCIONARIO_CHOFERES.keys())
        placa_seleccionada = st.selectbox("Seleccione la Placa del Camión:", lista_placas)
        chofer_assigned = DICCIONARIO_CHOFERES[placa_seleccionada]
        acoplado = st.checkbox("¿Lleva Acoplado?")
        
        # Variación del pago según acoplado solicitado
        pago_chofer = 450.0 if acoplado else 350.0
        st.success(f"👤 Chofer asignado: {chofer_assigned} | 💵 Pago Chofer calculado: {pago_chofer} Bs")
        st.divider()

        # Enlazados mediante 'key' a session_state para permitir su vaciado inmediato
        volumen_txt = st.text_input("Volumen transportado (m³):", key="volumen")
        distancia_txt = st.text_input("Distancia del viaje:", key="distancia")
        diesel_txt = st.text_input("Litros de Diésel cargados:", key="diesel")
        extras_txt = st.text_input("Gastos extras adicionales (Bs):", key="extras")
        precio_m3_txt = st.text_input("Precio por m3 del flete (Bs):", key="precio_flete")
        codigo_cfo = st.text_input("Código CFO de la Madera:", key="cfo")
        observaciones = st.text_area("Observaciones del viaje:", key="obs")

        try:
            volumen_m3 = float(volumen_txt.replace(",", ".")) if volumen_txt.strip() else 0.0
            distancia_km = float(distancia_txt.replace(",", ".")) if distancia_txt.strip() else 0.0
            litros_diesel = float(diesel_txt.replace(",", ".")) if diesel_txt.strip() else 0.0
            gastos_extras = float(extras_txt.replace(",", ".")) if extras_txt.strip() else 0.0
            precio_por_m3 = float(precio_m3_txt.replace(",",".")) if precio_m3_txt.strip() else 280.0
            
            if st.button("Guardar Registro de Viaje"):
                if not codigo_cfo:
                    st.error("⚠️ Por favor, ingrese el Código CFO de la Madera antes de guardar.")
                else:
                    total_flete_bs = volumen_m3 * precio_por_m3
                    desgaste_llantas_bs = distancia_km * COSTO_LLANTA_POR_KM
                    desgaste_aceite_bs = distancia_km * COSTO_ACEITE_POR_KM
                    total_mantenimiento_preventivo = desgaste_llantas_bs + desgaste_aceite_bs
                    gasto_diesel_bs = litros_diesel * PRECIO_DIESEL_POR_LITRO
                    extra_por_m3 = gastos_extras / volumen_m3 if volumen_m3 > 0 else 0.0
                    
                    # Se incluye el descuento del pago variable del chofer en el cálculo analítico
                    utilidad_neta_bs = total_flete_bs - (total_mantenimiento_preventivo + gasto_diesel_bs + gastos_extras + pago_chofer)

                    hoja = conectar_base_datos()
                    nuevo_registro = [
                        fecha_registro.strftime("%Y-%m-%d"),
                        placa_seleccionada,
                        chofer_assigned,
                        "Sí" if acoplado else "No",
                        codigo_cfo,
                        volumen_m3,
                        distancia_km,
                        litros_diesel,
                        gasto_diesel_bs,
                        desgaste_llantas_bs,
                        desgaste_aceite_bs,
                        gastos_extras,
                        precio_por_m3,
                        total_flete_bs,
                        utilidad_neta_bs,
                        observaciones
                    ]
                    hoja.append_row(nuevo_registro, value_input_option="USER_ENTERED")
                    
                    # Forzar vaciado de inputs tras guardar exitosamente
                    limpiar_formulario()
                    st.balloons()
                    st.success("✅ ¡Viaje guardado! Flete registrado correctamente en tu hoja de cálculo y formulario limpio.")
                    st.rerun()
        except Exception as e:
            st.error(f"❌ Error al guardar. Detalles del sistema: {e}")
    else:
        if contrasena != "":
            st.error("❌ Contraseña incorrecta. Solo personal autorizado.")

elif opcion_menu == "Panel del Dueño (Reportes)":
    st.markdown("# 📊 Panel de Control y Rendimiento")
    st.markdown("### Resumen semanal y comparación analítica de eficiencia de las 4 placas.")
    
    try:
        hoja = conectar_base_datos()
        datos = hoja.get_all_records()
        
        if datos:
            df = pd.DataFrame(datos)
            df.columns = [c.strip() for c in df.columns]
            
            # Formateo y limpieza de datos para cálculo
            df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
            df['Distancia'] = pd.to_numeric(df['Distancia'], errors='coerce').fillna(0)
            df['Litros Diesel'] = pd.to_numeric(df['Litros Diesel'], errors='coerce').fillna(0)
            df['Volumen m3'] = pd.to_numeric(df['Volumen m3'], errors='coerce').fillna(0)
            df['Gasto Diesel Bs'] = pd.to_numeric(df['Gasto Diesel Bs'], errors='coerce').fillna(0)
            df['Utilidad Neta Bs'] = pd.to_numeric(df['Utilidad Neta Bs'], errors='coerce').fillna(0)
            
            # FILTRO SEMANAL PERSONALIZABLE (Por defecto carga los últimos 7 días)
            st.sidebar.markdown("### 📅 Filtro de Reporte")
            hoy = datetime.date.today()
            hace_una_semana = hoy - datetime.timedelta(days=7)
            rango_fechas = st.sidebar.date_input("Seleccione Rango de Fechas:", [hace_una_semana, hoy])
            
            # Validar que el rango esté completo antes de filtrar
            if isinstance(rango_fechas, list) or isinstance(rango_fechas, tuple):
                if len(rango_fechas) == 2:
                    fecha_ini, fecha_fin = rango_fechas
                    df_filtrado = df[(df['Fecha'].dt.date >= fecha_ini) & (df['Fecha'].dt.date <= fecha_fin)]
                else:
                    df_filtrado = df
            else:
                df_filtrado = df

            # KPIs del Periodo Filtrado
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Distancia", f"{df_filtrado['Distancia'].sum():,.1f} Km")
            with col2:
                st.metric("Diésel Consumido", f"{df_filtrado['Litros Diesel'].sum():,.1f} Ltrs")
            with col3:
                st.metric("Utilidad en el Periodo", f"{df_filtrado['Utilidad Neta Bs'].sum():,.2f} Bs")
                
            st.divider()
            
            # TABLA COMPARATIVA ENTRE LAS CUATRO PLACAS
            st.subheader("⚔️ Análisis de Desempeño por Camión")
            if not df_filtrado.empty:
                resumen_placas = df_filtrado.groupby('Placa').agg(
                    Viajes_Totales=('Placa', 'count'),
                    Madera_m3_Traida=('Volumen m3', 'sum'),
                    Km_Recorridos=('Distancia', 'sum'),
                    Total_Litros_Diesel=('Litros Diesel', 'sum'),
                    Utilidad_Bs=('Utilidad Neta Bs', 'sum')
                ).reset_index()

                   resumen_placas['Rendimiento_Km_L'] = resumen_placas['Km_Recorridos'] / resumen_placas['Total_Litros_Diesel']
                resumen_placas['Consumo_L_por_m3'] = resumen_placas['Total_Litros_Diesel'] / resumen_placas['Madera_m3_Traida']
                
                resumen_placas.fillna(0, inplace=True)
                resumen_placas.replace([float('inf'), float('-inf')], 0, inplace=True)
                
                st.dataframe(
                    resumen_placas.style.format({
                        "Madera_m3_Traida": "{:,.1f} m³",
                        "Km_Recorridos": "{:,.1f} Km",
                        "Total_Litros_Diesel": "{:,.1f} Ltrs",
                        "Utilidad_Bs": "{:,.2f} Bs",
