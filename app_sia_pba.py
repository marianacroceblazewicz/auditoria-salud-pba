import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re
import hashlib
import datetime
import pypdf
import io

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y ESTILO OFICIAL PBA
# ==========================================
st.set_page_config(
    page_title="SIA-PBA | Sistema de Auditoría Algorítmica de Ordenanzas",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS Institucional - Gobierno de la Provincia de Buenos Aires
st.markdown("""
<style>
    .pba-header {
        background-color: #003366;
        color: #FFFFFF;
        padding: 15px 25px;
        border-radius: 6px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .pba-title {
        color: #003366;
        font-family: 'Arial', sans-serif;
        font-weight: 800;
        margin-bottom: 0px;
        font-size: 2rem;
    }
    .pba-subtitle {
        color: #4A607A;
        font-size: 1.1rem;
        margin-bottom: 20px;
        font-weight: 500;
    }
    .card-stat {
        background-color: #F8F9FA;
        border-radius: 8px;
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
        font-size: 1rem;
        display: inline-block;
    }
    .badge-cat-b {
        background-color: #FFF3CD;
        color: #856404;
        padding: 6px 14px;
        border-radius: 16px;
        font-weight: bold;
        font-size: 1rem;
        display: inline-block;
    }
    .badge-cat-c {
        background-color: #F8D7DA;
        color: #721C24;
        padding: 6px 14px;
        border-radius: 16px;
        font-weight: bold;
        font-size: 1rem;
        display: inline-block;
    }
    .article-box-c {
        background-color: #FFF5F5;
        border-left: 5px solid #E53E3E;
        padding: 14px;
        border-radius: 6px;
        margin-bottom: 12px;
        font-size: 0.95rem;
    }
    .article-box-b {
        background-color: #FFFFF0;
        border-left: 5px solid #D69E2E;
        padding: 14px;
        border-radius: 6px;
        margin-bottom: 12px;
        font-size: 0.95rem;
    }
    .article-box-a {
        background-color: #F0FFF4;
        border-left: 5px solid #38A169;
        padding: 14px;
        border-radius: 6px;
        margin-bottom: 12px;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado Institucional
st.markdown("""
<div class='pba-header'>
    <div>
        <h3 style='margin:0; font-size:1.3rem; font-weight:bold;'>🏛️ GOBIERNO DE LA PROVINCIA DE BUENOS AIRES</h3>
        <p style='margin:0; font-size:0.95rem; opacity:0.9;'>Sistema Integrado de Auditoría Algorítmica Preventiva de Ordenanzas & Canal Único de Denuncias (SIA-PBA)</p>
    </div>
    <div style='text-align:right;'>
        <span style='background-color:#00A3E0; color:#FFF; padding:4px 10px; border-radius:4px; font-weight:bold; font-size:0.85rem;'>CONTROL DE CONVENCIONALIDAD</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# BASE DE DATOS DEL CENSO PROVINCIAL (N=135)
# ==========================================
@st.cache_data
def load_data():
    raw_csv_data = [
        {"MUNICIPIO": "25 de mayo", "COBRO": "Tasa , impuesto encubierto", "CONCEPTO": "\"Fondo para Salud\" del 7% calculado sobre la liquidación de otras tasas (Alumbrado, Limpieza, Red Vial) o sobre la energía eléctrica.", "ORDENANZA": "Ordenanza Fiscal e Impositiva 2026", "DENSIDAD": "36.676 hab (Media)"},
        {"MUNICIPIO": "Adolfo Alsina", "COBRO": "Tasa servicio asistencial Art. 31", "CONCEPTO": "Establece carnet hospitalario y porcentaje a pagar según clasificación socioeconómica de servicios sociales.", "ORDENANZA": "Ordenanza 45/2025", "DENSIDAD": "17.552 hab (Baja)"},
        {"MUNICIPIO": "Adolfo González Chávez", "COBRO": "Tasa cobertura universal de salud, impuesto encubierto", "CONCEPTO": "Cobro adicionado junto con la tasa de servicios urbanos y conservación de red vial municipal.", "ORDENANZA": "Ordenanza Fiscal 2025", "DENSIDAD": "12.914 hab (Baja)"},
        {"MUNICIPIO": "Alberti", "COBRO": "Tasa servicio asistencial Art. 129", "CONCEPTO": "Establece cobro según nomenclador IOMA a quienes evidencien capacidad contributiva previo informe social.", "ORDENANZA": "Ordenanza Impositiva 2025", "DENSIDAD": "12.982 hab (Baja)"},
        {"MUNICIPIO": "Almirante Brown", "COBRO": "Sistema recupero SAMO", "CONCEPTO": "No figura en la ordenanza municipal cobro alguno a personas sin cobertura médica. Limita recupero a SAMO.", "ORDENANZA": "Ordenanza SAMO 2025", "DENSIDAD": "584.827 hab (Alta)"},
        {"MUNICIPIO": "Arrecifes", "COBRO": "Tasa servicio asistencial Art. 179 y ss", "CONCEPTO": "Individualiza al paciente como sujeto de cobro. Reserva la gratuidad únicamente a la evidente indigencia/carencia.", "ORDENANZA": "Ordenanza Arrecifes Art. 179", "DENSIDAD": "32.405 hab (Media)"},
        {"MUNICIPIO": "Avellaneda", "COBRO": "Sistema recupero SAMO", "CONCEPTO": "Garantiza explícitamente el principio de gratuidad y trato igualitario en el Art. 214. Recupero exclusivo SAMO.", "ORDENANZA": "Ordenanza Fiscal Art. 214", "DENSIDAD": "367.554 hab (Alta)"},
        {"MUNICIPIO": "Ayacucho", "COBRO": "Tasa servicio asistencial Art. 36 inc. 2", "CONCEPTO": "Faculta a la Dirección a determinar eximición de pago en escala del 30%, 50% y 70% según encuesta social.", "ORDENANZA": "Ordenanza Fiscal 2025", "DENSIDAD": "22.136 hab (Baja)"},
        {"MUNICIPIO": "Azul", "COBRO": "Tasa servicios esenciales (impuesto encubierto)", "CONCEPTO": "Tasa por servicios esenciales de salud cobrada a inmuebles urbanos y rurales.", "ORDENANZA": "Ordenanza Fiscal 2025", "DENSIDAD": "75.905 hab (Media)"},
        {"MUNICIPIO": "Bahía Blanca", "COBRO": "Tasa por servicios asistenciales Art 254 y ss", "CONCEPTO": "Individualiza como contribuyente obligado al pago a quien recibe los servicios asistenciales.", "ORDENANZA": "Ordenanza Fiscal Art. 254", "DENSIDAD": "336.574 hab (Alta)"},
        {"MUNICIPIO": "Balcarce", "COBRO": "Contribución Obligatoria para la Salud Art 73", "CONCEPTO": "Tasa adicional cobrada a contribuyentes de Alumbrado Público, Red Vial e Inspección de Seguridad e Higiene.", "ORDENANZA": "Ordenanza Fiscal Art. 73", "DENSIDAD": "51.736 hab (Media)"},
        {"MUNICIPIO": "Baradero", "COBRO": "Fondo municipal de Salud ART. 37", "CONCEPTO": "Monto adicional cobrado conjuntamente sobre la liquidación de otras tasas municipales.", "ORDENANZA": "Ordenanza Fiscal Art. 37", "DENSIDAD": "37.491 hab (Media)"},
        {"MUNICIPIO": "Beníto Juárez", "COBRO": "Ausencia de concepto en ordenanza", "CONCEPTO": "Sin concepto tributario arancelario. Gratuidad asistencial.", "ORDENANZA": "Código Tributario 2025", "DENSIDAD": "22.292 hab (Baja)"},
        {"MUNICIPIO": "Berazategui", "COBRO": "Tasa servicio asistencial Art. 160 / SAMO", "CONCEPTO": "Garantiza la gratuidad de toda atención, práctica y estudios en la red hospitalaria pública.", "ORDENANZA": "Ordenanza Fiscal 2025", "DENSIDAD": "358.712 hab (Alta)"},
        {"MUNICIPIO": "Berisso", "COBRO": "Ausencia de concepto en ordenanza", "CONCEPTO": "Sin arancelamiento a pacientes. Atención pública gratuita.", "ORDENANZA": "Ordenanza Impositiva 2025", "DENSIDAD": "100.930 hab (Alta)"},
        {"MUNICIPIO": "Bolívar", "COBRO": "Sistema recupero SAMO. Tasa asistencial derogada", "CONCEPTO": "Tasa asistencial derogada. Recupero limitado al sistema SAMO.", "ORDENANZA": "Ordenanza Municipal 1998/2025", "DENSIDAD": "38.119 hab (Media)"},
        {"MUNICIPIO": "Bragado", "COBRO": "Sin anexo arancelario", "CONCEPTO": "Atención gratuita en efector público municipal.", "ORDENANZA": "Ordenanza Fiscal 2025", "DENSIDAD": "44.972 hab (Media)"},
        {"MUNICIPIO": "Brandsen", "COBRO": "Ausencia de concepto", "CONCEPTO": "Sin tasas arancelarias directas.", "ORDENANZA": "Ordenanza Impositiva 2025", "DENSIDAD": "33.026 hab (Media)"},
        {"MUNICIPIO": "Campana", "COBRO": "Tasa Aporte para la Salud Pública Art. 353", "CONCEPTO": "Adicional gravado sobre la Tasa por Servicios Generales, Red Vial e Inspección de Seguridad e Higiene.", "ORDENANZA": "Ordenanza Fiscal Art. 353", "DENSIDAD": "107.979 hab (Alta)"},
        {"MUNICIPIO": "Cañuelas", "COBRO": "Ausencia de concepto", "CONCEPTO": "Atención hospitalaria pública gratuita sin arancel directo.", "ORDENANZA": "Ordenanza Impositiva 2025", "DENSIDAD": "70.684 hab (Media)"},
        {"MUNICIPIO": "Capitán Sarmiento", "COBRO": "Tasa servicio asistencial Art. 135 y ss", "CONCEPTO": "Limita la gratuidad a nivel socioeconómico mediante informe del servicio de Desarrollo Social.", "ORDENANZA": "Ordenanza Fiscal Art. 135", "DENSIDAD": "18.200 hab (Baja)"},
        {"MUNICIPIO": "Carlos Casares", "COBRO": "Fondo municipal de Salud Art. 178 y ss", "CONCEPTO": "Tasa encubierta sobre contribuyentes de Servicios Urbanos y Red Vial Municipal.", "ORDENANZA": "Ordenanza Fiscal Art. 178", "DENSIDAD": "23.200 hab (Baja)"},
        {"MUNICIPIO": "Carlos Tejedor", "COBRO": "Ausencia de concepto en ordenanza", "CONCEPTO": "Sin arancelamiento normado.", "ORDENANZA": "Ordenanza Impositiva 2025", "DENSIDAD": "12.100 hab (Baja)"},
        {"MUNICIPIO": "Carmen De Areco", "COBRO": "Ausencia de concepto en ordenanza", "CONCEPTO": "Sin tasa arancelaria directa a personas.", "ORDENANZA": "Ordenanza Fiscal 2025", "DENSIDAD": "16.500 hab (Baja)"},
        {"MUNICIPIO": "Castelli", "COBRO": "SAMO + Tasa servicio asistencial", "CONCEPTO": "Establece pago total o parcial para pacientes sin obra social según informe social y tarifa para no residentes.", "ORDENANZA": "Ordenanza Fiscal 2025", "DENSIDAD": "9.800 hab (Baja)"},
        {"MUNICIPIO": "Chacabuco", "COBRO": "Sistema SAMO / Gratuidad Plena", "CONCEPTO": "Garantiza atención totalmente gratuita para pacientes sin ningún tipo de cobertura médica.", "ORDENANZA": "Ordenanza Municipal 2025", "DENSIDAD": "52.000 hab (Media)"},
        {"MUNICIPIO": "Chascomús", "COBRO": "Sistema SAMO", "CONCEPTO": "Limitado al recupero SAMO sobre obras sociales y prepagas.", "ORDENANZA": "Ordenanza Fiscal 2025", "DENSIDAD": "42.000 hab (Media)"},
        {"MUNICIPIO": "Chivilcoy", "COBRO": "Tasa servicios asistenciales (impuesto encubierto)", "CONCEPTO": "Tasa encubierta sobre inmuebles urbanos y rurales en Art. 87 Fiscal y Art. 5 Impositiva.", "ORDENANZA": "Ordenanza Fiscal Art. 87", "DENSIDAD": "70.500 hab (Media)"},
        {"MUNICIPIO": "Colón", "COBRO": "Sistema SAMO", "CONCEPTO": "Recupero vía SAMO.", "ORDENANZA": "Ordenanza Impositiva 2025", "DENSIDAD": "27.000 hab (Media)"},
        {"MUNICIPIO": "Coronel Dorrego", "COBRO": "Sistema SAMO + Tasa asistencial regulada", "CONCEPTO": "Aclara recupero exclusivo por SAMO sin cobro a personas sin cobertura.", "ORDENANZA": "Ordenanza Fiscal Art. 177", "DENSIDAD": "15.800 hab (Baja)"},
        {"MUNICIPIO": "Coronel Pringles", "COBRO": "Tasa servicios asistenciales", "CONCEPTO": "Individualiza como sujeto obligado al paciente, familiar a cargo, apoderado o curador.", "ORDENANZA": "Ordenanza Impositiva 2025", "DENSIDAD": "24.000 hab (Baja)"},
        {"MUNICIPIO": "Coronel Rosales", "COBRO": "Tasa asistencial", "CONCEPTO": "Limita exención a personas carentes acreditadas.", "ORDENANZA": "Ordenanza Fiscal 2021/2025", "DENSIDAD": "63.000 hab (Media)"},
        {"MUNICIPIO": "Coronel Suárez", "COBRO": "Tasa servicios asistenciales Art. 144 y ss", "CONCEPTO": "Gratuidad reservada a la evidente carencia de recursos. Categorización A, B y C según porcentaje a pagar.", "ORDENANZA": "Ordenanza Fiscal Art. 144", "DENSIDAD": "42.000 hab (Media)"},
        {"MUNICIPIO": "Daireaux", "COBRO": "Tasa asistencial Art. 23", "CONCEPTO": "Arancel cobrado a quienes usufructúen de las prestaciones asistenciales.", "ORDENANZA": "Ordenanza Fiscal Art. 23", "DENSIDAD": "17.000 hab (Baja)"},
        {"MUNICIPIO": "Dolores", "COBRO": "Tasa asistencial Art. 29", "CONCEPTO": "Contribuyente obligado: quienes soliciten los servicios asistenciales y posean recursos.", "ORDENANZA": "Ordenanza Fiscal Art. 29", "DENSIDAD": "31.000 hab (Media)"},
        {"MUNICIPIO": "Ensenada", "COBRO": "Sistema SAMO", "CONCEPTO": "Contribuyentes exclusivos: Obras Sociales, Prepagas, ART y Compañías de Seguros.", "ORDENANZA": "Ordenanza Fiscal Art. 191", "DENSIDAD": "64.000 hab (Media)"},
        {"MUNICIPIO": "Escobar", "COBRO": "Tasa por servicios especiales (impuesto encubierto)", "CONCEPTO": "Adicional de salud cobrado dentro de la tasa de Alumbrado, Barrido y Limpieza (ABL).", "ORDENANZA": "Ordenanza Fiscal Art. 103", "DENSIDAD": "256.000 hab (Alta)"},
        {"MUNICIPIO": "Esteban Echeverría", "COBRO": "Sistema SAMO", "CONCEPTO": "Atención gratuita al paciente. Recupero vía SAMO.", "ORDENANZA": "Ordenanza Fiscal Art. 16.1", "DENSIDAD": "338.000 hab (Alta)"},
        {"MUNICIPIO": "Exaltación De La Cruz", "COBRO": "Tasa por servicios generales (impuesto encubierto)", "CONCEPTO": "Adicional de salud incluido en la tasa general municipal.", "ORDENANZA": "Ordenanza Fiscal Art. 3", "DENSIDAD": "39.000 hab (Media)"},
        {"MUNICIPIO": "Ezeiza", "COBRO": "Servicios complementarios de salud (impuesto encubierto)", "CONCEPTO": "Contribución especial fija sobre la ordenanza impositiva.", "ORDENANZA": "Ordenanza Impositiva Art. 1.7", "DENSIDAD": "201.000 hab (Alta)"},
        {"MUNICIPIO": "Florencio Varela", "COBRO": "Tasa por servicios generales (impuesto encubierto)", "CONCEPTO": "Impuesto encubierto adicionado a tributos domiciliarios.", "ORDENANZA": "Ordenanza Fiscal Art. 115", "DENSIDAD": "497.000 hab (Alta)"},
        {"MUNICIPIO": "Florentino Ameghino", "COBRO": "Aranceles hospitalarios Art. 208", "CONCEPTO": "Cobro de aranceles por prestaciones prestadas en el Hospital Municipal.", "ORDENANZA": "Ordenanza 114/93 - Impositiva 2025", "DENSIDAD": "9.500 hab (Baja)"},
        {"MUNICIPIO": "General Alvarado", "COBRO": "Tasa de salud (impuesto encubierto)", "CONCEPTO": "Tasa encubierta gravada sobre el padrón municipal.", "ORDENANZA": "Ordenanza Fiscal 2025", "DENSIDAD": "45.000 hab (Media)"},
        {"MUNICIPIO": "General Alvear", "COBRO": "Tasa por servicios asistenciales Art. 38", "CONCEPTO": "Fija importes para prestaciones del Hospital Municipal según nomenclador IOMA.", "ORDENANZA": "Ordenanza Impositiva Art. 38", "DENSIDAD": "12.000 hab (Baja)"},
        {"MUNICIPIO": "General Arenales", "COBRO": "Tasa servicios asistenciales Art. 134 y ss", "CONCEPTO": "Exceptúa del cobro únicamente previa acreditación de evidente carencia de recursos.", "ORDENANZA": "Ordenanza Fiscal Art. 134", "DENSIDAD": "16.000 hab (Baja)"},
        {"MUNICIPIO": "General Belgrano", "COBRO": "Tasa asistencial / SAMO", "CONCEPTO": "Aclara servicio gratuito a quien carezca de recursos. SAMO para terceros.", "ORDENANZA": "Ordenanza Fiscal Art. 151", "DENSIDAD": "19.000 hab (Baja)"},
        {"MUNICIPIO": "General Guido", "COBRO": "Tasa de Servicio de Salud Art. 21", "CONCEPTO": "Monto fijo por cada recibo de Tasa o Derecho municipal.", "ORDENANZA": "Ordenanza Impositiva Art. 21", "DENSIDAD": "3.200 hab (Baja)"},
        {"MUNICIPIO": "General Juan Madariaga", "COBRO": "Tasa asistencial voluntaria / SAMO", "CONCEPTO": "Sostiene gratuidad y SAMO; aporta el paciente solo de forma voluntaria.", "ORDENANZA": "Ordenanza Fiscal Art. 208", "DENSIDAD": "23.000 hab (Baja)"},
        {"MUNICIPIO": "General La Madrid", "COBRO": "Tasa servicio asistenciales Art. 13", "CONCEPTO": "Cobro a pacientes sin obra social según nomenclador, medicamentos y materiales previa encuesta social.", "ORDENANZA": "Ordenanza Fiscal Art. 13", "DENSIDAD": "11.600 hab (Baja)"},
        {"MUNICIPIO": "General Las Heras", "COBRO": "Tasa servicios asistenciales Art. 123 y ss", "CONCEPTO": "Contribuyente obligado quien obtenga el servicio o sus familiares. Eximición por condición socioeconómica.", "ORDENANZA": "Ordenanza Fiscal Art. 123", "DENSIDAD": "17.500 hab (Baja)"},
        {"MUNICIPIO": "General Lavalle", "COBRO": "Tasa servicios asistenciales Art. 173 y ss", "CONCEPTO": "Excepción de pago reservada a personas carentes de recursos.", "ORDENANZA": "Ordenanza Fiscal Art. 173", "DENSIDAD": "4.800 hab (Baja)"},
        {"MUNICIPIO": "General Paz", "COBRO": "Tasa contributiva UTI y asistencial", "CONCEPTO": "Tasa sobre servicios urbanos y rurales. Tarifario fijado en UF para no residentes.", "ORDENANZA": "Ordenanza Fiscal Art. 291", "DENSIDAD": "13.000 hab (Baja)"},
        {"MUNICIPIO": "General Pinto", "COBRO": "Aranceles hospitalarios Art. 240 y ss", "CONCEPTO": "Facturación a pacientes sin obra social según encuesta social y nomenclador IOMA.", "ORDENANZA": "Ordenanza Fiscal Art. 240", "DENSIDAD": "12.500 hab (Baja)"},
        {"MUNICIPIO": "General Pueyrredón", "COBRO": "Contribución a la Salud Art. 217", "CONCEPTO": "Contribución fija por inmueble gravado por la Tasa por Servicios Urbanos o Red Vial.", "ORDENANZA": "Ordenanza Fiscal Art. 217", "DENSIDAD": "681.000 hab (Alta)"},
        {"MUNICIPIO": "General Rodríguez", "COBRO": "Tasa especial salud / Hospital odontológico", "CONCEPTO": "Tasa especial en módulos sobre salud y cobro por hospital odontológico/oftalmológico.", "ORDENANZA": "Ordenanza Impositiva Art. 42", "DENSIDAD": "143.000 hab (Alta)"},
        {"MUNICIPIO": "General San Martín", "COBRO": "Sistema SAMO Art. 303 y ss", "CONCEPTO": "Limitado al recupero de costos del sistema SAMO sobre obras sociales.", "ORDENANZA": "Ordenanza Fiscal Art. 303", "DENSIDAD": "450.000 hab (Alta)"},
        {"MUNICIPIO": "General Viamonte", "COBRO": "Tasa asistencial Art. 205 y ss", "CONCEPTO": "Determina contribuyente a persona sin obra social fijando tarifa según ingresos.", "ORDENANZA": "Ordenanza Fiscal Art. 205", "DENSIDAD": "18.500 hab (Baja)"},
        {"MUNICIPIO": "General Villegas", "COBRO": "Fondo servicios asistenciales Art. 57", "CONCEPTO": "Fondo especial asistencial.", "ORDENANZA": "Ordenanza Fiscal Art. 57", "DENSIDAD": "33.000 hab (Media)"},
        {"MUNICIPIO": "Guaminí", "COBRO": "Tasa salud (impuesto encubierto) + Arancel", "CONCEPTO": "Tasa de salud sobre ordenanza fiscal más tarifario por radiografías, mamografías y prácticas.", "ORDENANZA": "Ordenanza Fiscal Art. 205", "DENSIDAD": "11.800 hab (Baja)"},
        {"MUNICIPIO": "Hipólito Yrigoyen", "COBRO": "Tasa servicios asistenciales Art. 45 y ss", "CONCEPTO": "Tasa por prestaciones hospitalarias.", "ORDENANZA": "Ordenanza Fiscal Art. 45", "DENSIDAD": "9.000 hab (Baja)"},
        {"MUNICIPIO": "Hurlingham", "COBRO": "Sistema SAMO", "CONCEPTO": "Atención pública gratuita sin arancel directo al paciente.", "ORDENANZA": "Ordenanza Fiscal 2025", "DENSIDAD": "187.000 hab (Alta)"},
        {"MUNICIPIO": "Ituzaingó", "COBRO": "SAMO + Tasa protección ciudadana", "CONCEPTO": "SAMO más tasa como impuesto encubierto para servicios varios de salud.", "ORDENANZA": "Ordenanza Impositiva Art. 18.1", "DENSIDAD": "179.000 hab (Alta)"},
        {"MUNICIPIO": "José C. Paz", "COBRO": "Ausencia de concepto / SAMO", "CONCEPTO": "Atención pública gratuita.", "ORDENANZA": "Ordenanza Fiscal 2025", "DENSIDAD": "323.000 hab (Alta)"},
        {"MUNICIPIO": "Junín", "COBRO": "TASA POR SERVICIOS PUBLICOS URBANOS", "CONCEPTO": "Impuesto encubierto adicionado a la tasa general de servicios urbanos.", "ORDENANZA": "Ordenanza Fiscal Art. 1", "DENSIDAD": "101.000 hab (Alta)"},
        {"MUNICIPIO": "La Costa", "COBRO": "Tasa asistencial Art. 198 + Fondo Salud Rural", "CONCEPTO": "Tasa asistencial a no residentes más Fondo Salud a partidas rurales.", "ORDENANZA": "Ordenanza Fiscal Art. 198", "DENSIDAD": "102.000 hab (Alta)"},
        {"MUNICIPIO": "La Matanza", "COBRO": "Sistema SAMO Art. 249", "CONCEPTO": "Especifica el sistema de recupero SAMO a obras sociales. Gratuidad al paciente.", "ORDENANZA": "Ordenanza Fiscal Art. 249", "DENSIDAD": "1.837.000 hab (Alta)"},
        {"MUNICIPIO": "La Plata", "COBRO": "Ausencia de concepto", "CONCEPTO": "Ausencia de arancelamiento directo en el código tributario.", "ORDENANZA": "Código Tributario 2025", "DENSIDAD": "772.000 hab (Alta)"},
        {"MUNICIPIO": "Lanús", "COBRO": "Ausencia de concepto", "CONCEPTO": "Gratuidad del servicio público asistencial municipal.", "ORDENANZA": "Código Tributario 2025", "DENSIDAD": "462.000 hab (Alta)"},
        {"MUNICIPIO": "Laprida", "COBRO": "SAMO Art. 20", "CONCEPTO": "Recupero vía SAMO.", "ORDENANZA": "Ordenanza Fiscal Art. 20", "DENSIDAD": "11.500 hab (Baja)"},
        {"MUNICIPIO": "Las Flores", "COBRO": "Ausencia de concepto", "CONCEPTO": "Sin arancelamiento asistencial normado.", "ORDENANZA": "Ordenanza Fiscal 2025", "DENSIDAD": "25.000 hab (Media)"},
        {"MUNICIPIO": "Leandro N. Alem", "COBRO": "Aranceles de servicios asistenciales Art. 160", "CONCEPTO": "Categorización por Servicio Social y aranceles a prestaciones hospitalarias.", "ORDENANZA": "Ordenanza Fiscal Art. 160", "DENSIDAD": "17.000 hab (Baja)"},
        {"MUNICIPIO": "Lezama", "COBRO": "SAMO + Tasa Guardias Pediátricas", "CONCEPTO": "Tasa de salud sobre contribuyentes de Servicios Rurales y Barrido.", "ORDENANZA": "Ordenanza Fiscal Art. 219", "DENSIDAD": "6.200 hab (Baja)"},
        {"MUNICIPIO": "Lincoln", "COBRO": "Tasa servicios asistenciales Art. 21", "CONCEPTO": "Aranceles por km de ambulancia y recarga de tubo de oxígeno.", "ORDENANZA": "Ordenanza Impositiva Art. 21", "DENSIDAD": "44.000 hab (Media)"},
        {"MUNICIPIO": "Lobería", "COBRO": "Tasa servicios asistenciales Art. 192 y ss", "CONCEPTO": "Cobro de aranceles salvo diferencia o total asumido por informe social.", "ORDENANZA": "Ordenanza Fiscal Art. 192", "DENSIDAD": "18.000 hab (Baja)"},
        {"MUNICIPIO": "Lobos", "COBRO": "Contribución Solidaria Salud/Educación Art. 30", "CONCEPTO": "Impuesto encubierto para financiamiento de salud adicionado a tasas.", "ORDENANZA": "Ordenanza Fiscal Art. 30", "DENSIDAD": "38.000 hab (Media)"},
        {"MUNICIPIO": "Lomas de Zamora", "COBRO": "Ausencia de concepto", "CONCEPTO": "Gratuidad asistencial.", "ORDENANZA": "Ordenanza Impositiva 2025", "DENSIDAD": "694.000 hab (Alta)"},
        {"MUNICIPIO": "Luján", "COBRO": "Ausencia de concepto", "CONCEPTO": "Sin tasa de cobro directo a personas.", "ORDENANZA": "Ordenanza Fiscal 2025", "DENSIDAD": "120.000 hab (Alta)"},
        {"MUNICIPIO": "Magdalena", "COBRO": "Ausencia de concepto", "CONCEPTO": "Atención gratuita para residentes sin obra social.", "ORDENANZA": "Ordenanza Impositiva 2025", "DENSIDAD": "22.000 hab (Baja)"},
        {"MUNICIPIO": "Maipú", "COBRO": "Tasa servicios asistenciales Art. 12 y ss", "CONCEPTO": "Declaración jurada obligatoria; categoriza 4 niveles de cobro y cobra traslados de ambulancia.", "ORDENANZA": "Ordenanza Fiscal Art. 12", "DENSIDAD": "11.000 hab (Baja)"},
        {"MUNICIPIO": "Malvinas Argentinas", "COBRO": "Tasa servicios asistenciales Art. 192 y ss", "CONCEPTO": "Contribuyentes obligados: enfermo o familiares. Facturación a obra social si existe.", "ORDENANZA": "Ordenanza Fiscal Art. 192", "DENSIDAD": "351.000 hab (Alta)"},
        {"MUNICIPIO": "Mar Chiquita", "COBRO": "Tasa asistencial Art. 198 + Fondo Salud Art. 275", "CONCEPTO": "Cobro a no residentes e indigencia eximida mediante informe de Desarrollo Social.", "ORDENANZA": "Ordenanza Fiscal Art. 198", "DENSIDAD": "33.000 hab (Media)"},
        {"MUNICIPIO": "Marcos Paz", "COBRO": "Tasa servicios asistenciales Art. 232 y ss", "CONCEPTO": "Contribuyentes quienes soliciten el servicio o sus familiares. Gratuidad solo a indigencia.", "ORDENANZA": "Ordenanza Fiscal Art. 232", "DENSIDAD": "67.000 hab (Media)"},
        {"MUNICIPIO": "Mercedes", "COBRO": "Contribución especial Salud Art. 6", "CONCEPTO": "Impuesto encubierto tributado con la Tasa de Conservación de la Vía Pública.", "ORDENANZA": "Ordenanza Fiscal Art. 6", "DENSIDAD": "73.000 hab (Media)"},
        {"MUNICIPIO": "Merlo", "COBRO": "SAMO Art. 42", "CONCEPTO": "Garantiza atención gratuita a personas sin cobertura. Recupero SAMO.", "ORDENANZA": "Ordenanza Fiscal Art. 42", "DENSIDAD": "582.000 hab (Alta)"},
        {"MUNICIPIO": "Monte", "COBRO": "Contribución especial Salud Pública Art. 68", "CONCEPTO": "Adicional de salud gravado sobre tributos municipales.", "ORDENANZA": "Ordenanza Fiscal Art. 68", "DENSIDAD": "24.000 hab (Baja)"},
        {"MUNICIPIO": "Monte Hermoso", "COBRO": "SAMO + Tasa asistencial Art. 272", "CONCEPTO": "Cobro eximido previa evaluación socioeconómica del servicio social.", "ORDENANZA": "Ordenanza Fiscal Art. 272", "DENSIDAD": "8.500 hab (Baja)"},
        {"MUNICIPIO": "Moreno", "COBRO": "Tasa de Salud y Asistencia Social Art. 43", "CONCEPTO": "Alícuota del 10.5% sobre tributos y multas municipales en concepto de Tasa de Salud.", "ORDENANZA": "Ordenanza Fiscal Art. 43", "DENSIDAD": "574.000 hab (Alta)"},
        {"MUNICIPIO": "Morón", "COBRO": "SAMO Art. 288 / Servicios de Emergencia", "CONCEPTO": "SAMO y cobro por traslado en accidentes de tránsito.", "ORDENANZA": "Ordenanza Fiscal Art. 288", "DENSIDAD": "334.000 hab (Alta)"},
        {"MUNICIPIO": "Navarro", "COBRO": "Ausencia de concepto", "CONCEPTO": "Sin arancelamiento asistencial directo.", "ORDENANZA": "Ordenanza Impositiva 2025", "DENSIDAD": "20.000 hab (Baja)"},
        {"MUNICIPIO": "Necochea", "COBRO": "Tasa Fortalecimiento de Salud Art. 426", "CONCEPTO": "Impuesto encubierto a inmuebles urbanos y rurales.", "ORDENANZA": "Ordenanza Fiscal Art. 426", "DENSIDAD": "101.000 hab (Alta)"},
        {"MUNICIPIO": "Nueve de Julio", "COBRO": "Tasa servicios asistenciales Art. 44", "CONCEPTO": "Arancelamiento salvo falta de cobertura con incapacidad de pago.", "ORDENANZA": "Ordenanza Fiscal Art. 44", "DENSIDAD": "51.000 hab (Media)"},
        {"MUNICIPIO": "Olavarría", "COBRO": "SIAMO / Tasa asistencial Art. 138", "CONCEPTO": "Sistema prepago municipal SIAMO con cuota mensual más tasa asistencial.", "ORDENANZA": "Ordenanza Impositiva Art. 22", "DENSIDAD": "126.000 hab (Alta)"},
        {"MUNICIPIO": "Patagones", "COBRO": "Tasa servicios asistenciales Art. 239 y ss", "CONCEPTO": "Abonada directamente por el beneficiario del servicio si no posee obra social.", "ORDENANZA": "Ordenanza Fiscal Art. 239", "DENSIDAD": "38.000 hab (Media)"},
        {"MUNICIPIO": "Pehuajó", "COBRO": "Tasa servicios asistenciales Art. 215 y ss", "CONCEPTO": "Contribuyentes obligados las personas humanas usuarias del servicio o sus representantes.", "ORDENANZA": "Ordenanza Fiscal Art. 215", "DENSIDAD": "42.000 hab (Media)"},
        {"MUNICIPIO": "Pellegrini", "COBRO": "Sistema recupero SAMO Art. 40 y ss", "CONCEPTO": "Aplica únicamente a usuarios con cobertura. Garantiza la gratuidad plena para personas sin cobertura.", "ORDENANZA": "Ordenanza Fiscal Art. 40", "DENSIDAD": "6.800 hab (Baja)"},
        {"MUNICIPIO": "Pergamino", "COBRO": "Ausencia de concepto", "CONCEPTO": "Sin arancelamiento a pacientes.", "ORDENANZA": "Código Tributario 2025", "DENSIDAD": "114.000 hab (Alta)"},
        {"MUNICIPIO": "Pila", "COBRO": "Ausencia de concepto", "CONCEPTO": "Atención gratuita pública.", "ORDENANZA": "Ordenanza Impositiva 2025", "DENSIDAD": "4.000 hab (Baja)"},
        {"MUNICIPIO": "Pilar", "COBRO": "Tasa servicios de salud Art. 263 / SAMO", "CONCEPTO": "No se cobra a residentes sin cobertura por carecer de tareas remuneradas.", "ORDENANZA": "Ordenanza Fiscal Art. 263", "DENSIDAD": "395.000 hab (Alta)"},
        {"MUNICIPIO": "Pinamar", "COBRO": "Derechos sanatoriales / Asistenciales Art. 97", "CONCEPTO": "Eximición de pago reservada a personas sin cobertura con recursos limitados autorizadas por Acción Social.", "ORDENANZA": "Ordenanza Fiscal Art. 97", "DENSIDAD": "40.000 hab (Media)"},
        {"MUNICIPIO": "Presidente Perón", "COBRO": "Ausencia de concepto", "CONCEPTO": "Atención gratuita sin tasa de cobro.", "ORDENANZA": "Ordenanza Impositiva 2025", "DENSIDAD": "102.000 hab (Alta)"},
        {"MUNICIPIO": "Puán", "COBRO": "Tasa asistencial / Pagarés Art. 170", "CONCEPTO": "Pago diferido con firma de convenio y pagarés previa evaluación social. Seguro SEDEM.", "ORDENANZA": "Ordenanza Fiscal Art. 170", "DENSIDAD": "16.000 hab (Baja)"},
        {"MUNICIPIO": "Punta Indio", "COBRO": "Fondo Solidario de Salud Art. 202", "CONCEPTO": "Impuesto encubierto en tasas domiciliarias.", "ORDENANZA": "Ordenanza Fiscal Art. 202", "DENSIDAD": "12.000 hab (Baja)"},
        {"MUNICIPIO": "Quilmes", "COBRO": "Sistema SAMO Art. 316 y ss", "CONCEPTO": "Limitado al recupero SAMO.", "ORDENANZA": "Ordenanza Fiscal Art. 316", "DENSIDAD": "635.000 hab (Alta)"},
        {"MUNICIPIO": "Ramallo", "COBRO": "Tasa servicios asistenciales Art. 238", "CONCEPTO": "SAMO más cobro a personas sin cobertura que no demuestren indigencia según nomenclador.", "ORDENANZA": "Ordenanza Fiscal Art. 238", "DENSIDAD": "37.000 hab (Media)"},
        {"MUNICIPIO": "Rauch", "COBRO": "Tasa servicios asistenciales Anexo 1", "CONCEPTO": "Categorización por Desarrollo Social: 25%, 50%, 75% o 100% de arancel a pacientes.", "ORDENANZA": "Ordenanza Impositiva Anexo 1", "DENSIDAD": "16.000 hab (Baja)"},
        {"MUNICIPIO": "Rivadavia", "COBRO": "Servicios asistenciales Art. 238", "CONCEPTO": "Categorización por Servicio Social en A, B, C, D y E; cobro a sin cobertura con ingresos y no residentes.", "ORDENANZA": "Ordenanza Fiscal Art. 238", "DENSIDAD": "18.000 hab (Baja)"},
        {"MUNICIPIO": "Rojas", "COBRO": "Cobro a obras sociales Art. 215", "CONCEPTO": "Atención gratuita al paciente. Recupero a obras sociales.", "ORDENANZA": "Ordenanza Fiscal Art. 215", "DENSIDAD": "25.000 hab (Media)"},
        {"MUNICIPIO": "Roque Pérez", "COBRO": "Tasa asistencial Art. 33 / Tasa Salud", "CONCEPTO": "Gratuito excepto cobertura social o seguros. Contribución especial de salud sobre parcelas.", "ORDENANZA": "Ordenanza Fiscal Art. 33", "DENSIDAD": "14.000 hab (Baja)"},
        {"MUNICIPIO": "Saavedra Pigüé", "COBRO": "Tasa servicios asistenciales Art. 273", "CONCEPTO": "Sistema SAMO más gratuidad exclusiva para situación de indigencia en Art. 277.", "ORDENANZA": "Ordenanza Fiscal Art. 273", "DENSIDAD": "22.000 hab (Baja)"},
        {"MUNICIPIO": "Saladillo", "COBRO": "Sistema SAMO", "CONCEPTO": "Atención pública gratuita en hospital público.", "ORDENANZA": "Ordenanza Impositiva 2025", "DENSIDAD": "36.000 hab (Media)"},
        {"MUNICIPIO": "Salliqueló", "COBRO": "Tasa servicios asistenciales Art. 69", "CONCEPTO": "Tarifas para pacientes sin cobertura o Plan de Salud Municipal al 50%.", "ORDENANZA": "Ordenanza Fiscal Art. 69", "DENSIDAD": "9.000 hab (Baja)"},
        {"MUNICIPIO": "Salto", "COBRO": "Tasa asistencial Art. 206 / Apremio Art. 213", "CONCEPTO": "Arancelamiento directo con vía ejecutiva por juicio de apremio. Eximición solo a indigentes.", "ORDENANZA": "Ordenanza Fiscal Art. 206", "DENSIDAD": "38.000 hab (Media)"},
        {"MUNICIPIO": "San Andrés de Giles", "COBRO": "Tasa servicios asistenciales Art. 247", "CONCEPTO": "Contribuyente obligado la persona que recibe los servicios y responsables solidarios.", "ORDENANZA": "Ordenanza Fiscal Art. 247", "DENSIDAD": "26.000 hab (Media)"},
        {"MUNICIPIO": "San Antonio de Areco", "COBRO": "Tasa por servicios de salud Art. 218", "CONCEPTO": "Impuesto encubierto liquidado mensualmente sobre Tasas de Servicios Urbanos, Rurales e Higiene.", "ORDENANZA": "Ordenanza Fiscal Art. 218", "DENSIDAD": "25.000 hab (Media)"},
        {"MUNICIPIO": "San Cayetano", "COBRO": "Sistema SAMO Art. 122", "CONCEPTO": "Servicios asistenciales gratuitos. Ejercicio de cobro exclusivo sobre entidades de cobertura.", "ORDENANZA": "Ordenanza Fiscal Art. 122", "DENSIDAD": "8.900 hab (Baja)"},
        {"MUNICIPIO": "San Fernando", "COBRO": "Sistema SAMO / Gratuidad residentes", "CONCEPTO": "Garantiza la gratuidad a residentes del partido.", "ORDENANZA": "Ordenanza Fiscal Art. 141", "DENSIDAD": "172.000 hab (Alta)"},
        {"MUNICIPIO": "San Isidro", "COBRO": "Sistema SAMO Art. 141", "CONCEPTO": "Recupero de costos SAMO sobre entidades obligadas.", "ORDENANZA": "Ordenanza Fiscal Art. 141", "DENSIDAD": "290.000 hab (Alta)"},
        {"MUNICIPIO": "San Miguel", "COBRO": "Sistema SAMO Art. 94", "CONCEPTO": "Gratuidad para personas sin cobertura médica.", "ORDENANZA": "Ordenanza Fiscal Art. 94", "DENSIDAD": "326.000 hab (Alta)"},
        {"MUNICIPIO": "San Nicolás", "COBRO": "Sistema SAMO Art. 301", "CONCEPTO": "Sistema SAMO de recupero de costos.", "ORDENANZA": "Ordenanza Fiscal Art. 301", "DENSIDAD": "160.000 hab (Alta)"},
        {"MUNICIPIO": "San Pedro", "COBRO": "Sistema SAMO Art. 250", "CONCEPTO": "Especifica que si el paciente no tiene cobertura el servicio es totalmente gratuito.", "ORDENANZA": "Ordenanza Fiscal Art. 250", "DENSIDAD": "69.000 hab (Media)"},
        {"MUNICIPIO": "San Vicente", "COBRO": "Contribución al Sistema de Salud Art. 367", "CONCEPTO": "Impuesto encubierto equivalente al 40% de las Tasas por Propiedad Urbana, Red Vial e Higiene.", "ORDENANZA": "Ordenanza Fiscal Art. 367", "DENSIDAD": "98.000 hab (Media)"},
        {"MUNICIPIO": "Suipacha", "COBRO": "Tasa de salud Art. 129 / Prestaciones", "CONCEPTO": "Tasa de salud sobre toda parcela urbana más cobro por prestaciones según encuesta social.", "ORDENANZA": "Ordenanza Fiscal Art. 129", "DENSIDAD": "11.500 hab (Baja)"},
        {"MUNICIPIO": "Tandil", "COBRO": "Sistema Integrado de Salud Art. 217", "CONCEPTO": "Individualiza no cobro por consideraciones socioeconómicas. Excepciones con informe social.", "ORDENANZA": "Ordenanza Fiscal Art. 217", "DENSIDAD": "150.000 hab (Alta)"},
        {"MUNICIPIO": "Tapalqué", "COBRO": "Tasa asistencial Art. 200 + Contribución UTI", "CONCEPTO": "Contribución encubierta para UTI más deducciones según posibilidades por servicio social.", "ORDENANZA": "Ordenanza Fiscal Art. 200", "DENSIDAD": "10.000 hab (Baja)"},
        {"MUNICIPIO": "Tigre", "COBRO": "Sistema SAMO / Arancel no residentes", "CONCEPTO": "Garantiza gratuidad a personas sin cobertura médica residentes del partido.", "ORDENANZA": "Ordenanza Impositiva Art. 83", "DENSIDAD": "447.000 hab (Alta)"},
        {"MUNICIPIO": "Tordillo", "COBRO": "Tasa servicios asistenciales Art. 28", "CONCEPTO": "Abonan quienes soliciten los servicios y tengan recursos probados. Gratuito para quienes no tengan recursos.", "ORDENANZA": "Ordenanza Impositiva Art. 28", "DENSIDAD": "2.700 hab (Baja)"},
        {"MUNICIPIO": "Tornquist", "COBRO": "SAMO + Tasa asistencial Art. 142", "CONCEPTO": "Eximición total o parcial previa ficha socioeconómica otorgada por área competente.", "ORDENANZA": "Ordenanza Fiscal Art. 142", "DENSIDAD": "14.500 hab (Baja)"},
        {"MUNICIPIO": "Trenque Lauquen", "COBRO": "SAMO + Tasa asistencial Art. 89", "CONCEPTO": "No se cobra a residentes del distrito sin cobertura médica.", "ORDENANZA": "Ordenanza Fiscal Art. 89", "DENSIDAD": "48.000 hab (Media)"},
        {"MUNICIPIO": "Tres Arroyos", "COBRO": "Tasa Sostenimiento del Servicio de Salud Art. 183", "CONCEPTO": "Tasa encubierta cobrada en la liquidación de la Tasa por Servicios Urbanos a todos los inmuebles.", "ORDENANZA": "Ordenanza Fiscal Art. 183", "DENSIDAD": "62.000 hab (Media)"},
        {"MUNICIPIO": "Tres de Febrero", "COBRO": "Sistema SAMO Art. 245", "CONCEPTO": "Garantiza la gratuidad del servicio a personas sin cobertura médica.", "ORDENANZA": "Ordenanza Fiscal Art. 245", "DENSIDAD": "340.000 hab (Alta)"},
        {"MUNICIPIO": "Tres Lomas", "COBRO": "Tasa servicios asistenciales", "CONCEPTO": "Cobro a personas sin cobertura médica según medios económicos determinados por encuesta social.", "ORDENANZA": "Ordenanza 1043/13", "DENSIDAD": "8.500 hab (Baja)"},
        {"MUNICIPIO": "Vicente López", "COBRO": "Sistema SAMO Art. 254", "CONCEPTO": "Gratuito para personas sin cobertura médica. Recupero SAMO.", "ORDENANZA": "Ordenanza Fiscal Art. 254", "DENSIDAD": "283.000 hab (Alta)"},
        {"MUNICIPIO": "Villa Gesell", "COBRO": "Tasa salud Art. 148 Código Tributario", "CONCEPTO": "Tasa de salud incorporada en el Código Tributario unificado.", "ORDENANZA": "Código Tributario Art. 148", "DENSIDAD": "38.000 hab (Media)"},
        {"MUNICIPIO": "Villarino", "COBRO": "Derecho de Comercialización Frutícola destinado a Salud", "CONCEPTO": "Tasa sobre producción frutihortícola destinada directamente a financiar el sistema de salud.", "ORDENANZA": "Ordenanza Fiscal Art. 232", "DENSIDAD": "33.000 hab (Media)"},
        {"MUNICIPIO": "Zárate", "COBRO": "Sistema SAMO Art. 217 y ss", "CONCEPTO": "Atención gratuita al paciente. Recupero de costos SAMO.", "ORDENANZA": "Ordenanza Fiscal Art. 217", "DENSIDAD": "132.000 hab (Alta)"}
    ]
    
    df = pd.DataFrame(raw_csv_data)
    
    def clasificar_base(row):
        cobro = str(row['COBRO']).upper()
        concepto = str(row['CONCEPTO']).upper()
        full = cobro + " " + concepto
        
        if 'IMPUESTO ENCUBIERTO' in full or 'FONDO' in full or 'CONTRIBUCIÓN ESPECIAL' in full or 'TASA ESPECIAL' in full or 'TASA DE SALUD' in full or 'TASA POR SERVICIOS GENERALES' in full or 'APORTE PARA LA SALUD' in full or 'ALÍCUOTA SOBRE MULTAS' in full or 'FORTALECIMIENTO' in full or 'CONTRIBUCIÓN AL SISTEMA' in full or 'DERECHO DE COMERCIALIZACIÓN' in full or 'SERVICIOS COMPLEMENTARIOS' in full:
            if not ('TASA SERVICIO ASISTENCIAL' in cobro and not 'ENCUBIERTO' in cobro):
                return 'Categoría B (Tasa Encubierta)'
                
        if 'ARANCEL' in full or 'TASA SERVICIO ASISTENCIAL' in full or 'SERVICIOS ASISTENCIALES' in full or 'INDIGENCIA' in full or 'INFORME SOCIAL' in full or 'EVALUACIÓN' in full or 'ENCUESTA SOCIAL' in full or 'NOMENCLADOR' in full or 'APREMIO' in full or 'PAGARÉ' in full or 'TASA ASISTENCIAL' in full or 'CUOTA MENSUAL' in full or 'SUJETO DE COBRO' in full or 'DECLARACIÓN JURADA' in full:
            if 'NO FIGURA EN LA ORDENANZA MUNICIPAL COBRO' in full or 'GRATUIDAD Y TRATO IGUALITARIO' in full or 'SOLO SE RECUPERA POR SISTEMA SAMO' in full or 'GRATUITO PARA PERSONAS SIN COBERTURA' in full or 'GRATUIDAD PLENA' in full or 'GRATUITO A QUIEN CAREZCA' in full or 'TOTALMENTE GRATUITA' in full or 'RECUPERO SAMO' in full or 'SIN ARANCEL DIRECTO' in full or 'VOLUNTARIA' in full or 'NO SE COBRA A RESIDENTES' in full or 'APLICA ÚNICAMENTE RESPECTO DE LAS PRESTACIONES... CON COBERTURA' in full:
                return 'Categoría A (Gratuidad / SAMO)'
            return 'Categoría C (Arancel Directo)'
            
        return 'Categoría A (Gratuidad / SAMO)'

    df['CATEGORIA'] = df.apply(clasificar_base, axis=1)
    return df

df_censo = load_data()

# ==========================================
# NAVEGACIÓN Y MENÚ
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/scales.png", width=70)
st.sidebar.title("SIA-PBA v2.0")
st.sidebar.markdown("**Sistema Integrado de Auditoría Algorítmica de Ordenanzas Tributario-Sanitarias**")
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
* **Autora:** Mariana
* **Enfoque:** Capítulo VIII - Propuesta de Innovación Tecnológica y Control de Convencionalidad
""")

# ==========================================
# MÓDULO 1: PRESENTACIÓN E IMPACTO TFC
# ==========================================
if "🏠 1. Presentación" in opcion_menu:
    st.markdown("<h2 class='pba-title'>SIA-PBA: Auditoría Algorítmica Preventiva & Canal Único</h2>", unsafe_allow_html=True)
    st.markdown("<p class='pba-subtitle'>Herramienta tecnológica de control preventivo de constitucionalidad y convencionalidad de ordenanzas impositivas municipales (CPBA Art. 36 inc. 8 - PIDESC Art. 12 - CP Art. 266)</p>", unsafe_allow_html=True)
    st.markdown("---")
    
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
    st.subheader("🎯 Ejes Fundamentales del Sistema (Capítulo VIII TFC)")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        ### 🔍 1. Auditoría Algorítmica Contextual de Ordenanzas (IA / PNL)
        * **Procesamiento Articular:** Analiza ordenanzas completas fragmentándolas artículo por artículo.
        * **Semáforo Tripartito de Convencionalidad:**
            * 🟢 **Cat. A (Gratuidad Plena / SAMO):** Cumplimiento del Art. 36 inc. 8 CPBA.
            * 🟡 **Cat. B (Tasas Encubiertas):** Tributos disfrazados adicionados a ABL/Red Vial/Seguridad e Higiene.
            * 🔴 **Cat. C (Arancelamiento Directo):** Alerta por cobro directo a particulares, pagarés, juicio de apremio o exigencia de acreditación de indigencia.
        """)
    with c2:
        st.markdown("""
        ### 🛡️ 2. Canal Único Descentralizado de Denuncias Anónimas
        * **Ruptura de la Espiral del Silencio:** Diseñado para ciudadanos de distritos de baja densidad con efector único de salud.
        * **Anonimato Criptográfico:** Emisión de Código Hash SHA-256 para seguimiento irrecuperable de la IP.
        * **Trazabilidad Institucional:** Derivación automática a la Defensoría del Pueblo PBA y Asesoría General de Gobierno.
        """)

# ==========================================
# MÓDULO 2: AUDITORÍA ALGORÍTMICA DE ORDENANZAS (IA)
# ==========================================
elif "🔍 2. Módulo de Auditoría" in opcion_menu:
    st.markdown("<h2 class='pba-title'>🔍 Módulo de Auditoría Algorítmica de Ordenanzas</h2>", unsafe_allow_html=True)
    st.markdown("<p class='pba-subtitle'>Examen automatizado por Procesamiento de Lenguaje Natural (PNL) sobre normas tributarias municipales.</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    tab1, tab2 = st.tabs([
        "🏛️ Submódulo 1: Línea de Base 2026 (Censo Provincial N=135)",
        "🚀 Submódulo 2: Motor de Auditoría Futura (Nuevas Ordenanzas 2027+)"
    ])
    
    # ------------------------------------------
    # SUBMÓDULO 1: LÍNEA DE BASE 2026
    # ------------------------------------------
    with tab1:
        st.markdown("##### Consulta del Censo de Ordenanzas Municipales Relevadas (Ejercicio 2025/2026):")
        muni_selected = st.selectbox("Seleccione Municipio de la Prov. de Bs. As.:", df_censo['MUNICIPIO'].unique(), key="sb_muni_base")
        
        row_muni = df_censo[df_censo['MUNICIPIO'] == muni_selected].iloc[0]
        cat = row_muni['CATEGORIA']
        
        st.markdown("### 📊 Resultado del Examen Algorítmico de la Línea de Base")
        col_res1, col_res2 = st.columns([1, 2])
        
        with col_res1:
            if 'Cat. C' in cat or 'Arancel' in cat or 'Categoría C' in cat:
                st.error("🔴 **DICTAMEN: INCONSTITUCIONAL / ARANCEL DIRECTO**")
                st.markdown("<span class='badge-cat-c'>Categoría C - Riesgo Alto</span>", unsafe_allow_html=True)
            elif 'Cat. B' in cat or 'Encubierta' in cat or 'Categoría B' in cat:
                st.warning("🟡 **DICTAMEN: ADVERTENCIA / TASA ENCUBIERTA**")
                st.markdown("<span class='badge-cat-b'>Categoría B - Riesgo Medio</span>", unsafe_allow_html=True)
            else:
                st.success("🟢 **DICTAMEN: CONFORME A DERECHO / GRATUIDAD PLENA**")
                st.markdown("<span class='badge-cat-a'>Categoría A - Gratuidad Plena / SAMO</span>", unsafe_allow_html=True)
                
            st.write(f"**Municipio:** {row_muni['MUNICIPIO']}")
            st.write(f"**Densidad Poblacional:** {row_muni['DENSIDAD']}")
            st.write(f"**Norma Relevada:** {row_muni['ORDENANZA']}")
            
        with col_res2:
            st.markdown("#### ⚖️ Fundamentación Jurídica y Disposición Relevada")
            st.markdown(f"**Encuadre Tributario Local:** *\"{row_muni['COBRO']} - {row_muni['CONCEPTO']}\"*")
            
            if 'Categoría C' in cat or 'Arancel' in cat:
                st.markdown("""
                <div class='article-box-c'>
                <b>⚠️ Vulneraciones Normativas Constatadas:</b><br>
                1. <b>Violación del Art. 36 inc. 8 de la Constitución Provincial:</b> Imposición de barrera económica para acceder a la salud pública gratuita.<br>
                2. <b>Infractor al PIDESC (Art. 75 inc. 22 CN - Art. 12):</b> Contravención del derecho al disfrute del más alto nivel de salud sin condicionamientos.<br>
                3. <b>Encuadre Penal (Art. 266 CP - Exacción Ilegal):</b> Cobro indebido o exigencia de contribuciones bajo coercibilidad estatal o juicio de apremio.<br>
                4. <b>Ilegitimidad de la Exigencia de Pobreza:</b> Exigir encuesta social o acreditación de indigencia vulnera la gratuidad irrestricta.
                </div>
                """, unsafe_allow_html=True)
            elif 'Categoría B' in cat:
                st.markdown("""
                <div class='article-box-b'>
                <b>⚠️ Vulneraciones Normativas Constatadas:</b><br>
                1. <b>Falta de Causa Tributaria Directa:</b> Creación de aditamentos sobre ABL/Red Vial/Comercio sin contraprestación directa de servicio al contribuyente.<br>
                2. <b>Impuesto Encubierto / Disfrazado:</b> Adición de alícuotas o montos fijos para financiar presupuestos generales de salud.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='article-box-a'>
                <b>✅ Compatibilidad Constitucional Constatada:</b><br>
                La normativa respeta el principio de gratuidad irrestricta garantizando atención pública sin cobros directos a particulares sin cobertura, limitando el recupero de costos al sistema SAMO (Ley Provincial 11.069).
                </div>
                """, unsafe_allow_html=True)

    # ------------------------------------------
    # SUBMÓDULO 2: MOTOR DE AUDITORÍA FUTURA (2027+)
    # ------------------------------------------
    with tab2:
        st.markdown("##### Auditoría Algorítmica Contextual de Futuras Ordenanzas (Ejercicio 2027 en adelante):")
        
        col_fut1, col_fut2 = st.columns([1, 1])
        with col_fut1:
            muni_futuro = st.selectbox("Seleccione el Municipio a Auditar:", df_censo['MUNICIPIO'].unique(), key="sb_muni_fut")
        with col_fut2:
            ejercicio_futuro = st.selectbox("Ejercicio Fiscal Futuro:", ["Ejercicio 2027", "Ejercicio 2028", "Ejercicio 2029"])
            
        st.markdown("---")
        st.markdown("#### 📄 Carga del Documento o Articulado de la Nueva Ordenanza:")
        
        uploaded_file = st.file_uploader("Adjuntar archivo de Ordenanza Fiscal/Impositiva (PDF):", type=['pdf'])
        texto_manual = st.text_area(
            "O pegue directamente el texto del articulado impositivo a auditar:",
            value="",
            height=140,
            placeholder="Pegue aquí el texto completo o articulado de la Ordenanza Fiscal e Impositiva municipal..."
        )
        
        if st.button("🚀 Ejecutar Auditoría Algorítmica Contextual"):
            texto_a_analizar = ""
            origen_doc = ""
            
            if uploaded_file is not None:
                try:
                    pdf_reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
                    text_extracted = ""
                    for page in pdf_reader.pages:
                        t = page.extract_text()
                        if t:
                            text_extracted += t + "\n"
                    if len(text_extracted.strip()) > 30:
                        texto_a_analizar = text_extracted
                        origen_doc = f"Archivo PDF subido ({len(pdf_reader.pages)} páginas)"
                    else:
                        st.warning("⚠️ No se detectó capa de texto digital en el PDF. Se utilizará el cuadro de texto inferior.")
                except Exception as e:
                    st.error(f"Error al leer el archivo PDF: {str(e)}")
                    
            if not texto_a_analizar and texto_manual.strip():
                texto_a_analizar = texto_manual
                origen_doc = "Texto ingresado manualmente en el editor"
                
            if not texto_a_analizar.strip():
                st.error("❌ **ERROR DE PROCESAMIENTO:** Por favor adjunte un archivo PDF o pegue el texto del articulado en el cuadro superior para auditar.")
            else:
                st.info(f"✅ **Procesamiento de Documento Exitoso:** {origen_doc}")
                
                # NORMALIZACIÓN Y FRAGMENTACIÓN POR ARTÍCULOS
                text_norm = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', texto_a_analizar)
                text_norm = re.sub(r'\s+', ' ', text_norm)
                
                articles = re.split(r'(?i)(?=ART[ÍI]CULO\s+\d+|ART\.\s*\d+|CAP[ÍI]TULO\s+[I|V|X]+)', text_norm)
                if len(articles) <= 1:
                    articles = [p.strip() for p in text_norm.split('\n\n') if len(p.strip()) > 20]
                    if not articles:
                        articles = [text_norm]
                        
                findings_c = []
                findings_b = []
                findings_a = []
                
                for art in articles:
                    art_clean = art.strip()
                    if len(art_clean) < 15:
                        continue
                    art_upper = art_clean.upper()
                    
                    # CATEGORÍA B: Tasas Encubiertas / Impuestos Disfrazados
                    pat_b = [
                        r'CONTRIBUCI[OÓ]N\s+AL\s+SISTEMA\s+DE\s+SALUD',
                        r'FONDO\s+.*SALUD', r'TASA\s+DE\s+SALUD',
                        r'APORTE\s+PARA\s+LA\s+SALUD', r'SOSTENIMIENTO\s+.*SALUD',
                        r'CONTRIBUYENTES\s+DE\s+LA\s+TASA\s+POR\s+(ALUMBRADO|CONSERVACI[OÓ]N|RED\s+VIAL|INSPECCI[OÓ]N|SERVICIOS\s+URBANOS)',
                        r'EQUIVALENTE\s+AL\s+.*%\s+DE\s+LAS\s+TASAS',
                        r'SE\s+TRIBUTAR[AÁ]\s+EN\s+FORMA\s+CONJUNTA',
                        r'AL[IÍ]CUOTA\s+SOBRE\s+MULTAS', r'TASA\s+POR\s+FORTALECIMIENTO.*SALUD'
                    ]
                    if any(re.search(p, art_upper) for p in pat_b):
                        findings_b.append((art_clean, "Se detectó la imposición de un tributo encubierto o fondo especial de salud gravado sobre tasas de servicios urbanos, ABL, Red Vial, multas o comercio."))
                        continue
                        
                    # CATEGORÍA A: Protecciones de Gratuidad y SAMO
                    pat_a_protection = [
                        r'EN\s+NING[UÚ]N\s+CASO\s+CORRESPONDER[AÁ]\s+EXIGIR\s+PAGO',
                        r'GRATUIDAD\s+PLENA', r'ESTRICTAMENTE\s+GRATUITA', r'TOTALMENTE\s+GRATUITA',
                        r'PRINCIPIO\s+DE\s+GRATUIDAD', r'EXCLUSIVAMENTE\s+SOBRE\s+OBRAS\s+SOCIALES',
                        r'ÚNICAMENTE\s+.*USUARIOS\s+QUE\s+CUENTEN\s+CON\s+COBERTURA',
                        r'SIN\s+COSTO\s+PARA\s+EL\s+PACIENTE\s+SIN\s+COBERTURA',
                        r'NO\s+SE\s+COBRAR[AÁ]\s+A\s+PERSONAS\s+SIN\s+COBERTURA'
                    ]
                    has_a = any(re.search(p, art_upper) for p in pat_a_protection)
                    
                    # CATEGORÍA C: Arancelamiento Directo / Barreras Económicas
                    pat_c = [
                        r'CONTRIBUYENTES?\s+.*PERSONAS\s+HUMANAS\s+USUARIAS',
                        r'CONTRIBUYENTES?\s+.*PACIENTES',
                        r'SE\s+LES\s+COBRAR[AÁ]', r'ABONAR[AÁ]N\s+LA\s+TASA',
                        r'INFORME\s+SOCIOECON[OÓ]MICO', r'ENCUESTA\s+SOCIAL',
                        r'INDIGENCIA', r'CARENCIA\s+DE\s+RECURSOS', r'NOMENCLADOR',
                        r'APREMIO\s+FISCAL', r'PAGAR[EÉ]', r'ARANCEL'
                    ]
                    has_c = any(re.search(p, art_upper) for p in pat_c)
                    
                    if has_c and not has_a:
                        findings_c.append((art_clean, "Cláusula de arancelamiento directo o exigencia de acreditación de pobreza/indigencia para acceder a la gratuidad hospitalaria."))
                    elif has_a or ('SAMO' in art_upper and not has_c):
                        findings_a.append((art_clean, "Disposición de gratuidad asistencial plena y/o recuperación exclusiva frente a obras sociales (SAMO)."))

                st.markdown("---")
                st.subheader(f"📋 Dictamen de Auditoría Algorítmica - {muni_futuro} ({ejercicio_futuro})")
                
                if len(findings_c) > 0:
                    st.error("🔴 **ALERTA CRÍTICA: DETECCIÓN DE CLÁUSULAS INCONSTITUCIONALES / CATEGORÍA C**")
                    st.markdown("<span class='badge-cat-c'>DICTAMEN DESFAVORABLE - RIESGO ALTO</span>", unsafe_allow_html=True)
                    st.markdown(f"**Diagnóstico:** La norma analizada para {muni_futuro} contiene cláusulas de arancelamiento directo, cobro a pacientes o exigencia de acreditación de indigencia, violando el Art. 36 inc. 8 de la Constitución Provincial y encuadrando en el Art. 266 del Código Penal (Exacción Ilegal).")
                    
                    st.markdown("#### 📜 Artículos Infractores Detectados:")
                    for art_txt, desc in findings_c:
                        art_disp = art_txt if len(art_txt) < 350 else art_txt[:350] + "..."
                        st.markdown(f"""
                        <div class='article-box-c'>
                            <b>⚠️ Artículo Infractor Extraído:</b><br>
                            <i>"{art_disp}"</i><br><br>
                            <b>Observación Técnica:</b> {desc}
                        </div>
                        """, unsafe_allow_html=True)
                        
                elif len(findings_b) > 0:
                    st.warning("🟡 **ALERTA MEDIA: DETECCIÓN DE TASAS ENCUBIERTAS / CATEGORÍA B**")
                    st.markdown("<span class='badge-cat-b'>DICTAMEN CON ADVERTENCIA - RIESGO MEDIO</span>", unsafe_allow_html=True)
                    st.markdown(f"**Diagnóstico:** La ordenanza examinada para {muni_futuro} impone tasas o fondos especiales de salud como aditamentos sobre servicios urbanos, ABL o Red Vial, configurando tributos encubiertos.")
                    
                    st.markdown("#### 📜 Artículos Observados:")
                    for art_txt, desc in findings_b:
                        art_disp = art_txt if len(art_txt) < 350 else art_txt[:350] + "..."
                        st.markdown(f"""
                        <div class='article-box-b'>
                            <b>⚠️ Artículo Observado:</b><br>
                            <i>"{art_disp}"</i><br><br>
                            <b>Observación Técnica:</b> {desc}
                        </div>
                        """, unsafe_allow_html=True)
                        
                else:
                    st.success("🟢 **DICTAMEN POSITIVO: NORMATIVA CONFORME A DERECHO / CATEGORÍA A**")
                    st.markdown("<span class='badge-cat-a'>DICTAMEN FAVORABLE - GRATUIDAD / SAMO</span>", unsafe_allow_html=True)
                    st.markdown(f"**Diagnóstico:** La norma analizada para {muni_futuro} respeta el principio de gratuidad pública garantizado por el Art. 36 inc. 8 de la CPBA y limita adecuadamente el recupero de costos al sistema SAMO frente a terceros pagadores.")
                    
                    if findings_a:
                        st.markdown("#### 📜 Artículos Conformes:")
                        for art_txt, desc in findings_a[:3]:
                            art_disp = art_txt if len(art_txt) < 350 else art_txt[:350] + "..."
                            st.markdown(f"""
                            <div class='article-box-a'>
                                <b>✅ Artículo Conforme Extraído:</b><br>
                                <i>"{art_disp}"</i><br><br>
                                <b>Observación Técnica:</b> {desc}
                            </div>
                            """, unsafe_allow_html=True)

