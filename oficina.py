import streamlit as st
import datetime
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

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
ID_HOJA_CALCULO = "1ItJpJgMGdD-QyblMErYeEvnzQ-WPpSb7Gb6J2cS8EJQ"

# Conexión directa buscando la pestaña real "Hoja 1"
def conectar_base_datos():
    scope = ["https://googleapis.com", "https://googleapis.com"]
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
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_key(ID_HOJA_CALCULO).worksheet("Hoja 1")

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

        volumen_txt = st.text_input("Volumen transportado (m³):", "0")
        distancia_txt = st.text_input("Distancia del viaje (Km):", "0")
        diesel_txt = st.text_input("Litros de Diésel cargados:", "0")
        extras_txt = st.text_input("Gastos extras adicionales (Bs):", "0")
        codigo_cfo = st.text_input("Código CFO de la Madera:")

        try:
            volumen_m3 = float(volumen_txt.replace(",", ".")) if volumen_txt.strip() else 0.0
            distancia_km = float(distancia_txt.replace(",", ".")) if distancia_txt.strip() else 0.0
            litros_diesel = float(diesel_txt.replace(",", ".")) if diesel_txt.strip() else 0.0
            gastos_extras = float(extras_txt.replace(",", ".")) if extras_txt.strip() else 0.0
            
            if st.button("Guardar Registro de Viaje"):
                if not codigo_cfo:
                    st.error("⚠️ Por favor, ingrese el Código CFO de la Madera antes de guardar.")
                else:
                    # Cálculos comerciales
                    pago_por_madera = volumen_m3 * 18.0
                    total_flete_bs = pago_por_madera
                    desgaste_llantas_bs = distancia_km * COSTO_LLANTA_POR_KM
                    desgaste_aceite_bs = distancia_km * COSTO_ACEITE_POR_KM
                    total_mantenimiento_preventivo = desgaste_llantas_bs + desgaste_aceite_bs
                    gasto_diesel_bs = litros_diesel * PRECIO_DIESEL_POR_LITRO
                    extra_por_m3 = gastos_extras / volumen_m3 if volumen_m3 > 0 else 0.0
                    utilidad_neta_bs = total_flete_bs - (total_mantenimiento_preventivo + gasto_diesel_bs + gastos_extras)

                    # Inserción limpia apuntando a la "Hoja 1"
                    hoja = conectar_base_datos()
                    nueva_fila = [
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
                        extra_por_m3,
                        total_flete_bs,
                        utilidad_neta_bs,
                        observaciones
                    ]
                    
                    hoja.append_row(nueva_fila)
                    st.balloons()
                    st.success("✅ ¡Viaje guardado! Registro insertado con éxito en tu archivo control_flota.")
                    
        except ValueError:
            st.error("⚠️ Error: Por favor introduzca solo números en las casillas correspondientes.")
        except Exception as e:
            st.error(f"❌ Error al guardar datos. Detalles del sistema: {e}")
    else:
        if contrasena != "":
            st.error("❌ Contraseña incorrecta. Solo personal autorizado.")

# ==============================================================================
# PANTALLA 2: PANEL DEL DUEÑO (Reportes en el Celular)
# ==============================================================================
elif opcion_menu == "Panel del Dueño (Reportes)":
    st.markdown("# 📊 Panel de Control y Rendimiento")
    st.markdown("### Información en tiempo real del consumo de combustible y ganancias.")
    
    try:
        hoja = conectar_base_datos()
        datos = hoja.get_all_records()
        
        if datos:
            df = pd.DataFrame(datos)
            
            # Cambiamos los nombres para asegurar la compatibilidad con tus columnas reales de Excel
            df.columns = [c.strip() for c in df.columns]
            
            df['Distancia Km'] = pd.to_numeric(df['Distancia Km'], errors='coerce').fillna(0)
            df['Litros Diesel'] = pd.to_numeric(df['Litros Diesel'], errors='coerce').fillna(0)
            df['Utilidad Neta Bs'] = pd.to_numeric(df['Utilidad Neta Bs'], errors='coerce').fillna(0)
            
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
            st.info("💡 Aún no hay registros de viajes guardados en la Hoja 1 para mostrar.")
            
    except Exception as e:
        st.error(f"No se pudieron cargar los reportes. Detalles técnicos: {e}")
