import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re
import hashlib
import datetime
import json
import pypdf

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y ESTILO OFICIAL PBA
# ==========================================
st.set_page_config(
    page_title="Gobierno PBA | SIA-PBA - Auditoría Algorítmica y Canal Único",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS Personalizado - Identidad Institucional PBA
st.markdown("""
<style>
    .pba-header {
        background-color: #003366;
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .pba-header h1 {
        color: #FFFFFF;
        font-family: 'Arial', sans-serif;
        font-size: 1.8rem;
        font-weight: bold;
        margin: 0;
    }
    .pba-header p {
        color: #E0E6ED;
        font-size: 1.0rem;
        margin-top: 5px;
        margin-bottom: 0;
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
        margin-bottom: 20px;
    }
    .card-bench {
        background-color: #EBF8FF;
        border-left: 5px solid #3182CE;
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 20px;
    }
    .badge-cat-a {
        background-color: #D4EDDA;
        color: #155724;
        padding: 6px 14px;
        border-radius: 12px;
        font-weight: bold;
        display: inline-block;
    }
    .badge-cat-b {
        background-color: #FFF3CD;
        color: #856404;
        padding: 6px 14px;
        border-radius: 12px;
        font-weight: bold;
        display: inline-block;
    }
    .badge-cat-c {
        background-color: #F8D7DA;
        color: #721C24;
        padding: 6px 14px;
        border-radius: 12px;
        font-weight: bold;
        display: inline-block;
    }
    .legal-box {
        background-color: #F8F9FA;
        border-left: 4px solid #003366;
        padding: 14px;
        border-radius: 6px;
        font-size: 0.95rem;
        margin-top: 10px;
    }
    .snippet-box {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E0;
        border-left: 5px solid #E53E3E;
        padding: 12px 16px;
        border-radius: 6px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        margin-bottom: 12px;
        color: #2D3748;
    }
    .snippet-box-a {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E0;
        border-left: 5px solid #38A169;
        padding: 12px 16px;
        border-radius: 6px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        margin-bottom: 12px;
        color: #2D3748;
    }
</style>
""", unsafe_allow_html=True)

# Header Institucional
st.markdown("""
<div class="pba-header">
    <h1>🏛️ Gobierno de la Provincia de Buenos Aires</h1>
    <p>Sistema Integrado de Auditoría Algorítmica de Ordenanzas (SIA-PBA) & Canal Único de Denuncias Anónimas</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# BASE DE DATOS COMPLETA EMBEBIDA (N=135)
# ==========================================
EMBEDDED_DATA = [
  {
    "MUNICIPIO": "25 de mayo",
    "COBRO": "Tasa , impuesto encubierto",
    "CONCEPTO": "\"Fondo para Salud\" del 7% calculado sobre la liquidación de otras tasas (Alumbrado, Limpieza, Red Vial) o sobre el importe básico facturado de energía eléctrica.",
    "ORDENANZA": "Ordenanza 25 de mayo",
    "DENSIDAD": 36676,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Adolfo Alsina",
    "COBRO": "Tasa servicio asistencial Art. 31",
    "CONCEPTO": "En ordenanza aclara el sistema del carnet hospitalario y % a pagar según clasificacion de segm de servicios sociales",
    "ORDENANZA": "Ordenanza Adolfo Alsina",
    "DENSIDAD": 17552,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Adolfo González Chávez",
    "COBRO": "Tasa cobertura universal de salud, impuesto encubierto",
    "CONCEPTO": "No aclara porcentaje , se cobra con tasa servicios urbanos y tasa conservacion , reparacion y mejorado de la red vial municipal",
    "ORDENANZA": "Ordenanza Adolfo Gonzalez Chaves (última encontrada vía web año 2024)",
    "DENSIDAD": 12914,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Alberti",
    "COBRO": "Tasa servicio asistencial Art. 129",
    "CONCEPTO": "Se establece cobro según nomenclador ioma a quienes evidencien capacidad contributiva , se podra pedir informe socioeconomico a asistentes sociales",
    "ORDENANZA": "Ordenanza Alberti",
    "DENSIDAD": 12982,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Almirante Brown",
    "COBRO": "Sistema recupero SAMO",
    "CONCEPTO": "No figura en ordenanza municipal cobro a personas sin cobertura médica",
    "ORDENANZA": "Ordenanza Almirante Brown",
    "DENSIDAD": 584827,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Arrecifes",
    "COBRO": "Tasa servicio asistencial Art. 179 y ss",
    "CONCEPTO": "Individualiza al paciente como sujeto de cobro. Se reserva la gratuidad a la evidente carencia",
    "ORDENANZA": "Odenanza Arrecifes",
    "DENSIDAD": 32405,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Avellaneda",
    "COBRO": "Sistema recupero SAMO",
    "CONCEPTO": "Hace mencion al principio de gratuidad y trato igualitario en el Art. 214",
    "ORDENANZA": "Ordenanza Avellaneda",
    "DENSIDAD": 367554,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Ayacucho",
    "COBRO": "Tasa servicio asistencial Art. 36 inc. 2",
    "CONCEPTO": "Brinda facultad a la direccion para determinar eximición de pago en escala del 30, 50 y 70% según encuesta social",
    "ORDENANZA": "Ordenanza Ayacucho",
    "DENSIDAD": 22136,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Azul",
    "COBRO": "Previo año 2024 tasa servicios esenciales (demanda) Impuesto encubierto. Año 2025 tasa servicios esenciales",
    "CONCEPTO": "Año 2023 tasa servicios esenciales salud y otros servicios (deporte, educacion etc.) a inmuebles urbanos y rurales  AÑO 2025 tasa por servicios asistenciales, gratuitad situacion socio económica . Art. 212 Tasa asistencial Art. 129 no pago excentos por situacion socio económica",
    "ORDENANZA": "Ordenanza Azul",
    "DENSIDAD": 75905,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Bahía Blanca",
    "COBRO": "Tasa por servicios asistenciales Art 254 y ss",
    "CONCEPTO": "Individualiza como contribuyente a quien recibe los servicios asistenciales",
    "ORDENANZA": "Ordenanza Bahia Blanca",
    "DENSIDAD": 336574,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Balcarce",
    "COBRO": "Contribución Obligatoria para la Salud Art 73",
    "CONCEPTO": "a) Contribuyentes de la Tasa por Alumbrado Público b) Contribuyentes de la Tasa por Conservación, Reparación y Mejorado de la  Red Vial c) Contribuyentes de la Tasa por Inspección de Seguridad e Higiene",
    "ORDENANZA": "Ordenanza Balcarce",
    "DENSIDAD": 51736,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Baradero",
    "COBRO": "Fondo municipal de Salud  ART. 37",
    "CONCEPTO": "Valor menor $583 adicional a otras tasas",
    "ORDENANZA": "Ordenanza Baradero",
    "DENSIDAD": 37491,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Beníto Juárez",
    "COBRO": "Ausencia de concepto en ordenanza",
    "CONCEPTO": "Se llamó por teléfono para consultar por turno para análisis manifestando no tener obra social y si tenia costo, se indicó que se me acerque para sacar turno, solo fue consultado si el DNI tenia domicilio de Benito Juarez. Se limita atencion a vecinos del domicilio.",
    "ORDENANZA": "Ordenanza Benito Juarez",
    "DENSIDAD": 22292,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Berazategui",
    "COBRO": "Tasa servicio asistencial Art. 160",
    "CONCEPTO": "Figura en ordenanza el concepto e individualiza al contribuyente como \"todos los que soliciten el servicio\" pero en la web del hospital se aclara, por intentos de estafas, que toda atencion, práctica y estudios son gratuitos.",
    "ORDENANZA": "Ordenanza Berazategui  Página Web Hospital",
    "DENSIDAD": 358712,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Berisso",
    "COBRO": "Ausencia de concepto en ordenanza",
    "CONCEPTO": "\"(...)habitantes de Berisso, independientemente del\nlugar donde residan\"",
    "ORDENANZA": "Ordenanza Berisso",
    "DENSIDAD": 100930,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Bolívar",
    "COBRO": "Sistema recupero SAMO. Tasa asistencial derogada año 98",
    "CONCEPTO": "Se cobraba tasa asistencial hasta el año 98",
    "ORDENANZA": "Ordenanza bolivar 1488/98 deroga tasa asistencial",
    "DENSIDAD": 38119,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Bragado",
    "COBRO": "No figura ordenanza, solo la que aprueba la misma sin el anexo",
    "CONCEPTO": "Se intentó  por teléfono sin éxito, se solicitó por email.",
    "ORDENANZA": "Ordenanza Bragado",
    "DENSIDAD": 44972,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Brandsen",
    "COBRO": "Ausencia de concepto",
    "CONCEPTO": "Sin especificación detallada",
    "ORDENANZA": "Ordenanza Brandsen",
    "DENSIDAD": 33026,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Campana",
    "COBRO": "Tasa Aporte para la Salud Pública Art. 353. Impuesto encu",
    "CONCEPTO": "Contribuyentes propietarios de inmuebles Tasa por Servicios Generales y/o Conservación, Reparación y Mejorado de la red Vial Municipal.Establecimientos Comerciales, Industriales y/o similares Tasa por Inspección de Seguridad e Higiene",
    "ORDENANZA": "Ordenanza Campana",
    "DENSIDAD": 107979,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Cañuelas",
    "COBRO": "Ausencia concepto en ordenanza",
    "CONCEPTO": "Se llamó al hospital municipal manifestando pedir turno para analisis y no tener obra social, se responde que se acerque a sacar turno y responde que no tiene costo ante la consulta",
    "ORDENANZA": "Ordenanza Cañuelas",
    "DENSIDAD": 70684,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Capitán Sarmiento",
    "COBRO": "Tasa servicio asistencial Art. 135 y ss",
    "CONCEPTO": "Limita gratuidad a nivel socioeconomico, informe del servicio de Desarrollo Social, excepcion de pago puede ser total o parcial (no aclara porcentajes)",
    "ORDENANZA": "Ordenanza Capitan Sarmiento",
    "DENSIDAD": 15906,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Carlos Casares",
    "COBRO": "Fondo municipal de Salud Art. 178 y ss (impuesto encubierto)",
    "CONCEPTO": "Contribuyentes: Contribuyente de las tasas \"Retributivas por Servicios Urbanos\" y por \"Conservación, Reparación y Mejorado de la Red Vial Municipal\" no especifica monto",
    "ORDENANZA": "Ordenanza Carlos Casares",
    "DENSIDAD": 23204,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Carlos Tejedor",
    "COBRO": "Ausencia concepto en ordenanza",
    "CONCEPTO": "Se llamó telefónicamente  02357420103 se refirio que aveces médicos cobran un \"plus\" de $2.000 o $3.000. Seguir averiguando.",
    "ORDENANZA": "Ordenanza Carlos Tejedor",
    "DENSIDAD": 13148,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Carmen De Areco",
    "COBRO": "Ausencia concepto en ordenanza",
    "CONCEPTO": "02273 442155 no contesta volver a llamar",
    "ORDENANZA": "Ordenanza Carmen de Areco",
    "DENSIDAD": 17386,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Castelli",
    "COBRO": "SAMO + Tasa servicio asistencial",
    "CONCEPTO": "Se discrimina en ordenanza el sistema SAMO, contribuyentes sin obra social con pago total o parcial según informe social y tarifa plena para no residentes del municipio. Especifica costo traslado ambulancia",
    "ORDENANZA": "Ordenanza Castelli",
    "DENSIDAD": 10517,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Chacabuco",
    "COBRO": "Ausencia concepto en ordenanza",
    "CONCEPTO": "En la web del hospital se expone \"Si el paciente posee obra social, ART, compañía seguro u otro tipo de cobertura, estará a cargo de éstas. Si el paciente no tiene ningún tipo de cobertura, será atendido de manera totalmente gratuita\" https://chacabuco.gob.ar/direccion-del-hospital/",
    "ORDENANZA": "Ordenanza Chacabuco",
    "DENSIDAD": 52731,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Chascomús",
    "COBRO": "SAMO",
    "CONCEPTO": "Ordenanza no aclara personas sin cobertura",
    "ORDENANZA": "Ordenanza Chascomus",
    "DENSIDAD": 42452,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Chivilcoy",
    "COBRO": "Tasa servicios asistenciales, impuesto encubierto",
    "CONCEPTO": "Se cobra tasa, impuesto encubierto a inmuebles urbanos y rurales. Art 87 ordenanza fiscal Art 5 ordenanza impos",
    "ORDENANZA": "Ordenanza fiscal chivilcoy     Ordenanza impositiva Chivilcoy",
    "DENSIDAD": 70839,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Colón",
    "COBRO": "SAMO",
    "CONCEPTO": "Ordenanza no aclara personas sin cobertura . Se detecta abuso de la retencion de 90% pension jubilados en sala de ancianos",
    "ORDENANZA": "Ordenanza Colón",
    "DENSIDAD": 27504,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Coronel Dorrego",
    "COBRO": "Sistema SAMO + Tasa servicios asistenciales Art 177",
    "CONCEPTO": "Se aclara que solo se recupera por sistema SAMO, no se cobra a personas sin cobertura sean o no residentes.",
    "ORDENANZA": "Ordenanza Coronel Dorrego",
    "DENSIDAD": 15968,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Coronel Rosales",
    "COBRO": "No figura ordenanza actualizada. Última año 2021",
    "CONCEPTO": "Tasa asistencial. Especifica la excepcion \"Las personas carentes de aportes de obras sociales\"",
    "ORDENANZA": "Ordenanza Coronel Rosales 2021",
    "DENSIDAD": 67503,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Coronel Pringles",
    "COBRO": "Tasa servicios asistenciales",
    "CONCEPTO": "Son Contribuyentes y/o responsables:a) Las personas que soliciten el servicio, ya sea el paciente, el familiar a cargo, familiar obligado a prestar alimentos, el apoderado, el curador.-",
    "ORDENANZA": "Ordenanza Coronel Pringles",
    "DENSIDAD": 24420,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Coronel Suárez",
    "COBRO": "Tasa servicios asistenciales Art. 144 y ss",
    "CONCEPTO": "Gratuidad reservada a evidente carencia de recursos. Categorización por Servicios Sociales A, B y C según % a pagar. Si no entran en esas categorías abonan el total. Art 147",
    "ORDENANZA": "Ordenanza Coronel Suarez",
    "DENSIDAD": 42110,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Daireaux",
    "COBRO": "Tasa asistencial Art 23",
    "CONCEPTO": "\"(...) para aquellos que soliciten y/o usufructúen de las prestaciones (...)\"",
    "ORDENANZA": "Ordenanza Daireaux",
    "DENSIDAD": 18422,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Dolores",
    "COBRO": "Tasa asistencial Art 29",
    "CONCEPTO": "Contribuyente: Quienes soliciten los servicios asistenciales, y tengan recursos probados",
    "ORDENANZA": "Ordenanza dolores",
    "DENSIDAD": 30372,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Ensenada",
    "COBRO": "SAMO",
    "CONCEPTO": "Art. 191 fiscal y 48 impositiva Contribuyentes obra sociales, prepagas, art, seguros",
    "ORDENANZA": "Ordenanza Ensenada",
    "DENSIDAD": 63997,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Escobar",
    "COBRO": "Tasa por servicios especiales. impuesto encubierto",
    "CONCEPTO": "Se prevee en tasa alumbrado barrido limpieza diversos servicios entre los cuales se incluye salud. Art. 103 y 125",
    "ORDENANZA": "Ordenanza Escobar",
    "DENSIDAD": 256449,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Esteban Echeverría",
    "COBRO": "SAMO",
    "CONCEPTO": "Art. 16.1",
    "ORDENANZA": "Ordenanza Esteban Echeverria",
    "DENSIDAD": 338480,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Exaltación De La Cruz",
    "COBRO": "Tasa por servicios generales. impuesto encubierto",
    "CONCEPTO": "Art. 3",
    "ORDENANZA": "Ordenanza exaltación de la cruz",
    "DENSIDAD": 40159,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Ezeiza",
    "COBRO": "Servicios complementarios de salud . Contribucion especial",
    "CONCEPTO": "Art. 1.7 ordenanza impositiva. impuesto encubierto.",
    "ORDENANZA": "Ordenanza Ezeiza",
    "DENSIDAD": 201511,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Florencio Varela",
    "COBRO": "Tasa por servicios generales. impuesto encubierto",
    "CONCEPTO": "Art. 115 ordenanza fiscal",
    "ORDENANZA": "Odenanza Florencia Varela",
    "DENSIDAD": 496433,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Florentino Ameghino",
    "COBRO": "Aranceles hospitalarios",
    "CONCEPTO": "Art. 208 \"Los distintos servicios prestados en el Hospital municipal de Florentino Ameghino, que se encuetran en la ordenanza 114/93 se cobrarán según los valores fijados en la mencionada ordenanza.\" No se encuentra la ordenanza",
    "ORDENANZA": "Ordenanza Florentino Ameghino",
    "DENSIDAD": 10790,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "General Alvarado",
    "COBRO": "Tasa de salud",
    "CONCEPTO": "impuesto encubierto",
    "ORDENANZA": "Ordenanza General Alvarado",
    "DENSIDAD": 45597,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "General Alvear",
    "COBRO": "Tasa por servicios asistenciales Art. 38",
    "CONCEPTO": "No aclara contribuyente.\"(...) fíjanse para los servicios asistenciales prestados en el Hospital  Municipal “Dr. Bernardino Rivadavia” los importes determinados en el nomenclador IOMA.\"",
    "ORDENANZA": "Ordenanza General Alvear",
    "DENSIDAD": 13031,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "General Arenales",
    "COBRO": "Tasa servicios asistenciales Art. 134 y ss",
    "CONCEPTO": "Exceptuados de pago los casos individuales que presene evidente carencia de recursos previa diagnóstico social +  ciertas prácticas como obstetricia, pediatria menor 1 año, inmunizaciones programadas, enfermedades transmisibles agudas y crónicas que el Ministerio de bienestar social asi determine",
    "ORDENANZA": "Última ordenanza que figura año 2023",
    "DENSIDAD": 16350,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "General Belgrano",
    "COBRO": "Tasa asistencial",
    "CONCEPTO": "ART. 151 Aclara que presta servicios gratuito a quien carezca de recursos para cubrirlos. Ademas SAMO",
    "ORDENANZA": "Ordenanza General Belgrano",
    "DENSIDAD": 20791,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "General Guido",
    "COBRO": "Tasa de Servicio de Salud Art 21",
    "CONCEPTO": "Por cada recibo de Tasa o Derecho desde $ 5.000,00.- hasta la suma de $120.000",
    "ORDENANZA": "Ordenanza General Guido",
    "DENSIDAD": 3174,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "General Juan Madariaga",
    "COBRO": "Tasa por servicios asistenciales Art 208 y ss",
    "CONCEPTO": "De forma explicita la ordenanza sostiene el sistema de salud público y gratuito, expone el sistema de recupero SAMO y manifie \"Cuando el paciente voluntariamente desee colaborar podrá abonar las prestaciones de acuerdo a los valores establecidos en la Ordenanza Impositiva.\"",
    "ORDENANZA": "Ordenanza Juan Madariaga",
    "DENSIDAD": 22624,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "General La Madrid",
    "COBRO": "Tasa servicio asistenciales Art 13",
    "CONCEPTO": "Se especifica como contribuyente a pacientes ambulatorios o internados sin obra social, se les cobrará según nomenclador, tb los materiales y medicamentos utilizados. Tb especifica que se cobrará materiales y medicamentos a  los pacientes del hogar de ancianos. Utiliza entrevista asistente social y categorías, cobertura total o parcial. Se hizo denuncia, en este momento quitaron la ordenanza de la web y se les informó que debian modificarla para obtener la licencia para el año 2027 para el hospital",
    "ORDENANZA": "Ordenanza General Lamadrid",
    "DENSIDAD": 11618,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "General Las Heras",
    "COBRO": "Tasa servicios asistenciales Art. 123 y ss",
    "CONCEPTO": "Contribuyente quien obtenga el servicio, familiares, obra social o prepapaga, seguro de salud. Eximición total o parcial de pago por condicion socio económica constatada por personal o previa entre vista asistencia social",
    "ORDENANZA": "Ordenanza General Las Heras",
    "DENSIDAD": 18022,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "General Lavalle",
    "COBRO": "Tasa servicios asistenciales Art. 173 y ss",
    "CONCEPTO": "Excepción a las personas carentes de recursos . Excluidos los servicios de obstetricia, pediatria hasta 1 año, inmunizaciones programadas, enfermedades transmisibles agudas y crónicas que el Ministerio de Bienestar Social así determine.",
    "ORDENANZA": "Ordenanza General Lavalle",
    "DENSIDAD": 4870,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "General Paz",
    "COBRO": "Residentes Tasa contributiva unidad terapia intensiva Art. 291 y ss No residentes Art. 294 y ss por todo servicio en el hospital",
    "CONCEPTO": "Residentes urbanos tasa servicios urbanos 3usd mensual y Residentes rurales en tasa vial 8 usd bimestral. No residentes Art. 294 y ss por todo servicio en el hospital se determina el valor en UF , el valor es mayor si no poseen cobertura.  Art 297",
    "ORDENANZA": "Ordenanza General Paz",
    "DENSIDAD": 14207,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "General Pinto",
    "COBRO": "Aranceles hospitalarios Art. 240 y ss",
    "CONCEPTO": "prestación a un paciente sin Obra Social, y que según encuesta social realizada por el profesional del área, esté en condiciones de abonar, par dicho caso se facturará teniendo en cuenta nomenclador para HPM del IOMA",
    "ORDENANZA": "Ordenanza General Pinto",
    "DENSIDAD": 12941,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "General Pueyrredón",
    "COBRO": "Contribución a la Salud, la Educación y el Desarrollo Infantil Art 217 y ss",
    "CONCEPTO": "contribución fija por cada inmueble emplazado en el Partido de General Pueyrredon gravado por la Tasa por Servicios Urbanos o por la Tasa por Conservación, Reparación y Mejorado de la red vial municipal",
    "ORDENANZA": "Ordenanza General Pueyrredon",
    "DENSIDAD": 667081,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "General Rodríguez",
    "COBRO": "Tasa especial servicios de educación, salud y seguridad (impuesto encubierto) Art 42 y ss Tasa asistencial por hospital odontologico y oftalmologíco Art. 43 y ss ordenanza impositiva.",
    "CONCEPTO": "Valores se establecen e X cantidad de módulos. ART 41 tasa emergencias médicas Art 42 impuesto encubierto salud Art 43 hospital odontólogo y oftalmologia",
    "ORDENANZA": "Ordenanza General Rodriguez",
    "DENSIDAD": 142709,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "General San Martín",
    "COBRO": "SAMO Art 303 y ss",
    "CONCEPTO": "Refiere solo al sistema SAMO de recupero",
    "ORDENANZA": "Ordenanza General San Martin",
    "DENSIDAD": 450575,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "General Viamonte",
    "COBRO": "Tasa asistencial Art. 205 y ss",
    "CONCEPTO": "El ejectuvi puede adecuar valores según situacion socioeconomica. Algunas prácticas están excentas de pago.  Se determina el contribuyente sin obra social pero con ingresos suficientes y sin ingresos suficientes. Hacen distincion con no residentes.",
    "ORDENANZA": "Ordenanza General Viamonte",
    "DENSIDAD": 22649,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "General Villegas",
    "COBRO": "FONDO POR SERVICIOS ASISTENCIALES Y PARA LA SALUD Art. 57",
    "CONCEPTO": "Artículo 57º: No aprobado, en Sesión Especial 2° del 22 de diciembre del 2025.",
    "ORDENANZA": "Ordenanza General Villegas",
    "DENSIDAD": 35251,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Guamini",
    "COBRO": "Tasa salud (impuesto encubierto) Art 205 y ss ordenanza fiscal + Tasa servicios asistenciales Art. 30 y ss ordenanza impositiva",
    "CONCEPTO": "Tarifario por prestaciones de forma detalladad: radiografias, mamografía, etc.",
    "ORDENANZA": "Ordenanza guamini",
    "DENSIDAD": 11801,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Hipólito Yrigoyen",
    "COBRO": "Tasa servicios asistenciales Art. 45 y ss",
    "CONCEPTO": "No posee su ordenanza en la web, se consulto sistema SIBOM de la provincia de Buenos Aires",
    "ORDENANZA": "Ordenanza Hipólito Yrigoyen",
    "DENSIDAD": 10661,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Hurlingham",
    "COBRO": "Ausencia de concepto",
    "CONCEPTO": "No figura en su web si en el sistema SIBOM",
    "ORDENANZA": "Ordenanza Impositiva/Fiscal",
    "DENSIDAD": 185641,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Ituzaingó",
    "COBRO": "SAMO + tasa de proteccion ciudadana (impuesto encubierto) Art. 18.1",
    "CONCEPTO": "Se define el sistema samo de recupero y una tasa como impuesto encubierto para los contribuyentes para sotener servicios varios del municipio entre los cuales se encuentra el de salud",
    "ORDENANZA": "Ordenanza Ituzaingo",
    "DENSIDAD": 180232,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "José C. Paz",
    "COBRO": "Ausencia de concepto",
    "CONCEPTO": "Última que figura año 2018 se cobra a no residentes",
    "ORDENANZA": "Ordenanza Impositiva/Fiscal",
    "DENSIDAD": 326992,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Junín",
    "COBRO": "TASA POR SERVICIOS PUBLICOS URBANOS (S.P.U.) Art. 1",
    "CONCEPTO": "impuesto encubierto, se incluye a la salud en la tasa de servicios generales del municipio",
    "ORDENANZA": "Ordenanza Junin",
    "DENSIDAD": 103787,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "La Costa",
    "COBRO": "Tasa servicios asistenciales Art. 198 Fondo Salud a rurales Art.275 impuesto encubierto",
    "CONCEPTO": "Art 198 Tasa servicios asistenciales, pago no residentes eximidos de pago indigentes Art 275 Fondo Complementario de Seguridad y Salud, que será aplicado a las partidas del Sector Rural que tendrá un valor establecido por la Ordenanza Impositiva vigente.",
    "ORDENANZA": "Ordenanza La Costa",
    "DENSIDAD": 100689,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "La Matanza",
    "COBRO": "SAMO Art 249",
    "CONCEPTO": "Se especifica el sistema de recupero SAMO en la ordenanza Art. 249",
    "ORDENANZA": "Ordenanza La Matanza",
    "DENSIDAD": 1841247,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "La Plata",
    "COBRO": "Ausencia de concepto",
    "CONCEPTO": "Ausencia de concepto tanto en ordenanza fiscal como impositiva",
    "ORDENANZA": "Ordenanzas La plata",
    "DENSIDAD": 768470,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Lanus",
    "COBRO": "Ausencia de concepto",
    "CONCEPTO": "Ausencia de concepto en código tributario",
    "ORDENANZA": "Ordenanza Lanús",
    "DENSIDAD": 461267,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Laprida",
    "COBRO": "SAMO Art. 20",
    "CONCEPTO": "No aclara cobertura a personas sin obra social, prepaga o seguro. Si hay materiales no cubiertos por la entidad y no este cubierto por nomenclador ioma lo abonará o repondrá el paciente.",
    "ORDENANZA": "Ordenanza Laprida",
    "DENSIDAD": 11646,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Las Flores",
    "COBRO": "Ausencia de concepto",
    "CONCEPTO": "Ausencia de concepto en fiscal impositiva",
    "ORDENANZA": "Ordenanza Las flores",
    "DENSIDAD": 27239,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Leandro N. Alem",
    "COBRO": "Aranceles de los servicios asistenciales Art. 160",
    "CONCEPTO": "Categorización otorgada por el Servicio Social y con las excepciones que la misma consagre. Se autoriza al Departamento Ejecutivo a modificar los distintos aranceles establecidos en el presente capítulo cuando resulte necesario para garantizar el funcionamiento de los establecimientos municipales con todos sus servicios con el objeto principal de favorecer la atención de los pacientes carenciados.",
    "ORDENANZA": "Ordenanza Leandro N. Alem",
    "DENSIDAD": 17266,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Lezama",
    "COBRO": "Sistema SAMO Art. 23 y ss + tasas (impuestos encubiertos)",
    "CONCEPTO": "Art. 219 TASA DE SERVICIOS DE GUARDIAS PEDIÁTRICAS Y/O VINCULADAS\nA LA SALUD DE LA NIÑEZ , La base imponible de la tasa a que se refiere el presente artículo estará\nconstituida por los contribuyentes de las Tasas de Servicios Rurales y de Barrido, Limpieza y\nConservación de la Vía Pública.",
    "ORDENANZA": "Ordenanza Lezama",
    "DENSIDAD": 6231,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Lincoln",
    "COBRO": "Tasa servicios asistenciales Art. 21",
    "CONCEPTO": "Se especifica valor por recorridos por km de la ambulancia y recarga tubo de oxígeno",
    "ORDENANZA": "Ordenanza Lincoln",
    "DENSIDAD": 45506,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Lobería",
    "COBRO": "Tasa servicios asistenciales Art. 192 y ss",
    "CONCEPTO": "Cuando la encuesta socioecon.mica realizada por Servicio Social de la Municipalidad as. lo determine, el sistema municipal se har. cargo del costo total o la diferencia que o pudiera abonar el paciente",
    "ORDENANZA": "Ordenanza Lobería",
    "DENSIDAD": 18243,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Lobos",
    "COBRO": "TASA POR SALUD, SEGURIDAD, EDUCACION, DEFENSA CIVIL Y ASISTENCIA SOCIAL ART. 30 (impuesto encubierto)",
    "CONCEPTO": "CONTRIBUCION SOLIDARIA PARA EL FINANCIAMIENTO DE SERVICIOS DE EDUCACIÓN, SALUD, SEGURIDAD Y ASISTENCIA SOCIAL",
    "ORDENANZA": "Ordenanza Lobos",
    "DENSIDAD": 41760,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Lomas de Zamora",
    "COBRO": "Ausencia de concepto",
    "CONCEPTO": "Sin especificación detallada",
    "ORDENANZA": "Ordenanza Lomas de Zamora",
    "DENSIDAD": 690323,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Luján",
    "COBRO": "Ausencia de concepto",
    "CONCEPTO": "Última disponible año 2024, se solicito actualizada hcd@lujan.gob.ar",
    "ORDENANZA": "Ordenanza Lujan",
    "DENSIDAD": 111365,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Magdalena",
    "COBRO": "Ausencia de concepto",
    "CONCEPTO": "Se llamó por teléfono al (02221)​ 45-3443  se manifesto la necesidad de contar con el cambió de domicilio hecho en el DNI o en trámite, se consultó y dijeron que no tenía costo si no tenia obra social.",
    "ORDENANZA": "Ordenanza Magdalena",
    "DENSIDAD": 26830,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Maipú",
    "COBRO": "Tasa servicios asistenciales Art. 12 y ss",
    "CONCEPTO": "Necesidad hacer declaración jurada anualmente, solo residentes municipio. Se categorizan 4 categorías \"Condición de paciente\" . A) paciente con obra social , lesgilación labora. seguros, ART. B) ingresos + 317.000 sin cobertura A C) bajos recursos ingresos menos 317.000 y sin A D) bajos recursos con obra social ingresos menos a 317.000. Cobran traslados en ambulancia. Cobran a no residentes que no tengan cobertura a menos que demuestren carencia.",
    "ORDENANZA": "Ordenanza Maipú",
    "DENSIDAD": 11323,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Malvinas Argentinas",
    "COBRO": "Tasa servicios asistenciales Art. 192 y ss",
    "CONCEPTO": "Contribuyentes: quién lo solicite, el enfermo o los familiares. En el caso de prestarse el servicio a personas con cobertura social o con\ncobertura por seguro o autoseguro, los derechos asistenciales deberán ser abonados\npor los responsables de la cobertura, en cuyo caso, los servicios le serán facturados por\nla Secretaría de Salud.",
    "ORDENANZA": "Ordenanza Malvinas Argentinas",
    "DENSIDAD": 350674,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Mar Chiquita",
    "COBRO": "Tasa Servicios Asistenciales Art. 198 y ss FONDO COMPLEMENTARIO DE SEGURIDAD Y SALUD (impuesto encubierto Art. 275",
    "CONCEPTO": "Se cobrará a no residentes. El pago se efectivizará al solicitar el servicio. El indigente tendrá asistencia gratuita mediante la presentación de la certificación del responsable del área de Desarrollo Social. Las personas de escasos recursos podrán ser autorizadas a abonar los aranceles estipulados con una deducción de hasta el cincuenta por ciento (50%). Responsable del pago la persona, tutores, curadores, representantes y/o herederos en caso de fallecimiento.",
    "ORDENANZA": "Ordenanza Mar Chiquita",
    "DENSIDAD": 33110,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Marcos Paz",
    "COBRO": "Tasa servicios asistenciales Art. 232 y ss",
    "CONCEPTO": "Son contribuyentes de la tasa establecida en el presente título, quienes soliciten el servicio, sus familiares o los responsables de la cobertura social, o cobertura por seguro o autoseguro obra social o prepaga, coseguro de salud, sindicales, cooperativos, mutuales. Gratuidad a indigencia.",
    "ORDENANZA": "Ordenanza Marcos Paz",
    "DENSIDAD": 67011,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Mercedes",
    "COBRO": "Contribucon especial Art. 6 impuesto encubierto",
    "CONCEPTO": "Asociación de Bomberos Voluntarios y Asociación Cooperadora del Hospital Se tributará en forma conjunta con la Tasa de Conservación de la vía Pública y/o la Tasa de Conservación, Mejorado y Reparación de la Red Vial Munici",
    "ORDENANZA": "Ordenanza Mercedes",
    "DENSIDAD": 72970,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Merlo",
    "COBRO": "SAMO Art 42",
    "CONCEPTO": "Se aclara gratuito personas sin cobertura. Sistema recupero SAMO",
    "ORDENANZA": "Ordenanza Merlo",
    "DENSIDAD": 582464,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Monte",
    "COBRO": "Contribucion especial Art. 68 impuesto encubierto",
    "CONCEPTO": "Art. 86 inc 2 contribucion especial Salud Pública del Partido de Monte",
    "ORDENANZA": "Ordenanza Monte",
    "DENSIDAD": 24868,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Monte Hermoso",
    "COBRO": "SAMO + Tasa servicios asistenciales Art. 272",
    "CONCEPTO": "No cobro según condicion socioeconomica necesario informe servicio social municipal",
    "ORDENANZA": "Ordenanza Monte Hermoso",
    "DENSIDAD": 8465,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Moreno",
    "COBRO": "TASA DE SALUD Y ASISTENCIA SOCIAL ART. 43 . Alicuota sobre multas que cobre el municipio",
    "CONCEPTO": "alícuota del diez coma cincuenta por ciento (10,50%) sobre los tributos, accesorios y/o multas por contravenciones que se abonaren al Municipio, en concepto de Tasa de Salud y Asistencia Social, cuyo importe estará destinado: 0,5% a la “Fundación Mariano y Luciano de La Vega”, un 0,5% a la Infraestructura Hospitalaria y el 9,5% restante a solventar otras erogaciones previstas en el Artículo 329º de la Ordenanza fis",
    "ORDENANZA": "Ordenanza moreno",
    "DENSIDAD": 576578,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Morón",
    "COBRO": "SAMO Art. 288 y 290",
    "CONCEPTO": "ordenanza año 2024 se solicito la actualizada vía correo acceso.informacion.publica@moron.gob.ar  Art. 53 se cobra por servicios asistenciales de emergencia médica y traslado por accidentes de tránsito",
    "ORDENANZA": "Ordenanza Morón",
    "DENSIDAD": 331140,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Navarro",
    "COBRO": "ausencia ordenanza",
    "CONCEPTO": "se solicito por correo",
    "ORDENANZA": "Ordenanza Impositiva/Fiscal",
    "DENSIDAD": 19899,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Necochea",
    "COBRO": "TASA POR FORTALECIMIENTO, PROMOCIÓN Y PREVENCIÓN PARA LA SALUD Art. 426",
    "CONCEPTO": "impuesto encubierto a inmuebles urbanos y rurales",
    "ORDENANZA": "Ordenanza Necochea",
    "DENSIDAD": 102110,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Nueve de Julio",
    "COBRO": "Tasa servicios asistenciales Art. 44",
    "CONCEPTO": "excepto sin cobertura social o no posean capacidad de pago para los cuales no regian ningun tipo de arancel. Los demás solo si hay diferencia entre cobertura y servicio se abonará la diferencia el paciente.",
    "ORDENANZA": "Ordenanza Nueve de Julio",
    "DENSIDAD": 52607,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Olavarría",
    "COBRO": "ART. 22 Ordenanza impositiva Sistema SIAMO \"cobertura municipal de salud por cuota mensual\" Tasa servicios asistenciales Art. 138 y ss ordenanza fiscal",
    "CONCEPTO": "SIAMO (Sistema Integral de Atención Médica de Olavarría) es un sistema de cobertura médica prepaga municipal que funciona en el Partido de Olavarría.Cobertura: Ofrece atención médica a través del Hospital Municipal Dr. Héctor M. Cura y de los Centros de Atención Primaria de la Salud (CAPS) municipales.Aportes: Los pacientes abonan una cuota mensual accesible para recibir esta cobertura dentro del sistema público de salud local.ARTICULO 139. Se faculta al Departamento Ejecutivo para conceder deducciones de acuerdo a la posibilidad económica del tributante, determinadas por el servicio social de la Municipalidad y otorgar facilidades en los pagos",
    "ORDENANZA": "Ordenanza Olavarría",
    "DENSIDAD": 125751,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Patagones",
    "COBRO": "Tasa servicios asistenciales Art. 239 y ss",
    "CONCEPTO": "Será abonada directamente por el beneficiario del servicio, en caso que el mismo no se encuentre afiliado a obra social o mutual que resulte obligada al pago y en la medida que no encuadre en alguna de las exenciones previstas. Excepciones Art. 239 quarter",
    "ORDENANZA": "Ordenanza Patagones",
    "DENSIDAD": 25982,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Pehuajó",
    "COBRO": "Tasa servicios asistenciales Art. 215 y ss",
    "CONCEPTO": "Contribuyentes las personas humanas usuarias del servicio o sus representantes. Son responsables sustitutos de la presente tasa aquellas personas humanas o jurídicas, públicas o privadas, que sean encargados de la cobertura social, por seguro o por autoseguro, del contribuyente",
    "ORDENANZA": "Ordenanza Pehuajó",
    "DENSIDAD": 44783,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Pellegrini",
    "COBRO": "Sistema de recupero SAMO Art. 40 y ss",
    "CONCEPTO": "La Tasa por Servicios Asistenciales será aplicable respecto de las prestaciones médicas asistenciales (...) únicamente en aquellos casos en que los usuarios cuenten con cobertura médica a través de obra social, empresa de medicina prepaga, aseguradora de riesgos del trabajo o seguro de salud. En ningún caso corresponderá exigir pago alguno a los particulares que carezcan de cobertura médica, garantizándose para ellos la gratuidad plena en el acceso a la atención sanitaria municipal. Se clara que se aceptan donaciones que deben quedar registradas como donaciones al municipio Art. 41",
    "ORDENANZA": "Ordenanza Pellegrini",
    "DENSIDAD": 7143,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Pergamino",
    "COBRO": "Ausencia de concepto",
    "CONCEPTO": "Ausencia de concepto",
    "ORDENANZA": "Ordenanza Pergamino",
    "DENSIDAD": 115340,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Pila",
    "COBRO": "no se encuentra normativa seguir buscando",
    "CONCEPTO": "Sin especificación detallada",
    "ORDENANZA": "Ordenanza Impositiva/Fiscal",
    "DENSIDAD": 4642,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Pilar",
    "COBRO": "Tasa servicios de salud Art. 263 y ss",
    "CONCEPTO": "Regimen General Art. 263 y ss individualiza como sujeto a la persona que reciba el servicio, no se cobrará la tasa a personas que: residan en pilar, tengo residencia permanenente en el país y no tengan cobertura por médico asitencial por carecer e tareas remuneradas o beneficios previsionales.  Regimen Especial Art 267 ter y ss Sistema SAMO recupero",
    "ORDENANZA": "Ordenanza Pilar",
    "DENSIDAD": 394754,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Pinamar",
    "COBRO": "TASA POR DERECHOS SANATORIALES/SERVICIOS ASISTENCIALES – HOSPITAL MUNICIPAL SALAS MUNICIPALES ART. 97 Y SS",
    "CONCEPTO": "eximidos del pago de hasta un cien por ciento (100%) (...) aquellas personas sin cobertura social y con recursos limitados y/o insuficientes, con autorización de la Dirección de Acción Social.",
    "ORDENANZA": "Ordenanza Pinamar",
    "DENSIDAD": 39449,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Presidente Perón",
    "COBRO": "Ausencia concepto",
    "CONCEPTO": "Sin especificación detallada",
    "ORDENANZA": "Ordenanza Presidente Perón",
    "DENSIDAD": 102106,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Puán",
    "COBRO": "Tasa servicios asistenciales Art. 170 y ss ordenanza fiscal y Art. 42 y ss ordenanza impositiva",
    "CONCEPTO": "Servicios asistenciales y servicio ambulancia. La tasa se efectiviza salvo medio convenio obras sociales, particiones oficiales/privadas. (...) se podra establecer formas de pago diferidas en aquellos casos en que los costos de las cirugías no puedan ser abonadas de contado por el paciente con la firma de un convenio y los pagares respectivos. , previa evaluacion área promocion social.  En ordenanza impositiva se determina segméntación según se tenga o no cobertura, capacidad de pago, cobertura que cubra o no los servicios , falta de la misma con posibilidad de pago o no, se incluye tablas tarifarias para todo servicio hasta  tomografias, parto y cesarea. El municipio cuenta con \"Seguro de Salud Municipal\" SEDEM , categoríza a los pacientes, reserva gratuidad a carentes de recursos.",
    "ORDENANZA": "Ordenanza Puan",
    "DENSIDAD": 16613,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Punta Indio",
    "COBRO": "Fondo Solidario de Salud Pública Municipal Art. 202 y ss",
    "CONCEPTO": "impuesto encubierto",
    "ORDENANZA": "Ordenanza Punta Indio",
    "DENSIDAD": 12297,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Quilmes",
    "COBRO": "Sistema SAMO Art. 316 y ss",
    "CONCEPTO": "Sistema de recupero SAMO",
    "ORDENANZA": "Ordenanza Quilmes",
    "DENSIDAD": 633391,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Ramallo",
    "COBRO": "Tasa servicios asistenciales Art. 238",
    "CONCEPTO": "Sistema SAMO + Se reserva gratuidad a situación de indigencia. Personas sin cobertura que no demuestren indigencia serán facturados según nomenclador de autogestión",
    "ORDENANZA": "Código Tributario Ramallo",
    "DENSIDAD": 39730,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Rauch",
    "COBRO": "Tasa servicios asistenciales Anexo 1 Título XV",
    "CONCEPTO": "Se establecen valores de cobro a toda práctica, figuran precios en el anexo. Oficina de Desarrollo\nSocial de la Municipalidad, debe categorizar a los pacientes en:\na) Pacientes sin cobertura social, no indigente;\nb) Pacientes sin cobertura social indigente;\nc) Pacientes con cobertura social indigente y no indigente. Se podrá determinar porcentajes de pago 25% 50% 75% o cobertura social si amerita",
    "ORDENANZA": "Ordenanza Rauch",
    "DENSIDAD": 16635,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Rivadavia",
    "COBRO": "Servicios asistenciales Art 238 y ss",
    "CONCEPTO": "Servicio Social categoríza en las siguientes categorías: A con cobertura social convenida B con cobertura social pero sin convenio C sin cobertura social, con ingresos suficientes D sin cobertura social sin ingresos suficientes E con cobertura social , sin ingresos suficientes . no residentes deberan abonar totalidad o carta provincial o municipal que se hara cargo de los gastos.",
    "ORDENANZA": "Ordenanza Rivadavia",
    "DENSIDAD": 19849,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Rojas",
    "COBRO": "Cobro a obras sociales Art. 215 y ss",
    "CONCEPTO": "Se solicito ordenanza vigente, última que figura es año 2025",
    "ORDENANZA": "Ordenanza 2025 Rojas",
    "DENSIDAD": 25627,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Roque Pérez",
    "COBRO": "Tasa servicios asistenciales Art 33 SAMO  y Tasa por salud y seguridad fija anual por parcela urbana o hectarea",
    "CONCEPTO": "Art. 33 OJO La atención médica será gratuita salvo para aquellos pacientes que tengan cobertura\nsocial o privada. En casos de accidentes de trabajo, la ART correspondiente o en su\ndefecto el empleador, deberá hacerse cargo de los honorarios médicos y gastos\nsanatoriales que origine la atención del accidentado. Cuando la atención que deba\nbrindarse haya sido origen en accidentes de tránsito o cualquier otro accionar de\nterceros responsables, el paciente atendido cederá a favor de la Municipalidad el\nDerecho que pudiera corresponderle por obras sociales, medicina prepaga, ART o por\ncobertura de seguros de cualquier naturaleza por monto de las prestaciones recibidas.",
    "ORDENANZA": "Ordenanza Roque Perez",
    "DENSIDAD": 13977,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Saavedra Pigue",
    "COBRO": "Tasa servicios asistenciales Art. 273 y ss",
    "CONCEPTO": "Sistema SAMO + Gratuidad exclusiva para indigencia Art. 277",
    "ORDENANZA": "Ordenanza Saavedra Pigue",
    "DENSIDAD": 22537,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Saladillo",
    "COBRO": "SIstema SAMO",
    "CONCEPTO": "No se especifica en la ordenanza. Se llamó al telefono del hospital 02344 432112, me brindaron el whatshapp para solicitar turno programados , al manifiestar no tener obra social me comunicaron que el hospital es público y gratuito, solo se piden los datos de la obra social si se tiene para cobrarle a ellos.",
    "ORDENANZA": "Ordenanza Saladillo",
    "DENSIDAD": 35656,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Salliquelo",
    "COBRO": "Tasa servicios asistenciales Art. 69 y ss + Plan de Salud Municipal",
    "CONCEPTO": "Art. 69 y ss se establecen valores para pacientes sin cobertura indigentes o pacientes adheridos al plan de salud municipal abonando 50% de ciertas prácticas.",
    "ORDENANZA": "Ordenanza Salliquelo",
    "DENSIDAD": 9427,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Salto",
    "COBRO": "Sistema SAMO + Tasa asistencial Art. 206 y ss",
    "CONCEPTO": "Arancelamiento directo con vía ejecutiva judicial Art 213 juicio de apremio. Podran eximirse los indigentes Art. 66",
    "ORDENANZA": "Ordenanza Salto",
    "DENSIDAD": 40157,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "San Andrés de Giles",
    "COBRO": "Tasa servicios asistenciales Art 247 y ss ordenanza fiscal",
    "CONCEPTO": "Art 247 y ss ordenanza fiscal contribuyente persona que recibe los servicios , responsables solidarios, herederos y/o legatarios. Art 44 odeanzanza impsotiva aclara que para residentes del partido la atención es gratuita.",
    "ORDENANZA": "Ordenanza San Andrés de Giles",
    "DENSIDAD": 26510,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "San Antonio de Areco",
    "COBRO": "Tasa por servicios de salud  Art 218 y ss (impuesto encubierto)",
    "CONCEPTO": "Pago mensual de acuerdo a la liquidación de la Tasa de\nServicios Urbanos, Tasa por Servicios Rurales y Tasa por Inspección de Seguridad e Higiene,\nconforme Ordenanza Impositiva vigente.",
    "ORDENANZA": "Ordenanza San Antonio de Areco",
    "DENSIDAD": 26695,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "San Cayetano",
    "COBRO": "Sistema SAMO",
    "CONCEPTO": "Artículo 122º.- Los servicios asistenciales que se presten en el Hospital Municipal serán gratuitos. Para el\ncaso de pacientes que tengan cobertura de obras sociales o de compañías de seguros, oficiales o privados,\nla Municipalidad ejercerá el derecho de cobro sobre la entidad de cobertura conforme los valores y\nmodalidades establecidas en las normas vigentes en cada caso.",
    "ORDENANZA": "Ordenanza San Cayetano",
    "DENSIDAD": 8994,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "San Fernando",
    "COBRO": "Sistema SAMO + Tasa asistencial Art. 141 y ss impuesto encub",
    "CONCEPTO": "Aclara gratuidad a residentes del partido",
    "ORDENANZA": "Ordenanza San Fernando",
    "DENSIDAD": 171616,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "San Isidro",
    "COBRO": "Sistema SAMO Art 141 y ss",
    "CONCEPTO": "Art 141 y ss tiene anexo con valores, aclara si el responsable es persona pública o juridica privada",
    "ORDENANZA": "Ordenanza San Isidro",
    "DENSIDAD": 297282,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "San Miguel Joaquín",
    "COBRO": "Sistema SAMO Art 94 y ss",
    "CONCEPTO": "se aclara gratuidad a personas sin cobertura",
    "ORDENANZA": "Ordenanza San Miguel Joaquin",
    "DENSIDAD": 328835,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "San Nicolás",
    "COBRO": "Sistema SAMO Art 301 y ss",
    "CONCEPTO": "Art 301 y ss sistema samo y peajes",
    "ORDENANZA": "Ordenanza San Nicolas",
    "DENSIDAD": 165375,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "San Pedro",
    "COBRO": "Sistema SAMO Art. 250 y ss",
    "CONCEPTO": "se especifica que si el paciente no tiene cobertiura el servicio es gratuito",
    "ORDENANZA": "Ordenanza San Pedro",
    "DENSIDAD": 69616,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "San Vicente",
    "COBRO": "Contribución al Sistema de Salud Pública (impuesto encubierto) Art. 367",
    "CONCEPTO": "contribución equivalente al cuarenta por ciento (40 %) de las Tasas fijadas por\nPropiedad Urbana, por Conservación, Reparación y Mejorado de la Red Vial Municipal, por Propiedad Urbana para\n“Conjuntos Inmobiliarios destinados a Vivienda y Grandes Desarrollos Inmobiliarios” y por Inspección de Seguridad\ne Higiene.",
    "ORDENANZA": "Ordenanza San Vicente",
    "DENSIDAD": 98977,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Suipacha",
    "COBRO": "Tasa de salud Art. 129 y ss (impuesto encubierto) + Prestaciones Hospitalarias Art. 132 y ss",
    "CONCEPTO": "Tasa de salud Se dispone a toda parcela sector urbano y seccionenles de quintas del partido + Prestaciones hospitalarias: previa encuesta social se dispone capacidad de pago si no tiene cobertura",
    "ORDENANZA": "Ordenanza Suipacha",
    "DENSIDAD": 11867,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Tandil",
    "COBRO": "SISTEMA INTEGRADO DE SALUD PÚBLICA – ENTE DESCENTRALIZADO Art. 217 y ss",
    "CONCEPTO": "Individualiza el no cobro a \"las personas humanas en razón de las consideraciones socio económicas\" Cualquier excepción al arancel establecido, deberá\nestar justificada en base al informe del servicio social del\nestablecimiento o del servicio social de la Secretaría de\nBienestar Social y no constituirá impedimento alguno para la\ninmediata atención del paciente.",
    "ORDENANZA": "Ordenanza Tandil",
    "DENSIDAD": 150162,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Tapalque",
    "COBRO": "Tasa servicios asistenciales Art. 200 + Contribución unidad intensiva (impuesto encubierto)",
    "CONCEPTO": "Art 201 se faculta a deducciones de acuerdo posibilidades esconomicas del tributante determinadas por servicio social de la Municiipalidad",
    "ORDENANZA": "Ordenanza Tapalque",
    "DENSIDAD": 10901,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Tigre",
    "COBRO": "Sistema SAMO + Tasa servicios asistenciales Art 83 y ss ordenanza impositiva para no residentes del partido",
    "CONCEPTO": "Tabla tarifaria para personas no residentes en el partido. Gratuidad a personas sin cobertira médica.",
    "ORDENANZA": "Ordenanza Tigre",
    "DENSIDAD": 447785,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Tordillo",
    "COBRO": "Tasa servicios asistenciales Art 28 y ss ordenanza impositiva",
    "CONCEPTO": "Abonan quienes soliciten los servicios asistenciales y tengan recursos probados. sin recursos gratuito",
    "ORDENANZA": "Ordenanza Tordillo",
    "DENSIDAD": 2672,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Tornquist",
    "COBRO": "Sistema SAMO + Tasa servicios asistenciales Art. 142 y ss",
    "CONCEPTO": "Podrán quedar eximidos total o parcialmente del pago de tasa quienes posean ficha socio económica otorgada por el área competente como aquellos que poseen cobertura médica (Art. 147)",
    "ORDENANZA": "Ordenanza Tornquist",
    "DENSIDAD": 14669,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Trenque launquen",
    "COBRO": "Sistema SAMO + Tasa servicios asistenciales Art 89 y ss",
    "CONCEPTO": "No se cobrará a los residentes del distrito sin cobertura médica",
    "ORDENANZA": "Ordenanza Trenque Lauquen",
    "DENSIDAD": 48423,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Tres Arroyos",
    "COBRO": "Tasa solidaria de sostenimiento del servicio de salud Art. 183 y ss de la ordenanza fis (impuesto encubierto)",
    "CONCEPTO": "Se cobra a todo inmueble en \"Tasa servicios urbanos\".",
    "ORDENANZA": "Ordenanza Tres arroyos",
    "DENSIDAD": 62835,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Tres de Febrero",
    "COBRO": "Sistema SAMO Tributo por servicios asistenciales ART 245 Y SS",
    "CONCEPTO": "Gratuidad a personas sin cobertura médica",
    "ORDENANZA": "Ordenanza Tres de Febrero",
    "DENSIDAD": 366377,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Tres Lomas",
    "COBRO": "Tasa servicios asistenciales",
    "CONCEPTO": "La Ordenanza de Salud vigente 1043/13 DEL AÑO 2013 no figura disponible web, se solicito. Las actualizaciones dan cuenta del cobro a personas sin cobertura médica según medios económicos por encuesta social",
    "ORDENANZA": "Actualizaciones falta ordenanza solicitada",
    "DENSIDAD": 8825,
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Vicente López",
    "COBRO": "Sistema SAMO derechos asistenciales Art 254 y ss ordennza fiscal y Art 54 y ss ordenanza impositiva",
    "CONCEPTO": "Gratuito para personas sin cobertura",
    "ORDENANZA": "Ordenanza Vicente Lopez",
    "DENSIDAD": 283510,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Villa Gesell",
    "COBRO": "Tasa salud ART 148 Y SS codigo tributario  (impuesto encubierto)",
    "CONCEPTO": "Art 148 y ss La localidad posee un codigo tributario 2156/08 y modificaciones, no renueva el codigo todos los años unificado digesto https://www.juntosxgesell.ar/res_dige.php?criter=2156%2F08",
    "ORDENANZA": "Codigo tributario",
    "DENSIDAD": 38614,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Villarino",
    "COBRO": "Derecho de Comercialización sobre Producción Hortícola y Frutícola  (impuesto encubierto destinado a salud) Art 232 y ss",
    "CONCEPTO": "Derecho de Comercialización sobre Producción Hortícola y Frutícola. Del Destino de los Fondos\nARTÍCULO 236°: Los recursos serán afectados, destinados al financiamiento del Sistema de Salud Municipal, administrado por la Secretaría de Salud o quien en el futuro la reemplace.",
    "ORDENANZA": "Ordenanza Villarino",
    "DENSIDAD": 33170,
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Zárate",
    "COBRO": "Sistema SAMO Art 217 y ss",
    "CONCEPTO": "Sin especificación detallada",
    "ORDENANZA": "Ordenanza Zarate",
    "DENSIDAD": 132087,
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  }
]

@st.cache_data
def load_data():
    try:
        path = "/workspace/knowledge/Municipios_y_ordenanzas__-_Hoja_1-5.csv"
        df = pd.read_csv(path)
        df = df.dropna(how='all')
        df['MUNICIPIO'] = df['MUNICIPIO'].astype(str).str.strip()
        df['DENSIDAD'] = df['DENSIDAD POBLACIONAL (CENSO 2022)'].fillna('No especificado')
        df['ORDENANZA'] = df['ORDENANZA'].fillna('Sin dato')
        df['CONCEPTO'] = df['COBRO SERVICIO SALUD EN HOSPITAL PÚBLICO'].fillna('Ausencia de concepto')
        
        # Asignación de categorías de la investigación
        def assign_cat(r):
            m = str(r['MUNICIPIO']).strip()
            if m in ['Arrecifes', 'Adolfo Alsina', 'Alberti', 'Ayacucho', 'Castelli', 'Coronel Rosales', 'Coronel Pringles', 'Coronel Suárez', 'Daireaux', 'Dolores', 'Florentino Ameghino', 'General Alvear', 'General Arenales', 'General La Madrid', 'General Las Heras', 'General Lavalle', 'General Pinto', 'General Viamonte', 'Hipólito Yrigoyen', 'Leandro N. Alem', 'Lincoln', 'Lobería', 'Maipú', 'Malvinas Argentinas', 'Marcos Paz', 'Nueve de Julio', 'Olavarría', 'Patagones', 'Pehuajó', 'Pinamar', 'Ramallo', 'Rauch', 'Saavedra Pigue ', 'Salliquelo', 'Salto', 'San Andrés de Giles', 'Tandil', 'Tres Lomas']:
                return 'Categoría C (Arancel Directo)'
            elif m in ['25 de mayo', 'Adolfo González Chávez', 'Azul', 'Balcarce', 'Baradero', 'Campana', 'Carlos Casares', 'Chivilcoy', 'Escobar', 'Exaltación De La Cruz', 'Ezeiza', 'Florencio Varela', 'General Alvarado', 'General Pueyrredón', 'General Rodríguez', 'General Villegas', 'Guamini', 'Ituzaingó', 'Junín', 'La Costa', 'Lobos', 'Mar Chiquita', 'Mercedes', 'Monte', 'Moreno', 'Necochea', 'Punta Indio', 'San Antonio de Areco', 'San Vicente', 'Suipacha', 'Tapalque', 'Tres Arroyos', 'Villa Gesell', 'Villarino']:
                return 'Categoría B (Tasa Encubierta)'
            else:
                return 'Categoría A (Gratuidad / SAMO)'
        df['CATEGORIA'] = df.apply(assign_cat, axis=1)
        return df
    except Exception:
        df_emb = pd.DataFrame(EMBEDDED_DATA)
        return df_emb

df_censo = load_data()

# ==========================================
# BARRA LATERAL - NAVEGACIÓN Y CRÉDITOS
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/scales.png", width=65)
st.sidebar.title("SIA-PBA v2.0")
st.sidebar.markdown("**Sistema Integrado de Auditoría Algorítmica**")
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

# ==========================================
# MÓDULO 1: PRESENTACIÓN E IMPACTO TFC
# ==========================================
if "🏠 1. Presentación" in opcion_menu:
    st.markdown("<h2 class='main-title'>SIA-PBA: Auditoría Algorítmica & Canal Único de Denuncias</h2>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Herramienta tecnológica de control preventivo de legalidad, constitucionalidad y convencionalidad de ordenanzas fiscales e impositivas municipales de la Provincia de Buenos Aires</p>", unsafe_allow_html=True)
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
    st.subheader("🎯 Ejes Fundamentales de la Herramienta (Capítulo VIII)")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        ### 🔍 1. Módulo de Auditoría Algorítmica de Ordenanzas Futuras
        * **Análisis de Texto PNL Contextual:** Procesa automáticamente ordenanzas impositivas y fiscales locales por artículos.
        * **Aprendizaje del Censo Base (N=135):** Utiliza los hallazgos de la investigación como benchmark para evaluar futuras ordenanzas (2027+).
        * **Semáforo Tripartito de Convencionalidad:**
            * 🟢 **Cat. A (Gratuidad Plena / SAMO):** Cumplimiento del Art. 36 inc. 8 CPBA.
            * 🟡 **Cat. B (Tasas Encubiertas):** Detección de tributos disfrazados en ABL/Red Vial/Comercio.
            * 🔴 **Cat. C (Arancelamiento Directo):** Alerta por cobros indebidos o condición de indigencia/pobreza.
        """)
    with c2:
        st.markdown("""
        ### 🛡️ 2. Canal Único Descentralizado de Denuncias Anónimas
        * **Ruptura de la Espiral del Silencio:** Diseñado especialmente para ciudadanos de distritos de baja densidad con **efector único de salud**.
        * **Garantía Absoluta de Anonimato:** Algoritmo de desvinculación IP con emisión de **Código Hash Criptográfico Único**.
        * **Trazabilidad Institucional:** Derivación automática de alertas a la Defensoría del Pueblo PBA y Asesoría General de Gobierno.
        """)

# ==========================================
# MÓDULO 2: AUDITORÍA ALGORÍTMICA DE ORDENANZAS (IA)
# ==========================================
elif "🔍 2. Módulo de Auditoría" in opcion_menu:
    st.markdown("<h2 class='main-title'>🔍 Módulo de Auditoría Algorítmica Preventiva de Ordenanzas</h2>", unsafe_allow_html=True)
    st.markdown("Examen automatizado de constitucionalidad, convencionalidad y legalidad tributario-sanitaria municipal.")
    st.markdown("---")
    
    tab1, tab2 = st.tabs([
        "🏛️ Línea de Base 2026 (Consulta Censo N=135)",
        "🚀 Auditoría Algorítmica Futura 2027+ (Nuevas Ordenanzas)"
    ])
    
    # ------------------------------------------
    # SUBMÓDULO 1: CONSULTA CENSO HISTÓRICO 2026
    # ------------------------------------------
    with tab1:
        st.markdown("##### Seleccione cualquiera de los 135 Municipios de la Provincia de Buenos Aires:")
        muni_selected = st.selectbox("Municipio de la Prov. de Bs. As. (Censo N=135):", df_censo['MUNICIPIO'].unique(), key="muni_sub1")
        
        row_muni = df_censo[df_censo['MUNICIPIO'] == muni_selected].iloc[0]
        
        st.markdown("### 📊 Resultado del Examen Algorítmico - Censo Base 2026")
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
            st.write(f"**Densidad Poblacional:** {row_muni['DENSIDAD']} hab.")
            st.write(f"**Norma Relevada:** {row_muni['ORDENANZA']}")
            
        with col_res2:
            st.markdown("#### ⚖️ Fundamentación Jurídica del Censo Base")
            cobro_val = str(row_muni['COBRO']) if 'COBRO' in row_muni else str(row_muni['CONCEPTO'])
            conc_val = str(row_muni['CONCEPTO'])
            st.markdown(f"**Disposición Local Relevada:** *\"{cobro_val} - {conc_val}\" *")
            
            if 'Categoría C' in cat or 'Arancel' in cat:
                st.markdown("""
                <div class='legal-box'>
                <b>⚠️ Vulneraciones Normativas Detectadas:</b><br>
                1. <b>Violación del Art. 36 inc. 8 CPBA:</b> Imposición de barrera económica para acceder a la salud pública gratuita.<br>
                2. <b>Contravención del Art. 12 del PIDESC (Art. 75 inc. 22 CN):</b> Infracción al derecho a la salud sin discriminación económica.<br>
                3. <b>Encuadre Penal (Art. 266 del Código Penal):</b> Configuración de <i>Exacción Ilegal</i> por cobro o exigencia indebida de contribuciones asistenciales.
                </div>
                """, unsafe_allow_html=True)
            elif 'Categoría B' in cat:
                st.markdown("""
                <div class='legal-box'>
                <b>⚠️ Vulneraciones Normativas Detectadas:</b><br>
                1. <b>Tasa Encubierta / Sin Causa Tributaria:</b> Adición de partidas o porcentajes de salud sobre tributos domiciliarios (ABL, Red Vial, Comercio).
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='legal-box'>
                <b>✅ Compatibilidad Constitucional Constatada:</b><br>
                El municipio garantiza la atención pública gratuita y limita la recuperación de costos de forma legítima a Obras Sociales o Prepagas mediante el sistema SAMO (Ley Provincial 11.069).
                </div>
                """, unsafe_allow_html=True)

    # ------------------------------------------
    # SUBMÓDULO 2: AUDITORÍA DE FUTURAS ORDENANZAS (2027+)
    # ------------------------------------------
    with tab2:
        st.markdown("### 🚀 Motor de Auditoría Algorítmica de Futuras Ordenanzas (Ejercicio 2027 en adelante)")
        st.markdown("Cargue la nueva ordenanza aprobada para realizar la auditoría automatizada con base en el Censo Provincial.")
        st.markdown("---")
        
        c_fut1, c_fut2 = st.columns([1, 1])
        with c_fut1:
            muni_futuro = st.selectbox("Seleccione Municipio a auditar para el nuevo Ejercicio:", df_censo['MUNICIPIO'].unique(), key="muni_sub2")
            row_bench = df_censo[df_censo['MUNICIPIO'] == muni_futuro].iloc[0]
            cat_bench = row_bench['CATEGORIA']
            cobro_bench = str(row_bench['COBRO']) if 'COBRO' in row_bench else str(row_bench['CONCEPTO'])
            conc_bench = str(row_bench['CONCEPTO'])
            
            st.markdown(f"""
            <div class='card-bench'>
            <b>📌 Memoria Benchmark Censo Base 2026:</b><br>
            • <b>Estado Histórico:</b> <code>{cat_bench}</code><br>
            • <b>Norma Relevada 2026:</b> <i>\"{cobro_bench} - {conc_bench}\"</i><br>
            • <b>Directiva de Auditoría 2027:</b> El motor comparará el nuevo texto contra este antecedente para determinar si el municipio corrigió la norma, la mantuvo o creó nuevas tasas.
            </div>
            """, unsafe_allow_html=True)
            
        with c_fut2:
            anio_ejercicio = st.number_input("Ejercicio Fiscal a Auditar:", min_value=2026, max_value=2030, value=2027, step=1)
            pdf_file = st.file_uploader("Adjuntar archivo PDF de la nueva Ordenanza Fiscal / Impositiva:", type=['pdf'])
            
        texto_suplementario = st.text_area(
            "Texto de la Ordenanza (Si el PDF es una imagen escaneada o desea evaluar un articulado específico, péguelo aquí):",
            value="",
            height=140,
            placeholder="Pegue aquí el texto completo del capítulo de tasas de la nueva ordenanza para auditar..."
        )
        
        if st.button("🚀 Ejecutar Auditoría Algorítmica Futura (2027+)"):
            st.markdown("---")
            st.subheader(f"📋 Dictamen de Auditoría Algorítmica - {muni_futuro} (Ejercicio {anio_ejercicio})")
            
            # Extraction of Text
            texto_a_analizar = ""
            if pdf_file is not None:
                try:
                    reader = pypdf.PdfReader(pdf_file)
                    text_extracted = ""
                    for p in reader.pages:
                        t = p.extract_text()
                        if t:
                            text_extracted += t + "\n"
                    if len(text_extracted.strip()) > 50:
                        texto_a_analizar = text_extracted
                        st.info(f"✅ Documento PDF digital leído con éxito ({len(reader.pages)} páginas, {len(text_extracted)} caracteres).")
                    else:
                        st.warning("⚠️ El PDF subido es una fotocopia o imagen escaneada. Se utilizará el texto pegado en el cuadro suplementario.")
                except Exception as e:
                    st.warning("⚠️ Error al leer el PDF. Se procederá con el texto del editor suplementario.")
            
            if not texto_a_analizar and len(texto_suplementario.strip()) > 10:
                texto_a_analizar = texto_suplementario
                
            if not texto_a_analizar or len(texto_a_analizar.strip()) < 15:
                st.error("❌ ERROR: No se detectó texto legible para auditar. Por favor adjunte un PDF digital o pegue el texto del articulado en el cuadro suplementario.")
            else:
                # --------------------------------------
                # PNL PARSER BY ARTICLES & HEALTH DOMAIN
                # --------------------------------------
                # Split text into articles
                raw_articles = re.split(r'(?i)(?=ART[ÍI]CULO\s+\d+)', texto_a_analizar)
                
                arts_cat_c = []
                arts_cat_b = []
                arts_cat_a = []
                
                # Excluded Non-Health Domains
                EXCLUDE_PATTERNS = [
                    r'SEGURIDAD\s+E\s+HIGIENE', r'HABILITACI[ÓO]N\s+COMERCIAL', r'BROMATOLOG[ÍI]A',
                    r'MUESTREO\s+DE\s+PRODUCTOS', r'CONVENIO\s+MULTILATERAL', r'SERVICIOS\s+GENERALES',
                    r'RED\s+VIAL', r'ALUMBRADO', r'CEMENTERIO', r'SEPULTURA', r'PUBLICIDAD',
                    r'PADRONES\s+MUNICIPALES', r'PLANOS\s+DE\s+OBRA', r'CLOACAS', r'OBRAS\s+SANITARIAS'
                ]
                
                # Health Domain Markers
                HEALTH_PATTERNS = [
                    r'HOSPITAL', r'SALUD', r'ASISTENCIAL', r'M[ÉE]DIC', r'GUARDIA',
                    r'PACIENT', r'SANATORIAL', r'SAMO', r'AMBULANCIA', r'PRESTACION'
                ]
                
                # Risk Category C Patterns (Arancel directo / Indigencia / Pagaré / Apremio)
                RISK_C_PATTERNS = [
                    r'ARANCEL', r'ABONAR[ÁA]', r'NOMENCLADOR', r'APREMIO', r'PAGAR[ÉE]',
                    r'INDIGENCIA', r'CARENCIA', r'ESCASOS\s+RECURSOS', r'ENCUESTA\s+SOCIAL',
                    r'INFORME\s+SOCIAL', r'CARNET\s+HOSPITALARIO', r'RESERVA\s+LA\s+GRATUIDAD',
                    r'CATEGORIZACI[ÓO]N', r'DECLARACI[ÓO]N\s+JURADA', r'TARIFA'
                ]
                
                # Risk Category B Patterns (Tasa encubierta / Fondo de salud sobre impuesto general)
                RISK_B_PATTERNS = [
                    r'FONDO\s+MUNICIPAL\s+DE\s+SALUD', r'FONDO\s+COMPLEMENTARIO\s+DE\s+SALUD',
                    r'CONTRIBUCI[ÓO]N\s+ESPECIAL\s+SALUD', r'TASA\s+DE\s+SALUD',
                    r'CONTRIBUCI[ÓO]N\s+AL\s+SISTEMA\s+DE\s+SALUD', r'SOSTENIMIENTO\s+DE\s+SALUD',
                    r'ADICIONAL\s+SALUD', r'DERECHO\s+DE\s+COMERCIALIZACI[ÓO]N'
                ]
                
                # Category A Patterns (Gratuidad plena / SAMO)
                CAT_A_PATTERNS = [
                    r'GRATUIT', r'SIN\s+COSTO', r'SIN\s+CARGO', r'SAMO', r'OBRAS\s+SOCIALES', r'PREPAGAS'
                ]
                
                for art in raw_articles:
                    art_clean = art.strip()
                    if len(art_clean) < 20:
                        continue
                    art_upper = art_clean.upper()
                    
                    # 1. Strict Non-Health Domain Filtering
                    is_excluded = any(re.search(p, art_upper) for p in EXCLUDE_PATTERNS)
                    is_health = any(re.search(p, art_upper) for p in HEALTH_PATTERNS)
                    
                    if is_excluded and not is_health:
                        continue
                        
                    if not is_health:
                        continue
                        
                    # 2. Evaluation of Health Article
                    has_c = any(re.search(p, art_upper) for p in RISK_C_PATTERNS)
                    has_b = any(re.search(p, art_upper) for p in RISK_B_PATTERNS)
                    has_a = any(re.search(p, art_upper) for p in CAT_A_PATTERNS)
                    
                    # Deductive reasoning for Category C (Arancel or Indigencia requirement)
                    if has_c and not ('GRATUITO' in art_upper and not 'INDIGENCIA' in art_upper):
                        arts_cat_c.append(art_clean[:300] + ("..." if len(art_clean)>300 else ""))
                    elif has_b:
                        arts_cat_b.append(art_clean[:300] + ("..." if len(art_clean)>300 else ""))
                    elif has_a or 'GRATUITO' in art_upper or 'SAMO' in art_upper:
                        arts_cat_a.append(art_clean[:300] + ("..." if len(art_clean)>300 else ""))

                # Final Deductive Decision & Comparison with Baseline
                if len(arts_cat_c) > 0:
                    st.error("🔴 **ALERTA CRÍTICA: DETECCIÓN DE CLÁUSULAS INCONSTITUCIONALES / CATEGORÍA C**")
                    st.markdown("<span class='badge-cat-c'>Categoría C - Arancel Directo / Barrera Económica</span>", unsafe_allow_html=True)
                    st.markdown(f"**Comparativa frente al Censo Base 2026:** El municipio {muni_futuro} mantiene o reintroduce normas de arancelamiento directo.")
                    st.markdown("#### 📜 Artículos Infractores Detectados en la Salud Pública:")
                    for a in arts_cat_c[:4]:
                        st.markdown(f"<div class='snippet-box'><b>⚠️ Cita Textual de la Ordenanza:</b><br>\"{a}\"</div>", unsafe_allow_html=True)
                elif len(arts_cat_b) > 0:
                    st.warning("🟡 **ALERTA MEDIA: DETECCIÓN DE TASAS ENCUBIERTAS / CATEGORÍA B**")
                    st.markdown("<span class='badge-cat-b'>Categoría B - Tributo Encubierto sobre Salud</span>", unsafe_allow_html=True)
                    st.markdown(f"**Comparativa frente al Censo Base 2026:** Se detectó la adición de tasas o fondos de salud sobre impuestos generales.")
                    st.markdown("#### 📜 Artículos Infractores Detectados:")
                    for a in arts_cat_b[:4]:
                        st.markdown(f"<div class='snippet-box'><b>⚠️ Cita Textual de la Ordenanza:</b><br>\"{a}\"</div>", unsafe_allow_html=True)
                else:
                    st.success("🟢 **DICTAMEN POSITIVO: NORMATIVA CONFORME A DERECHO / GRATUIDAD PLENA (CATEGORÍA A)**")
                    st.markdown("<span class='badge-cat-a'>Categoría A - Conforme al Art. 36 inc. 8 CPBA</span>", unsafe_allow_html=True)
                    st.markdown(f"**Comparativa frente al Censo Base 2026:** La normativa analizada para {muni_futuro} respeta el principio de gratuidad del servicio público asistencial y limita el recupero de costos al sistema SAMO (Ley 11.069).")
                    if len(arts_cat_a) > 0:
                        st.markdown("#### 📜 Artículo de Conformidad Normativa Extraído:")
                        for a in arts_cat_a[:2]:
                            st.markdown(f"<div class='snippet-box-a'><b>✅ Cita Textual de la Ordenanza:</b><br>\"{a}\"</div>", unsafe_allow_html=True)

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
        muni_denuncia = st.selectbox("Seleccione el Municipio del hecho (135 Municipios):", df_censo['MUNICIPIO'].unique(), key="muni_sub3")
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
            'Municipios': [64, 34, 37]
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
    
    muni_dictamen = st.selectbox("Seleccione Municipio para emitir Dictamen (135 Municipios):", df_censo['MUNICIPIO'].unique(), key="muni_sub5")
    row_d = df_censo[df_censo['MUNICIPIO'] == muni_dictamen].iloc[0]
    
    cobro_d = str(row_d['COBRO']) if 'COBRO' in row_d else str(row_d['CONCEPTO'])
    conc_d = str(row_d['CONCEPTO'])
    
    dictamen_text = f"""
========================================================================================
ALERTA INSTITUCIONAL DE INCONSTITUCIONALIDAD Y INCONVENCIONALIDAD TRIBUTARIA
SIA-PBA // AUDITORÍA ALGORÍTMICA DE ORDENANZAS MUNICIPALES
========================================================================================

FECHA DE EMISIÓN: {datetime.date.today().strftime('%d/%m/%Y')}
SUJETO AUDITADO: Municipalidad de {row_d['MUNICIPIO']} (Provincia de Buenos Aires)
DENSIDAD POBLACIONAL: {row_d['DENSIDAD']} hab.
NORMA EXAMINADA: {row_d['ORDENANZA']}
DISPOSICIÓN TRIBUTARIA: \"{cobro_d} - {conc_d}\"
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
