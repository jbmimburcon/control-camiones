import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. BASE DE DATOS DE TUS CHOFERES FIJOS (Se puede cambiar cuando quieras)
ASIGNACION_FLOTA = {
    "Camión 1": {"chofer": "Juan Carlos", "pago_flete": 150},
    "Camión 2": {"chofer": "Pedro Gómez", "pago_flete": 150},
    "Camión 3": {"chofer": "Luis Mamani", "pago_flete": 160},
    "Camión 4": {"chofer": "Carlos Flores", "pago_flete": 150},
    "Camión 5": {"chofer": "Miguel Choque", "pago_flete": 170},
    "Camión 6": {"chofer": "Andrés Vargas", "pago_flete": 160}
}

st.set_page_config(page_title="Registro de Viajes - Oficina", layout="centered")
st.title("📝 Registro Rápido de Viajes (Madera)")
st.write("Complete solo los campos del viaje. La fecha y el chofer se cargan solos.")

# ARCHIVO EXCEL DONDE SE GUARDA TODO (En tu OneDrive o Google Drive)
EXCEL_PATH = "Control.xlsx"

# 2. FORMULARIO VISUAL
with st.form("formulario_viaje", clear_on_submit=True):
    # Fecha automática del día de hoy
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    st.info(f"📅 Fecha del registro: *{fecha_hoy}*")
    
    # Selección de Camión (Menú desplegable)
    camion_seleccionado = st.selectbox("Seleccione el Camión:", list(ASIGNACION_FLOTA.keys()))
    
    # Chofer automático según el camión elegido
    chofer_automatico = ASIGNACION_FLOTA[camion_seleccionado]["chofer"]
    pago_automatico = ASIGNACION_FLOTA[camion_seleccionado]["pago_flete"]
    st.success(f"👤 Chofer asignado: *{chofer_automatico}* | Pago por flete: ${pago_automatico}")
    
    # Campos que el secretario SI debe llenar a mano
    codigo_cefo = st.text_input("Código CEFO (Si fue vacío, ponga N/A):", value="N/A")
    volumen_m3 = st.number_input("Volumen Métrico Transportado (m³):", min_value=0.0, step=0.1)
    distancia_km = st.number_input("Distancia del Viaje según Camioneta (Km):", min_value=0.0, step=1.0)
    diesel_litros = st.number_input("Litros de Diésel Cargados:", min_value=0.0, step=1.0)
    
    # Observaciones rápidas
    observaciones = st.text_input("Observaciones (Ej: Volvió vacío, ruta con lodo):", value="Sin novedad")
    
    # Botón para guardar
    boton_guardar = st.form_submit_button("💾 Guardar Viaje al Instante")

# 3. LÓGICA PARA INYECTAR LOS DATOS EN EL EXCEL
if boton_guardar:
    nuevo_registro = {
        "Fecha": [fecha_hoy],
        "Camion": [camion_seleccionado],
        "Chofer": [chofer_automatico],
        "Codigo_CFO": [codigo_cfo],
        "Volumen_M3": [volumen_m3],
        "Distancia_Viaje_Km": [distancia_km],
        "Diesel_Litros": [diesel_litros],
        "Pago_Chofer": [pago_automatico],
        "Observaciones": [observaciones]
    }
    df_nuevo = pd.DataFrame(nuevo_registro)
    
    # Si el archivo de Excel ya existe, le añade la nueva fila abajo. Si no, lo crea desde cero.
    if os.path.exists(EXCEL_PATH):
        df_existente = pd.read_excel(EXCEL_PATH)
        df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
    else:
        df_final = df_nuevo
        
    df_final.to_excel(EXCEL_PATH, index=False)
    st.balloons() # Animación de éxito
    st.success(f"✅ ¡Viaje del {camion_seleccionado} guardado en el Excel correctamente!")