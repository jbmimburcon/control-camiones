import streamlit as st
from streamlit_gsheets import GSheetsConnection
import datetime
import pandas as pd

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

# Precios fijos reales actualizados
COSTO_LLANTA_POR_KM = 0.60
COSTO_ACEITE_POR_KM = 0.20
PRECIO_DIESEL_POR_LITRO = 18.0

# ==============================================================================
# 2. CREACIÓN DEL MENÚ DE NAVEGACIÓN
# ==============================================================================
opcion_menu = st.sidebar.radio(
    "Seleccione una opción:",
    ["Panel del Dueño (Reportes)", "Formulario de la Secretaria"]
)

# ==============================================================================
# PANTALLA 1: FORMULARIO DE INGRESO (Para la Secretaria) - PROTEGIDO CON CLAVE
# ==============================================================================
if opcion_menu == "Formulario de la Secretaria":
    st.markdown("# 📝 Acceso Restringido")
    
    # Campo para escribir la contraseña secreta
    contrasena = st.text_input("Ingrese la clave para registrar viajes:", type="password")
    
    if contrasena == "AdminFlota2026":
        st.markdown("# 📝 Registro de Viaje Diario")
        st.markdown("### Ingrese los datos solicitados en las casillas.")
        
        fecha_registro = st.date_input("📆 Fecha del registro:", datetime.date.today())
        lista_placas = list(DICCIONARIO_CHOFERES.keys())
        placa_seleccionada = st.selectbox("Seleccione la Placa del Camión:", lista_placas)
        chofer_assigned = DICCIONARIO_CHOFERES[placa_seleccionada]
        acoplado = st.checkbox("¿Lleva Acoplado?")
        observaciones = st.text_area("Observaciones del viaje:")
        
        st.success(f"👤 Chofer asignado: {chofer_assigned}")
        st.divider()

        # Inputs de texto manejando valores vacíos
        volumen_txt = st.text_input("Volumen transportado (m³):", "0")
        distancia_txt = st.text_input("Distancia del viaje (Km):", "0")
        diesel_txt = st.text_input("Litros de Diésel cargados:", "0")
        extras_txt = st.text_input("Gastos extras adicionales (Bs):", "0")
        codigo_cfo = st.text_input("Código CFO de la Madera:")

        # Conversión de datos y proceso de guardado seguro
        try:
            volumen_m3 = float(volumen_txt.replace(",", ".")) if volumen_txt.strip() else 0.0
            distancia_km = float(distancia_txt.replace(",", ".")) if distancia_txt.strip() else 0.0
            litros_diesel = float(diesel_txt.replace(",", ".")) if diesel_txt.strip() else 0.0
            gastos_extras = float(extras_txt.replace(",", ".")) if extras_txt.strip() else 0.0
            
            if st.button("Guardar Registro de Viaje"):
                if not codigo_cfo:
                    st.error("⚠️ Por favor, ingrese el Código CFO de la Madera antes de guardar.")
                else:
                    # Cálculos matemáticos en el backend
                    pago_por_madera = volumen_m3 * 18.0
                    total_flete_bs = pago_por_madera
                    desgaste_llantas_bs = distancia_km * COSTO_LLANTA_POR_KM
                    desgaste_aceite_bs = distancia_km * COSTO_ACEITE_POR_KM
                    total_mantenimiento_preventivo = desgaste_llantas_bs + desgaste_aceite_bs
                    gasto_diesel_bs = litros_diesel * PRECIO_DIESEL_POR_LITRO
                    extra_por_m3 = gastos_extras / volumen_m3 if volumen_m3 > 0 else 0.0
                    utilidad_neta_bs = total_flete_bs - (total_mantenimiento_preventivo + gasto_diesel_bs + gastos_extras)

                    # Conexión nativa corregida usando Secrets de Streamlit
                    conn = st.connection("gsheets", type=GSheetsConnection)
                    df_existente = conn.read()
                    
                    if df_existente is None:
                        df_existente = pd.DataFrame()

                    # Estructura de la nueva fila a guardar
                    nuevo_registro = {
                        "Fecha": fecha_registro.strftime("%Y-%m-%d"),
                        "Placa": placa_seleccionada,
                        "Chofer": chofer_assigned,
                        "Lleva Acoplado": "Sí" if acoplado else "No",
                        "Codigo CFO": codigo_cfo,
                        "Volumen m3": volumen_m3,
                        "Distancia Km": distancia_km,
                        "Litros Diesel": litros_diesel,
                        "Gasto Diesel Bs": gasto_diesel_bs,
                        "Prorrateo Llantas Bs": desgaste_llantas_bs,
                        "Prorrateo Aceite Bs": desgaste_aceite_bs,
                        "Gastos Extras Bs": gastos_extras,
                        "Extra por m3_Bs": extra_por_m3,
                        "Total Flete Bs": total_flete_bs,
                        "Utilidad Neta Bs": utilidad_neta_bs,
                        "Observaciones": observaciones
                    }
                    
                    # Guardado de datos corregido para la versión actual de Streamlit
                    nueva_fila = pd.DataFrame([nuevo_registro])
                    df_actualizado = df_existente._append(nuevo_registro, ignore_index=True)
                    conn.update(data=df_actualizado)
                    
                    st.balloons()
                    st.success("✅ ¡Viaje guardado! Flete registrado correctamente en la base de datos de Google Sheets.")
                    
        except ValueError:
            st.error("⚠️ Error: Por favor introduzca solo números en las casillas de volumen, distancia, diésel y extras.")
        except Exception as e:
            st.error(f"❌ Error al guardar. Verifica la configuración de Secrets en Streamlit. Detalles: {e}")
    else:
        if contrasena != "":
            st.error("❌ Contraseña incorrecta. Solo personal authorized.")

# ==============================================================================
# PANTALLA 2: PANEL DEL DUEÑO (Optimizado para tu Teléfono Celular)
# ==============================================================================
elif opcion_menu == "Panel del Dueño (Reportes)":
    st.markdown("# 📊 Panel de Control y Rendimiento")
    st.markdown("### Información en tiempo real del consumo de combustible y ganancias.")
    
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read()
        
        if df is not None and not df.empty:
            # Limpieza básica para evitar errores en las sumas
            df['Distancia Km'] = pd.to_numeric(df['Distancia Km'], errors='coerce').fillna(0)
            df['Litros Diesel'] = pd.to_numeric(df['Litros Diesel'], errors='coerce').fillna(0)
            df['Utilidad Neta Bs'] = pd.to_numeric(df['Utilidad Neta Bs'], errors='coerce').fillna(0)
            
            # Métricas rápidas de visualización
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Distancia Recorrida", f"{df['Distancia Km'].sum():,.1f} Km")
            with col2:
                st.metric("Combustible Total Consumido", f"{df['Litros Diesel'].sum():,.1f} Ltrs")
            with col3:
                st.metric("Utilidad Total Acumulada", f"{df['Utilidad Neta Bs'].sum():,.2f} Bs")
                
            st.divider()
            st.subheader("📋 Historial Completo de Viajes")
            st.dataframe(df)
        else:
            st.info("💡 Aún no hay registros de viajes guardados para mostrar.")
            
    except Exception as e:
        st.error(f"No se pudieron cargar los reportes en el celular. Asegúrate de configurar los Secrets de Google Sheets. {e}")
