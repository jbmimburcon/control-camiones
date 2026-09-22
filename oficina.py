
import streamlit as st
import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuración de la plataforma
st.set_page_config(page_title="Transporte Concepción", page_icon="🚛", layout="wide")

# --- PARÁMETROS CONFIGURABLES DE COSTOS ---
PRECIO_DIESEL_POR_LITRO = 18.00       
COSTO_CAMBIO_LLANTAS_TOTAL = 30000.0  
VIDA_UTIL_LLANTAS_KM = 50000.0
COSTO_CAMBIO_ACEITE_TOTAL = 1800.0   
VIDA_UTIL_ACEITE_KM = 8000.0         

COSTO_LLANTA_POR_KM = COSTO_CAMBIO_LLANTAS_TOTAL / VIDA_UTIL_LLANTAS_KM  
COSTO_ACEITE_POR_KM = COSTO_CAMBIO_ACEITE_TOTAL / VIDA_UTIL_ACEITE_KM    

DICCIONARIO_CHOFERES = {
    "2447 CIN": "PEDRO FERNANDEZ",
    "432 AIL": "JUAN CALIXTO",
    "1156 FER": "RAMIRO FERNÁNDEZ",
    "311 SLP": "JUAN ORTIZ",
    "472 PXA": "SIN CHOFER"
}

# 2. Creación del menú de navegación para Celular/PC
opcion_menu = st.sidebar.radio("📋 Menú de Navegación", ["Formulario de la Secretaria", "Panel del Dueño (Reportes)"])

# ==============================================================================
# PANTALLA 1: FORMULARIO DE INGRESO (Para la Secretaria)
# ==============================================================================
if opcion_menu == "Formulario de la Secretaria":
    st.markdown("# 📝 Registro de Viaje Diario")
    st.markdown("### Escriba los números directamente en las casillas.")
    
    fecha_registro = st.date_input("📅 Fecha del registro:", datetime.date.today())
    lista_placas = list(DICCIONARIO_CHOFERES.keys())
    placa_seleccionada = st.selectbox("Seleccione la Placa del Camión:", lista_placas)
    chofer_assigned = DICCIONARIO_CHOFERES[placa_seleccionada]
    
    st.success(f"👤 Chofer asignado: {chofer_assigned}")
    st.divider()
    
    st.markdown("### Configuración del Flete")
    acoplado = st.radio("¿El camión lleva acoplado (Burro) en este viaje?", ["Sí (450 Bs)", "No (350 Bs)"], index=0)
    valor_acoplado = 450.0 if "Sí" in acoplado else 350.0
    st.divider()
    
    st.markdown("### Datos del Viaje")
    codigo_cfo = st.text_input("Código CFO de la Madera:")
    volumen_m3 = st.number_input("Volumen Métrico Transportado (m³):", min_value=0.0, step=0.01, format="%.2f")
    distancia_km = st.number_input("Distancia del Viaje (Km):", min_value=0.0, step=1.0, format="%.2f")
    litros_diesel = st.number_input("Litros de Diésel Cargados:", min_value=0.0, step=1.0, format="%.2f")
    gastos_extras = st.number_input("Gastos Extras / Imprevistos del Viaje (Bs):", min_value=0.0, step=10.0, format="%.2f")
    observaciones = st.text_area("Observaciones o Ruta:", value="Sin novedad")
    
    # Cálculos en tiempo real
    pago_por_madera = volumen_m3 * 18.0
    total_flete_bs = pago_por_madera + valor_acoplado
    desgaste_llantas_bs = distancia_km * COSTO_LLANTA_POR_KM
    desgaste_aceite_bs = distancia_km * COSTO_ACEITE_POR_KM
    total_mantenimiento_preventivo = desgaste_llantas_bs + desgaste_aceite_bs
    gasto_diesel_bs = litros_diesel * PRECIO_DIESEL_POR_LITRO
    extra_por_m3 = gastos_extras / volumen_m3 if volumen_m3 > 0 else 0.0
    utilidad_neta_bs = total_flete_bs - (total_mantenimiento_preventivo + gasto_diesel_bs + gastos_extras)
    
    st.divider()
    if st.button("💾 Guardar Registro de Viaje"):
        if not codigo_cfo:
            st.error("⚠️ Por favor, ingrese el Código CFO de la Madera antes de guardar.")
        else:
            try:
                conn = st.connection("gsheets", type=GSheetsConnection)
                df_existente = conn.read(ttl=0)
                
                nueva_fila = pd.DataFrame([{
                    "Fecha": fecha_registro.strftime("%Y-%m-%d"),
                    "Placa": placa_seleccionada,
                    "Chofer": chofer_assigned,
                    "Lleva Acoplado": acoplado,
                    "Codigo CFO": codigo_cfo,
                    "Volumen m3": volumen_m3,
                    "Distancia Km": distancia_km,
                    "Litros Diesel": litros_diesel,
                    "Gasto Diesel Bs": gasto_diesel_bs,
                    "Prorrateo Llantas Bs": desgaste_llantas_bs,
                    "Prorrateo Aceite Bs": desgaste_aceite_bs,
                    "Gastos Extras Bs": gastos_extras,
                    "Extra por m3 Bs": extra_por_m3,
                    "Total Flete Bs": total_flete_bs,
                    "Utilidad Neta Bs": utilidad_neta_bs,
                    "Observaciones": observaciones
                }])
                
                # Filtrar posibles filas completamente vacías
                if not df_existente.empty:
                    df_existente = df_existente.dropna(how='all')
                
                df_actualizado = pd.concat([df_existente, nueva_fila], ignore_index=True)
                conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=df_actualizado)
                st.balloons()
                st.success("✅ ¡Viaje guardado exitosamente!")
            except Exception as e:
                st.error("❌ Error al guardar. Verifica la configuración de Secrets en Streamlit.")

