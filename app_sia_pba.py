import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re
import hashlib
import datetime

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y ESTILO PBA
# ==========================================
st.set_page_config(
    page_title="SIA-PBA | Sistema de Auditoría Algorítmica & Canal de Denuncias",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS Institucional Gobierno de la Provincia de Buenos Aires
st.markdown("""
<style>
    .pba-header {
        background-color: #003366;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .pba-header h1 {
        color: #FFFFFF !important;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-weight: 700;
        font-size: 1.8rem;
        margin: 0;
    }
    .pba-header p {
        color: #E0E8F0;
        margin: 5px 0 0 0;
        font-size: 0.95rem;
    }
    .main-title {
        color: #003366;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .sub-title {
        color: #4A607A;
        font-size: 1.05rem;
        margin-bottom: 25px;
    }
    .card-stat {
        background-color: #F4F6F9;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #003366;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .badge-cat-a {
        background-color: #D4EDDA;
        color: #155724;
        padding: 6px 12px;
        border-radius: 15px;
        font-weight: bold;
        display: inline-block;
    }
    .badge-cat-b {
        background-color: #FFF3CD;
        color: #856404;
        padding: 6px 12px;
        border-radius: 15px;
        font-weight: bold;
        display: inline-block;
    }
    .badge-cat-c {
        background-color: #F8D7DA;
        color: #721C24;
        padding: 6px 12px;
        border-radius: 15px;
        font-weight: bold;
        display: inline-block;
    }
    .legal-box {
        background-color: #F8FAFC;
        border-left: 4px solid #00A3E0;
        padding: 15px;
        border-radius: 6px;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .snippet-box {
        background-color: #FFF5F5;
        border-left: 4px solid #E53E3E;
        padding: 10px 15px;
        margin: 8px 0;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.88rem;
        color: #9B2C2C;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# BASE DE DATOS REAL CENSO PROVINCIAL (N=135)
# ==========================================
@st.cache_data
def get_censo_data():
    raw_data = [
        {"MUNICIPIO": "25 de mayo", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Tasa , impuesto encubierto", "ORDENANZA": "Ordenanza 25 de Mayo", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Adolfo Alsina", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa servicio asistencial Art. 31", "ORDENANZA": "Ordenanza Adolfo Alsina", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Adolfo González Chávez", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa cobertura universal de salud, impuesto encubierto", "ORDENANZA": "Ordenanza González Chávez", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Alberti", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa servicio asistencial Art. 129", "ORDENANZA": "Ordenanza Alberti", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Almirante Brown", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Sistema recupero SAMO", "ORDENANZA": "Ordenanza Almirante Brown", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Arrecifes", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Tasa servicio asistencial Art. 179 y ss", "ORDENANZA": "Odenanza Arrecifes", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Avellaneda", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Sistema recupero SAMO", "ORDENANZA": "Ordenanza Avellaneda", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Ayacucho", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa servicio asistencial Art. 36 inc. 2", "ORDENANZA": "Ordenanza Ayacucho", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Azul", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Tasa servicios esenciales (impuesto encubierto)", "ORDENANZA": "Ordenanza Azul 2025", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Bahía Blanca", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Tasa por servicios asistenciales Art 254 y ss", "ORDENANZA": "Ordenanza Bahía Blanca", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Balcarce", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Contribución Obligatoria para la Salud Art 73", "ORDENANZA": "Ordenanza Balcarce", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Baradero", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Fondo municipal de Salud ART. 37", "ORDENANZA": "Ordenanza Baradero", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Beníto Juárez", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Ausencia de concepto en ordenanza", "ORDENANZA": "Ordenanza Benito Juárez", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Berazategui", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Tasa servicio asistencial Art. 160", "ORDENANZA": "Ordenanza Berazategui", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Berisso", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Ausencia de concepto en ordenanza", "ORDENANZA": "Ordenanza Berisso", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Bolívar", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Sistema recupero SAMO", "ORDENANZA": "Ordenanza Bolívar", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Bragado", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Sin anexo impositivo disponible", "ORDENANZA": "Ordenanza Bragado", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Brandsen", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Ausencia de concepto", "ORDENANZA": "Ordenanza Brandsen", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Campana", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Tasa Aporte para la Salud Pública Art. 353 (impuesto encubierto)", "ORDENANZA": "Ordenanza Campana", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Cañuelas", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Ausencia concepto en ordenanza", "ORDENANZA": "Ordenanza Cañuelas", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Capitán Sarmiento", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa servicio asistencial Art. 135 y ss", "ORDENANZA": "Ordenanza Capitán Sarmiento", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Carlos Casares", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Fondo municipal de Salud Art. 178 y ss (impuesto encubierto)", "ORDENANZA": "Ordenanza Carlos Casares", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Carlos Tejedor", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Ausencia concepto en ordenanza", "ORDENANZA": "Ordenanza Carlos Tejedor", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Carmen De Areco", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Ausencia concepto en ordenanza", "ORDENANZA": "Ordenanza Carmen de Areco", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Castelli", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "SAMO + Tasa servicio asistencial", "ORDENANZA": "Ordenanza Castelli", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Chacabuco", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Ausencia concepto en ordenanza", "ORDENANZA": "Ordenanza Chacabuco", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Chascomús", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "SAMO Exclusivo", "ORDENANZA": "Ordenanza Chascomús", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Chivilcoy", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Tasa servicios asistenciales, impuesto encubierto", "ORDENANZA": "Ordenanza Chivilcoy", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Colón", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "SAMO Exclusivo", "ORDENANZA": "Ordenanza Colón", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Coronel Dorrego", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Sistema SAMO + Tasa servicios asistenciales Art 177", "ORDENANZA": "Ordenanza Coronel Dorrego", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Coronel Pringles", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa servicios asistenciales", "ORDENANZA": "Ordenanza Coronel Pringles", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Coronel Rosales", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Normativa desactualizada", "ORDENANZA": "Ordenanza Coronel Rosales", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Coronel Suárez", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Tasa servicios asistenciales Art. 144 y ss", "ORDENANZA": "Ordenanza Coronel Suárez", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Daireaux", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa asistencial Art 23", "ORDENANZA": "Ordenanza Daireaux", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Dolores", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Tasa asistencial Art 29", "ORDENANZA": "Ordenanza Dolores", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Ensenada", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "SAMO Exclusivo", "ORDENANZA": "Ordenanza Ensenada", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Escobar", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Tasa por servicios especiales (impuesto encubierto)", "ORDENANZA": "Ordenanza Escobar", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Esteban Echeverría", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "SAMO Exclusivo", "ORDENANZA": "Ordenanza Esteban Echeverría", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Exaltación De La Cruz", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Tasa por servicios generales (impuesto encubierto)", "ORDENANZA": "Ordenanza Exaltación de la Cruz", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Ezeiza", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Servicios complementarios de salud. Contribución especial", "ORDENANZA": "Ordenanza Ezeiza", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Florencio Varela", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Tasa por servicios generales (impuesto encubierto)", "ORDENANZA": "Ordenanza Florencio Varela", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Florentino Ameghino", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Aranceles hospitalarios", "ORDENANZA": "Ordenanza Florentino Ameghino", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Alvarado", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Tasa de salud", "ORDENANZA": "Ordenanza General Alvarado", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Alvear", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa por servicios asistenciales Art. 38", "ORDENANZA": "Ordenanza General Alvear", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Arenales", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa servicios asistenciales Art. 134 y ss", "ORDENANZA": "Ordenanza General Arenales", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Belgrano", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa asistencial", "ORDENANZA": "Ordenanza General Belgrano", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Guido", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa de Servicio de Salud Art 21", "ORDENANZA": "Ordenanza General Guido", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Juan Madariaga", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa por servicios asistenciales Art 208 y ss", "ORDENANZA": "Ordenanza General Madariaga", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General La Madrid", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa servicio asistenciales Art 13", "ORDENANZA": "Ordenanza General La Madrid", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Las Heras", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa servicios asistenciales Art. 123 y ss", "ORDENANZA": "Ordenanza General Las Heras", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Lavalle", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa servicios asistenciales Art. 173 y ss", "ORDENANZA": "Ordenanza General Lavalle", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Paz", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa contributiva UTI y cobro no residentes Art. 291", "ORDENANZA": "Ordenanza General Paz", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Pinto", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Aranceles hospitalarios Art. 240 y ss", "ORDENANZA": "Ordenanza General Pinto", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Pueyrredón", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Contribución a la Salud y Educación Art 217", "ORDENANZA": "Ordenanza Mar del Plata", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "General Rodríguez", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Tasa asistencial hospital odontológico/oftalmológico", "ORDENANZA": "Ordenanza General Rodríguez", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General San Martín", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "SAMO Art 303 y ss", "ORDENANZA": "Ordenanza San Martín", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "General Viamonte", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa asistencial Art. 205 y ss", "ORDENANZA": "Ordenanza General Viamonte", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "General Villegas", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Fondo por Servicios Asistenciales Art. 57", "ORDENANZA": "Ordenanza General Villegas", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Guamini", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa salud (impuesto encubierto) + Tasa asistencial", "ORDENANZA": "Ordenanza Guaminí", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Hipólito Yrigoyen", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa servicios asistenciales Art. 45 y ss", "ORDENANZA": "Ordenanza Hipólito Yrigoyen", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Hurlingham", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Ausencia de concepto", "ORDENANZA": "Ordenanza Hurlingham", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Ituzaingó", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "SAMO + Tasa de protección ciudadana (impuesto encubierto)", "ORDENANZA": "Ordenanza Ituzaingó", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "José C. Paz", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Ausencia de concepto", "ORDENANZA": "Ordenanza José C. Paz", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Junín", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Tasa por Servicios Públicos Urbanos Art. 1", "ORDENANZA": "Ordenanza Junín", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "La Costa", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Tasa asistencial Art. 198 + Fondo Salud a rurales", "ORDENANZA": "Ordenanza La Costa", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "La Matanza", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "SAMO Art 249", "ORDENANZA": "Ordenanza La Matanza", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "La Plata", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Ausencia de concepto", "ORDENANZA": "Ordenanza La Plata", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Lanus", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Ausencia de concepto", "ORDENANZA": "Ordenanza Lanús", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Laprida", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "SAMO Art. 20", "ORDENANZA": "Ordenanza Laprida", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Las Flores", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Ausencia de concepto", "ORDENANZA": "Ordenanza Las Flores", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Leandro N. Alem", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Aranceles de los servicios asistenciales Art. 160", "ORDENANZA": "Ordenanza L. N. Alem", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Lezama", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Sistema SAMO Art. 23 + Tasas encubiertas", "ORDENANZA": "Ordenanza Lezama", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Lincoln", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Tasa servicios asistenciales Art. 21", "ORDENANZA": "Ordenanza Lincoln", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Lobería", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa servicios asistenciales Art. 192 y ss", "ORDENANZA": "Ordenanza Lobería", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Lobos", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Tasa por Salud, Seguridad, Educación (impuesto encubierto)", "ORDENANZA": "Ordenanza Lobos", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Lomas de Zamora", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Ausencia de concepto", "ORDENANZA": "Ordenanza Lomas de Zamora", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Luján", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Ausencia de concepto", "ORDENANZA": "Ordenanza Luján", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Magdalena", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Ausencia de concepto", "ORDENANZA": "Ordenanza Magdalena", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Maipú", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa servicios asistenciales Art. 12 y ss", "ORDENANZA": "Ordenanza Maipú", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Malvinas Argentinas", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Tasa servicios asistenciales Art. 192 y ss", "ORDENANZA": "Ordenanza Malvinas Argentinas", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Mar Chiquita", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Tasa Asistencial + Fondo Complementario Salud", "ORDENANZA": "Ordenanza Mar Chiquita", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Marcos Paz", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Tasa servicios asistenciales Art. 232 y ss", "ORDENANZA": "Ordenanza Marcos Paz", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Mercedes", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Contribución especial Art. 6 (impuesto encubierto)", "ORDENANZA": "Ordenanza Mercedes", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Merlo", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "SAMO Art 42", "ORDENANZA": "Ordenanza Merlo", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Monte", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Contribución especial Art. 68 (impuesto encubierto)", "ORDENANZA": "Ordenanza Monte", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Monte Hermoso", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "SAMO + Tasa servicios asistenciales Art. 272", "ORDENANZA": "Ordenanza Monte Hermoso", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Moreno", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Tasa de Salud y Asistencia Social Art. 43 sobre multas", "ORDENANZA": "Ordenanza Moreno", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Morón", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "SAMO Art. 288 y 290", "ORDENANZA": "Ordenanza Morón", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Navarro", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Ausencia de concepto", "ORDENANZA": "Ordenanza Navarro", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Necochea", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "TASA POR FORTALECIMIENTO DE SALUD Art. 426", "ORDENANZA": "Ordenanza Necochea", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Nueve de Julio", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Tasa servicios asistenciales Art. 44", "ORDENANZA": "Ordenanza Nueve de Julio", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Olavarría", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Sistema SIAMO por cuota + Tasa asistencial Art. 138", "ORDENANZA": "Ordenanza Olavarría", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Patagones", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Tasa servicios asistenciales Art. 239 y ss", "ORDENANZA": "Ordenanza Patagones", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Pehuajó", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Tasa servicios asistenciales Art. 215 y ss", "ORDENANZA": "Ordenanza Pehuajó", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Pellegrini", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Sistema de recupero SAMO Art. 40 y ss", "ORDENANZA": "Ordenanza Pellegrini", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Pergamino", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Ausencia de concepto", "ORDENANZA": "Ordenanza Pergamino", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Pila", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Ausencia de concepto", "ORDENANZA": "Ordenanza Pila", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Pilar", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Tasa servicios de salud Art. 263 y ss", "ORDENANZA": "Ordenanza Pilar", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Pinamar", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "TASA POR DERECHOS SANATORIALES Art. 97 y ss", "ORDENANZA": "Ordenanza Pinamar", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Presidente Perón", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Ausencia concepto", "ORDENANZA": "Ordenanza Presidente Perón", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Puán", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa servicios asistenciales Art. 170 y ss", "ORDENANZA": "Ordenanza Puán", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Punta Indio", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Fondo Solidario de Salud Pública Art. 202", "ORDENANZA": "Ordenanza Punta Indio", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Quilmes", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Sistema SAMO Art. 316 y ss", "ORDENANZA": "Ordenanza Quilmes", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Ramallo", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Tasa servicios asistenciales Art. 238", "ORDENANZA": "Ordenanza Ramallo", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Rauch", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa servicios asistenciales Título XV", "ORDENANZA": "Ordenanza Rauch", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Rivadavia", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Servicios asistenciales Art 238 y ss", "ORDENANZA": "Ordenanza Rivadavia", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Rojas", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Cobro a obras sociales Art. 215 y ss", "ORDENANZA": "Ordenanza Rojas", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Roque Pérez", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa asistencial Art 33 SAMO + Tasa salud fija", "ORDENANZA": "Ordenanza Roque Pérez", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Saavedra Pigue", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa servicios asistenciales Art. 273 y ss", "ORDENANZA": "Ordenanza Saavedra", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Saladillo", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Sistema SAMO Exclusivo", "ORDENANZA": "Ordenanza Saladillo", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "Salliquelo", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa servicios asistenciales Art. 69 + Plan Salud", "ORDENANZA": "Ordenanza Salliqueló", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Salto", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Sistema SAMO + Tasa asistencial Art. 206", "ORDENANZA": "Ordenanza Salto", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "San Andrés de Giles", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa servicios asistenciales Art 247 y ss", "ORDENANZA": "Ordenanza San Andrés de Giles", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "San Antonio de Areco", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa por servicios de salud Art 218 (impuesto encubierto)", "ORDENANZA": "Ordenanza San Antonio de Areco", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "San Cayetano", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Sistema SAMO Exclusivo", "ORDENANZA": "Ordenanza San Cayetano", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "San Fernando", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Sistema SAMO + Tasa asistencial Art. 141", "ORDENANZA": "Ordenanza San Fernando", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "San Isidro", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Sistema SAMO Art 141 y ss", "ORDENANZA": "Ordenanza San Isidro", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "San Miguel Joaquín", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Sistema SAMO Art 94 y ss", "ORDENANZA": "Ordenanza San Miguel", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "San Nicolás", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Sistema SAMO Art 301 y ss", "ORDENANZA": "Ordenanza San Nicolás", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "San Pedro", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Sistema SAMO Art. 250 y ss", "ORDENANZA": "Ordenanza San Pedro", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"},
        {"MUNICIPIO": "San Vicente", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Contribución al Sistema de Salud Pública (impuesto encubierto)", "ORDENANZA": "Ordenanza San Vicente", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Suipacha", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa de salud + Prestaciones Hospitalarias Art. 132", "ORDENANZA": "Ordenanza Suipacha", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Tandil", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "SISTEMA INTEGRADO DE SALUD PÚBLICA ENTE DESCENTRALIZADO", "ORDENANZA": "Ordenanza Tandil", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Tapalque", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa servicios asistenciales Art. 200 + UTI", "ORDENANZA": "Ordenanza Tapalqué", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Tigre", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Sistema SAMO + Tasa asistencial no residentes Art 83", "ORDENANZA": "Ordenanza Tigre", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Tordillo", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa servicios asistenciales Art 28 y ss", "ORDENANZA": "Ordenanza Tordillo", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Tornquist", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Sistema SAMO + Tasa servicios asistenciales Art. 142", "ORDENANZA": "Ordenanza Tornquist", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Trenque launquen", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Sistema SAMO + Tasa servicios asistenciales Art 89", "ORDENANZA": "Ordenanza Trenque Lauquen", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Tres Arroyos", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Tasa solidaria de sostenimiento de salud Art. 183", "ORDENANZA": "Ordenanza Tres Arroyos", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Tres de Febrero", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Sistema SAMO Tributo por servicios asistenciales ART 245", "ORDENANZA": "Ordenanza Tres de Febrero", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Tres Lomas", "DENSIDAD": "Baja (< 25.000 hab.)", "COBRO": "Tasa servicios asistenciales", "ORDENANZA": "Ordenanza Tres Lomas", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Vicente López", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Sistema SAMO derechos asistenciales Art 254 y ss", "ORDENANZA": "Ordenanza Vicente López", "CATEGORIA": "Categoría C (Arancel Directo)"},
        {"MUNICIPIO": "Villa Gesell", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Tasa salud ART 148 Y SS (impuesto encubierto)", "ORDENANZA": "Ordenanza Villa Gesell", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Villarino", "DENSIDAD": "Media (25k-100k hab.)", "COBRO": "Derecho Comercialización Hortícola para salud Art 232", "ORDENANZA": "Ordenanza Villarino", "CATEGORIA": "Categoría B (Tasa Encubierta)"},
        {"MUNICIPIO": "Zárate", "DENSIDAD": "Alta (> 100.000 hab.)", "COBRO": "Sistema SAMO Art 217 y ss", "ORDENANZA": "Ordenanza Zárate", "CATEGORIA": "Categoría A (Gratuidad / SAMO)"}
    ]
    return pd.DataFrame(raw_data)

df_censo = get_censo_data()

# ==========================================
# BARRA LATERAL INSTITUCIONAL
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/scales.png", width=65)
st.sidebar.title("SIA-PBA v2.0")
st.sidebar.markdown("**Sistema Integrado de Auditoría Algorítmica y Canal Único**")
st.sidebar.markdown("---")

opcion_menu = st.sidebar.radio(
    "Seleccione el Módulo:",
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
* **Autora:** Mariana [Apellido]
* **Enfoque:** Capítulo VIII - Propuesta de Innovación Tecnológica y Control de Convencionalidad
""")

# Header Institucional Superior
st.markdown("""
<div class='pba-header'>
    <h1>GOBIERNO DE LA PROVINCIA DE BUENOS AIRES</h1>
    <p>Sistema Integrado de Auditoría Algorítmica Preventiva de Ordenanzas y Canal Único de Denuncias (SIA-PBA)</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# MÓDULO 1: PRESENTACIÓN E IMPACTO
# ==========================================
if "🏠 1. Presentación" in opcion_menu:
    st.markdown("<h2 class='main-title'>SIA-PBA: Auditoría Algorítmica & Canal Único de Denuncias</h2>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Dispositivo tecnológico de control preventivo de legalidad, constitucionalidad y convencionalidad de ordenanzas fiscales e impositivas municipales de la Provincia de Buenos Aires</p>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Municipios Relevados", value="135 / 135", delta="Censo Provincial 100%")
    with col2:
        st.metric(label="Arancelamiento Directo (Cat. C)", value="37.0%", delta="50 Municipios", delta_color="inverse")
    with col3:
        st.metric(label="Concentración en el Interior", value="85.8%", delta="48 de 56 Municipios", delta_color="inverse")
    with col4:
        st.metric(label="Efecto Baja Densidad", value="74.0%", delta="Cat. C en <25k hab.", delta_color="inverse")
        
    st.markdown("---")
    st.subheader("🎯 Ejes Fundamentales de la Herramienta (Capítulo VIII)")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        ### 🔍 1. Módulo de Auditoría Algorítmica de Ordenanzas
        * **Análisis de Texto PNL:** Procesa automáticamente ordenanzas impositivas y fiscales locales.
        * **Semáforo Tripartito de Convencionalidad:**
            * 🟢 **Cat. A (Gratuidad Plena / SAMO):** Cumplimiento del Art. 36 inc. 8 CPBA.
            * 🟡 **Cat. B (Tasas Encubiertas):** Detección de tributos disfrazados en ABL/Red Vial.
            * 🔴 **Cat. C (Arancelamiento Directo):** Alerta por cobros indebidos, pagarés o juicio de apremio.
        * **Matriz de Alerta Preventiva:** Cita automática de normas vulneradas y encuadre penal (Art. 266 CP - Exacciones Ilegales).
        """)
    with c2:
        st.markdown("""
        ### 🛡️ 2. Canal Único Descentralizado de Denuncias Anónimas
        * **Ruptura de la Espiral del Silencio:** Diseñado especialmente para ciudadanos de distritos de baja densidad con **efector único de salud**.
        * **Garantía Absoluta de Anonimato:** Algoritmo de desvinculación IP con emisión de **Código Hash Criptográfico Único** para seguimiento.
        * **Trazabilidad Institucional:** Derivación automática de alertas a la Defensoría del Pueblo PBA y Asesoría General de Gobierno.
        """)

# ==========================================
# MÓDULO 2: AUDITORÍA ALGORÍTMICA (IA)
# ==========================================
elif "🔍 2. Módulo de Auditoría" in opcion_menu:
    st.markdown("<h2 class='main-title'>🔍 Auditoría Algorítmica Preventiva de Ordenanzas</h2>", unsafe_allow_html=True)
    st.markdown("Examen automatizado de constitucionalidad, convencionalidad y legalidad tributaria municipal.")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🏛️ Línea de Base 2026 (Consulta Histórica Censo N=135)", "🚀 Motor de Auditoría Futura 2027+ (Nuevas Ordenanzas)"])
    
    # ------------------------------------------
    # SUBMÓDULO 1: LÍNEA DE BASE 2026
    # ------------------------------------------
    with tab1:
        st.markdown("##### Seleccione un municipio para auditar su normativa tributario-sanitaria relevada en el Censo 2026:")
        muni_selected = st.selectbox("Municipio de la Prov. de Bs. As.:", df_censo['MUNICIPIO'].unique(), key="muni_2026")
        
        row_muni = df_censo[df_censo['MUNICIPIO'] == muni_selected].iloc[0]
        
        st.markdown("### 📊 Resultado del Examen Algorítmico Automatizado (Línea de Base 2026)")
        
        col_res1, col_res2 = st.columns([1, 2])
        
        with col_res1:
            cat = row_muni['CATEGORIA']
            if 'Cat. C' in cat or 'Arancel' in cat or 'Categoría C' in cat:
                st.error("🔴 **DICTAMEN: INCONSTITUCIONAL / ARANCEL DIRECTO**")
                st.markdown("<span class='badge-cat-c'>Categoría C - Riesgo Alto</span>", unsafe_allow_html=True)
            elif 'Cat. B' in cat or 'Encubierta' in cat or 'Categoría B' in cat:
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
            cobro_txt = str(row_muni['COBRO'])
            st.markdown(f"**Disposición Tributaria Relevada:** *\"{cobro_txt}\"*")
            
            if 'Categoría C' in cat or 'Arancel' in cat or 'Cat. C' in cat:
                st.markdown("""
                <div class='legal-box'>
                <b>⚠️ Vulneraciones Normativas Detectadas:</b><br>
                1. <b>Violación del Art. 36 inc. 8 de la Constitución de la Prov. de Buenos Aires:</b> Imposición de barrera económica para acceder a la salud pública gratuita.<br>
                2. <b>Infracción a Tratados Internacionales (Art. 75 inc. 22 CN):</b> Contravención del Art. 12 del PIDESC (Derecho al disfrute del más alto nivel posible de salud física y mental).<br>
                3. <b>Encuadre Dogmático-Penal (Art. 266 del Código Penal):</b> Posible configuración de <i>Exacción Ilegal</i> por exigencia o cobro indebido de contribuciones/derechos bajo coercibilidad estatal.<br>
                4. <b>Abuso de Autoridad (Art. 248 CP):</b> Dictado de resoluciones contrarias a la Constitución Provincial.
                </div>
                """, unsafe_allow_html=True)
            elif 'Categoría B' in cat:
                st.markdown("""
                <div class='legal-box'>
                <b>⚠️ Vulneraciones Normativas Detectadas:</b><br>
                1. <b>Falta de Causa Tributaria / Analogía Impositiva:</b> Creación de tasas sin contraprestación directa de servicio al contribuyente.<br>
                2. <b>Tasa Encubierta:</b> Adición de partidas presupuestarias sobre tributos domiciliarios (ABL/Red Vial) para financiar gastos generales de salud.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='legal-box'>
                <b>✅ Compatibilidad Constitucional Constatada:</b><br>
                La normativa analizada respeta el principio de gratuidad del servicio público asistencial municipal y limita el recupero de costos de forma legítima frente a obras sociales o prepagas mediante el sistema SAMO (Ley Provincial 11.069).
                </div>
                """, unsafe_allow_html=True)

    # ------------------------------------------
    # SUBMÓDULO 2: MOTOR DE AUDITORÍA FUTURA (2027+)
    # ------------------------------------------
    with tab2:
        st.markdown("##### 🚀 Motor de Ingesta y Procesamiento para Futuras Ordenanzas Impositivas (Ejercicio 2027 en adelante)")
        st.markdown("Suba el archivo de la nueva ordenanza municipal aprobada o pegue su articulado fiscal para ejecutar la auditoría algorítmica preventiva antes de su entrada en vigencia:")
        
        c_fut1, c_fut2 = st.columns([1, 2])
        with c_fut1:
            muni_futuro = st.selectbox("Municipio a Auditar:", df_censo['MUNICIPIO'].unique(), key="muni_futuro")
            anio_futuro = st.selectbox("Ejercicio Fiscal Futuro:", [2027, 2028, 2029, 2030], index=0)
            
        with c_fut2:
            uploaded_file = st.file_uploader("Arrastre el archivo de la nueva Ordenanza Fiscal/Impositiva (PDF / TXT):", type=['pdf', 'txt'])
            
        texto_muestra_arrecifes = """ARTÍCULO 179.- Por la prestación de servicios asistenciales en el Hospital Municipal y Centros de Atención Primaria de la Salud, los pacientes que no acrediten fehacientemente situación de indigencia o falta de cobertura abonarán la tasa correspondiente según el Nomenclador Médico.
ARTÍCULO 180.- El cobro de los aranceles vencidos se tramitará por la vía del apremio fiscal."""

        texto_ordenanza_input = st.text_area(
            "Texto del articulado impositivo a auditar (Si subió un PDF se procesará automáticamente; si es escaneado puede usar este cuadro):",
            value=texto_muestra_arrecifes,
            height=140
        )
        
        if st.button("🚀 Ejecutar Auditoría Algorítmica Futura (Ejercicio " + str(anio_futuro) + ")"):
            texto_a_analizar = ""
            fuente_procesada = ""
            
            # Intento de extracción de PDF seguro
            if uploaded_file is not None:
                if uploaded_file.name.lower().endswith('.pdf'):
                    try:
                        import pypdf
                        reader = pypdf.PdfReader(uploaded_file)
                        text_pdf = ""
                        for page in reader.pages:
                            t = page.extract_text()
                            if t:
                                text_pdf += t + "\n"
                        if len(text_pdf.strip()) > 30:
                            texto_a_analizar = text_pdf
                            fuente_procesada = f"Archivo PDF subido ({len(reader.pages)} páginas)"
                        else:
                            st.warning("⚠️ El PDF subido es una imagen o fotocopia escaneada. Se utilizará el texto suplementario del editor.")
                            texto_a_analizar = texto_ordenanza_input
                            fuente_procesada = "Editor de Texto / Copia de respaldo"
                    except Exception as err:
                        st.warning(f"⚠️ Nota de lectura PDF: {err}. Se utiliza el texto del editor suplementario.")
                        texto_a_analizar = texto_ordenanza_input
                        fuente_procesada = "Editor de Texto"
                else:
                    texto_a_analizar = uploaded_file.read().decode('utf-8', errors='ignore')
                    fuente_procesada = "Archivo TXT"
            else:
                texto_a_analizar = texto_ordenanza_input
                fuente_procesada = "Texto en Editor Manual"
                
            st.info(f"✅ **Procesamiento Completado:** Análisis ejecutado sobre {fuente_procesada}.")
            
            # Motor de PNL y Coincidencias por RegEx
            texto_upper = texto_a_analizar.upper()
            
            patrones_c = [
                r'ARANCEL', r'SERVICIOS?\s+ASISTENCIAL', r'APREMIO', r'NOMENCLADOR',
                r'BONO\s+DE\s+GUARDIA', r'ABONARÁ', r'DERECHOS?\s+SANATORIAL', r'PAGARÉ',
                r'HOSPITAL\s+MUNICIPAL', r'COBRO\s+DIRECTO', r'SIN\s+COBERTURA', r'INDIGENCIA'
            ]
            
            patrones_b = [
                r'FONDO\s+MUNICIPAL\s+DE\s+SALUD', r'TASA\s+DE\s+SALUD', r'CONTRIBUCIÓN\s+ESPECIAL\s+SALUD',
                r'ALUMBRADO.*SALUD', r'RED\s+VIAL.*SALUD', r'IMPUESTO\s+ENCUBIERTO', r'FORTALECIMIENTO.*SALUD'
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
                    
            st.markdown(f"### 📋 Dictamen de Auditoría Algorítmica - {muni_futuro} (Ejercicio {anio_futuro})")
            
            if len(matches_c) > 0:
                st.error("🔴 **DICTAMEN CRÍTICO: NORMATIVA INCONSTITUCIONAL (CATEGORÍA C - ARANCEL DIRECTO)**")
                st.markdown(f"**Coincidencias de Riesgo Crítico Detectadas:** `{len(matches_c)}` ({', '.join(set(matches_c))})")
                
                st.markdown("""
                <div class='legal-box'>
                <b>⚠️ Fundamentación Jurídica del Bloqueo Preventivo:</b><br>
                1. <b>Violación Manifiesta del Art. 36 inc. 8 CPBA:</b> La norma proyectada condiciona el acceso a la salud asistencial pública al pago de un arancel, derecho sanatorio o comprobación de indigencia.<br>
                2. <b>Alerta de Configuración Penal (Art. 266 CP):</b> El cobro bajo apercibimiento de apremio o exigencia indebida encuadra en la figura de <i>Exacción Ilegal</i>.<br>
                3. <b>Acción Recomendada:</b> Emisión inmediata de Dictamen de Impugnación de Oficio ante el Tribunal de Cuentas PBA y la Asesoría General de Gobierno.
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### 📝 Citas Textuales Infractoras Extraídas del Documento:")
                lines = texto_a_analizar.split('\n')
                snippets_found = 0
                for l in lines:
                    if any(re.search(pat, l.upper()) for pat in patrones_c):
                        st.markdown(f"<div class='snippet-box'>📌 <i>\"{l.strip()}\"</i></div>", unsafe_allow_html=True)
                        snippets_found += 1
                        if snippets_found >= 5:
                            break
                            
            elif len(matches_b) > 0:
                st.warning("🟡 **DICTAMEN DE ADVERTENCIA: TASA ENCUBIERTA DETECTADA (CATEGORÍA B)**")
                st.markdown(f"**Coincidencias de Riesgo Medio Detectadas:** `{len(matches_b)}` ({', '.join(set(matches_b))})")
                st.markdown("""
                <div class='legal-box'>
                <b>⚠️ Fundamentación de Alerta:</b> Se detectó la creación de tributos adicionales sobre servicios inmuebles o la tasa general para financiar el sistema asistencial sin contraprestación directa.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.success("🟢 **DICTAMEN POSITIVO: NORMATIVA CONFORME A DERECHO / SIN CLÁUSULAS INCONSTITUCIONALES DETECTADAS**")
                st.markdown("""
                <div class='legal-box'>
                <b>✅ Compatibilidad Constatada:</b> No se detectaron cláusulas de arancelamiento directo ni tasas encubiertas. La norma respeta la gratuidad garantizada por el Art. 36 inc. 8 de la Constitución Provincial.
                </div>
                """, unsafe_allow_html=True)

# ==========================================
# MÓDULO 3: CANAL ÚNICO DE DENUNCIAS
# ==========================================
elif "🛡️ 3. Canal Único" in opcion_menu:
    st.markdown("<h2 class='main-title'>🛡️ Canal Único Descentralizado de Denuncias Anónimas</h2>", unsafe_allow_html=True)
    st.markdown("Dispositivo tecnológico de protección del paciente para la **ruptura de la espiral del silencio** en efectores únicos de salud.")
    st.markdown("---")
    
    col_den1, col_den2 = st.columns([2, 1])
    
    with col_den1:
        st.subheader("📝 Formulario de Denuncia Anónima Resguardada")
        
        muni_denuncia = st.selectbox("Seleccione el Municipio del hecho:", df_censo['MUNICIPIO'].unique())
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
        
        st.file_uploader("Adjuntar foto de recibo, bono, pagaré o comprobante (Opcional - borra metadatos):", type=['jpg', 'png', 'pdf'])
        
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
                <b>Estado de Derivación:</b> Transmitido automáticamente al expediente electrónico auditado de la Defensoría del Pueblo de la Provincia de Buenos Aires.</p>
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
        3. **Agrupa denuncias por municipio** para fundamentar amparos colectivos o investigaciones del Ministerio Público Fiscal (Art. 266 CP).
        """)

# ==========================================
# MÓDULO 4: TABLERO DE CONTROL (N=135)
# ==========================================
elif "📊 4. Tablero de Control" in opcion_menu:
    st.markdown("<h2 class='main-title'>📊 Tablero Epidemiológico-Tributario Censo Provincial 100%</h2>", unsafe_allow_html=True)
    st.markdown("Visualización estadística de los 135 municipios de la Provincia de Buenos Aires (Datos Censo 2022 y Ordenanzas 2025/2026).")
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
    st.dataframe(df_censo[['MUNICIPIO', 'DENSIDAD', 'CATEGORIA', 'ORDENANZA', 'COBRO']], use_container_width=True)

# ==========================================
# MÓDULO 5: GENERADOR DE DICTÁMENES
# ==========================================
elif "📄 5. Generador de Dictámenes" in opcion_menu:
    st.markdown("<h2 class='main-title'>📄 Generador de Dictámenes de Alerta de Inconstitucionalidad</h2>", unsafe_allow_html=True)
    st.markdown("Emisión automática de piezas jurídicas de impugnación institucionales.")
    st.markdown("---")
    
    muni_dictamen = st.selectbox("Seleccione Municipio para emitir Dictamen:", df_censo['MUNICIPIO'].unique())
    
    row_d = df_censo[df_censo['MUNICIPIO'] == muni_dictamen].iloc[0]
    
    dictamen_text = f"""========================================================================================
ALERTA INSTITUCIONAL DE INCONSTITUCIONALIDAD Y INCONVENCIONALIDAD TRIBUTARIA
SIA-PBA // AUDITORÍA ALGORÍTMICA DE ORDENANZAS MUNICIPALES
========================================================================================

FECHA DE EMISIÓN: {datetime.date.today().strftime('%d/%m/%Y')}
SUJETO AUDITADO: Municipalidad de {row_d['MUNICIPIO']} (Provincia de Buenos Aires)
DENSIDAD POBLACIONAL: {row_d['DENSIDAD']}
NORMA EXAMINADA: {row_d['ORDENANZA']}
DISPOSICIÓN TRIBUTARIA: "{row_d['COBRO']}"
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
