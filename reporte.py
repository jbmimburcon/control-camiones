import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURACIÓN DEL PANEL DE REPORTE PARA EL DUEÑO
st.set_page_config(page_title="Reporte Diario de Flota", layout="centered")
st.title("📊 Reporte Diario de Flota")
st.subheader("Control de Viajes, Diésel y Madera en Vivo")
st.write("---")

# RUTA DEL EXCEL DE GOOGLE DRIVE
EXCEL_PATH = "Control.xlsx"

def cargar_datos():
    if os.path.exists(EXCEL_PATH):
        return pd.read_excel(EXCEL_PATH)
    else:
        return pd.DataFrame()

df = cargar_datos()

if df.empty:
    st.warning("⚠️ El secretario aún no ha registrado ningún viaje en el sistema de la oficina.")
else:
    # Asegurar formato de fecha correcto
    df['Fecha'] = df['Fecha'].astype(str)
    
    # 2. FILTRO DE FECHA AUTOMÁTICO (Elige hoy por defecto)
    fecha_hoy_sistema = datetime.now().strftime("%d/%m/%Y")
    
    st.sidebar.header("Filtro de Visualización")
    fecha_seleccionada = st.sidebar.text_input("Ver reportes del día:", value=fecha_hoy_sistema)
    
    # Filtrar los datos del Excel para mostrar SOLO lo del día seleccionado
    df_hoy = df[df['Fecha'] == fecha_seleccionada]
    
    # 3. RESUMEN EN CUADROS GRANDES PARA EL TELÉFONO
    st.header(f"📈 Resumen del Día: {fecha_seleccionada}")
    
    camiones_hoy = df_hoy['Camion'].nunique()
    madera_hoy = df_hoy['Volumen_M3'].sum()
    diesel_hoy = df_hoy['Diesel_Litros'].sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Camiones que Llegaron", value=f"{camiones_hoy} unidades")
    with col2:
        st.metric(label="Total Madera Entrada", value=f"{madera_hoy:.1f} m³")
    with col3:
        st.metric(label="Total Diésel Cargado", value=f"{int(diesel_hoy)} Lts")
        
    st.write("---")
    
    # 4. TABLA DETALLADA DE LOS CAMIONES QUE LLEGARON HOY
    st.header("📋 Detalle de Viajes Recibidos Hoy")
    if df_hoy.empty:
        st.info(f"ℹ️ Aún no se han reportado ingresos de camiones para la fecha {fecha_seleccionada}.")
    else:
        # Mostrar datos clave ordenados de manera sencilla para leer en pantalla móvil
        df_hoy_visual = df_hoy[['Camion', 'Chofer', 'Codigo_CEFO', 'Volumen_M3', 'Diesel_Litros', 'Observaciones']]
        st.dataframe(df_hoy_visual, use_container_width=True)
        
    st.write("---")
    
    # 5. ALARMAS DE MANTENIMIENTO ACUMULADO (Sigue vigilando los Km en segundo plano)
    st.header("🚨 Alertas de Mantenimiento Acumulado")
    LIMITE_ACEITE = 10000
    km_por_camion = df.groupby('Camion')['Distancia_Viaje_Km'].sum().to_dict()
    
    alertas_activas = False
    for i in range(1, 7):
        nombre_camion = f"Camión {i}"
        km_acumulados = km_por_camion.get(nombre_camion, 0)
        aceite_restante = LIMITE_ACEITE - (km_acumulados % LIMITE_ACEITE)
        
        if aceite_restante < 1000:
            st.error(f"⚠️ *{nombre_camion}:* Requiere cambio de aceite pronto. (Historial acumulado: {int(km_acumulados)} Km recorridos).")
            alertas_activas = True
            
    if not alertas_activas:
        st.success("✅ Estructura mecánica y kilometrajes de la flota bajo control seguro.")