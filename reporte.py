import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Reporte Inteligente - Concepción", layout="centered")
st.title("📊 Inteligencia de Flota - Modo Dueño")
st.write("Análisis financiero de rendimiento y ganancias en tiempo real.")
st.write("---")

PRECIO_DIESEL_BS = 18.00  # PRECIO ACTUAL EN BOLIVIA

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(ttl=5)
except:
    df = pd.DataFrame()

if df.empty or "Camion" not in df.columns:
    st.warning("⚠️ Su base de datos de Google Sheets está vacía o esperando el primer viaje de la oficina.")
else:
    # Asegurar tipos de datos numéricos
    df['Volumen_M3'] = pd.to_numeric(df['Volumen_M3'], errors='coerce').fillna(0)
    df['Diesel_Litros'] = pd.to_numeric(df['Diesel_Litros'], errors='coerce').fillna(0)
    df['Pago_Chofer'] = pd.to_numeric(df['Pago_Chofer'], errors='coerce').fillna(0)
    df['Distancia_Viaje_Km'] = pd.to_numeric(df['Distancia_Viaje_Km'], errors='coerce').fillna(0)
    
    # Calcular el gasto de diésel en dinero por cada fila
    df['Gasto_Diesel_Bs'] = df['Diesel_Litros'] * PRECIO_DIESEL_BS
    
    # RESUMEN GENERAL EN LA PARTE DE ARRIBA
    st.header("📈 Resumen Operativo General")
    tot_madera = df['Volumen_M3'].sum()
    tot_diesel_bs = df['Gasto_Diesel_Bs'].sum()
    tot_fletes = df['Pago_Chofer'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("🪵 Total Madera", f"{tot_madera:.1f} m³")
    c2.metric("⛽ Combustible", f"{int(tot_diesel_bs)} Bs")
    c3.metric("💵 Total Fletes", f"{int(tot_fletes)} Bs")
    
    st.write("---")
    
    # EL ANALIZADOR METRICO: ¿QUIÉN TE HACE GANAR O PERDER PLATA?
    st.header("🏆 Tabla de Rentabilidad por Camión")
    st.write("Este análisis evalúa el volumen transportado frente al gasto de combustible de cada unidad.")
    
    # Agrupar datos financieros por placa de camión
    analisis_camion = df.groupby('Camion').agg(
        Viajes_Realizados=('Fecha', 'count'),
        Madera_Total_m3=('Volumen_M3', 'sum'),
        Diesel_Total_Litros=('Diesel_Litros', 'sum'),
        Gasto_Diesel_Bs=('Gasto_Diesel_Bs', 'sum'),
        Fletes_A_Pagar_Bs=('Pago_Chofer', 'sum')
    ).reset_index()
    
    # Indicador de rendimiento técnico (Litros consumidos por cada Kilómetro recorrido)
    km_totales = df.groupby('Camion')['Distancia_Viaje_Km'].sum().to_dict()
    analisis_camion['Km_Recorridos'] = analisis_camion['Camion'].map(km_totales)
    analisis_camion['Rendimiento (L/Km)'] = (analisis_camion['Diesel_Total_Litros'] / analisis_camion['Km_Recorridos']).round(2).fillna(0)
    
    # Mostrar tabla limpia en tu pantalla
    st.dataframe(analisis_camion[[
        'Camion', 'Viajes_Realizados', 'Madera_Total_m3', 'Gasto_Diesel_Bs', 'Fletes_A_Pagar_Bs', 'Rendimiento (L/Km)'
    ]], use_container_width=True)
    
    st.write("---")
    st.header("📋 Historial Completo de Cargas de Hoy")
    st.dataframe(df[['Fecha', 'Camion', 'Chofer', 'Codigo_CFO', 'Volumen_M3', 'Diesel_Litros', 'Pago_Chofer']], use_container_width=True)
