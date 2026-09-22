
import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# BASE DE DATOS REAL DE TU FLOTA
ASIGNACION_FLOTA = {
    "2447 CIN": "PEDRO FERNANDEZ",
    "432 AIL": "JUAN CALIXTO",
    "1156 FER": "RAMIRO FERNÁNDEZ",
    "472 PXA (Sin Chofer)": "CHOFER TEMPORAL / N/A",
    "MERCEDES ROJO (Sin Placa)": "CHOFER TEMPORAL / N/A"
}

st.set_page_config(page_title="Registro de Viajes - Concepción", layout="centered")
st.title("📝 Control de Fletes - Oficina Principal")
st.write("Escriba los números directamente en las casillas.")

conn = st.connection("gsheets", type=GSheetsConnection)

with st.form("formulario_viaje", clear_on_submit=True):
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    st.info(f"📅 Fecha del registro: *{fecha_hoy}*")
    
    placa_seleccionada = st.selectbox("Seleccione la Placa del Camión:", list(ASIGNACION_FLOTA.keys()))
    chofer_automatico = ASIGNACION_FLOTA[placa_seleccionada]
    st.success(f"👤 Chofer asignado: *{chofer_automatico}*")
    
    st.write("---")
    st.subheader("Configuración del Flete")
    lleva_acoplado = st.radio("¿El camión lleva acoplado (Burro) en este viaje?", ("Sí (450 Bs)", "No (350 Bs)"))
    pago_flete = 450 if "Sí" in lleva_acoplado else 350
    
    st.write("---")
    st.subheader("Datos del Viaje")
    
    # CASILLAS LIMPIAS EN BLANCO PARA ESCRIBIR DIRECTO
    codigo_cfo = st.text_input("Código CFO de la Madera:", value="")
    volumen_m3 = st.text_input("Volumen Métrico Transportado (m³):", value="")
    distancia_km = st.text_input("Distancia del Viaje (Km):", value="")
    diesel_litros = st.text_input("Litros de Diésel Cargados:", value="")
    
    observaciones = st.text_input("Observaciones o Ruta:", value="Sin novedad")
    boton_guardar = st.form_submit_button("💾 Guardar Registro de Viaje")

if boton_guardar:
    try:
        # Conversión segura de textos a números para evitar errores de signos
        v_m3 = float(volumen_m3) if volumen_m3 else 0.0
        d_km = float(distancia_km) if distancia_km else 0.0
        l_dsl = float(diesel_litros) if diesel_litros else 0.0
        
        nuevo_registro = pd.DataFrame([{
            "Fecha": fecha_hoy,
            "Camion": placa_seleccionada,
            "Chofer": chofer_automatico,
            "Codigo_CFO": codigo_cfo if codigo_cfo else "N/A",
            "Volumen_M3": v_m3,
            "Distancia_Viaje_Km": d_km,
            "Diesel_Litros": l_dsl,
            "Pago_Chofer": pago_flete,
            "Observaciones": observaciones
        }])
        
        df_existente = conn.read(ttl=0)
        df_final = pd.concat([df_existente, nuevo_registro], ignore_index=True)
        conn.update(data=df_final)
        st.balloons()
        st.success("✅ ¡Viaje guardado y enviado a la nube con éxito!")
    except ValueError:
        st.error("⚠️ Por favor, asegúrese de colocar solo números enteros o con punto decimal en Volumen, Distancia y Diésel.")
