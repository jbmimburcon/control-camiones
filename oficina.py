import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. BASE DE DATOS REAL DE TU FLOTA (Placas y Choferes)
ASIGNACION_FLOTA = {
    "2447 CIN": "PEDRO FERNANDEZ",
    "432 AIL": "JUAN CALIXTO",
    "1156 FER": " RAMIRO FERNÁNDEZ",
    "472 PXA (Sin Chofer)": "CHOFER TEMPORAL / N/A",
    "MERCEDES ROJO (Sin Placa)": "CHOFER TEMPORAL / N/A"
}

st.set_page_config(page_title="Registro de Viajes - Concepción", layout="centered")
st.title("📝 Control de Fletes - Oficina Principal")
st.write("Complete los datos del viaje. El chofer y la fecha se cargan automáticamente.")

EXCEL_PATH = "Control.xlsx"

# 2. FORMULARIO VISUAL
with st.form("formulario_viaje", clear_on_submit=True):
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    st.info(f"📅 Fecha del registro: *{fecha_hoy}*")
    
    # Selección de Camión por Placa
    placa_seleccionada = st.selectbox("Seleccione la Placa del Camión:", list(ASIGNACION_FLOTA.keys()))
    
    # Muestra el chofer automático en pantalla
    chofer_automatico = ASIGNACION_FLOTA[placa_seleccionada]
    st.success(f"👤 Chofer asignado: *{chofer_automatico}*")
    
    st.write("---")
    st.subheader("Configuración del Flete")
    
    # PREGUNTA CLAVE DEL PAGO (450 Bs o 350 Bs)
    lleva_acoplado = st.radio("¿El camión lleva acoplado (Burro) en este viaje?", ("Sí (450 Bs)", "No (350 Bs)"))
    pago_flete = 450 if "Sí" in lleva_acoplado else 350
    
    st.write("---")
    st.subheader("Datos del Viaje")
    codigo_cefo = st.text_input("Código CFO de la Madera (Si fue vacío, ponga N/A):", value="N/A")
    volumen_m3 = st.number_input("Volumen Métrico Transportado (m³):", min_value=0.0, step=0.1)
    distancia_km = st.number_input("Distancia  (Km):", min_value=0.0, step=1.0)
    diesel_litros = st.number_input("Litros de Diésel Cargados en Viaje:", min_value=0.0, step=1.0)
    
    observaciones = st.text_input("Observaciones o Ruta:", value="Sin novedad")
    
    boton_guardar = st.form_submit_button("💾 Guardar Registro de Viaje")

# 3. LÓGICA PARA INYECTAR LOS DATOS EN EL EXCEL
if boton_guardar:
    nuevo_registro = {
        "Fecha": [fecha_hoy],
        "Camion": [placa_seleccionada],
        "Chofer": [chofer_automatico],
        "Codigo_CEFO": [codigo_cefo],
        "Volumen_M3": [volumen_m3],
        "Distancia_Viaje_Km": [distancia_km],
        "Diesel_Litros": [diesel_litros],
        "Pago_Chofer": [pago_flete],
        "Observaciones": [observaciones]
    }
    df_nuevo = pd.DataFrame(nuevo_registro)
    
    if os.path.exists(EXCEL_PATH):
        df_existente = pd.read_excel(EXCEL_PATH)
        df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
    else:
        df_final = df_nuevo
        
    df_final.to_excel(EXCEL_PATH, index=False)
    st.balloons()
    st.success(f"✅ ¡Viaje de la placa {placa_seleccionada} guardado con flete de {pago_flete} Bs!")
