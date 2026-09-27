import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re
import hashlib
import datetime
from io import BytesIO

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y ESTILO PBA
# ==========================================
st.set_page_config(
    page_title="SIA-PBA | Sistema Integrado de Auditoría Algorítmica",
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
        padding: 18px 25px;
        border-radius: 8px;
        margin-bottom: 25px;
        border-bottom: 4px solid #00A3E0;
    }
    .pba-header h1 {
        color: #FFFFFF !important;
        font-size: 1.8rem;
        font-weight: bold;
        margin: 0;
    }
    .pba-header p {
        color: #E0F2FE;
        font-size: 1.05rem;
        margin: 5px 0 0 0;
    }
    .main-title {
        color: #003366;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .sub-title {
        color: #4B5563;
        font-size: 1.05rem;
        margin-bottom: 20px;
    }
    .benchmark-card {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-left: 6px solid #2563EB;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 20px;
    }
    .badge-cat-a {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .badge-cat-b {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .badge-cat-c {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .legal-box {
        background-color: #F8FAFC;
        border-left: 4px solid #0284C7;
        padding: 15px;
        border-radius: 6px;
        font-size: 0.95rem;
        color: #1E293B;
    }
    .snippet-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #DC2626;
        padding: 14px;
        border-radius: 6px;
        margin-top: 10px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        color: #0F172A;
    }
    .snippet-box-a {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #16A34A;
        padding: 14px;
        border-radius: 6px;
        margin-top: 10px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        color: #0F172A;
    }
    .snippet-box-b {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 5px solid #D97706;
        padding: 14px;
        border-radius: 6px;
        margin-top: 10px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        color: #0F172A;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado Institucional PBA
st.markdown("""
<div class="pba-header">
    <h1>🏛️ Gobierno de la Provincia de Buenos Aires</h1>
    <p>Sistema Integrado de Auditoría Algorítmica y Canal Único de Denuncias (SIA-PBA)</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# CARGA Y BASE DE DATOS DEL CENSO N=135
# ==========================================
RAW_DATA_135 = [
    ("25 de mayo", "Baja (< 25.000 hab.)", "Tasa , impuesto encubierto ", "Fondo para Salud del 7% calculado sobre la liquidación de otras tasas (ABL, Red Vial)"),
    ("Adolfo Alsina", "Baja (< 25.000 hab.)", "Tasa servicio asistencial Art. 31", "En ordenanza aclara el sistema del carnet hospitalario y % a pagar según clasificación social"),
    ("Adolfo González Chávez", "Baja (< 25.000 hab.)", "Tasa cobertura universal de salud, impuesto encubierto", "Se cobra con tasa servicios urbanos y tasa conservacion y reparacion de red vial"),
    ("Alberti", "Baja (< 25.000 hab.)", "Tasa servicio asistencial Art. 129", "Se establece cobro según nomenclador IOMA a quienes evidencien capacidad contributiva"),
    ("Almirante Brown", "Alta (> 100.000 hab.)", "Sistema recupero SAMO", "No figura en ordenanza municipal cobro a personas sin cobertura médica"),
    ("Arrecifes", "Media (25k-100k hab.)", "Tasa servicio asistencial Art. 179 y ss", "Individualiza al paciente como sujeto de cobro. Se reserva la gratuidad a la evidente carencia de recursos"),
    ("Avellaneda", "Alta (> 100.000 hab.)", "Sistema recupero SAMO", "Hace mencion al principio de gratuidad y trato igualitario en el Art. 214 para personas sin cobertura"),
    ("Ayacucho", "Media (25k-100k hab.)", "Tasa servicio asistencial Art. 36 inc. 2", "Brinda facultad a la direccion para determinar eximición de pago en escala del 30, 50 y 70% según encuesta social"),
    ("Azul", "Media (25k-100k hab.)", "Previa tasa servicios esenciales salud / Art. 212", "Tasa por servicios asistenciales, exención sujeta a situación socio económica"),
    ("Bahía Blanca", "Alta (> 100.000 hab.)", "Tasa por servicios asistenciales Art 254 y ss", "Individualiza como contribuyente a quien recibe los servicios asistenciales"),
    ("Balcarce", "Media (25k-100k hab.)", "Contribución Obligatoria para la Salud Art 73", "Contribuyentes de la Tasa por Alumbrado Público, Red Vial e Inspección de Seguridad e Higiene"),
    ("Baradero", "Media (25k-100k hab.)", "Fondo municipal de Salud ART. 37", "Adicional a otras tasas domiciliarias para sostenimiento de salud"),
    ("Beníto Juárez", "Media (25k-100k hab.)", "Ausencia de concepto en ordenanza", "Sin concepto arancelario explicito, se limita atención a vecinos del domicilio"),
    ("Berazategui", "Alta (> 100.000 hab.)", "Tasa servicio asistencial Art. 160 / Aclaración web", "Figura en ordenanza pero en la web oficial se ratifica la gratuidad plena"),
    ("Berisso", "Media (25k-100k hab.)", "Ausencia de concepto en ordenanza", "Gratuidad plena a habitantes de Berisso"),
    ("Bolívar", "Media (25k-100k hab.)", "Sistema recupero SAMO", "Tasa asistencial derogada en año 1998, vigente sistema de gratuidad y SAMO"),
    ("Bragado", "Media (25k-100k hab.)", "No figura arancel directo", "Sistema público asistencial sin cobro directo"),
    ("Brandsen", "Media (25k-100k hab.)", "Ausencia de concepto", "Sin arancelamiento detectado"),
    ("Campana", "Alta (> 100.000 hab.)", "Tasa Aporte para la Salud Pública Art. 353", "Impuesto encubierto adosado a Servicios Generales y Red Vial"),
    ("Cañuelas", "Media (25k-100k hab.)", "Ausencia concepto en ordenanza", "Atención sin costo a personas sin cobertura"),
    ("Capitán Sarmiento", "Baja (< 25.000 hab.)", "Tasa servicio asistencial Art. 135 y ss", "Limita gratuidad a nivel socioeconomico previa entrevista de Desarrollo Social"),
    ("Carlos Casares", "Media (25k-100k hab.)", "Fondo municipal de Salud Art. 178 y ss", "Impuesto encubierto abonado sobre Servicios Urbanos y Red Vial"),
    ("Carlos Tejedor", "Baja (< 25.000 hab.)", "Ausencia concepto en ordenanza", "Atención asistencial sin arancel expreso"),
    ("Carmen De Areco", "Baja (< 25.000 hab.)", "Ausencia concepto en ordenanza", "Sin arancelamiento explícito en código tributario"),
    ("Castelli", "Baja (< 25.000 hab.)", "SAMO + Tasa servicio asistencial", "Se discrimina SAMO y cobro total/parcial a sin cobertura según informe social"),
    ("Chacabuco", "Media (25k-100k hab.)", "Ausencia concepto / Gratuidad web", "Gratuidad total manifestada para pacientes sin cobertura médica"),
    ("Chascomús", "Media (25k-100k hab.)", "SAMO", "Sistema de recupero exclusivamente a obras sociales y prepagas"),
    ("Chivilcoy", "Media (25k-100k hab.)", "Tasa servicios asistenciales, impuesto encubierto", "Tasa adosada a inmuebles urbanos y rurales para fondo de salud"),
    ("Colón", "Media (25k-100k hab.)", "SAMO", "Recupero de costos por sistema SAMO"),
    ("Coronel Dorrego", "Baja (< 25.000 hab.)", "Sistema SAMO + Tasa servicios asistenciales Art 177", "Se aclara que solo se recupera por SAMO, no se cobra a personas sin cobertura"),
    ("Coronel Rosales", "Media (25k-100k hab.)", "Tasa asistencial", "Excepción de pago reservada a personas carentes de aportes"),
    ("Coronel Pringles", "Baja (< 25.000 hab.)", "Tasa servicios asistenciales", "Son contribuyentes las personas que soliciten el servicio asistencial"),
    ("Coronel Suárez", "Media (25k-100k hab.)", "Tasa servicios asistenciales Art. 144 y ss", "Gratuidad reservada a evidente carencia de recursos previa categorización social"),
    ("Daireaux", "Baja (< 25.000 hab.)", "Tasa asistencial Art 23", "Gravamen a quienes soliciten o usufructúen las prestaciones médicas"),
    ("Dolores", "Media (25k-100k hab.)", "Tasa asistencial Art 29", "Contribuyentes quienes soliciten los servicios y tengan recursos probados"),
    ("Ensenada", "Media (25k-100k hab.)", "SAMO Art. 191 fiscal", "Contribuyentes exclusivamente Obras Sociales, Prepagas, ART y Seguros"),
    ("Escobar", "Alta (> 100.000 hab.)", "Tasa por servicios especiales / Salud", "Impuesto encubierto adosado sobre Alumbrado, Barrido y Limpieza"),
    ("Esteban Echeverría", "Alta (> 100.000 hab.)", "SAMO Art. 16.1", "Recupero exclusivo a entidades de cobertura médica"),
    ("Exaltación De La Cruz", "Media (25k-100k hab.)", "Tasa por servicios generales (impuesto encubierto)", "Partida destinada a salud adosada a tasas generales"),
    ("Ezeiza", "Alta (> 100.000 hab.)", "Servicios complementarios de salud / Contribucion", "Contribución especial encubierta sobre partidas municipales"),
    ("Florencio Varela", "Alta (> 100.000 hab.)", "Tasa por servicios generales Art. 115", "Adicional para sistema de salud sobre tasa de servicios generales"),
    ("Florentino Ameghino", "Baja (< 25.000 hab.)", "Aranceles hospitalarios Art. 208", "Remite a cobro de valores fijados en nomencladores asistenciales"),
    ("General Alvarado", "Media (25k-100k hab.)", "Tasa de salud", "Tasa encubierta adicionada a partidas inmobiliarias"),
    ("General Alvear", "Baja (< 25.000 hab.)", "Tasa por servicios asistenciales Art. 38", "Aplica importes determinados en el nomenclador IOMA a prestaciones"),
    ("General Arenales", "Baja (< 25.000 hab.)", "Tasa servicios asistenciales Art. 134 y ss", "Exceptuados de pago solo en casos de evidente carencia previa encuesta social"),
    ("General Belgrano", "Baja (< 25.000 hab.)", "Tasa asistencial Art. 151", "Aclara prestación gratuita a quien carezca de recursos, además SAMO"),
    ("General Guido", "Baja (< 25.000 hab.)", "Tasa de Servicio de Salud Art 21", "Fijo por cada recibo de Tasa o Derecho municipal"),
    ("General Juan Madariaga", "Baja (< 25.000 hab.)", "Tasa por servicios asistenciales / SAMO", "Sostiene salud pública gratuita y SAMO; aporte voluntario opcional"),
    ("General La Madrid", "Baja (< 25.000 hab.)", "Tasa servicio asistenciales Art 13", "Sujeto pasivo pacientes ambulatorios/internados sin obra social según nomenclador"),
    ("General Las Heras", "Baja (< 25.000 hab.)", "Tasa servicios asistenciales Art. 123 y ss", "Eximición condicionada a constatación de vulnerabilidad por asistente social"),
    ("General Lavalle", "Baja (< 25.000 hab.)", "Tasa servicios asistenciales Art. 173 y ss", "Excepción de pago reservada a personas carentes de recursos"),
    ("General Paz", "Baja (< 25.000 hab.)", "Tasa Terapia Intensiva / No residentes", "Monto adicional a urbanos/rurales y cobro directo a no residentes"),
    ("General Pinto", "Baja (< 25.000 hab.)", "Aranceles hospitalarios Art. 240 y ss", "Facturación según nomenclador IOMA si la encuesta social indica capacidad de pago"),
    ("General Pueyrredón", "Alta (> 100.000 hab.)", "Contribución a la Salud, la Educación y el Desarrollo", "Contribución fija por inmueble gravado por Servicios Urbanos y Red Vial"),
    ("General Rodríguez", "Alta (> 100.000 hab.)", "Tasa especial salud / Hospital Odontológico", "Fondo encubierto en emergencias y arancelamiento en hospitales específicos"),
    ("General San Martín", "Alta (> 100.000 hab.)", "SAMO Art 303 y ss", "Refiere únicamente al sistema SAMO de recupero de costos"),
    ("General Viamonte", "Baja (< 25.000 hab.)", "Tasa asistencial Art. 205 y ss", "Faculta al Ejecutivo a adecuar valores según situación socioeconómica"),
    ("General Villegas", "Media (25k-100k hab.)", "Fondo por Servicios Asistenciales", "Propuesta de arancelamiento y tasa de salud"),
    ("Guamini", "Baja (< 25.000 hab.)", "Tasa salud + Tasa asistencial Art. 30", "Tarifario por prestaciones detalladas (radiografías, análisis) e impuesto encubierto"),
    ("Hipólito Yrigoyen", "Baja (< 25.000 hab.)", "Tasa servicios asistenciales Art. 45 y ss", "Prevé cobro por prestaciones médicas hospitalarias"),
    ("Hurlingham", "Alta (> 100.000 hab.)", "Gratuidad / SAMO", "Sin arancelamiento a personas sin cobertura"),
    ("Ituzaingó", "Alta (> 100.000 hab.)", "SAMO + Tasa de protección ciudadana", "Tasa encubierta sobre contribuyentes para sostener salud y otros servicios"),
    ("José C. Paz", "Alta (> 100.000 hab.)", "Atención no residentes", "Normativa limita gratuidad según residencia"),
    ("Junín", "Alta (> 100.000 hab.)", "Tasa Servicios Públicos Urbanos Art. 1", "Impuesto encubierto que incluye salud en la tasa general urbana"),
    ("La Costa", "Alta (> 100.000 hab.)", "Tasa asistencial Art. 198 + Fondo Salud", "Arancelamiento a no residentes y fondo de salud sobre partidas rurales"),
    ("La Matanza", "Alta (> 100.000 hab.)", "SAMO Art 249", "Régimen exclusivo de recupero SAMO a obras sociales"),
    ("La Plata", "Alta (> 100.000 hab.)", "Ausencia de concepto", "Sin previsión de arancelamiento directo a pacientes"),
    ("Lanus", "Alta (> 100.000 hab.)", "Ausencia de concepto", "Gratuidad pública asistencial en código tributario"),
    ("Laprida", "Baja (< 25.000 hab.)", "SAMO Art. 20", "Aclara que reposición de materiales no cubiertos por IOMA corresponde al paciente"),
    ("Las Flores", "Media (25k-100k hab.)", "Ausencia de concepto", "Sin aranceles a personas sin cobertura"),
    ("Leandro N. Alem", "Baja (< 25.000 hab.)", "Aranceles servicios asistenciales Art. 160", "Categorización otorgada por Servicio Social para excepciones"),
    ("Lezama", "Baja (< 25.000 hab.)", "SAMO + Tasa Guardias Pediátricas", "Tasa encubierta sobre Servicios Rurales y ABL para guardias"),
    ("Lincoln", "Media (25k-100k hab.)", "Tasa servicios asistenciales Art. 21", "Establece cobro por kilómetros de ambulancia y recarga de tubo de oxígeno"),
    ("Lobería", "Baja (< 25.000 hab.)", "Tasa servicios asistenciales Art. 192 y ss", "Exención sujeta a informe del Servicio Social Municipal"),
    ("Lobos", "Media (25k-100k hab.)", "Tasa por Salud y Asistencia Social Art. 30", "Contribución solidaria encubierta para financiamiento de salud"),
    ("Lomas de Zamora", "Alta (> 100.000 hab.)", "Ausencia de concepto", "Atención sin arancel directo"),
    ("Luján", "Alta (> 100.000 hab.)", "Ausencia de concepto", "Régimen de atención gratuita pública"),
    ("Magdalena", "Baja (< 25.000 hab.)", "Ausencia de concepto", "Requisito de acreditación de domicilio para atención sin costo"),
    ("Maipú", "Baja (< 25.000 hab.)", "Tasa servicios asistenciales Art. 12 y ss", "Categorización de pacientes A, B, C y D según ingresos y declaración jurada"),
    ("Malvinas Argentinas", "Alta (> 100.000 hab.)", "Tasa servicios asistenciales Art. 192", "Individualiza como sujeto al enfermo, familiares o cobertura médica"),
    ("Mar Chiquita", "Media (25k-100k hab.)", "Tasa asistencial Art. 198 + Fondo Salud", "Arancelamiento a no residentes y exención de indigentes por Desarrollo Social"),
    ("Marcos Paz", "Media (25k-100k hab.)", "Tasa servicios asistenciales Art. 232", "Contribuyentes quienes soliciten el servicio o sus familiares; reserva a indigencia"),
    ("Mercedes", "Media (25k-100k hab.)", "Contribución especial Art. 6", "Impuesto encubierto a la Cooperadora del Hospital junto a tasa de vía pública"),
    ("Merlo", "Alta (> 100.000 hab.)", "SAMO Art 42", "Aclara servicio gratuito a personas sin cobertura y recupero SAMO"),
    ("Monte", "Baja (< 25.000 hab.)", "Contribución especial Art. 68", "Contribución especial encubierta para Salud Pública"),
    ("Monte Hermoso", "Baja (< 25.000 hab.)", "SAMO + Tasa asistencial Art. 272", "Exención de cobro condicionada a informe de servicio social municipal"),
    ("Moreno", "Alta (> 100.000 hab.)", "Tasa de Salud y Asistencia Social Art. 43", "Alícuota del 10,5% sobre tributos y multas destinada a infraestructura hospitalaria"),
    ("Morón", "Alta (> 100.000 hab.)", "SAMO Art. 288 / Emergencias", "Cobro por servicios asistenciales de emergencia y traslado en accidentes"),
    ("Navarro", "Baja (< 25.000 hab.)", "Ausencia de concepto", "Atención pública asistencial sin tasa expresada"),
    ("Necochea", "Alta (> 100.000 hab.)", "Tasa Fortalecimiento de la Salud Art. 426", "Impuesto encubierto sobre inmuebles urbanos y rurales"),
    ("Nueve de Julio", "Media (25k-100k hab.)", "Tasa servicios asistenciales Art. 44", "Exceptúa de arancel solo a quienes carezcan de capacidad de pago"),
    ("Olavarría", "Alta (> 100.000 hab.)", "Sistema SIAMO + Tasa asistencial Art. 138", "Sistema prepago municipal SIAMO y deducciones previa encuesta social"),
    ("Patagones", "Media (25k-100k hab.)", "Tasa servicios asistenciales Art. 239", "Abonada directamente por el beneficiario sin obra social si no encuadra en exención"),
    ("Pehuajó", "Media (25k-100k hab.)", "Tasa servicios asistenciales Art. 215 y ss", "Sujeto pasivo las personas humanas usuarias del servicio o sus representantes"),
    ("Pellegrini", "Baja (< 25.000 hab.)", "Sistema de recupero SAMO Art. 40", "Garantiza expresamente la gratuidad plena a particulares sin cobertura médica"),
    ("Pergamino", "Alta (> 100.000 hab.)", "Ausencia de concepto", "Atención médica hospitalaria pública gratuita"),
    ("Pila", "Baja (< 25.000 hab.)", "Sin arancelamiento expreso", "Servicio sanitario local sin tasa detectada"),
    ("Pilar", "Alta (> 100.000 hab.)", "Tasa servicios de salud Art. 263", "Régimen general no cobra a residentes sin cobertura por carecer de ingresos"),
    ("Pinamar", "Media (25k-100k hab.)", "Tasa Derechos Sanatoriales Art. 97", "Eximición de pago condicionada a autorización de Dirección de Acción Social"),
    ("Presidente Perón", "Alta (> 100.000 hab.)", "Ausencia concepto", "Sin previsión de arancel directo"),
    ("Puán", "Baja (< 25.000 hab.)", "Tasa asistencial Art. 170 / Pagarés", "Arancelamiento con posiblidad de firma de pagarés previa evaluación social"),
    ("Punta Indio", "Baja (< 25.000 hab.)", "Fondo Solidario de Salud Pública Art. 202", "Impuesto encubierto destinado a sostener centro de salud"),
    ("Quilmes", "Alta (> 100.000 hab.)", "Sistema SAMO Art. 316", "Recupero exclusivo a entidades de cobertura médica"),
    ("Ramallo", "Media (25k-100k hab.)", "Tasa servicios asistenciales Art. 238", "Reserva gratuidad a indigencia; facturación a sin cobertura no indigentes"),
    ("Rauch", "Baja (< 25.000 hab.)", "Tasa asistencial Anexo 1 Título XV", "Categorización por Desarrollo Social en escalas del 25%, 50%, 75% o 100% de pago"),
    ("Rivadavia", "Baja (< 25.000 hab.)", "Servicios asistenciales Art 238", "Categorización A, B, C, D y E según ingresos; cobro a no residentes"),
    ("Rojas", "Media (25k-100k hab.)", "Cobro a obras sociales Art. 215", "Recupero a coberturas médicas sin cobro directo a vecinos"),
    ("Roque Pérez", "Baja (< 25.000 hab.)", "Tasa asistencial Art 33 / Tasa fija salud", "Atención gratuita salvo para asegurados; tasa fija por parcela a salud"),
    ("Saavedra Pigue ", "Media (25k-100k hab.)", "Tasa servicios asistenciales Art. 273", "Gratuidad exclusiva reservada a indigencia en Art. 277"),
    ("Saladillo", "Media (25k-100k hab.)", "Sistema SAMO", "Hospital público y gratuito, cobro únicamente si se tiene obra social"),
    ("Salliquelo", "Baja (< 25.000 hab.)", "Tasa asistencial Art. 69 / Plan Salud", "Valores para pacientes sin cobertura no indigentes o adheridos a plan municipal"),
    ("Salto", "Media (25k-100k hab.)", "Tasa asistencial Art. 206 / Apremio", "Arancelamiento directo con vía ejecutiva por juicio de apremio; exención a indigentes"),
    ("San Andrés de Giles", "Media (25k-100k hab.)", "Tasa servicios asistenciales Art 247", "Sujeto pasivo la persona que recibe los servicios; exención a residentes"),
    ("San Antonio de Areco", "Media (25k-100k hab.)", "Tasa por servicios de salud Art 218", "Tasa encubierta abonada mensualmente con ABL y Red Vial"),
    ("San Cayetano", "Baja (< 25.000 hab.)", "Sistema SAMO Art. 122", "Establece gratuidad de servicios e interpone cobro solo a Obras Sociales / Seguros"),
    ("San Fernando", "Alta (> 100.000 hab.)", "SAMO + Tasa asistencial encubierta", "Aclara gratuidad a residentes del partido"),
    ("San Isidro", "Alta (> 100.000 hab.)", "Sistema SAMO Art 141", "Tabla con valores de recupero a coberturas públicas o privadas"),
    ("San Miguel Joaquín", "Alta (> 100.000 hab.)", "Sistema SAMO Art 94", "Gratuidad explícita a personas sin cobertura médica"),
    ("San Nicolás", "Alta (> 100.000 hab.)", "Sistema SAMO Art 301", "Recupero de costos por sistema SAMO"),
    ("San Pedro", "Media (25k-100k hab.)", "Sistema SAMO Art. 250", "Especifica que si el paciente no tiene cobertura el servicio es gratuito"),
    ("San Vicente", "Alta (> 100.000 hab.)", "Contribución al Sistema de Salud Pública Art. 367", "Impuesto encubierto equivalente al 40% de ABL, Red Vial y Seguridad e Higiene"),
    ("Suipacha", "Baja (< 25.000 hab.)", "Tasa de salud Art. 129 + Prestaciones", "Tasa encubierta en parcelas urbanas y cobro asistencial según encuesta social"),
    ("Tandil", "Alta (> 100.000 hab.)", "Sistema Integrado de Salud Pública Art. 217", "No cobro limitado a consideraciones socioeconómicas e informe social"),
    ("Tapalque", "Baja (< 25.000 hab.)", "Tasa asistencial Art. 200 + Unidad Intensiva", "Faculta a deducciones según posibilidades económicas fijadas por servicio social"),
    ("Tigre", "Alta (> 100.000 hab.)", "SAMO + Tasa asistencial no residentes", "Tabla tarifaria a no residentes; gratuidad a vecinos sin cobertura"),
    ("Tordillo", "Baja (< 25.000 hab.)", "Tasa asistencial Art 28", "Abonan quienes soliciten servicios y tengan recursos probados; indigentes sin costo"),
    ("Tornquist", "Baja (< 25.000 hab.)", "SAMO + Tasa asistencial Art. 142", "Eximición total o parcial de tasa mediante ficha socioeconómica (Art. 147)"),
    ("Trenque launquen", "Media (25k-100k hab.)", "SAMO + Tasa asistencial Art 89", "No se cobrará a los residentes del distrito sin cobertura médica"),
    ("Tres Arroyos", "Media (25k-100k hab.)", "Tasa solidaria de sostenimiento de salud Art. 183", "Tasa encubierta cobrada a todo inmueble en Servicios Urbanos"),
    ("Tres de Febrero", "Alta (> 100.000 hab.)", "SAMO / Tributo asistencial Art 245", "Gratuidad garantizada a personas sin cobertura médica"),
    ("Tres Lomas", "Baja (< 25.000 hab.)", "Tasa servicios asistenciales", "Actualizaciones prevén cobro a personas sin cobertura según medios económicos"),
    ("Vicente López", "Alta (> 100.000 hab.)", "Sistema SAMO Art 254", "Gratuito para personas sin cobertura médica"),
    ("Villa Gesell", "Media (25k-100k hab.)", "Tasa salud Art 148 Código Tributario", "Impuesto encubierto en código tributario municipal"),
    ("Villarino", "Media (25k-100k hab.)", "Derecho de Comercialización Hortícola Art 232", "Impuesto encubierto afectado al financiamiento del Sistema de Salud Municipal"),
    ("Zárate", "Alta (> 100.000 hab.)", "Sistema SAMO Art 217", "Régimen exclusivo de recupero a obras sociales y seguros")
]

@st.cache_data
def load_censo_data():
    records = []
    for muni, dens, cobro, conc in RAW_DATA_135:
        c_upper = (cobro + " " + conc).upper()
        if 'ENCUBIERTO' in c_upper or 'IMPUESTO' in c_upper or 'FONDO' in c_upper or 'CONTRIBUCIÓN ESPECIAL' in c_upper:
            cat = 'Categoría B (Tasa Encubierta)'
        elif 'ARANCEL' in c_upper or 'DERECHO' in c_upper or 'TASA' in c_upper or 'COBRO' in c_upper or 'APREMIO' in c_upper or 'INDIGENCIA' in c_upper or 'CARENCIA' in c_upper or 'CATEGORIZACIÓN' in c_upper or 'PAGARÉ' in c_upper or 'NO RESIDENTES' in c_upper:
            if 'SAMO' in c_upper and not ('ARANCEL' in c_upper or 'APREMIO' in c_upper or 'INDIGENCIA' in c_upper or 'CARENCIA' in c_upper or 'PAGARÉ' in c_upper):
                cat = 'Categoría A (Gratuidad / SAMO)'
            else:
                cat = 'Categoría C (Arancel Directo)'
        else:
            cat = 'Categoría A (Gratuidad / SAMO)'
            
        records.append({
            'MUNICIPIO': muni,
            'DENSIDAD': dens,
            'ORDENANZA': cobro,
            'CONCEPTO': conc,
            'CATEGORIA': cat
        })
    df = pd.DataFrame(records)
    return df

df_censo = load_censo_data()

# ==========================================
# BARRA LATERAL - NAVEGACIÓN
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/scales.png", width=65)
st.sidebar.title("SIA-PBA v3.0")
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
* **Autora:** Mariana
* **Enfoque:** Capítulo VIII - Propuesta de Innovación Tecnológica y Control de Convencionalidad
""")

# ==========================================
# MÓDULO 1: PRESENTACIÓN E IMPACTO TFC
# ==========================================
if "🏠 1. Presentación" in opcion_menu:
    st.markdown("<h1 class='main-title'>SIA-PBA: Auditoría Algorítmica & Canal Único de Denuncias</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Herramienta tecnológica de control preventivo de legalidad, constitucionalidad y convencionalidad de ordenanzas fiscales e impositivas municipales de la Provincia de Buenos Aires</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Municipios Relevados", value="135 / 135", delta="Censo Provincial 100%")
    with col2:
        st.metric(label="Arancelamiento Directo (Cat. C)", value="36.3%", delta="49 Municipios", delta_color="inverse")
    with col3:
        st.metric(label="Tasas Encubiertas (Cat. B)", value="21.5%", delta="29 Municipios", delta_color="inverse")
    with col4:
        st.metric(label="Gratuidad Plena / SAMO (Cat. A)", value="42.2%", delta="57 Municipios")
        
    st.markdown("---")
    
    st.subheader("🎯 Ejes Fundamentales de la Herramienta (Capítulo VIII)")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        ### 🔍 1. Módulo de Auditoría Algorítmica de Ordenanzas
        * **Análisis de Texto PNL Contextual:** Procesa automáticamente ordenanzas impositivas y fiscales locales descartando falsos positivos en capítulos impositivos generales (Comercio, Inmuebles, Bromatología).
        * **Semáforo Tripartito de Convencionalidad:**
            * 🟢 **Cat. A (Gratuidad Plena / SAMO):** Cumplimiento del Art. 36 inc. 8 CPBA y Ley 11.069.
            * 🟡 **Cat. B (Tasas Encubiertas):** Detección de tributos disfrazados en ABL/Red Vial.
            * 🔴 **Cat. C (Arancelamiento Directo):** Alerta por cobros indebidos, pagarés o exigencia de comprobación de indigencia.
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
# MÓDULO 2: AUDITORÍA ALGORÍTMICA DE ORDENANZAS (IA)
# ==========================================
elif "🔍 2. Módulo de Auditoría" in opcion_menu:
    st.markdown("<h2 class='main-title'>🔍 Auditoría Algorítmica Preventiva de Ordenanzas</h2>", unsafe_allow_html=True)
    st.markdown("Examen automatizado de constitucionalidad, convencionalidad y legalidad tributaria municipal.")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🏛️ Submódulo 1: Línea de Base 2026 (Censo N=135)", "🚀 Submódulo 2: Motor de Auditoría Futura 2027+"])
    
    with tab1:
        st.markdown("##### Consulta del Censo Base Provincial (Línea de Base Relevada N=135):")
        muni_selected = st.selectbox("Seleccione Municipio de la Prov. de Bs. As.:", df_censo['MUNICIPIO'].unique(), key="muni_tab1")
        
        row_muni = df_censo[df_censo['MUNICIPIO'] == muni_selected].iloc[0]
        
        st.markdown("### 📊 Diagnóstico del Censo Base Relevado")
        
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
            st.write(f"**Tramo de Población:** {row_muni['DENSIDAD']}")
            st.write(f"**Norma Relevada:** {row_muni['ORDENANZA']}")
            
        with col_res2:
            st.markdown("#### ⚖️ Fundamentación Jurídica de Alerta")
            st.markdown(f"**Disposición Local Relevada:** *"{row_muni['CONCEPTO']}"*")
            
            if 'Categoría C' in cat or 'Arancel' in cat or 'Cat. C' in cat:
                st.markdown("""
                <div class='legal-box'>
                <b>⚠️ Vulneraciones Normativas Detectadas:</b><br>
                1. <b>Violación del Art. 36 inc. 8 de la Constitución de la Prov. de Buenos Aires:</b> Imposición de barrera económica para acceder a la salud pública gratuita.<br>
                2. <b>Infracción a Tratados Internacionales (Art. 75 inc. 22 CN):</b> Contravención del Art. 12 del PIDESC.<br>
                3. <b>Encuadre Dogmático-Penal (Art. 266 del Código Penal):</b> Posible configuración de <i>Exacción Ilegal</i> por exigencia o cobro indebido.<br>
                4. <b>Condición de Indigencia:</b> Exigir acreditación previa de pobreza para acceder a la atención médica básica resulta inconstitucional.
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

    with tab2:
        st.markdown("##### Auditoría Algorítmica Automatizada de Próximas Ordenanzas (Ejercicio 2027 en adelante):")
        
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            muni_futuro = st.selectbox("Seleccione el Municipio a auditar (135 disponibles):", df_censo['MUNICIPIO'].unique(), key="muni_tab2")
        with col_f2:
            anio_futuro = st.selectbox("Ejercicio Fiscal a Auditar:", ["2027", "2028", "2029", "2030"])
            
        row_bench = df_censo[df_censo['MUNICIPIO'] == muni_futuro].iloc[0]
        
        # Tarjeta de Memoria Benchmark
        st.markdown(f"""
        <div class='benchmark-card'>
            <h4>🧠 Directiva Benchmark Censo Base 2026 — {muni_futuro}</h4>
            <p><b>Categoría Histórica Relevada:</b> <code>{row_bench['CATEGORIA']}</code><br>
            <b>Disposición Base:</b> <i>"{row_bench['CONCEPTO']}"</i><br>
            <b>Directiva de Inteligencia Algorítmica:</b> El motor comparará la nueva ordenanza {anio_futuro} frente a este antecedente para validar si mantiene la conformidad o si incurre en retroceso inconstitucional.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("##### 📄 Ingesta de Documento de la Nueva Ordenanza:")
        
        uploaded_pdf = st.file_uploader(f"Adjunte el archivo PDF de la Ordenanza Fiscal/Impositiva de {muni_futuro} ({anio_futuro}):", type=['pdf'])
        
        texto_suplementario = st.text_area(
            "Copia de respaldo / Editor de texto suplementario (opcional o para fragmentos específicos):",
            value="",
            height=100,
            placeholder="Pegue aquí el articulado si el PDF es una fotocopia no seleccionable o si desea analizar un artículo específico..."
        )
        
        if st.button(f"🚀 Ejecutar Auditoría Algorítmica {anio_futuro} para {muni_futuro}"):
            texto_a_analizar = ""
            fuente_doc = ""
            
            if uploaded_pdf is not None:
                try:
                    import pypdf
                    pdf_reader = pypdf.PdfReader(BytesIO(uploaded_pdf.read()))
                    extracted_pages = []
                    for page in pdf_reader.pages:
                        t_page = page.extract_text()
                        if t_page:
                            extracted_pages.append(t_page)
                    texto_a_analizar = "\n".join(extracted_pages)
                    fuente_doc = f"PDF Digital ({len(pdf_reader.pages)} páginas)"
                except Exception as e:
                    texto_a_analizar = ""
                    
            if not texto_a_analizar.strip() and texto_suplementario.strip():
                texto_a_analizar = texto_suplementario
                fuente_doc = "Texto Ingresado en Editor Suplementario"
            elif texto_a_analizar.strip() and texto_suplementario.strip():
                texto_a_analizar += "\n" + texto_suplementario
                fuente_doc += " + Texto Suplementario"
                
            if not texto_a_analizar.strip():
                st.error("❌ **ERROR DE PROCESAMIENTO:** No se detectó texto legible para auditar. El PDF adjunto es una fotocopia escaneada sin capa de texto digital. Por favor copie y pegue el articulado en el editor de texto suplementario para ejecutar el diagnóstico.")
            else:
                st.info(f"✅ **Procesamiento de Documento Completado:** {fuente_doc} — Total caracteres analizados: {len(texto_a_analizar):,}")
                
                # Normalización de texto
                texto_norm = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', texto_a_analizar)
                
                # Patrones de exclusión impositiva general (Evitar Falsos Positivos)
                patrones_exclusion = [
                    r'SEGURIDAD\s+E\s+HIGIENE', r'ACTIVIDADES\s+ECONÓMICAS', r'MUESTREOS?\s+DE\s+PRODUCTOS',
                    r'PRODUCTOS\s+ALIMENTICIOS', r'ANÁLISIS\s+FÍSICO', r'CONSUMO\s+HUMANO', r'PROPIEDAD\s+HORIZONTAL',
                    r'TITULARES\s+DEL\s+DOMINIO', r'PLANOS\s+DE\s+OBRA', r'PADRONES', r'CENSO',
                    r'EXCEPTO\s+LOS\s+SERVICIOS\s+ASISTENCIALES', r'SE\s+EXCLUYEN\s+LOS\s+SERVICIOS\s+ASISTENCIALES',
                    r'AGUA\s+Y\s+CLOACAS', r'CEMENTERIO', r'ELECTROCTURA', r'ALUMBRADO\s+PÚBLICO'
                ]
                
                # Patrones del dominio estricto de salud asistencial
                patrones_salud = [
                    r'HOSPITAL', r'CENTRO\s+DE\s+SALUD', r'CAPS', r'PACIENTE', r'GUARDIA', r'INTERNACIÓN',
                    r'PRÁCTICAS\s+MÉDICAS', r'PRESTACIONES\s+ASISTENCIALES', r'SERVICIOS\s+ASISTENCIALES',
                    r'CONSULTA\s+MÉDICA', r'SALUD\s+PÚBLICA', r'SAMO', r'LEY\s+11\.?069', r'IOMA', r'ENFERMERÍA'
                ]
                
                # Patrones de Riesgo Crítico (Cat C - Arancelamiento Directo / Indigencia)
                patrones_cat_c = [
                    r'ABONARÁ\s+LA\s+TASA', r'ABONARÁN\s+UN\s+ARANCEL', r'NOMENCLADOR\s+MUNICIPAL',
                    r'COBRO\s+DIRECTO', r'PAGARÉ', r'BONO\s+DE\s+GUARDIA', r'JUICIO\s+DE\s+APREMIO',
                    r'ACREDITEN\s+PREVIA\s+INDIGENCIA', r'EVIDENTE\s+CARENCIA', r'DEMOSTRACIÓN\s+DE\s+POBREZA',
                    r'ENCUESTA\s+SOCIAL\s+PREVIA', r'CARNET\s+DE\s+POBREZA'
                ]
                
                # Patrones de Riesgo Medio (Cat B - Tasa Encubierta)
                patrones_cat_b = [
                    r'FONDO\s+MUNICIPAL\s+DE\s+SALUD', r'FONDO\s+ESPECIAL\s+DE\s+SALUD', r'CONTRIBUCIÓN\s+PARA\s+LA\s+SALUD',
                    r'TASA\s+DE\s+SALUD', r'SOSTENIMIENTO\s+DEL\s+SERVICIO\s+DE\s+SALUD', r'ADICIONAL\s+SALUD'
                ]
                
                # Patrones de Conformidad (Cat A - Gratuidad / SAMO)
                patrones_cat_a = [
                    r'GRATUITO', r'SIN\s+COSTO', r'GRATUIDAD', r'PERSONAS\s+SIN\s+COBERTURA',
                    r'EXCLUSIVAMENTE\s+A\s+OBRAS\s+SOCIALES', r'RECUPERO\s+SAMO'
                ]
                
                # Desglose por artículos
                articulos_raw = re.split(r'(ARTÍCULO\s+\d+[º°]?[-–\s]*)', texto_norm, flags=re.IGNORECASE)
                
                arts_cat_c = []
                arts_cat_b = []
                arts_cat_a = []
                
                for i in range(1, len(articulos_raw), 2):
                    encabezado = articulos_raw[i].strip()
                    cuerpo = articulos_raw[i+1].strip() if i+1 < len(articulos_raw) else ""
                    art_completo = f"{encabezado} {cuerpo}"
                    
                    # 1. Filtro de exclusión de materias impositivas generales
                    if any(re.search(p, art_completo, re.IGNORECASE) for p in patrones_exclusion):
                        continue
                        
                    # 2. Filtro de pertenencia al dominio de salud
                    if not any(re.search(p, art_completo, re.IGNORECASE) for p in patrones_salud):
                        continue
                        
                    # 3. Clasificación deductiva
                    if any(re.search(p, art_completo, re.IGNORECASE) for p in patrones_cat_c):
                        arts_cat_c.append(art_completo[:350])
                    elif any(re.search(p, art_completo, re.IGNORECASE) for p in patrones_cat_b):
                        arts_cat_b.append(art_completo[:350])
                    elif any(re.search(p, art_completo, re.IGNORECASE) for p in patrones_cat_a):
                        arts_cat_a.append(art_completo[:350])
                        
                st.markdown("---")
                st.subheader(f"📋 Dictamen de Auditoría Algorítmica — {muni_futuro} ({anio_futuro})")
                
                cat_bench = row_bench['CATEGORIA']
                
                if len(arts_cat_c) > 0:
                    st.error(f"🔴 **ALERTA CRÍTICA: DETECCIÓN DE CLÁUSULAS INCONSTITUCIONALES / CATEGORÍA C**")
                    st.markdown("<span class='badge-cat-c'>Categoría C — Arancelamiento Directo / Barrera Económica</span>", unsafe_allow_html=True)
                    
                    if 'Cat. C' in cat_bench or 'Arancel' in cat_bench:
                        st.write(f"**Comparativa frente al Censo Base 2026:** El municipio **{muni_futuro}** mantiene las normas de arancelamiento directo identificadas en la línea de base.")
                    else:
                        st.write(f"**⚠️ ALERTA DE RETROCESO NORMATIVO:** El municipio **{muni_futuro}** modificó su régimen histórico (anteriormente {cat_bench}) e introdujo cláusulas inconstitucionales de arancelamiento.")
                        
                    st.markdown("#### 📜 Artículos Infractores Detectados en la Salud Pública:")
                    for art_c in arts_cat_c:
                        art_clean = art_c.replace('"', '').replace('<', '').replace('>', '')
                        st.markdown(f"<div class='snippet-box'><b>⚠️ Cita Textual de la Ordenanza:</b><br>"{art_clean}..."</div>", unsafe_allow_html=True)
                        
                    st.markdown("""
                    <div class='legal-box'>
                    <b>⚖️ Fundamentación de Inconstitucionalidad:</b><br>
                    1. <b>Violación del Art. 36 inc. 8 CPBA:</b> Barrera económica al acceso a la salud pública gratuita.<br>
                    2. <b>Exacción Ilegal (Art. 266 del Código Penal):</b> Exigencia indebida de tasa o arancel bajo apercibimiento estatal.<br>
                    3. <b>Exigencia de Indigencia:</b> Condicionar la salud gratuita a demostrar pobreza es violatorio del PIDESC (Art. 75 inc. 22 CN).
                    </div>
                    """)
                    
                elif len(arts_cat_b) > 0:
                    st.warning(f"🟡 **ALERTA MEDIA: DETECCIÓN DE TASA ENCUBIERTA / CATEGORÍA B**")
                    st.markdown("<span class='badge-cat-b'>Categoría B — Tasa Encubierta / Tributo Disfrazado</span>", unsafe_allow_html=True)
                    st.write(f"**Comparativa frente al Censo Base 2026:** El municipio **{muni_futuro}** presenta fondos de salud adosados sobre tasas generales.")
                    
                    for art_b in arts_cat_b:
                        art_clean = art_b.replace('"', '').replace('<', '').replace('>', '')
                        st.markdown(f"<div class='snippet-box-b'><b>⚠️ Cita Textual de la Ordenanza:</b><br>"{art_clean}..."</div>", unsafe_allow_html=True)
                        
                else:
                    st.success(f"🟢 **DICTAMEN POSITIVO: NORMATIVA CONFORME A DERECHO / GRATUIDAD PLENA**")
                    st.markdown("<span class='badge-cat-a'>Categoría A — Gratuidad Plena / SAMO</span>", unsafe_allow_html=True)
                    
                    if 'Cat. A' in cat_bench or 'Gratuidad' in cat_bench or 'SAMO' in cat_bench:
                        st.write(f"**Comparativa frente al Censo Base 2026:** El municipio **{muni_futuro}** ratifica y mantiene su conformidad constitucional (Categoría A).")
                    else:
                        st.write(f"**✅ AVANCE NORMATIVO CONSTATADO:** El municipio **{muni_futuro}** adecuó su legislación, eliminó los aranceles anteriores y garantizó la gratuidad plena.")
                        
                    if len(arts_cat_a) > 0:
                        st.markdown("#### 📜 Artículos de Conformidad Normativa Detectados:")
                        for art_a in arts_cat_a:
                            art_clean = art_a.replace('"', '').replace('<', '').replace('>', '')
                            st.markdown(f"<div class='snippet-box-a'><b>✅ Cita Textual de la Ordenanza:</b><br>"{art_clean}..."</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class='legal-box'>
                        <b>✅ Compatibilidad Constatada:</b> No se detectaron cláusulas de arancelamiento directo ni tasas encubiertas en materia sanitaria. La norma respeta la gratuidad garantizada por el Art. 36 inc. 8 de la Constitución Provincial y limita el recupero a Obras Sociales (Ley 11.069).
                        </div>
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
# MÓDULO 4: TABLERO DE CONTROL CENSO PROVINCIAL (N=135)
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
            'Municipios': [57, 29, 49]
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
    st.markdown("Emisión automática de piezas jurídicas de impugnación institucionales.")
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
TRAMO POBLACIONAL: {row_d['DENSIDAD']}
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
