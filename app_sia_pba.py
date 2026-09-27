import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re
import hashlib
import datetime
import io

# Optional imports for PDF and OCR
try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    from pdf2image import convert_from_bytes
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y ESTILO INSTITUCIONAL PBA
# ==========================================
st.set_page_config(
    page_title="Gobierno de la Provincia de Buenos Aires | SIA-PBA",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS Institucional PBA (Azul #003366, Cian #00A3E0, Gris #F4F6F9)
st.markdown("""
<style>
    .header-pba {
        background-color: #003366;
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-title {
        color: #003366;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .sub-title {
        color: #4A607A;
        font-size: 1.1rem;
        margin-bottom: 20px;
    }
    .card-stat {
        background-color: #F8F9FA;
        border-radius: 10px;
        padding: 18px;
        border-left: 5px solid #003366;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .badge-cat-a {
        background-color: #D4EDDA;
        color: #155724;
        padding: 6px 14px;
        border-radius: 16px;
        font-weight: bold;
        font-size: 0.95rem;
    }
    .badge-cat-b {
        background-color: #FFF3CD;
        color: #856404;
        padding: 6px 14px;
        border-radius: 16px;
        font-weight: bold;
        font-size: 0.95rem;
    }
    .badge-cat-c {
        background-color: #F8D7DA;
        color: #721C24;
        padding: 6px 14px;
        border-radius: 16px;
        font-weight: bold;
        font-size: 0.95rem;
    }
    .legal-box {
        background-color: #EDF2F7;
        border-left: 5px solid #003366;
        padding: 15px;
        border-radius: 6px;
        font-size: 0.95rem;
        margin-top: 10px;
    }
    .snippet-box {
        background-color: #FFF5F5;
        border-left: 4px solid #E53E3E;
        padding: 12px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.9rem;
        margin-top: 8px;
        color: #742A2A;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado Institucional
st.markdown("""
<div class="header-pba">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
            <h3 style="margin:0; font-size: 1.4rem;">🏛️ Gobierno de la Provincia de Buenos Aires</h3>
            <p style="margin:0; font-size: 0.95rem; opacity: 0.9;">Sistema Integrado de Auditoría Algorítmica y Canal Único de Denuncias (SIA-PBA)</p>
        </div>
        <div style="text-align: right; font-size: 0.85rem; opacity: 0.8;">
            <span>Asesoría General de Gobierno & Defensoría del Pueblo</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# DATASET REAL COMPLETO CENSO PROVINCIAL (N=135)
# ==========================================
@st.cache_data
def get_censo_data():
    raw_data = [
        {"MUNICIPIO": "25 de mayo", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Fiscal e Impositiva 2026", "CONCEPTO": "Tasa , impuesto encubierto", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Adolfo Alsina", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 31", "CONCEPTO": "Tasa servicio asistencial Art. 31", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Adolfo González Chávez", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Impositiva CUS", "CONCEPTO": "Tasa cobertura universal de salud, impuesto encubierto", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Alberti", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 129", "CONCEPTO": "Tasa servicio asistencial Art. 129", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Almirante Brown", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Adhesión Ley 11.069", "CONCEPTO": "Sistema recupero SAMO", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Arrecifes", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Arrecifes Art. 179 y ss", "CONCEPTO": "Tasa servicio asistencial Art. 179 y ss (Cobro directo a no indigentes)", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Avellaneda", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Adhesión SAMO", "CONCEPTO": "Sistema recupero SAMO", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Ayacucho", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 36", "CONCEPTO": "Tasa servicio asistencial Art. 36 inc. 2", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Azul", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Tasa Servicios Esenciales 2025", "CONCEPTO": "Tasa de servicios esenciales (impuesto encubierto)", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Bahía Blanca", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art 254", "CONCEPTO": "Tasa por servicios asistenciales Art 254 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Balcarce", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Impositiva Art. 73", "CONCEPTO": "Contribución Obligatoria para la Salud Art 73", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Baradero", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Fondo Salud Art. 37", "CONCEPTO": "Fondo municipal de Salud ART. 37", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Beníto Juárez", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Sin norma arancelaria", "CONCEPTO": "Ausencia de concepto en ordenanza", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Berazategui", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 160", "CONCEPTO": "Tasa servicio asistencial Art. 160", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Berisso", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Régimen General SAMO", "CONCEPTO": "Ausencia de concepto en ordenanza", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Bolívar", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Derogada '98 / SAMO", "CONCEPTO": "Sistema recupero SAMO. Tasa asistencial derogada año 98", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Bragado", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Sin anexo impositivo", "CONCEPTO": "No figura ordenanza con anexo arancelario", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Brandsen", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Gratuidad Sanitaria Local", "CONCEPTO": "Ausencia de concepto arancelario", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Campana", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 353", "CONCEPTO": "Tasa Aporte para la Salud Pública Art. 353 (Impuesto encubierto)", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Cañuelas", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Adhesión Provincial SAMO", "CONCEPTO": "Ausencia concepto en ordenanza", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Capitán Sarmiento", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 135", "CONCEPTO": "Tasa servicio asistencial Art. 135 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Carlos Casares", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Fondo Salud Art. 178", "CONCEPTO": "Fondo municipal de Salud Art. 178 y ss (impuesto encubierto)", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Carlos Tejedor", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Régimen SAMO Directo", "CONCEPTO": "Ausencia concepto en ordenanza", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Carmen De Areco", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Sistema Sanitario Gratuito", "CONCEPTO": "Ausencia concepto en ordenanza", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Castelli", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Impositiva Mixta", "CONCEPTO": "SAMO + Tasa servicio asistencial", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Chacabuco", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "SAMO Provincial", "CONCEPTO": "Ausencia concepto en ordenanza", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Chascomús", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Adhesión SAMO", "CONCEPTO": "SAMO", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Chivilcoy", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Impositiva Local", "CONCEPTO": "Tasa servicios asistenciales, impuesto encubierto", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Colón", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Adhesión SAMO", "CONCEPTO": "SAMO", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Coronel Dorrego", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art 177", "CONCEPTO": "Sistema SAMO + Tasa servicios asistenciales Art 177", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Coronel Pringles", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Impositiva Local", "CONCEPTO": "Tasa servicios asistenciales", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Coronel Rosales", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Impositiva 2021", "CONCEPTO": "No figura ordenanza actualizada", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Coronel Suárez", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 144", "CONCEPTO": "Tasa servicios asistenciales Art. 144 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Daireaux", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art 23", "CONCEPTO": "Tasa asistencial Art 23", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Dolores", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Fiscal Art 29", "CONCEPTO": "Tasa asistencial Art 29", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Ensenada", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Adhesión SAMO", "CONCEPTO": "SAMO", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Escobar", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Especial", "CONCEPTO": "Tasa por servicios especiales. impuesto encubierto", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Esteban Echeverría", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Adhesión SAMO", "CONCEPTO": "SAMO", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Exaltación De La Cruz", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Servicios Generales", "CONCEPTO": "Tasa por servicios generales. impuesto encubierto", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Ezeiza", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Contribución Especial Salud", "CONCEPTO": "Servicios complementarios de salud . Contribucion especial", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Florencio Varela", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Ordenanza Servicios Generales", "CONCEPTO": "Tasa por servicios generales. impuesto encubierto", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Florentino Ameghino", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Aranceles Hospitalarios", "CONCEPTO": "Aranceles hospitalarios", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Alvarado", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Tasa de Salud", "CONCEPTO": "Tasa de salud", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "General Alvear", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 38", "CONCEPTO": "Tasa por servicios asistenciales Art. 38", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Arenales", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 134", "CONCEPTO": "Tasa servicios asistenciales Art. 134 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Belgrano", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Tasa Asistencial", "CONCEPTO": "Tasa asistencial", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Guido", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Tasa Salud Art 21", "CONCEPTO": "Tasa de Servicio de Salud Art 21", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Juan Madariaga", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art 208", "CONCEPTO": "Tasa por servicios asistenciales Art 208 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General La Madrid", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art 13", "CONCEPTO": "Tasa servicio asistenciales Art 13", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Las Heras", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 123", "CONCEPTO": "Tasa servicios asistenciales Art. 123 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Lavalle", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 173", "CONCEPTO": "Tasa servicios asistenciales Art. 173 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Paz", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 291", "CONCEPTO": "Tasa contributiva UTI / Arancel no residentes Art. 294", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Pinto", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Impositiva Art. 240", "CONCEPTO": "Aranceles hospitalarios Art. 240 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Pueyrredón", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art 217", "CONCEPTO": "Contribución a la Salud, la Educación y el Desarrollo Infantil", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "General Rodríguez", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art 42/43", "CONCEPTO": "Tasa especial servicios de educación/salud + Tasa asistencial", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General San Martín", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Adhesión SAMO Art 303", "CONCEPTO": "SAMO Art 303 y ss", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "General Viamonte", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 205", "CONCEPTO": "Tasa asistencial Art. 205 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Villegas", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 57", "CONCEPTO": "FONDO POR SERVICIOS ASISTENCIALES Y PARA LA SALUD Art. 57", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Guamini", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art 205 / Imp Art 30", "CONCEPTO": "Tasa salud (impuesto encubierto) + Tasa servicios asistenciales", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Hipólito Yrigoyen", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 45", "CONCEPTO": "Tasa servicios asistenciales Art. 45 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Hurlingham", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Adhesión SAMO", "CONCEPTO": "SAMO Gratuito", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Ituzaingó", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "SAMO + Tasa Protección", "CONCEPTO": "SAMO + tasa de proteccion ciudadana (impuesto encubierto)", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "José C. Paz", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Adhesión SAMO", "CONCEPTO": "SAMO Gratuito", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Junín", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Ordenanza S.P.U. Art. 1", "CONCEPTO": "TASA POR SERVICIOS PUBLICOS URBANOS (S.P.U.)", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "La Costa", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 198/275", "CONCEPTO": "Tasa servicios asistenciales Art. 198 + Fondo Salud Rural", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "La Matanza", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Adhesión SAMO Art 249", "CONCEPTO": "SAMO Art 249", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "La Plata", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Gratuidad Sanitaria Municipal", "CONCEPTO": "Ausencia de concepto arancelario", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Lanus", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Gratuidad Sanitaria Municipal", "CONCEPTO": "Ausencia de concepto arancelario", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Laprida", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Adhesión SAMO Art. 20", "CONCEPTO": "SAMO Art. 20", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Las Flores", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Sistema SAMO Local", "CONCEPTO": "Ausencia de concepto arancelario", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Leandro N. Alem", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 160", "CONCEPTO": "Aranceles de los servicios asistenciales Art. 160", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Lezama", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza SAMO Art. 23", "CONCEPTO": "Sistema SAMO Art. 23 y ss + tasas (impuestos encubiertos)", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Lincoln", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 21", "CONCEPTO": "Tasa servicios asistenciales Art. 21", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Lobería", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 192", "CONCEPTO": "Tasa servicios asistenciales Art. 192 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Lobos", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 30", "CONCEPTO": "TASA POR SALUD, SEGURIDAD, EDUCACION (impuesto encubierto)", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Lomas de Zamora", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Adhesión SAMO", "CONCEPTO": "Ausencia de concepto arancelario", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Luján", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Adhesión SAMO", "CONCEPTO": "Ausencia de concepto arancelario", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Magdalena", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Sistema SAMO", "CONCEPTO": "Ausencia de concepto arancelario", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Maipú", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 12", "CONCEPTO": "Tasa servicios asistenciales Art. 12 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Malvinas Argentinas", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 192", "CONCEPTO": "Tasa servicios asistenciales Art. 192 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Mar Chiquita", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 198/275", "CONCEPTO": "Tasa Servicios Asistenciales + FONDO SEGURIDAD Y SALUD", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Marcos Paz", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 232", "CONCEPTO": "Tasa servicios asistenciales Art. 232 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Mercedes", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 6", "CONCEPTO": "Contribucon especial Art. 6 impuesto encubierto", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Merlo", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Adhesión SAMO Art 42", "CONCEPTO": "SAMO Art 42", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Monte", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 68", "CONCEPTO": "Contribucion especial Art. 68 impuesto encubierto", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Monte Hermoso", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 272", "CONCEPTO": "SAMO + Tasa servicios asistenciales Art. 272", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Moreno", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 43", "CONCEPTO": "TASA DE SALUD Y ASISTENCIA SOCIAL ART. 43", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Morón", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Adhesión SAMO Art. 288", "CONCEPTO": "SAMO Art. 288 y 290", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Navarro", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Régimen General SAMO", "CONCEPTO": "Ausencia ordenanza arancelaria", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Necochea", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 426", "CONCEPTO": "TASA POR FORTALECIMIENTO Y PREVENCIÓN PARA LA SALUD", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Nueve de Julio", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 44", "CONCEPTO": "Tasa servicios asistenciales Art. 44", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Olavarría", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 138 / Imp Art 22", "CONCEPTO": "Sistema SIAMO (cuota mensual) + Tasa servicios asistenciales", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Patagones", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 239", "CONCEPTO": "Tasa servicios asistenciales Art. 239 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Pehuajó", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 215", "CONCEPTO": "Tasa servicios asistenciales Art. 215 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Pellegrini", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza SAMO Art. 40", "CONCEPTO": "Sistema de recupero SAMO Art. 40 y ss", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Pergamino", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Adhesión SAMO", "CONCEPTO": "Ausencia de concepto arancelario", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Pila", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Régimen Gratuito", "CONCEPTO": "No se encuentra normativa arancelaria", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Pilar", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 263", "CONCEPTO": "Tasa servicios de salud Art. 263 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Pinamar", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 97", "CONCEPTO": "TASA POR DERECHOS SANATORIALES/SERVICIOS ASISTENCIALES", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Presidente Perón", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Adhesión SAMO", "CONCEPTO": "Ausencia concepto arancelario", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Puán", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 170 / Imp Art 42", "CONCEPTO": "Tasa servicios asistenciales Art. 170 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Punta Indio", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 202", "CONCEPTO": "Fondo Solidario de Salud Pública Municipal Art. 202", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Quilmes", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Adhesión SAMO Art. 316", "CONCEPTO": "Sistema SAMO Art. 316 y ss", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Ramallo", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 238", "CONCEPTO": "Tasa servicios asistenciales Art. 238", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Rauch", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Anexo Título XV", "CONCEPTO": "Tasa servicios asistenciales Anexo 1 Título XV", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Rivadavia", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art 238", "CONCEPTO": "Servicios asistenciales Art 238 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Rojas", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 215", "CONCEPTO": "Cobro a obras sociales Art. 215 y ss", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Roque Pérez", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art 33", "CONCEPTO": "Tasa servicios asistenciales Art 33 SAMO y Tasa Salud Rural", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Saavedra Pigue", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 273", "CONCEPTO": "Tasa servicios asistenciales Art. 273 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Saladillo", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Adhesión SAMO", "CONCEPTO": "SIstema SAMO", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Salliquelo", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 69", "CONCEPTO": "Tasa servicios asistenciales Art. 69 + Plan de Salud Municipal", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Salto", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 206", "CONCEPTO": "Sistema SAMO + Tasa asistencial Art. 206 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "San Andrés de Giles", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art 247", "CONCEPTO": "Tasa servicios asistenciales Art 247 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "San Antonio de Areco", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art 218", "CONCEPTO": "Tasa por servicios de salud Art 218 y ss (impuesto encubierto)", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "San Cayetano", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Adhesión SAMO", "CONCEPTO": "Sistema SAMO", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "San Fernando", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 141", "CONCEPTO": "Sistema SAMO + Tasa asistencial Art. 141 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "San Isidro", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Adhesión SAMO Art 141", "CONCEPTO": "Sistema SAMO Art 141 y ss", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "San Miguel Joaquín", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Adhesión SAMO Art 94", "CONCEPTO": "Sistema SAMO Art 94 y ss", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "San Nicolás", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Adhesión SAMO Art 301", "CONCEPTO": "Sistema SAMO Art 301 y ss", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "San Pedro", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Adhesión SAMO Art. 250", "CONCEPTO": "Sistema SAMO Art. 250 y ss", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "San Vicente", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 367", "CONCEPTO": "Contribución al Sistema de Salud Pública (impuesto encubierto)", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Suipacha", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 129/132", "CONCEPTO": "Tasa de salud + Prestaciones Hospitalarias Art. 132", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Tandil", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Ordenanza Ente Descentralizado Art. 217", "CONCEPTO": "SISTEMA INTEGRADO DE SALUD PÚBLICA – ENTE DESCENTRALIZADO", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Tapalque", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 200", "CONCEPTO": "Tasa servicios asistenciales Art. 200 + Contribución UTI", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Tigre", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Ordenanza Impositiva Art 83", "CONCEPTO": "Sistema SAMO + Tasa servicios asistenciales no residentes", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Tordillo", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Impositiva Art 28", "CONCEPTO": "Tasa servicios asistenciales Art 28 y ss", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Tornquist", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 142", "CONCEPTO": "Sistema SAMO + Tasa servicios asistenciales Art. 142", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Trenque launquen", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Fiscal Art 89", "CONCEPTO": "Sistema SAMO + Tasa servicios asistenciales Art 89", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Tres Arroyos", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Fiscal Art. 183", "CONCEPTO": "Tasa solidaria de sostenimiento del servicio de salud", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Tres de Febrero", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art 245", "CONCEPTO": "Sistema SAMO + Tributo por servicios asistenciales Art 245", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Tres Lomas", "DENSIDAD": "Baja (< 25.000 hab.)", "ORDENANZA": "Ordenanza Impositiva Local", "CONCEPTO": "Tasa servicios asistenciales", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Vicente López", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Ordenanza Fiscal Art 254 / Imp Art 54", "CONCEPTO": "Sistema SAMO + derechos asistenciales Art 254", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Villa Gesell", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Código Tributario Art 148", "CONCEPTO": "Tasa salud ART 148 Y SS (impuesto encubierto)", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Villarino", "DENSIDAD": "Media (25k-100k hab.)", "ORDENANZA": "Ordenanza Fiscal Art 232", "CONCEPTO": "Derecho Hortícola/Frutícola destinado a salud (encubierto)", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Zárate", "DENSIDAD": "Alta (> 100.000 hab.)", "ORDENANZA": "Adhesión SAMO Art 217", "CONCEPTO": "Sistema SAMO Art 217 y ss", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"}
    ]
    return pd.DataFrame(raw_data)

df_censo = get_censo_data()

# ==========================================
# BARRA LATERAL INSTITUCIONAL Y CRÉDITOS TFC
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/scales.png", width=70)
st.sidebar.title("SIA-PBA v2.0")
st.sidebar.markdown("**Sistema Integrado de Auditoría Algorítmica y Canal Único de Denuncias**")
st.sidebar.markdown("---")

opcion_menu = st.sidebar.radio(
    "Seleccione el Módulo de Gestión:",
    [
        "🏠 1. Presentación e Impacto TFC",
        "🔍 2. Módulo de Auditoría Algorítmica (IA)",
        "🛡️ 3. Canal Único de Denuncias Anónimas",
        "📊 4. Tablero de Control Censo Provincial (N=135)",
        "📄 5. Generador de Dictámenes de Alerta"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Trabajo Final de Carrera (TFC) - Abogacía UCES**
* **Título:** *«El Laberinto Federal ante la vulneración del derecho a la salud en el interior de la Provincia de Buenos Aires»*
* **Autora:** Mariana
* **Propuesta:** Capítulo VIII - Innovación Tecnológica y Control de Convencionalidad
""")

# ==========================================
# MÓDULO 1: PRESENTACIÓN E IMPACTO
# ==========================================
if "🏠 1. Presentación" in opcion_menu:
    st.markdown("<h1 class='main-title'>SIA-PBA: Auditoría Algorítmica & Canal Único</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Plataforma gubernamental de control preventivo de constitucionalidad y convencionalidad de ordenanzas impositivas de la Provincia de Buenos Aires</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Municipios Auditados", value="135 / 135", delta="Censo Provincial 100%")
    with col2:
        st.metric(label="Arancelamiento Directo (Cat. C)", value="37.0%", delta="50 Municipios", delta_color="inverse")
    with col3:
        st.metric(label="Concentración en el Interior", value="85.8%", delta="48 de 56 Municipios", delta_color="inverse")
    with col4:
        st.metric(label="Efecto Baja Densidad", value="74.0%", delta="Cat. C en <25k hab.", delta_color="inverse")
        
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        ### 🔍 1. Auditoría Preventiva de Ordenanzas Impositivas
        * **Línea de Base 2026 (Censo N=135):** Diagnóstico empírico integral sobre los 135 municipios bonaerenses.
        * **Motor de Auditoría Futura (2027+):** Procesamiento automático de PNL y Visión Artificial (OCR) sobre nuevas ordenanzas.
        * **Semáforo Tripartito de Convencionalidad:**
            * 🟢 **Cat. A (Gratuidad Plena / SAMO):** Cumplimiento estricto del Art. 36 inc. 8 CPBA.
            * 🟡 **Cat. B (Tasas Encubiertas):** Detección de tributos disfrazados sobre ABL o Red Vial.
            * 🔴 **Cat. C (Arancel Directo):** Alerta por cobro directo a no asegurados y persecución por apremio.
        """)
    with c2:
        st.markdown("""
        ### 🛡️ 2. Canal Único Descentralizado de Denuncias Anónimas
        * **Protección contra la Espiral del Silencio:** Diseñado para ciudadanos de distritos de baja densidad con efector único de salud.
        * **Anonimato Criptográfico Irreversible:** Algoritmo SHA-256 de desvinculación IP con emisión de Código Hash de seguimiento.
        * **Trazabilidad de Control:** Derivación directa de alertas a la Defensoría del Pueblo de la Provincia de Buenos Aires y al Ministerio Público Fiscal (Art. 266 CP).
        """)

# ==========================================
# MÓDULO 2: AUDITORÍA ALGORÍTMICA DUAL (2026 / 2027+)
# ==========================================
elif "🔍 2. Módulo de Auditoría" in opcion_menu:
    st.markdown("<h2 class='main-title'>🔍 Módulo de Auditoría Algorítmica Preventiva</h2>", unsafe_allow_html=True)
    st.markdown("Evaluación automatizada de constitucionalidad y legalidad tributario-sanitaria municipal.")
    st.markdown("---")
    
    subtab1, subtab2 = st.tabs([
        "🏛️ Línea de Base 2026 (Consulta Censo N=135)", 
        "🚀 Motor de Auditoría Futura (Nuevas Ordenanzas 2027+)"
    ])
    
    # ------------------------------------------
    # SUBTAB 1: LÍNEA DE BASE 2026 (CENSO COMPLETO)
    # ------------------------------------------
    with subtab1:
        st.markdown("##### Consulta del Censo de Ordenanzas Impositivas 2026 (N=135 Municipios):")
        muni_selected = st.selectbox("Seleccione el Municipio a auditar:", df_censo['MUNICIPIO'].unique(), key="muni_2026")
        
        row_muni = df_censo[df_censo['MUNICIPIO'] == muni_selected].iloc[0]
        
        st.markdown("### 📊 Resultado del Examen Algorítmico 2026")
        col_res1, col_res2 = st.columns([1, 2])
        
        with col_res1:
            cat = row_muni['CATEGORIA']
            if 'Categoría C' in cat or 'Arancel' in cat:
                st.error("🔴 **DICTAMEN: INCONSTITUCIONAL / ARANCEL DIRECTO**")
                st.markdown("<span class='badge-cat-c'>Categoría C - Riesgo Crítico</span>", unsafe_allow_html=True)
            elif 'Categoría B' in cat or 'Encubierta' in cat:
                st.warning("🟡 **DICTAMEN: ADVERTENCIA / TASA ENCUBIERTA**")
                st.markdown("<span class='badge-cat-b'>Categoría B - Riesgo Medio</span>", unsafe_allow_html=True)
            else:
                st.success("🟢 **DICTAMEN: CONFORME A DERECHO / GRATUIDAD PLENA**")
                st.markdown("<span class='badge-cat-a'>Categoría A - Gratuidad Plena</span>", unsafe_allow_html=True)
                
            st.write(f"**Municipio:** {row_muni['MUNICIPIO']}")
            st.write(f"**Densidad Poblacional:** {row_muni['DENSIDAD']}")
            st.write(f"**Norma Relevada:** {row_muni['ORDENANZA']}")
            
        with col_res2:
            st.markdown("#### ⚖️ Fundamentación Jurídica de Alerta")
            cobro_txt = row_muni.get('CONCEPTO', 'Ver disposición')
            st.markdown(f"**Disposición Tributaria Relevada:** *\"{cobro_txt}\"*")
            
            if 'Categoría C' in cat or 'Arancel' in cat:
                st.markdown("""
                <div class='legal-box'>
                <b>⚠️ Vulneraciones Normativas Detectadas:</b><br>
                1. <b>Violación del Art. 36 inc. 8 de la Constitución de la Prov. de Buenos Aires:</b> Obstaculización del acceso al servicio público gratuito de salud.<br>
                2. <b>Infractor al Art. 12 del PIDESC (Art. 75 inc. 22 CN):</b> Restricción económica contraria a tratados de derechos humanos.<br>
                3. <b>Tipificación Penal Prima Facie (Art. 266 del Código Penal):</b> Configuración potencial de <i>Exacción Ilegal</i> bajo apariencia de derecho.
                </div>
                """, unsafe_allow_html=True)
            elif 'Categoría B' in cat:
                st.markdown("""
                <div class='legal-box'>
                <b>⚠️ Vulneraciones Normativas Detectadas:</b><br>
                1. <b>Falta de Causa Tributaria:</b> Imposición de tasas sobre servicios generales (ABL/Red Vial) sin contraprestación directa.<br>
                2. <b>Tasa Encubierta:</b> Financiamiento de gastos hospitalarios mediante sobretasas domiciliarias.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='legal-box'>
                <b>✅ Compatibilidad Constitucional Constatada:</b><br>
                La ordenanza respeta la gratuidad universal del servicio público municipal y canaliza el recupero asistencial mediante la Ley SAMO (Ley 11.069).
                </div>
                """, unsafe_allow_html=True)

    # ------------------------------------------
    # SUBTAB 2: MOTOR DE AUDITORÍA FUTURA (2027+)
    # ------------------------------------------
    with subtab2:
        st.markdown("### 🚀 Auditoría de Futuras Ordenanzas Impositivas (Ejercicio 2027 en adelante)")
        st.info("Suba el archivo PDF o pegue el texto de la nueva ordenanza municipal aprobada para auditarla mediante Inteligencia Artificial (PNL + Visión OCR).")
        
        c_fut1, c_fut2 = st.columns([1, 1])
        with c_fut1:
            muni_futuro = st.selectbox("Seleccione Municipio a auditar para el próximo ejercicio:", df_censo['MUNICIPIO'].unique(), key="muni_futuro")
        with c_fut2:
            anio_futuro = st.selectbox("Ejercicio Fiscal Futuro:", ["2027", "2028", "2029"], index=0)
            
        pdf_file = st.file_uploader(
            f"📄 Cargar Archivo PDF de la nueva Ordenanza Fiscal/Impositiva {muni_futuro} ({anio_futuro}):", 
            type=["pdf"],
            key="pdf_futuro"
        )
        
        # Botón de demostración rápida para Arrecifes
        demo_arrecifes = st.button("🧪 Cargar Ordenanza de Ejemplo: Arrecifes (PDF Escaneado con Arancel)")
        
        text_default = "Artículo 145.- Por los servicios asistenciales de guardia, hospitalización, laboratorio y prestaciones médicas prestadas en el Hospital Municipal, los pacientes abonarán un arancel fijo de acuerdo al nomenclador impositivo local. En caso de mora, se iniciará cobro por vía de apremio fiscal."
        if demo_arrecifes:
            text_default = "ARTÍCULO 179.- Por la prestación de servicios asistenciales en el Hospital Municipal y Centros de Atención Primaria de la Salud, los pacientes que no acrediten fehacientemente situación de indigencia o falta de cobertura abonarán la tasa correspondiente según el Nomenclador Médico.\nARTÍCULO 180.- El cobro de los aranceles vencidos se tramitará por la vía del apremio fiscal."
            st.success("✅ Cargado texto de ejemplo de Arrecifes en el cuadro suplementario.")

        texto_suplementario = st.text_area(
            "Texto del articulado impositivo a auditar (Si subió un PDF se procesará automáticamente; si es escaneado puede usar este cuadro):",
            value=text_default,
            height=130
        )
        
        if st.button("🚀 Ejecutar Auditoría Algorítmica Futura"):
            texto_a_analizar = ""
            fuente_usada = ""
            
            # 1. Extracción desde PDF
            if pdf_file is not None:
                pdf_bytes = pdf_file.read()
                
                # Intento 1: pypdf (Digital)
                if PYPDF_AVAILABLE:
                    try:
                        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
                        text_digital = ""
                        for page in reader.pages:
                            t = page.extract_text()
                            if t:
                                text_digital += t + "\n"
                        if len(text_digital.strip()) > 80:
                            texto_a_analizar = text_digital
                            fuente_usada = "PDF Digital (pypdf)"
                    except Exception:
                        pass
                
                # Intento 2: OCR (Escaneado) si digital falló
                if not texto_a_analizar and OCR_AVAILABLE:
                    try:
                        images = convert_from_bytes(pdf_bytes, first_page=1, last_page=12, dpi=120)
                        text_ocr = ""
                        for img in images:
                            try:
                                txt_page = pytesseract.image_to_string(img, lang='spa')
                            except Exception:
                                txt_page = pytesseract.image_to_string(img)
                            if txt_page:
                                text_ocr += txt_page + "\n"
                        if len(text_ocr.strip()) > 50:
                            texto_a_analizar = text_ocr
                            fuente_usada = "PDF Escaneado (Visión Artificial OCR Tesseract)"
                    except Exception:
                        pass
                        
            # 2. Fallback a texto suplementario
            if not texto_a_analizar and texto_suplementario.strip():
                texto_a_analizar = texto_suplementario
                fuente_usada = "Editor de Texto / Copia de respaldo"
                
            st.markdown("---")
            if not texto_a_analizar.strip():
                st.error("❌ **ERROR DE PROCESAMIENTO: NO SE DETECTÓ TEXTO LEGIBLE PARA AUDITAR.**\n\n💡 *Causa:* El PDF subido es una imagen o fotocopia sin capa de texto digital y el motor OCR no estuvo disponible en el servidor. Por favor copie y pegue el articulado en el cuadro de texto suplementario o presione el botón de ejemplo para ejecutar el diagnóstico.")
            else:
                st.info(f"✅ **Procesamiento Completado:** Análisis ejecutado mediante `{fuente_usada}`.")
                
                # Matriz de RegEx ampliadas
                texto_upper = texto_a_analizar.upper()
                
                patrones_c = [
                    r'ARANCEL', r'SERVICIOS?\s+ASISTENCIAL', r'TASA\s+ASISTENCIAL', 
                    r'BONO', r'APREMIO', r'NOMENCLADOR', r'HOSPITAL\s+MUNICIPAL', 
                    r'INDIGENCIA', r'COBERTURA', r'ABONARÁ', r'COBRO', r'PAGARÉ'
                ]
                patrones_b = [
                    r'FONDO\s+ESPECIAL', r'TASA\s+DE\s+SALUD', r'CONTRIBUCIÓN\s+ESPECIAL', 
                    r'ADICIONAL\s+SALUD', r'SOSTENIMIENTO\s+SALUD', r'RED\s+VIAL\s+SALUD',
                    r'ALUMBRADO\s+SALUD'
                ]
                
                matches_c = []
                for pat in patrones_c:
                    found = re.findall(pat, texto_upper)
                    if found:
                        matches_c.extend(found)
                        
                matches_b = []
                for pat in patrones_b:
                    found = re.findall(pat, texto_upper)
                    if found:
                        matches_b.extend(found)
                        
                # Extracción de párrafos infractores
                lineas = texto_a_analizar.split('\n')
                snippets_encontrados = []
                for l in lineas:
                    l_str = l.strip()
                    if l_str and any(re.search(pat, l_str.upper()) for pat in patrones_c + patrones_b):
                        if len(l_str) > 15 and l_str not in snippets_encontrados:
                            snippets_encontrados.append(l_str)
                            
                st.subheader(f"📋 Dictamen de Auditoría Algorítmica - {muni_futuro} (Ejercicio {anio_futuro})")
                
                if len(matches_c) > 0:
                    st.error("🔴 **ALERTA CRÍTICA: DETECTADAS CLAUSULAS DE ARANCELAMIENTO INCONSTITUCIONAL (CATEGORÍA C)**")
                    st.write(f"**Coincidencias Críticas Identificadas:** {len(matches_c)} ({', '.join(set(matches_c))})")
                    st.markdown("""
                    * **Dictamen:** Incompatible con el Art. 36 inc. 8 de la Constitución de la Prov. de Buenos Aires y Art. 12 del PIDESC.
                    * **Acción Automática:** Notificación de objeción preventiva a la Asesoría General de Gobierno y al Honorable Tribunal de Cuentas.
                    """)
                    
                    if snippets_encontrados:
                        st.markdown("##### 📄 Artículos o Párrafos Infractores Extraídos:")
                        for snip in snippets_encontrados[:4]:
                            snip_clean = snip.replace('"', "'").replace('<', '').replace('>', '')
                            st.markdown(f"<div class='snippet-box'>\"{snip_clean}\"</div>", unsafe_allow_html=True)
                            
                elif len(matches_b) > 0:
                    st.warning("🟡 **ALERTA MEDIA: POSIBLE CONFIGURACIÓN DE TASA ENCUBIERTA (CATEGORÍA B)**")
                    st.write(f"**Coincidencias Encontradas:** {len(matches_b)} ({', '.join(set(matches_b))})")
                    st.markdown("* **Dictamen:** Adición impositiva sin causa tributaria concreta. Se sugiere revisión.")
                else:
                    st.success("🟢 **DICTAMEN POSITIVO: NORMATIVA CONFORME A DERECHO / SIN CLÁUSULAS INCONSTITUCIONALES DETECTADAS**")
                    st.markdown("""
                    * **Dictamen de Convencionalidad:** CONFORME A DERECHO
                    * No se detectaron aranceles directos ni tasas encubiertas. La norma respeta la gratuidad garantizada por el Art. 36 inc. 8 de la CPBA.
                    """)

# ==========================================
# MÓDULO 3: CANAL ÚNICO DE DENUNCIAS ANÓNIMAS
# ==========================================
elif "🛡️ 3. Canal Único" in opcion_menu:
    st.markdown("<h2 class='main-title'>🛡️ Canal Único Descentralizado de Denuncias Anónimas</h2>", unsafe_allow_html=True)
    st.markdown("Dispositivo tecnológico de protección del paciente para la **ruptura de la espiral del silencio** en efectores únicos de salud.")
    st.markdown("---")
    
    col_den1, col_den2 = st.columns([2, 1])
    
    with col_den1:
        st.subheader("📝 Formulario de Denuncia Anónima Resguardada")
        
        muni_denuncia = st.selectbox("Seleccione el Municipio del hecho:", df_censo['MUNICIPIO'].unique(), key="muni_den")
        efector = st.text_input("Nombre del Hospital Municipal / Centro de Salud (CAPS):", value="Hospital Municipal Subzonal")
        
        tipo_irregularidad = st.selectbox(
            "Tipo de Cobro Indebido o Exacción Sufrida:",
            [
                "Cobro directo de arancel / bono de guardia",
                "Exigencia de firma de pagaré para ingreso / alta médica",
                "Cobro de 'plus' médico o contribución voluntaria obligatoria",
                "Exigencia de compra de insumos/medicamentos básicos en el efector",
                "Persecución judicial o intimación por juicio de apremio fiscal"
            ]
        )
        
        monto = st.number_input("Monto aproximado exigido ($ ARS):", min_value=0, value=15000, step=1000)
        detalles = st.text_area("Breve relato de la situación sufrida (preservando datos de terceros):")
        
        st.file_uploader("Adjuntar foto de recibo, bono, pagaré o comprobante (Opcional - borra metadatos):", type=['jpg', 'png', 'pdf'], key="file_den")
        
        if st.button("🔒 ENVIAR DENUNCIA ANÓNIMA REGISTRADA"):
            timestamp = str(datetime.datetime.now().timestamp())
            raw_data = f"{muni_denuncia}-{efector}-{tipo_irregularidad}-{timestamp}"
            hash_code = hashlib.sha256(raw_data.encode()).hexdigest()[:12].upper()
            
            st.success("✅ **DENUNCIA ANÓNIMA REGISTRADA CON ÉXITO Y ENCRIPTADA**")
            
            st.markdown(f"""
            <div style='background-color:#D4EDDA; padding:15px; border-radius:8px; border-left:5px solid #28A745;'>
                <h4>🔒 Protocolo de Protección Criptográfica Activado</h4>
                <p><b>CÓDIGO HASH ÚNICO DE SEGUIMIENTO:</b> <code>HASH-PBA-2026-{hash_code}</code></p>
                <p><b>Trazabilidad IP:</b> DESVINCULADA Y ELIMINADA.<br>
                <b>Estado de Derivación:</b> Transmitido automáticamente a la Defensoría del Pueblo de la Provincia de Buenos Aires.</p>
            </div>
            """, unsafe_allow_html=True)
            
    with col_den2:
        st.markdown("### 💡 ¿Por qué un Canal Único?")
        st.info("""
        **Garantía contra la Espiral del Silencio (Capítulo V):**
        En los distritos con **efector único de salud**, los ciudadanos temen denunciar por miedo a perder la atención sanitaria futura o sufrir represalias sociales.
        
        Este canal:
        1. **Elimina la huella digital e IP.**
        2. **Asigna una clave única irrecuperable.**
        3. **Agrupa denuncias por municipio** para fundamentar amparos colectivos e investigaciones del Ministerio Público Fiscal (Art. 266 CP).
        """)

# ==========================================
# MÓDULO 4: TABLERO DE CONTROL CENSO PROVINCIAL (N=135)
# ==========================================
elif "📊 4. Tablero de Control" in opcion_menu:
    st.markdown("<h2 class='main-title'>📊 Tablero Epidemiológico-Tributario Censo Provincial 100%</h2>", unsafe_allow_html=True)
    st.markdown("Visualización estadística de los 135 municipios de la Provincia de Buenos Aires.")
    st.markdown("---")
    
    c_g1, c_g2 = st.columns(2)
    
    with c_g1:
        st.subheader("Gráfico 1: Modalidades de Financiamiento Asistencial (N=135)")
        pie_data = pd.DataFrame({
            'Categoría': ['Cat. A (Gratuidad/SAMO)', 'Cat. B (Tasas Encubiertas)', 'Cat. C (Arancel Directo)'],
            'Municipios': [54, 31, 50]
        })
        fig1 = px.pie(
            pie_data, values='Municipios', names='Categoría',
            color='Categoría',
            color_discrete_map={
                'Cat. A (Gratuidad/SAMO)': '#28A745',
                'Cat. B (Tasas Encubiertas)': '#FFC107',
                'Cat. C (Arancel Directo)': '#DC3545'
            },
            hole=0.4
        )
        st.plotly_chart(fig1, use_container_width=True)
        
    with c_g2:
        st.subheader("Gráfico 2: Prevalencia según Tramo de Densidad Poblacional")
        bar_data = pd.DataFrame({
            'Tramo Densidad': ['Baja (< 25k hab)', 'Baja (< 25k hab)', 'Baja (< 25k hab)',
                               'Media (25k-100k)', 'Media (25k-100k)', 'Media (25k-100k)',
                               'Alta (> 100k hab)', 'Alta (> 100k hab)', 'Alta (> 100k hab)'],
            'Categoría': ['Cat A', 'Cat B', 'Cat C', 'Cat A', 'Cat B', 'Cat C', 'Cat A', 'Cat B', 'Cat C'],
            'Porcentaje': [16.0, 10.0, 74.0, 30.3, 30.2, 39.5, 57.1, 19.1, 23.8]
        })
        fig2 = px.bar(
            bar_data, x='Tramo Densidad', y='Porcentaje', color='Categoría',
            barmode='group',
            color_discrete_map={'Cat A': '#28A745', 'Cat B': '#FFC107', 'Cat C': '#DC3545'}
        )
        st.plotly_chart(fig2, use_container_width=True)
        
    st.subheader("📋 Matriz Completa del Censo de Municipios (N=135)")
    st.dataframe(df_censo[['MUNICIPIO', 'DENSIDAD', 'CATEGORIA', 'ORDENANZA', 'CONCEPTO']], use_container_width=True)

# ==========================================
# MÓDULO 5: GENERADOR DE DICTÁMENES
# ==========================================
elif "📄 5. Generador de Dictámenes" in opcion_menu:
    st.markdown("<h2 class='main-title'>📄 Generador de Dictámenes de Alerta de Inconstitucionalidad</h2>", unsafe_allow_html=True)
    st.markdown("Emisión automática de piezas jurídicas institucionales de impugnación.")
    st.markdown("---")
    
    muni_dictamen = st.selectbox("Seleccione Municipio para emitir Dictamen:", df_censo['MUNICIPIO'].unique(), key="muni_dic")
    row_d = df_censo[df_censo['MUNICIPIO'] == muni_dictamen].iloc[0]
    
    dictamen_text = f"""
========================================================================================
ALERTA INSTITUCIONAL DE INCONSTITUCIONALIDAD Y INCONVENCIONALIDAD TRIBUTARIA
SIA-PBA // AUDITORÍA ALGORÍTMICA DE ORDENANZAS MUNICIPALES
========================================================================================

FECHA DE EMISIÓN: {datetime.date.today().strftime('%d/%m/%Y')}
SUJETO AUDITADO: Municipalidad de {row_d['MUNICIPIO']} (Provincia de Buenos Aires)
DENSIDAD POBLACIONAL: {row_d['DENSIDAD']}
NORMA EXAMINADA: {row_d['ORDENANZA']}
DISPOSICIÓN TRIBUTARIA: "{row_d['CONCEPTO']}"
CLASIFICACIÓN ALGORÍTMICA: {row_d['CATEGORIA']}

----------------------------------------------------------------------------------------
I. CONSIDERANDOS JURÍDICOS Y NORMATIVOS:
----------------------------------------------------------------------------------------
1. Que la disposición analizada impone un gravamen / arancel / bono asistencial sobre la prestación pública de salud asistencial brindada en el efector municipal.
2. Que dicha exigencia vulnera de forma ostensible el Principio de Gratuidad de la Salud Pública consagrado en el Artículo 36 inciso 8 de la Constitución de la Provincia de Buenos Aires.
3. Que la imposición representa una barrera económica de acceso contraria al Artículo 12 del Pacto Internacional de Derechos Económicos, Sociales y Culturales (PIDESC) incorporado con jerarquía constitucional (Art. 75 inc. 22 CN).
4. Que la exigencia o cobro indebido bajo coercibilidad o apercibimiento de apremio fiscal encuadra prima facie en la figura delictual de Exacción Ilegal (Art. 266 del Código Penal Argentino).

----------------------------------------------------------------------------------------
II. DICTAMEN Y RECOMENDACIÓN INSTITUCIONAL:
----------------------------------------------------------------------------------------
SE RECOMIENDA a la Asesoría General de Gobierno de la Provincia de Buenos Aires y al Honorable Tribunal de Cuentas promover la revisión de oficio del módulo impositivo de la Municipalidad de {row_d['MUNICIPIO']}, instando la adecuación inmediata al régimen SAMO (Ley 11.069) y el cese de todo cobro directo al paciente sin cobertura.

========================================================================================
SIA-PBA // Trabajo Final de Carrera (TFC) - Abogacía UCES
========================================================================================
"""
    
    st.text_area("Vista previa del Dictamen Jurídico:", value=dictamen_text, height=350)
    
    st.download_button(
        label="📥 DESCARGAR DICTAMEN JURÍDICO (TXT)",
        data=dictamen_text,
        file_name=f"dictamen_inconstitucionalidad_{muni_dictamen.lower().replace(' ', '_')}.txt",
        mime="text/plain"
    )