# ==============================================================================
# PANTALLA 2: PANEL DEL DUEÑO (Optimizado para tu Teléfono Celular)
# ==============================================================================
elif opcion_menu == "Panel del Dueño (Reportes)":
    st.markdown("# 📊 Control de Rendimiento Operativo")
    st.write("Vista exclusiva de control gerencial para el análisis de flotas y costos.")
    
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(ttl=0)
        
        # Limpieza básica para evitar leer filas en blanco de Google Sheets
        if not df.empty:
            df = df.dropna(subset=['Fecha', 'Placa', 'Total Flete Bs'])
            
        if df.empty:
            st.warning("Aún no existen registros de viajes válidos guardados en la base de datos.")
        else:
            df['Fecha'] = pd.to_datetime(df['Fecha'])
            hoy = pd.Timestamp(datetime.date.today())
            
            df_semana = df[df['Fecha'] >= (hoy - pd.Timedelta(days=7))]
            df_mes = df[df['Fecha'] >= (hoy - pd.Timedelta(days=30))]
            
            st.markdown("## 📅 Resumen Financiero de la Empresa")
            periodo = st.selectbox("Seleccione el periodo visual a evaluar en pantalla:", ["Últimos 30 días (Mensual)", "Últimos 7 días (Semanal)"])
            df_filtrado = df_mes if "Mensual" in periodo else df_semana
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("💵 Ingresos Totales (Fletes)", f"{df_filtrado['Total Flete Bs'].sum():,.2f} Bs")
            with c2:
                gasto_total = df_filtrado['Gasto Diesel Bs'].sum() + df_filtrado['Gastos Extras Bs'].sum() + df_filtrado['Prorrateo Llantas Bs'].sum() + df_filtrado['Prorrateo Aceite Bs'].sum()
                st.metric("📉 Gastos Operativos Totales", f"{gasto_total:,.2f} Bs")
            with c3:
                st.metric("📈 Utilidad Neta Consolidada", f"{df_filtrado['Utilidad Neta Bs'].sum():,.2f} Bs")
            
            st.divider()
            
            st.markdown("## 🚨 Alertas de Eficiencia de Camiones")
            
            analisis_camion = df.groupby('Placa').agg({
                'Litros Diesel': 'sum',
                'Volumen m3': 'sum',
                'Gasto Diesel Bs': 'sum'
            }).reset_index()
            
            analisis_camion['Diesel_por_m3'] = analisis_camion['Litros Diesel'] / analisis_camion['Volumen m3']
            
            camion_mas_gaston = analisis_camion.sort_values(by='Diesel_por_m3', ascending=False).iloc[0]
            st.error(f"""
            *⚠️ CAMIÓN CON MAYOR CONSUMO DE DIÉSEL POR m³:*
            El camión con placa *{camion_mas_gaston['Placa']}* requiere *{camion_mas_gaston['Diesel_por_m3']:.2f} Litros de Diésel* para lograr mover un solo metro cúbico ($m^3$) de madera.
            """)
            
            camion_menos_madera = analisis_camion.sort_values(by='Volumen m3', ascending=True).iloc[0]
            st.warning(f"""
            *📉 CAMIÓN QUE MENOS MADERA HA TRANSPORTADO:*
            El camión con placa *{camion_menos_madera['Placa']}* presenta el menor volumen de carga acumulado, registrando *{camion_menos_madera['Volumen m3']:.2f} m³* movilizados.
            """)
            
            st.divider()
            
            st.markdown("### 📊 Tabla de Rendimiento por Placa (Histórico)")
            analisis_camion.columns = ["Placa Camión", "Total Litros Diésel", "Total Madera (m³)", "Gasto Diésel total (Bs)", "Litros por cada m³"]
            st.dataframe(analisis_camion.style.format({"Total Litros Diésel": "{:,.1f}", "Total Madera (m³)": "{:,.2f}", "Gasto Diésel total (Bs)": "{:,.2f} Bs", "Litros por cada m³": "{:,.2f} L/m³"}), use_container_width=True)
            
    except Exception as e:
        st.error("Esperando los primeros registros válidos para estructurar el panel.")