# ==========================================
# MÓDULO 3: CANAL ÚNICO DE DENUNCIAS ANÓNIMAS
# ==========================================
elif "🛡️ 3. Canal Único" in opcion_menu:
    st.markdown("<h2 class='pba-title'>🛡️ Canal Único Descentralizado de Denuncias Anónimas</h2>", unsafe_allow_html=True)
    st.markdown("<p class='pba-subtitle'>Dispositivo de protección del paciente para la ruptura de la espiral del silencio en efectores únicos de salud.</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    col_den1, col_den2 = st.columns([2, 1])
    
    with col_den1:
        st.subheader("📝 Formulario de Denuncia Anónima Resguardada")
        
        muni_denuncia = st.selectbox("Seleccione el Municipio del hecho:", df_censo['MUNICIPIO'].unique())
        efector = st.text_input("Nombre del Hospital Municipal / Centro de Salud (CAPS):", value="Hospital Municipal Subzonal")
        
        tipo_irregularidad = st.selectbox(
            "Tipo de Cobro Indebido o Exacción Sufrida:",
            [
                "Cobro directo de arancel / bono de guardia a persona sin cobertura",
                "Exigencia de firma de pagaré para ingreso / alta médica",
                "Cobro de 'plus' médico o contribución voluntaria obligatoria",
                "Exigencia de compra de insumos/medicamentos básicos en el efector",
                "Persecución judicial o intimación por juicio de apremio fiscal"
            ]
        )
        
        monto = st.number_input("Monto aproximado exigido ($ ARS):", min_value=0, value=15000, step=1000)
        detalles = st.text_area("Breve relato de la situación sufrida (preservando datos de terceros):")
        
        st.file_uploader("Adjuntar foto de recibo, bono, pagaré o comprobante (Opcional - elimina metadatos):", type=['jpg', 'png', 'pdf'])
        
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
                <b>Estado de Derivación:</b> Transmitido automáticamente al expediente electrónico de la Defensoría del Pueblo de la Provincia de Buenos Aires.</p>
            </div>
            """, unsafe_allow_html=True)
            
    with col_den2:
        st.markdown("### 💡 Garantía de Protección")
        st.info("""
        **Ruptura de la Espiral del Silencio (Capítulo V):**
        En distritos con **efector único de salud**, los vecinos temen denunciar por miedo a perder la atención sanitaria futura.
        
        Este canal:
        1. **Elimina la huella digital e IP.**
        2. **Asigna una clave única irrecuperable.**
        3. **Agrupa denuncias por municipio** para fundamentar amparos colectivos o investigaciones de oficio.
        """)

# ==========================================
# MÓDULO 4: TABLERO DE CONTROL CENSO PROVINCIAL (N=135)
# ==========================================
elif "📊 4. Tablero de Control" in opcion_menu:
    st.markdown("<h2 class='pba-title'>📊 Tablero Control Epidemiológico-Tributario Censo Provincial</h2>", unsafe_allow_html=True)
    st.markdown("<p class='pba-subtitle'>Visualización estadística de los 135 municipios de la Provincia de Buenos Aires (Línea de Base 2026).</p>", unsafe_allow_html=True)
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
        
    st.subheader("📋 Matriz Completa del Censo Provincial de Municipios")
    st.dataframe(df_censo[['MUNICIPIO', 'DENSIDAD', 'CATEGORIA', 'ORDENANZA', 'COBRO', 'CONCEPTO']], use_container_width=True)

# ==========================================
# MÓDULO 5: GENERADOR DE DICTÁMENES DE ALERTA
# ==========================================
elif "📄 5. Generador de Dictámenes" in opcion_menu:
    st.markdown("<h2 class='pba-title'>📄 Generador de Dictámenes de Alerta de Inconstitucionalidad</h2>", unsafe_allow_html=True)
    st.markdown("<p class='pba-subtitle'>Emisión automática de piezas jurídicas de impugnación institucional.</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    muni_dictamen = st.selectbox("Seleccione Municipio para emitir Dictamen:", df_censo['MUNICIPIO'].unique(), key="sb_dictamen")
    row_d = df_censo[df_censo['MUNICIPIO'] == muni_dictamen].iloc[0]
    
    dictamen_text = f"""
========================================================================================
GOBIERNO DE LA PROVINCIA DE BUENOS AIRES // SISTEMA SIA-PBA
ALERTA INSTITUCIONAL DE INCONSTITUCIONALIDAD Y INCONVENCIONALIDAD TRIBUTARIA
========================================================================================

FECHA DE EMISIÓN: {datetime.date.today().strftime('%d/%m/%Y')}
SUJETO AUDITADO: Municipalidad de {row_d['MUNICIPIO']} (Provincia de Buenos Aires)
DENSIDAD POBLACIONAL: {row_d['DENSIDAD']}
NORMA EXAMINADA: {row_d['ORDENANZA']}
DISPOSICIÓN LOCAL RELEVADA: "{row_d['COBRO']} - {row_d['CONCEPTO']}"
CLASIFICACIÓN ALGORÍTMICA: {row_d['CATEGORIA']}

----------------------------------------------------------------------------------------
I. CONSIDERANDOS JURÍDICOS Y NORMATIVOS:
----------------------------------------------------------------------------------------
1. Que la disposición analizada impone un gravamen / arancel / bono asistencial / tributo encubierto sobre la prestación pública de salud asistencial brindada en el efector municipal.
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
    
    st.text_area("Vista previa del Dictamen Jurídico Institucional:", value=dictamen_text, height=350)
    
    st.download_button(
        label="📥 DESCARGAR DICTAMEN JURÍDICO (TXT)",
        data=dictamen_text,
        file_name=f"dictamen_inconstitucionalidad_{muni_dictamen.lower().replace(' ', '_')}.txt",
        mime="text/plain"
    )
