import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURACIÓN DEL REPORTE DEL DUEÑO
st.set_page_config(page_title="Reporte Diario - Concepción", layout="centered")
st.title("📊 Reporte Diario de Flota")
st.subheader("Control de Viajes, Diésel y Madera en Vivo")
st.write("---")

EXCEL_PATH = "Control.xlsx"
PRECIO_DIESEL_BS = 18.00  # <--- PRECIO ACTUAL DEL DIÉSEL EN BOLIVIA

def cargar_datos():
    if os.path.exists(EXCEL_PATH):
        return pd.read_excel(EXCEL_PATH)
    else:
        return pd.DataFrame()

df = cargar_datos()

if df.empty:
    st.warning("⚠️ El secretario aún no ha registrado ningún viaje el día de hoy.")
else:
    df['Fecha'] = df['Fecha'].astype(str)
    
    # 2. FILTRO DE FECHA AUTOMÁTICO
    fecha_hoy_sistema = datetime.now().strftime("%d/%m/%Y")
    st.sidebar.header("Filtro de Visualización")
    fecha_seleccionada = st.sidebar.text_input("Ver reportes del día:", value=fecha_hoy_sistema)
    
    df_hoy = df[df['Fecha'] == fecha_seleccionada]
    
    # 3. RESUMEN EN PANTALLA EN CUADROS GRANDES (Multiplicando el diésel por 18 Bs)
    st.header(f"📈 Resumen del Día: {fecha_seleccionada}")
    
    camiones_hoy = df_hoy['Camion'].nunique()
    madera_hoy = df_hoy['Volumen_M3'].sum()
    litros_hoy = df_hoy['Diesel_Litros'].sum()
    
    # AQUÍ SE HACE LA MULTIPLICACIÓN PARA TU PANTALLA
    dinero_diesel_hoy = litros_hoy * PRECIO_DIESEL_BS
    flete_total_hoy = df_hoy['Pago_Chofer'].sum()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="🚚 Camiones en Ruta", value=f"{camiones_hoy} unidades")
        st.metric(label="🪵 Total Madera Entrada", value=f"{madera_hoy:.1f} m³")
    with col2:
        st.metric(label="⛽ Gasto Diésel del Día", value=f"{int(dinero_diesel_hoy)} Bs", delta=f"{int(litros_hoy)} Litros cargados")
        st.metric(label="💵 Total Fletes a Pagar", value=f"{int(flete_total_hoy)} Bs")
        
    st.write("---")
    
    # 4. TABLA DETALLADA PARA EL CELULAR
    st.header("📋 Detalle de Viajes Recibidos Hoy")
    if df_hoy.empty:
        st.info(f"ℹ️ No hay fletes registrados para la fecha {fecha_seleccionada}.")
    else:
        df_hoy_visual = df_hoy[['Camion', 'Chofer', 'Codigo_CEFO', 'Volumen_M3', 'Diesel_Litros', 'Pago_Chofer', 'Observaciones']]
        st.dataframe(df_hoy_visual, use_container_width=True)
        
    st.write("---")
    
    # 5. HISTORIAL DE ALARMAS DE ACEITE
    st.header("🚨 Alertas de Mantenimiento Acumulado")
    LIMITE_ACEITE = 10000
    km_por_camion = df.groupby('Camion')['Distancia_Viaje_Km'].sum().to_dict()
    
    alertas_activas = False
    for camion_placa in ["2447 CIN", "432 AIL", "1156 FER", "472 PXA (Sin Chofer)", "MERCEDES ROJO (Sin Placa)"]:
        km_acumulados = km_por_camion.get(camion_placa, 0)
        aceite_restante = LIMITE_ACEITE - (km_acumulados % LIMITE_ACEITE)
        
        if aceite_restante < 1000:
            st.error(f"⚠️ *{camion_placa}:* Requiere cambio de aceite pronto. (Historial: {int(km_acumulados)} Km acumulados).")
            alertas_activas = True
            
    if not alertas_activas:
        st.success("✅ Kilometrajes y motores operando en rangos seguros.")
