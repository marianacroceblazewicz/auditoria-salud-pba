import streamlit as st
import tempfile
import json
import os
from google import genai
from google.genai import types

# 1. Configuración Segura de Gemini
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("⚠️ Configura 'GEMINI_API_KEY' en los Secrets de tu panel de Streamlit.")
    st.stop()

# 2. Interfaz de Usuario Básica
st.set_page_config(page_title="Auditor de Salud Pro", layout="wide")
st.title("🔎 Analizador Riguroso de PDFs de Salud (Evita Falsos Positivos)")
st.markdown("Sube tu archivo PDF (digital o escaneado). La IA mantendrá el contexto visual original.")

uploaded_file = st.file_uploader("Selecciona tu archivo PDF", type=["pdf"])

if uploaded_file is not None:
    st.info("🔄 Procesando documento de forma rigurosa... Por favor espera.")
    
    # Crear archivo temporal para subir a Google
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        # Subir archivo directamente a la API de Gemini (Mantiene formato de tablas y escaneos)
        with st.spinner("Cargando PDF en la infraestructura de Google..."):
            pdf_file = client.files.upload(file=tmp_file_path)
        
        # El Prompt estrictamente cerrado para eliminar falsos positivos
        prompt = """
        Analiza detalladamente este documento médico/legal adjunto. Identifica con precisión matemática 
        los artículos o cláusulas que estipulen el cobro directo de servicios de salud.
        
        REGLAS DE CONTEXTO OBLIGATORIAS PARA EVITAR FALSOS POSITIVOS:
        1. POSITIVO: Clasifica como VERDADERO únicamente si el texto describe un cobro activo por prestaciones, 
           procedimientos médicos, cirugías, insumos hospitalarios o consultas de salud directas.
        2. NEGATIVO (FALSOS POSITIVOS): Clasifica como FALSO e ignora por completo si el cobro se refiere a:
           - Multas o penalizaciones por inasistencia a citas médicas ya agendadas.
           - Trámites netamente administrativos (copias de historias clínicas, carnets, certificaciones).
           - Cobros de intereses por mora en pagos previos.
           - Menciones cruzadas a otras leyes o ejemplos hipotéticos que no correspondan al objeto actual del artículo.
        
        MÉTODO DE ANÁLISIS:
        Evalúa quién paga, a quién se le cobra y si el cobro está directamente ligado a la ejecución de un acto clínico o médico. 
        Si no cumple rigurosamente con la Regla 1, clasifícalo como FALSO POSITIVO y no generes la alerta.
        
        Devuelve tu respuesta EXCLUSIVAMENTE en este formato JSON:
        {
          "alertas_detectadas": [
            {
              "articulo_seccion": "Nombre o número del apartado",
              "texto_exacto_citado": "La cita exacta del PDF que motivó la alerta",
              "razonamiento_contextual": "Explicación breve de por qué cumple la Regla 1 y por qué NO es una multa o trámite administrativo",
              "es_cobro_salud_valido": true
            }
          ]
        }
        """
        
        with st.spinner("Gemini analizando la estructura y el contexto..."):
            # Usamos gemini-1.5-pro para el razonamiento legal y contratos complejos
            response = client.models.generate_content(
                model='gemini-1.5-pro',
                contents=[pdf_file, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1  # Forzamos rigurosidad extrema (quita la creatividad)
                ),
            )
        
        # Procesar la respuesta JSON de la IA
        resultado_json = json.loads(response.text)
        
        if resultado_json.get("alertas_detectadas"):
            st.warning(f"🚨 Se detectaron {len(resultado_json['alertas_detectadas'])} cobros válidos de servicios de salud:")
            for alerta in resultado_json["alertas_detectadas"]:
                with st.expander(f"📌 {alerta['articulo_seccion']}"):
                    st.markdown(f"**Texto en el PDF:** *\"{alerta['texto_exacto_citado']}\"*")
                    st.markdown(f"**Análisis de contexto:** {alerta['razonamiento_contextual']}")
        else:
            st.success("✅ Análisis completado. No se detectaron cobros de salud (Los falsos positivos administrativos se filtraron con éxito).")

    except Exception as e:
        st.error(f"Error técnico durante el análisis: {e}")
        
    finally:
        # Eliminamos el archivo de la nube de Google por privacidad
        if 'pdf_file' in locals():
            try:
                client.files.delete(name=pdf_file.name)
            except:
                pass
        # Eliminar archivo temporal local
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
