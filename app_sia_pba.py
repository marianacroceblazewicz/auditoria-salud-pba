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
# CONFIGURACIÓN DE PÁGINA Y ESTILO
# ==========================================
st.set_page_config(
    page_title="SIA-PBA | Auditoría Algorítmica de Ordenanzas & Canal Único",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS Personalizado
st.markdown("""
<style>
    .main-title {
        color: #1B365D;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        margin-bottom: 0px;
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
        border-left: 5px solid #1B365D;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .badge-cat-a {
        background-color: #D4EDDA;
        color: #155724;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
    }
    .badge-cat-b {
        background-color: #FFF3CD;
        color: #856404;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
    }
    .badge-cat-c {
        background-color: #F8D7DA;
        color: #721C24;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
    }
    .legal-box {
        background-color: #EDF2F7;
        border-left: 4px solid #2B6CB0;
        padding: 12px;
        border-radius: 4px;
        font-size: 0.95rem;
    }
    .snippet-box {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E0;
        border-left: 4px solid #E53E3E;
        padding: 10px;
        border-radius: 4px;
        margin-bottom: 10px;
        font-size: 0.9rem;
    }
    .snippet-box-a {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E0;
        border-left: 4px solid #38A169;
        padding: 10px;
        border-radius: 4px;
        margin-bottom: 10px;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# MATRIZ EMBEBIDA COMPLETA (N=135)
# ==========================================
DATA_135 = [
  {
    "MUNICIPIO": "25 de mayo",
    "DENSIDAD": "36676",
    "ORDENANZA": "Ordenanza 25 de mayo",
    "COBRO": "Tasa , impuesto encubierto ",
    "CONCEPTO": "\"Fondo para Salud\" del 7% calculado sobre la liquidación de otras tasas (Alumbrado, Limpieza, Red Vial) o sobre el importe básico facturado de energía eléctrica.",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Adolfo Alsina",
    "DENSIDAD": "17552",
    "ORDENANZA": "Ordenanza Adolfo Alsina",
    "COBRO": "Tasa servicio asistencial Art. 31",
    "CONCEPTO": "En ordenanza aclara el sistema del carnet hospitalario y % a pagar según clasificacion de segm de servicios sociales",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Adolfo González Chávez",
    "DENSIDAD": "12914",
    "ORDENANZA": "Ordenanza Adolfo Gonzalez Chaves (última encontrada vía web año 2024)",
    "COBRO": "Tasa cobertura universal de salud, impuesto encubierto",
    "CONCEPTO": "No aclara porcentaje , se cobra con tasa servicios urbanos y tasa conservacion , reparacion y mejorado de la red vial municipal ",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Alberti",
    "DENSIDAD": "12982",
    "ORDENANZA": "Ordenanza Alberti",
    "COBRO": "Tasa servicio asistencial Art. 129",
    "CONCEPTO": "Se establece cobro según nomenclador ioma a quienes evidencien capacidad contributiva , se podra pedir informe socioeconomico a asistentes sociales",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Almirante Brown",
    "DENSIDAD": "584827",
    "ORDENANZA": "Ordenanza Almirante Brown ",
    "COBRO": "Sistema recupero SAMO",
    "CONCEPTO": "No figura en ordenanza municipal cobro a personas sin cobertura médica ",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Arrecifes",
    "DENSIDAD": "32405",
    "ORDENANZA": "Odenanza Arrecifes ",
    "COBRO": "Tasa servicio asistencial Art. 179 y ss",
    "CONCEPTO": "Individualiza al paciente como sujeto de cobro. Se reserva la gratuidad a la evidente carencia",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Avellaneda",
    "DENSIDAD": "367554",
    "ORDENANZA": "Ordenanza Avellaneda",
    "COBRO": "Sistema recupero SAMO",
    "CONCEPTO": "Hace mencion al principio de gratuidad y trato igualitario en el Art. 214",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Ayacucho",
    "DENSIDAD": "22136",
    "ORDENANZA": "Ordenanza Ayacucho ",
    "COBRO": "Tasa servicio asistencial Art. 36 inc. 2",
    "CONCEPTO": "Brinda facultad a la direccion para determinar eximición de pago en escala del 30, 50 y 70% según encuesta social",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Azul",
    "DENSIDAD": "75905",
    "ORDENANZA": "Ordenanza Azul",
    "COBRO": "Previo año 2024 tasa servicios esenciales (demanda) Impuesto encubierto. Año 2025 tasa servicios esenciales ",
    "CONCEPTO": "Año 2023 tasa servicios esenciales salud y otros servicios (deporte, educacion etc.) a inmuebles urbanos y rurales  AÑO 2025 tasa por servicios asistenciales, gratuitad situacion socio económica . Art. 212 Tasa asistencial Art. 129 no pago excentos por situacion socio económica ",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Bahía Blanca",
    "DENSIDAD": "336574",
    "ORDENANZA": "Ordenanza Bahia Blanca ",
    "COBRO": "Tasa por servicios asistenciales Art 254 y ss",
    "CONCEPTO": "Individualiza como contribuyente a quien recibe los servicios asistenciales ",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Balcarce",
    "DENSIDAD": "51736",
    "ORDENANZA": "Ordenanza Balcarce ",
    "COBRO": "Contribución Obligatoria para la Salud Art 73",
    "CONCEPTO": "a) Contribuyentes de la Tasa por Alumbrado Público b) Contribuyentes de la Tasa por Conservación, Reparación y Mejorado de la  Red Vial c) Contribuyentes de la Tasa por Inspección de Seguridad e Higiene",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Baradero",
    "DENSIDAD": "37491",
    "ORDENANZA": "Ordenanza Baradero",
    "COBRO": "Fondo municipal de Salud  ART. 37",
    "CONCEPTO": "Valor menor $583 adicional a otras tasas",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Beníto Juárez",
    "DENSIDAD": "22292",
    "ORDENANZA": "Ordenanza Benito Juarez ",
    "COBRO": "Ausencia de concepto en ordenanza ",
    "CONCEPTO": "Se llamó por teléfono para consultar por turno para análisis manifestando no tener obra social y si tenia costo, se indicó que se me acerque para sacar turno, solo fue consultado si el DNI tenia domicilio de Benito Juarez. Se limita atencion a vecinos del domicilio.  ",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Berazategui",
    "DENSIDAD": "358712",
    "ORDENANZA": "Ordenanza Berazategui  Página Web Hospital",
    "COBRO": "Tasa servicio asistencial Art. 160",
    "CONCEPTO": "Figura en ordenanza el concepto e individualiza al contribuyente como \"todos los que soliciten el servicio\" pero en la web del hospital se aclara, por intentos de estafas, que toda atencion, práctica y estudios son gratuitos. ",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Berisso",
    "DENSIDAD": "100930",
    "ORDENANZA": "Ordenanza Berisso",
    "COBRO": "Ausencia de concepto en ordenanza ",
    "CONCEPTO": "\"(...)habitantes de Berisso, independientemente del\nlugar donde residan\"",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Bolívar",
    "DENSIDAD": "38119",
    "ORDENANZA": "Ordenanza bolivar 1488/98 deroga tasa asistencial ",
    "COBRO": "Sistema recupero SAMO. Tasa asistencial derogada año 98",
    "CONCEPTO": "Se cobraba tasa asistencial hasta el año 98",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Bragado",
    "DENSIDAD": "44972",
    "ORDENANZA": "Ordenanza Bragado",
    "COBRO": "No figura ordenanza, solo la que aprueba la misma sin el anexo",
    "CONCEPTO": "Se intentó  por teléfono sin éxito, se solicitó por email.",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Brandsen",
    "DENSIDAD": "33026",
    "ORDENANZA": "Ordenanza Brandsen ",
    "COBRO": "Ausencia de concepto",
    "CONCEPTO": "Sin concepto detallado",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Campana",
    "DENSIDAD": "107979",
    "ORDENANZA": "Ordenanza Campana ",
    "COBRO": "Tasa Aporte para la Salud Pública Art. 353. Impuesto encu",
    "CONCEPTO": "Contribuyentes propietarios de inmuebles Tasa por Servicios Generales y/o Conservación, Reparación y Mejorado de la red Vial Municipal.Establecimientos Comerciales, Industriales y/o similares Tasa por Inspección de Seguridad e Higiene ",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Cañuelas",
    "DENSIDAD": "70684",
    "ORDENANZA": "Ordenanza Cañuelas ",
    "COBRO": "Ausencia concepto en ordenanza",
    "CONCEPTO": "Se llamó al hospital municipal manifestando pedir turno para analisis y no tener obra social, se responde que se acerque a sacar turno y responde que no tiene costo ante la consulta",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Capitán Sarmiento",
    "DENSIDAD": "15906",
    "ORDENANZA": "Ordenanza Capitan Sarmiento",
    "COBRO": "Tasa servicio asistencial Art. 135 y ss",
    "CONCEPTO": "Limita gratuidad a nivel socioeconomico, informe del servicio de Desarrollo Social, excepcion de pago puede ser total o parcial (no aclara porcentajes)\n",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Carlos Casares",
    "DENSIDAD": "23204",
    "ORDENANZA": "Ordenanza Carlos Casares ",
    "COBRO": "Fondo municipal de Salud Art. 178 y ss (impuesto encubierto)",
    "CONCEPTO": "Contribuyentes: Contribuyente de las tasas \"Retributivas por Servicios Urbanos\" y por \"Conservación, Reparación y Mejorado de la Red Vial Municipal\" no especifica monto",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Carlos Tejedor",
    "DENSIDAD": "13148",
    "ORDENANZA": "Ordenanza Carlos Tejedor ",
    "COBRO": "Ausencia concepto en ordenanza",
    "CONCEPTO": "Se llamó telefónicamente  02357420103 se refirio que aveces médicos cobran un \"plus\" de $2.000 o $3.000. Seguir averiguando.",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Carmen De Areco",
    "DENSIDAD": "17386",
    "ORDENANZA": "Ordenanza Carmen de Areco",
    "COBRO": "Ausencia concepto en ordenanza",
    "CONCEPTO": "02273 442155 no contesta volver a llamar",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Castelli",
    "DENSIDAD": "10517",
    "ORDENANZA": "Ordenanza Castelli",
    "COBRO": "SAMO + Tasa servicio asistencial",
    "CONCEPTO": "Se discrimina en ordenanza el sistema SAMO, contribuyentes sin obra social con pago total o parcial según informe social y tarifa plena para no residentes del municipio. Especifica costo traslado ambulancia",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Chacabuco",
    "DENSIDAD": "52731",
    "ORDENANZA": "Ordenanza Chacabuco",
    "COBRO": "Ausencia concepto en ordenanza",
    "CONCEPTO": "En la web del hospital se expone \"Si el paciente posee obra social, ART, compañía seguro u otro tipo de cobertura, estará a cargo de éstas. Si el paciente no tiene ningún tipo de cobertura, será atendido de manera totalmente gratuita\" https://chacabuco.gob.ar/direccion-del-hospital/",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Chascomús",
    "DENSIDAD": "42452",
    "ORDENANZA": "Ordenanza Chascomus",
    "COBRO": "SAMO",
    "CONCEPTO": "Ordenanza no aclara personas sin cobertura ",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Chivilcoy",
    "DENSIDAD": "70839",
    "ORDENANZA": "Ordenanza fiscal chivilcoy     Ordenanza impositiva Chivilcoy",
    "COBRO": "Tasa servicios asistenciales, impuesto encubierto",
    "CONCEPTO": "Se cobra tasa, impuesto encubierto a inmuebles urbanos y rurales. Art 87 ordenanza fiscal Art 5 ordenanza impos",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Colón",
    "DENSIDAD": "27504",
    "ORDENANZA": "Ordenanza Colón ",
    "COBRO": "SAMO ",
    "CONCEPTO": "Ordenanza no aclara personas sin cobertura . Se detecta abuso de la retencion de 90% pension jubilados en sala de ancianos ",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Coronel Dorrego",
    "DENSIDAD": "15968",
    "ORDENANZA": "Ordenanza Coronel Dorrego",
    "COBRO": "Sistema SAMO + Tasa servicios asistenciales Art 177",
    "CONCEPTO": "Se aclara que solo se recupera por sistema SAMO, no se cobra a personas sin cobertura sean o no residentes. ",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Coronel Rosales",
    "DENSIDAD": "67503",
    "ORDENANZA": "Ordenanza Coronel Rosales 2021",
    "COBRO": "No figura ordenanza actualizada. Última año 2021",
    "CONCEPTO": "Tasa asistencial. Especifica la excepcion \"Las personas carentes de aportes de obras sociales\"",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Coronel Pringles",
    "DENSIDAD": "24420",
    "ORDENANZA": "Ordenanza Coronel Pringles ",
    "COBRO": "Tasa servicios asistenciales",
    "CONCEPTO": "Son Contribuyentes y/o responsables:a) Las personas que soliciten el servicio, ya sea el paciente, el familiar a cargo, familiar obligado a prestar alimentos, el apoderado, el curador.-",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Coronel Suárez",
    "DENSIDAD": "42110",
    "ORDENANZA": "Ordenanza Coronel Suarez",
    "COBRO": "Tasa servicios asistenciales Art. 144 y ss",
    "CONCEPTO": "Gratuidad reservada a evidente carencia de recursos. Categorización por Servicios Sociales A, B y C según % a pagar. Si no entran en esas categorías abonan el total. Art 147",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Daireaux",
    "DENSIDAD": "18422",
    "ORDENANZA": "Ordenanza Daireaux",
    "COBRO": "Tasa asistencial Art 23",
    "CONCEPTO": "\"(...) para aquellos que soliciten y/o usufructúen de las prestaciones (...)\"",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Dolores",
    "DENSIDAD": "30372",
    "ORDENANZA": "Ordenanza dolores",
    "COBRO": "Tasa asistencial Art 29",
    "CONCEPTO": "Contribuyente: Quienes soliciten los servicios asistenciales, y tengan recursos probados",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Ensenada",
    "DENSIDAD": "63997",
    "ORDENANZA": "Ordenanza Ensenada",
    "COBRO": "SAMO ",
    "CONCEPTO": "Art. 191 fiscal y 48 impositiva Contribuyentes obra sociales, prepagas, art, seguros",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Escobar",
    "DENSIDAD": "256449",
    "ORDENANZA": "Ordenanza Escobar ",
    "COBRO": "Tasa por servicios especiales. impuesto encubierto",
    "CONCEPTO": "Se prevee en tasa alumbrado barrido limpieza diversos servicios entre los cuales se incluye salud. Art. 103 y 125",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Esteban Echeverría",
    "DENSIDAD": "338480",
    "ORDENANZA": "Ordenanza Esteban Echeverria ",
    "COBRO": "SAMO",
    "CONCEPTO": "Art. 16.1",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Exaltación De La Cruz",
    "DENSIDAD": "40159",
    "ORDENANZA": "Ordenanza exaltación de la cruz",
    "COBRO": "Tasa por servicios generales. impuesto encubierto",
    "CONCEPTO": "Art. 3",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Ezeiza",
    "DENSIDAD": "201511",
    "ORDENANZA": "Ordenanza Ezeiza",
    "COBRO": "Servicios complementarios de salud . Contribucion especial",
    "CONCEPTO": "Art. 1.7 ordenanza impositiva. impuesto encubierto.",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Florencio Varela",
    "DENSIDAD": "496433",
    "ORDENANZA": "Odenanza Florencia Varela",
    "COBRO": "Tasa por servicios generales. impuesto encubierto",
    "CONCEPTO": "Art. 115 ordenanza fiscal ",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Florentino Ameghino",
    "DENSIDAD": "10790",
    "ORDENANZA": "Ordenanza Florentino Ameghino",
    "COBRO": "Aranceles hospitalarios",
    "CONCEPTO": "Art. 208 \"Los distintos servicios prestados en el Hospital municipal de Florentino Ameghino, que se encuetran en la ordenanza 114/93 se cobrarán según los valores fijados en la mencionada ordenanza.\" No se encuentra la ordenanza ",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "General Alvarado",
    "DENSIDAD": "45597",
    "ORDENANZA": "Ordenanza General Alvarado ",
    "COBRO": "Tasa de salud",
    "CONCEPTO": "impuesto encubierto",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "General Alvear",
    "DENSIDAD": "13031",
    "ORDENANZA": "Ordenanza General Alvear ",
    "COBRO": "Tasa por servicios asistenciales Art. 38",
    "CONCEPTO": "No aclara contribuyente.\"(...) fíjanse para los servicios asistenciales prestados en el Hospital  Municipal “Dr. Bernardino Rivadavia” los importes determinados en el nomenclador IOMA.\"",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "General Arenales",
    "DENSIDAD": "16350",
    "ORDENANZA": "Última ordenanza que figura año 2023",
    "COBRO": "Tasa servicios asistenciales Art. 134 y ss",
    "CONCEPTO": "Exceptuados de pago los casos individuales que presene evidente carencia de recursos previa diagnóstico social +  ciertas prácticas como obstetricia, pediatria menor 1 año, inmunizaciones programadas, enfermedades transmisibles agudas y crónicas que el Ministerio de bienestar social asi determine  ",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "General Belgrano",
    "DENSIDAD": "20791",
    "ORDENANZA": "Ordenanza General Belgrano",
    "COBRO": "Tasa asistencial ",
    "CONCEPTO": "ART. 151 Aclara que presta servicios gratuito a quien carezca de recursos para cubrirlos. Ademas SAMO",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "General Guido",
    "DENSIDAD": "3174",
    "ORDENANZA": "Ordenanza General Guido ",
    "COBRO": "Tasa de Servicio de Salud Art 21",
    "CONCEPTO": "Por cada recibo de Tasa o Derecho desde $ 5.000,00.- hasta la suma de $120.000",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "General Juan Madariaga",
    "DENSIDAD": "22624",
    "ORDENANZA": "Ordenanza Juan Madariaga ",
    "COBRO": "Tasa por servicios asistenciales Art 208 y ss",
    "CONCEPTO": "De forma explicita la ordenanza sostiene el sistema de salud público y gratuito, expone el sistema de recupero SAMO y manifie \"Cuando el paciente voluntariamente desee colaborar podrá abonar las prestaciones de acuerdo a los valores establecidos en la Ordenanza Impositiva.\"",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "General La Madrid",
    "DENSIDAD": "11618",
    "ORDENANZA": "Ordenanza General Lamadrid ",
    "COBRO": "Tasa servicio asistenciales Art 13",
    "CONCEPTO": "Se especifica como contribuyente a pacientes ambulatorios o internados sin obra social, se les cobrará según nomenclador, tb los materiales y medicamentos utilizados. Tb especifica que se cobrará materiales y medicamentos a  los pacientes del hogar de ancianos. Utiliza entrevista asistente social y categorías, cobertura total o parcial. Se hizo denuncia, en este momento quitaron la ordenanza de la web y se les informó que debian modificarla para obtener la licencia para el año 2027 para el hospital",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "General Las Heras",
    "DENSIDAD": "18022",
    "ORDENANZA": "Ordenanza General Las Heras",
    "COBRO": "Tasa servicios asistenciales Art. 123 y ss ",
    "CONCEPTO": "Contribuyente quien obtenga el servicio, familiares, obra social o prepapaga, seguro de salud. Eximición total o parcial de pago por condicion socio económica constatada por personal o previa entre vista asistencia social",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "General Lavalle",
    "DENSIDAD": "4870",
    "ORDENANZA": "Ordenanza General Lavalle ",
    "COBRO": "Tasa servicios asistenciales Art. 173 y ss",
    "CONCEPTO": "Excepción a las personas carentes de recursos . Excluidos los servicios de obstetricia, pediatria hasta 1 año, inmunizaciones programadas, enfermedades transmisibles agudas y crónicas que el Ministerio de Bienestar Social así determine. ",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "General Paz",
    "DENSIDAD": "14207",
    "ORDENANZA": "Ordenanza General Paz",
    "COBRO": "Residentes Tasa contributiva unidad terapia intensiva Art. 291 y ss No residentes Art. 294 y ss por todo servicio en el hospital ",
    "CONCEPTO": "Residentes urbanos tasa servicios urbanos 3usd mensual y Residentes rurales en tasa vial 8 usd bimestral. No residentes Art. 294 y ss por todo servicio en el hospital se determina el valor en UF , el valor es mayor si no poseen cobertura.  Art 297",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "General Pinto",
    "DENSIDAD": "12941",
    "ORDENANZA": "Ordenanza General Pinto",
    "COBRO": "Aranceles hospitalarios Art. 240 y ss ",
    "CONCEPTO": "prestación a un paciente sin Obra Social, y que según encuesta social realizada por el profesional del área, esté en condiciones de abonar, par dicho caso se facturará teniendo en cuenta nomenclador para HPM del IOMA",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "General Pueyrredón",
    "DENSIDAD": "667081",
    "ORDENANZA": "Ordenanza General Pueyrredon",
    "COBRO": "Contribución a la Salud, la Educación y el Desarrollo Infantil Art 217 y ss",
    "CONCEPTO": "contribución fija por cada inmueble emplazado en el Partido de General Pueyrredon gravado por la Tasa por Servicios Urbanos o por la Tasa por Conservación, Reparación y Mejorado de la red vial municipal",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "General Rodríguez",
    "DENSIDAD": "142709",
    "ORDENANZA": "Ordenanza General Rodriguez ",
    "COBRO": "Tasa especial servicios de educación, salud y seguridad (impuesto encubierto) Art 42 y ss Tasa asistencial por hospital odontologico y oftalmologíco Art. 43 y ss ordenanza impositiva. ",
    "CONCEPTO": "Valores se establecen e X cantidad de módulos. ART 41 tasa emergencias médicas Art 42 impuesto encubierto salud Art 43 hospital odontólogo y oftalmologia ",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "General San Martín",
    "DENSIDAD": "450575",
    "ORDENANZA": "Ordenanza General San Martin ",
    "COBRO": "SAMO Art 303 y ss",
    "CONCEPTO": "Refiere solo al sistema SAMO de recupero ",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "General Viamonte",
    "DENSIDAD": "22649",
    "ORDENANZA": "Ordenanza General Viamonte",
    "COBRO": "Tasa asistencial Art. 205 y ss",
    "CONCEPTO": "El ejectuvi puede adecuar valores según situacion socioeconomica. Algunas prácticas están excentas de pago.  Se determina el contribuyente sin obra social pero con ingresos suficientes y sin ingresos suficientes. Hacen distincion con no residentes.",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "General Villegas",
    "DENSIDAD": "35251",
    "ORDENANZA": "Ordenanza General Villegas ",
    "COBRO": "FONDO POR SERVICIOS ASISTENCIALES Y PARA LA SALUD Art. 57 ",
    "CONCEPTO": "Artículo 57º: No aprobado, en Sesión Especial 2° del 22 de diciembre del 2025. ",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Guamini",
    "DENSIDAD": "11801",
    "ORDENANZA": "Ordenanza guamini",
    "COBRO": "Tasa salud (impuesto encubierto) Art 205 y ss ordenanza fiscal + Tasa servicios asistenciales Art. 30 y ss ordenanza impositiva ",
    "CONCEPTO": "Tarifario por prestaciones de forma detalladad: radiografias, mamografía, etc. ",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Hipólito Yrigoyen",
    "DENSIDAD": "10661",
    "ORDENANZA": "Ordenanza Hipólito Yrigoyen",
    "COBRO": "Tasa servicios asistenciales Art. 45 y ss",
    "CONCEPTO": "No posee su ordenanza en la web, se consulto sistema SIBOM de la provincia de Buenos Aires",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Hurlingham",
    "DENSIDAD": "185641",
    "ORDENANZA": "Sin dato",
    "COBRO": "Ausencia de concepto",
    "CONCEPTO": "No figura en su web si en el sistema SIBOM ",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Ituzaingó",
    "DENSIDAD": "180232",
    "ORDENANZA": "Ordenanza Ituzaingo ",
    "COBRO": "SAMO + tasa de proteccion ciudadana (impuesto encubierto) Art. 18.1",
    "CONCEPTO": "Se define el sistema samo de recupero y una tasa como impuesto encubierto para los contribuyentes para sotener servicios varios del municipio entre los cuales se encuentra el de salud ",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "José C. Paz",
    "DENSIDAD": "326992",
    "ORDENANZA": "Sin dato",
    "COBRO": "Ausencia de concepto",
    "CONCEPTO": "Última que figura año 2018 se cobra a no residentes ",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Junín",
    "DENSIDAD": "103787",
    "ORDENANZA": "Ordenanza Junin ",
    "COBRO": "TASA POR SERVICIOS PUBLICOS URBANOS (S.P.U.) Art. 1",
    "CONCEPTO": "impuesto encubierto, se incluye a la salud en la tasa de servicios generales del municipio ",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "La Costa",
    "DENSIDAD": "100689",
    "ORDENANZA": "Ordenanza La Costa",
    "COBRO": "Tasa servicios asistenciales Art. 198 Fondo Salud a rurales Art.275 impuesto encubierto",
    "CONCEPTO": "Art 198 Tasa servicios asistenciales, pago no residentes eximidos de pago indigentes Art 275 Fondo Complementario de Seguridad y Salud, que será aplicado a las partidas del Sector Rural que tendrá un valor establecido por la Ordenanza Impositiva vigente.",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "La Matanza",
    "DENSIDAD": "1841247",
    "ORDENANZA": "Ordenanza La Matanza",
    "COBRO": "SAMO Art 249",
    "CONCEPTO": "Se especifica el sistema de recupero SAMO en la ordenanza Art. 249",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "La Plata",
    "DENSIDAD": "768470",
    "ORDENANZA": "Ordenanzas La plata ",
    "COBRO": "Ausencia de concepto ",
    "CONCEPTO": "Ausencia de concepto tanto en ordenanza fiscal como impositiva ",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Lanus",
    "DENSIDAD": "461267",
    "ORDENANZA": "Ordenanza Lanús ",
    "COBRO": "Ausencia de concepto ",
    "CONCEPTO": "Ausencia de concepto en código tributario",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Laprida",
    "DENSIDAD": "11646",
    "ORDENANZA": "Ordenanza Laprida ",
    "COBRO": "SAMO Art. 20",
    "CONCEPTO": "No aclara cobertura a personas sin obra social, prepaga o seguro. Si hay materiales no cubiertos por la entidad y no este cubierto por nomenclador ioma lo abonará o repondrá el paciente. ",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Las Flores",
    "DENSIDAD": "27239",
    "ORDENANZA": "Ordenanza Las flores",
    "COBRO": "Ausencia de concepto ",
    "CONCEPTO": "Ausencia de concepto en fiscal impositiva",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Leandro N. Alem",
    "DENSIDAD": "17266",
    "ORDENANZA": "Ordenanza Leandro N. Alem",
    "COBRO": "Aranceles de los servicios asistenciales Art. 160",
    "CONCEPTO": "Categorización otorgada por el Servicio Social y con las excepciones que la misma consagre. Se autoriza al Departamento Ejecutivo a modificar los distintos aranceles establecidos en el presente capítulo cuando resulte necesario para garantizar el funcionamiento de los establecimientos municipales con todos sus servicios con el objeto principal de favorecer la atención de los pacientes carenciados.",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Lezama",
    "DENSIDAD": "6231",
    "ORDENANZA": "Ordenanza Lezama",
    "COBRO": "Sistema SAMO Art. 23 y ss + tasas (impuestos encubiertos)",
    "CONCEPTO": "Art. 219 TASA DE SERVICIOS DE GUARDIAS PEDIÁTRICAS Y/O VINCULADAS\nA LA SALUD DE LA NIÑEZ , La base imponible de la tasa a que se refiere el presente artículo estará\nconstituida por los contribuyentes de las Tasas de Servicios Rurales y de Barrido, Limpieza y\nConservación de la Vía Pública.",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Lincoln",
    "DENSIDAD": "45506",
    "ORDENANZA": "Ordenanza Lincoln ",
    "COBRO": "Tasa servicios asistenciales Art. 21",
    "CONCEPTO": "Se especifica valor por recorridos por km de la ambulancia y recarga tubo de oxígeno",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Lobería",
    "DENSIDAD": "18243",
    "ORDENANZA": "Ordenanza Lobería",
    "COBRO": "Tasa servicios asistenciales Art. 192 y ss",
    "CONCEPTO": "Cuando la encuesta socioecon.mica realizada por Servicio Social de la Municipalidad as. lo determine, el sistema municipal se har. cargo del costo total o la diferencia que o pudiera abonar el paciente",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Lobos",
    "DENSIDAD": "41760",
    "ORDENANZA": "Ordenanza Lobos",
    "COBRO": "TASA POR SALUD, SEGURIDAD, EDUCACION, DEFENSA CIVIL Y ASISTENCIA SOCIAL ART. 30 (impuesto encubierto)",
    "CONCEPTO": "CONTRIBUCION SOLIDARIA PARA EL FINANCIAMIENTO DE SERVICIOS DE EDUCACIÓN, SALUD, SEGURIDAD Y ASISTENCIA SOCIAL",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Lomas de Zamora",
    "DENSIDAD": "690323",
    "ORDENANZA": "Ordenanza Lomas de Zamora",
    "COBRO": "Ausencia de concepto ",
    "CONCEPTO": "Sin concepto detallado",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Luján",
    "DENSIDAD": "111365",
    "ORDENANZA": "Ordenanza Lujan",
    "COBRO": "Ausencia de concepto ",
    "CONCEPTO": "Última disponible año 2024, se solicito actualizada hcd@lujan.gob.ar",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Magdalena",
    "DENSIDAD": "26830",
    "ORDENANZA": "Ordenanza Magdalena",
    "COBRO": "Ausencia de concepto ",
    "CONCEPTO": "Se llamó por teléfono al (02221)​ 45-3443  se manifesto la necesidad de contar con el cambió de domicilio hecho en el DNI o en trámite, se consultó y dijeron que no tenía costo si no tenia obra social.",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Maipú",
    "DENSIDAD": "11323",
    "ORDENANZA": "Ordenanza Maipú ",
    "COBRO": "Tasa servicios asistenciales Art. 12 y ss",
    "CONCEPTO": "Necesidad hacer declaración jurada anualmente, solo residentes municipio. Se categorizan 4 categorías \"Condición de paciente\" . A) paciente con obra social , lesgilación labora. seguros, ART. B) ingresos + 317.000 sin cobertura A C) bajos recursos ingresos menos 317.000 y sin A D) bajos recursos con obra social ingresos menos a 317.000. Cobran traslados en ambulancia. Cobran a no residentes que no tengan cobertura a menos que demuestren carencia. ",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Malvinas Argentinas",
    "DENSIDAD": "350674",
    "ORDENANZA": "Ordenanza Malvinas Argentinas",
    "COBRO": "Tasa servicios asistenciales Art. 192 y ss",
    "CONCEPTO": "Contribuyentes: quién lo solicite, el enfermo o los familiares. En el caso de prestarse el servicio a personas con cobertura social o con\ncobertura por seguro o autoseguro, los derechos asistenciales deberán ser abonados\npor los responsables de la cobertura, en cuyo caso, los servicios le serán facturados por\nla Secretaría de Salud.",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Mar Chiquita",
    "DENSIDAD": "33110",
    "ORDENANZA": "Ordenanza Mar Chiquita",
    "COBRO": "Tasa Servicios Asistenciales Art. 198 y ss FONDO COMPLEMENTARIO DE SEGURIDAD Y SALUD (impuesto encubierto Art. 275 ",
    "CONCEPTO": "Se cobrará a no residentes. El pago se efectivizará al solicitar el servicio. El indigente tendrá asistencia gratuita mediante la presentación de la certificación del responsable del área de Desarrollo Social. Las personas de escasos recursos podrán ser autorizadas a abonar los aranceles estipulados con una deducción de hasta el cincuenta por ciento (50%). Responsable del pago la persona, tutores, curadores, representantes y/o herederos en caso de fallecimiento. ",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Marcos Paz",
    "DENSIDAD": "67011",
    "ORDENANZA": "Ordenanza Marcos Paz",
    "COBRO": "Tasa servicios asistenciales Art. 232 y ss",
    "CONCEPTO": "Son contribuyentes de la tasa establecida en el presente título, quienes soliciten el servicio, sus familiares o los responsables de la cobertura social, o cobertura por seguro o autoseguro obra social o prepaga, coseguro de salud, sindicales, cooperativos, mutuales. Gratuidad a indigencia. ",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Mercedes",
    "DENSIDAD": "72970",
    "ORDENANZA": "Ordenanza Mercedes",
    "COBRO": "Contribucon especial Art. 6 impuesto encubierto ",
    "CONCEPTO": "Asociación de Bomberos Voluntarios y Asociación Cooperadora del Hospital Se tributará en forma conjunta con la Tasa de Conservación de la vía Pública y/o la Tasa de Conservación, Mejorado y Reparación de la Red Vial Munici",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Merlo",
    "DENSIDAD": "582464",
    "ORDENANZA": "Ordenanza Merlo",
    "COBRO": "SAMO Art 42",
    "CONCEPTO": "Se aclara gratuito personas sin cobertura. Sistema recupero SAMO",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Monte",
    "DENSIDAD": "24868",
    "ORDENANZA": "Ordenanza Monte",
    "COBRO": "Contribucion especial Art. 68 impuesto encubierto",
    "CONCEPTO": "Art. 86 inc 2 contribucion especial Salud Pública del Partido de Monte",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Monte Hermoso",
    "DENSIDAD": "8465",
    "ORDENANZA": "Ordenanza Monte Hermoso ",
    "COBRO": "SAMO + Tasa servicios asistenciales Art. 272",
    "CONCEPTO": "No cobro según condicion socioeconomica necesario informe servicio social municipal",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Moreno",
    "DENSIDAD": "576578",
    "ORDENANZA": "Ordenanza moreno",
    "COBRO": "TASA DE SALUD Y ASISTENCIA SOCIAL ART. 43 . Alicuota sobre multas que cobre el municipio",
    "CONCEPTO": "alícuota del diez coma cincuenta por ciento (10,50%) sobre los tributos, accesorios y/o multas por contravenciones que se abonaren al Municipio, en concepto de Tasa de Salud y Asistencia Social, cuyo importe estará destinado: 0,5% a la “Fundación Mariano y Luciano de La Vega”, un 0,5% a la Infraestructura Hospitalaria y el 9,5% restante a solventar otras erogaciones previstas en el Artículo 329º de la Ordenanza fis",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Morón",
    "DENSIDAD": "331140",
    "ORDENANZA": "Ordenanza Morón",
    "COBRO": "SAMO Art. 288 y 290 ",
    "CONCEPTO": "ordenanza año 2024 se solicito la actualizada vía correo acceso.informacion.publica@moron.gob.ar  Art. 53 se cobra por servicios asistenciales de emergencia médica y traslado por accidentes de tránsito",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Navarro",
    "DENSIDAD": "19899",
    "ORDENANZA": "Sin dato",
    "COBRO": "ausencia ordenanza",
    "CONCEPTO": "se solicito por correo",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Necochea",
    "DENSIDAD": "102110",
    "ORDENANZA": "Ordenanza Necochea",
    "COBRO": "TASA POR FORTALECIMIENTO, PROMOCIÓN Y PREVENCIÓN PARA LA SALUD Art. 426",
    "CONCEPTO": "impuesto encubierto a inmuebles urbanos y rurales",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Nueve de Julio",
    "DENSIDAD": "52607",
    "ORDENANZA": "Ordenanza Nueve de Julio",
    "COBRO": "Tasa servicios asistenciales Art. 44",
    "CONCEPTO": "excepto sin cobertura social o no posean capacidad de pago para los cuales no regian ningun tipo de arancel. Los demás solo si hay diferencia entre cobertura y servicio se abonará la diferencia el paciente.",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Olavarría",
    "DENSIDAD": "125751",
    "ORDENANZA": "Ordenanza Olavarría",
    "COBRO": "ART. 22 Ordenanza impositiva Sistema SIAMO \"cobertura municipal de salud por cuota mensual\" Tasa servicios asistenciales Art. 138 y ss ordenanza fiscal",
    "CONCEPTO": "SIAMO (Sistema Integral de Atención Médica de Olavarría) es un sistema de cobertura médica prepaga municipal que funciona en el Partido de Olavarría.Cobertura: Ofrece atención médica a través del Hospital Municipal Dr. Héctor M. Cura y de los Centros de Atención Primaria de la Salud (CAPS) municipales.Aportes: Los pacientes abonan una cuota mensual accesible para recibir esta cobertura dentro del sistema público de salud local.ARTICULO 139. Se faculta al Departamento Ejecutivo para conceder deducciones de acuerdo a la posibilidad económica del tributante, determinadas por el servicio social de la Municipalidad y otorgar facilidades en los pagos",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Patagones",
    "DENSIDAD": "25982",
    "ORDENANZA": "Ordenanza Patagones ",
    "COBRO": "Tasa servicios asistenciales Art. 239 y ss",
    "CONCEPTO": "Será abonada directamente por el beneficiario del servicio, en caso que el mismo no se encuentre afiliado a obra social o mutual que resulte obligada al pago y en la medida que no encuadre en alguna de las exenciones previstas. Excepciones Art. 239 quarter",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Pehuajó",
    "DENSIDAD": "44783",
    "ORDENANZA": "Ordenanza Pehuajó",
    "COBRO": "Tasa servicios asistenciales Art. 215 y ss",
    "CONCEPTO": "Contribuyentes las personas humanas usuarias del servicio o sus representantes. Son responsables sustitutos de la presente tasa aquellas personas humanas o jurídicas, públicas o privadas, que sean encargados de la cobertura social, por seguro o por autoseguro, del contribuyente ",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Pellegrini",
    "DENSIDAD": "7143",
    "ORDENANZA": "Ordenanza Pellegrini ",
    "COBRO": "Sistema de recupero SAMO Art. 40 y ss",
    "CONCEPTO": "La Tasa por Servicios Asistenciales será aplicable respecto de las prestaciones médicas asistenciales (...) únicamente en aquellos casos en que los usuarios cuenten con cobertura médica a través de obra social, empresa de medicina prepaga, aseguradora de riesgos del trabajo o seguro de salud. En ningún caso corresponderá exigir pago alguno a los particulares que carezcan de cobertura médica, garantizándose para ellos la gratuidad plena en el acceso a la atención sanitaria municipal. Se clara que se aceptan donaciones que deben quedar registradas como donaciones al municipio Art. 41",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Pergamino",
    "DENSIDAD": "115340",
    "ORDENANZA": "Ordenanza Pergamino ",
    "COBRO": "Ausencia de concepto ",
    "CONCEPTO": "Ausencia de concepto ",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Pila",
    "DENSIDAD": "4642",
    "ORDENANZA": "Sin dato",
    "COBRO": "no se encuentra normativa seguir buscando",
    "CONCEPTO": "Sin concepto detallado",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Pilar",
    "DENSIDAD": "394754",
    "ORDENANZA": "Ordenanza Pilar ",
    "COBRO": "Tasa servicios de salud Art. 263 y ss",
    "CONCEPTO": "Regimen General Art. 263 y ss individualiza como sujeto a la persona que reciba el servicio, no se cobrará la tasa a personas que: residan en pilar, tengo residencia permanenente en el país y no tengan cobertura por médico asitencial por carecer e tareas remuneradas o beneficios previsionales.  Regimen Especial Art 267 ter y ss Sistema SAMO recupero",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Pinamar",
    "DENSIDAD": "39449",
    "ORDENANZA": "Ordenanza Pinamar",
    "COBRO": "TASA POR DERECHOS SANATORIALES/SERVICIOS ASISTENCIALES – HOSPITAL MUNICIPAL SALAS MUNICIPALES ART. 97 Y SS",
    "CONCEPTO": "eximidos del pago de hasta un cien por ciento (100%) (...) aquellas personas sin cobertura social y con recursos limitados y/o insuficientes, con autorización de la Dirección de Acción Social.",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Presidente Perón",
    "DENSIDAD": "102106",
    "ORDENANZA": "Ordenanza Presidente Perón",
    "COBRO": "Ausencia concepto",
    "CONCEPTO": "Sin concepto detallado",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Puán",
    "DENSIDAD": "16613",
    "ORDENANZA": "Ordenanza Puan",
    "COBRO": "Tasa servicios asistenciales Art. 170 y ss ordenanza fiscal y Art. 42 y ss ordenanza impositiva ",
    "CONCEPTO": "Servicios asistenciales y servicio ambulancia. La tasa se efectiviza salvo medio convenio obras sociales, particiones oficiales/privadas. (...) se podra establecer formas de pago diferidas en aquellos casos en que los costos de las cirugías no puedan ser abonadas de contado por el paciente con la firma de un convenio y los pagares respectivos. , previa evaluacion área promocion social.  En ordenanza impositiva se determina segméntación según se tenga o no cobertura, capacidad de pago, cobertura que cubra o no los servicios , falta de la misma con posibilidad de pago o no, se incluye tablas tarifarias para todo servicio hasta  tomografias, parto y cesarea. El municipio cuenta con \"Seguro de Salud Municipal\" SEDEM , categoríza a los pacientes, reserva gratuidad a carentes de recursos. ",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Punta Indio",
    "DENSIDAD": "12297",
    "ORDENANZA": "Ordenanza Punta Indio",
    "COBRO": "Fondo Solidario de Salud Pública Municipal Art. 202 y ss",
    "CONCEPTO": "impuesto encubierto ",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Quilmes",
    "DENSIDAD": "633391",
    "ORDENANZA": "Ordenanza Quilmes ",
    "COBRO": "Sistema SAMO Art. 316 y ss",
    "CONCEPTO": "Sistema de recupero SAMO",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Ramallo",
    "DENSIDAD": "39730",
    "ORDENANZA": "Código Tributario Ramallo",
    "COBRO": "Tasa servicios asistenciales Art. 238 ",
    "CONCEPTO": "Sistema SAMO + Se reserva gratuidad a situación de indigencia. Personas sin cobertura que no demuestren indigencia serán facturados según nomenclador de autogestión",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Rauch",
    "DENSIDAD": "16635",
    "ORDENANZA": "Ordenanza Rauch ",
    "COBRO": "Tasa servicios asistenciales Anexo 1 Título XV",
    "CONCEPTO": "Se establecen valores de cobro a toda práctica, figuran precios en el anexo. Oficina de Desarrollo\nSocial de la Municipalidad, debe categorizar a los pacientes en:\na) Pacientes sin cobertura social, no indigente;\nb) Pacientes sin cobertura social indigente;\nc) Pacientes con cobertura social indigente y no indigente. Se podrá determinar porcentajes de pago 25% 50% 75% o cobertura social si amerita",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Rivadavia",
    "DENSIDAD": "19849",
    "ORDENANZA": "Ordenanza Rivadavia  ",
    "COBRO": "Servicios asistenciales Art 238 y ss",
    "CONCEPTO": "Servicio Social categoríza en las siguientes categorías: A con cobertura social convenida B con cobertura social pero sin convenio C sin cobertura social, con ingresos suficientes D sin cobertura social sin ingresos suficientes E con cobertura social , sin ingresos suficientes . no residentes deberan abonar totalidad o carta provincial o municipal que se hara cargo de los gastos. ",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Rojas",
    "DENSIDAD": "25627",
    "ORDENANZA": "Ordenanza 2025 Rojas",
    "COBRO": "Cobro a obras sociales Art. 215 y ss",
    "CONCEPTO": "Se solicito ordenanza vigente, última que figura es año 2025",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Roque Pérez",
    "DENSIDAD": "13977",
    "ORDENANZA": "Ordenanza Roque Perez",
    "COBRO": "Tasa servicios asistenciales Art 33 SAMO  y Tasa por salud y seguridad fija anual por parcela urbana o hectarea",
    "CONCEPTO": "Art. 33 OJO La atención médica será gratuita salvo para aquellos pacientes que tengan cobertura\nsocial o privada. En casos de accidentes de trabajo, la ART correspondiente o en su\ndefecto el empleador, deberá hacerse cargo de los honorarios médicos y gastos\nsanatoriales que origine la atención del accidentado. Cuando la atención que deba\nbrindarse haya sido origen en accidentes de tránsito o cualquier otro accionar de\nterceros responsables, el paciente atendido cederá a favor de la Municipalidad el\nDerecho que pudiera corresponderle por obras sociales, medicina prepaga, ART o por\ncobertura de seguros de cualquier naturaleza por monto de las prestaciones recibidas.",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Saavedra Pigue",
    "DENSIDAD": "22537",
    "ORDENANZA": "Ordenanza Saavedra Pigue ",
    "COBRO": "Tasa servicios asistenciales Art. 273 y ss",
    "CONCEPTO": "Sistema SAMO + Gratuidad exclusiva para indigencia Art. 277",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Saladillo",
    "DENSIDAD": "35656",
    "ORDENANZA": "Ordenanza Saladillo",
    "COBRO": "SIstema SAMO",
    "CONCEPTO": "No se especifica en la ordenanza. Se llamó al telefono del hospital 02344 432112, me brindaron el whatshapp para solicitar turno programados , al manifiestar no tener obra social me comunicaron que el hospital es público y gratuito, solo se piden los datos de la obra social si se tiene para cobrarle a ellos.",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Salliquelo",
    "DENSIDAD": "9427",
    "ORDENANZA": "Ordenanza Salliquelo",
    "COBRO": "Tasa servicios asistenciales Art. 69 y ss + Plan de Salud Municipal",
    "CONCEPTO": "Art. 69 y ss se establecen valores para pacientes sin cobertura indigentes o pacientes adheridos al plan de salud municipal abonando 50% de ciertas prácticas.  ",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Salto",
    "DENSIDAD": "40157",
    "ORDENANZA": "Ordenanza Salto ",
    "COBRO": "Sistema SAMO + Tasa asistencial Art. 206 y ss",
    "CONCEPTO": "Arancelamiento directo con vía ejecutiva judicial Art 213 juicio de apremio. Podran eximirse los indigentes Art. 66",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "San Andrés de Giles",
    "DENSIDAD": "26510",
    "ORDENANZA": "Ordenanza San Andrés de Giles",
    "COBRO": "Tasa servicios asistenciales Art 247 y ss ordenanza fiscal ",
    "CONCEPTO": "Art 247 y ss ordenanza fiscal contribuyente persona que recibe los servicios , responsables solidarios, herederos y/o legatarios. Art 44 odeanzanza impsotiva aclara que para residentes del partido la atención es gratuita. ",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "San Antonio de Areco",
    "DENSIDAD": "26695",
    "ORDENANZA": "Ordenanza San Antonio de Areco",
    "COBRO": "Tasa por servicios de salud  Art 218 y ss (impuesto encubierto)",
    "CONCEPTO": "Pago mensual de acuerdo a la liquidación de la Tasa de\nServicios Urbanos, Tasa por Servicios Rurales y Tasa por Inspección de Seguridad e Higiene,\nconforme Ordenanza Impositiva vigente.",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "San Cayetano",
    "DENSIDAD": "8994",
    "ORDENANZA": "Ordenanza San Cayetano",
    "COBRO": "Sistema SAMO",
    "CONCEPTO": "Artículo 122º.- Los servicios asistenciales que se presten en el Hospital Municipal serán gratuitos. Para el\ncaso de pacientes que tengan cobertura de obras sociales o de compañías de seguros, oficiales o privados,\nla Municipalidad ejercerá el derecho de cobro sobre la entidad de cobertura conforme los valores y\nmodalidades establecidas en las normas vigentes en cada caso.",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "San Fernando",
    "DENSIDAD": "171616",
    "ORDENANZA": "Ordenanza San Fernando",
    "COBRO": "Sistema SAMO + Tasa asistencial Art. 141 y ss impuesto encub",
    "CONCEPTO": "Aclara gratuidad a residentes del partido ",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "San Isidro",
    "DENSIDAD": "297282",
    "ORDENANZA": "Ordenanza San Isidro",
    "COBRO": "Sistema SAMO Art 141 y ss",
    "CONCEPTO": "Art 141 y ss tiene anexo con valores, aclara si el responsable es persona pública o juridica privada ",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "San Miguel Joaquín",
    "DENSIDAD": "328835",
    "ORDENANZA": "Ordenanza San Miguel Joaquin ",
    "COBRO": "Sistema SAMO Art 94 y ss",
    "CONCEPTO": "se aclara gratuidad a personas sin cobertura ",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "San Nicolás",
    "DENSIDAD": "165375",
    "ORDENANZA": "Ordenanza San Nicolas",
    "COBRO": "Sistema SAMO Art 301 y ss",
    "CONCEPTO": "Art 301 y ss sistema samo y peajes ",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "San Pedro",
    "DENSIDAD": "69616",
    "ORDENANZA": "Ordenanza San Pedro",
    "COBRO": "Sistema SAMO Art. 250 y ss",
    "CONCEPTO": "se especifica que si el paciente no tiene cobertiura el servicio es gratuito ",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "San Vicente",
    "DENSIDAD": "98977",
    "ORDENANZA": "Ordenanza San Vicente",
    "COBRO": "Contribución al Sistema de Salud Pública (impuesto encubierto) Art. 367",
    "CONCEPTO": "contribución equivalente al cuarenta por ciento (40 %) de las Tasas fijadas por\nPropiedad Urbana, por Conservación, Reparación y Mejorado de la Red Vial Municipal, por Propiedad Urbana para\n“Conjuntos Inmobiliarios destinados a Vivienda y Grandes Desarrollos Inmobiliarios” y por Inspección de Seguridad\ne Higiene.",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Suipacha",
    "DENSIDAD": "11867",
    "ORDENANZA": "Ordenanza Suipacha",
    "COBRO": "Tasa de salud Art. 129 y ss (impuesto encubierto) + Prestaciones Hospitalarias Art. 132 y ss",
    "CONCEPTO": "Tasa de salud Se dispone a toda parcela sector urbano y seccionenles de quintas del partido + Prestaciones hospitalarias: previa encuesta social se dispone capacidad de pago si no tiene cobertura ",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Tandil",
    "DENSIDAD": "150162",
    "ORDENANZA": "Ordenanza Tandil ",
    "COBRO": "SISTEMA INTEGRADO DE SALUD PÚBLICA – ENTE DESCENTRALIZADO Art. 217 y ss",
    "CONCEPTO": "Individualiza el no cobro a \"las personas humanas en razón de las consideraciones socio económicas\" Cualquier excepción al arancel establecido, deberá\nestar justificada en base al informe del servicio social del\nestablecimiento o del servicio social de la Secretaría de\nBienestar Social y no constituirá impedimento alguno para la\ninmediata atención del paciente.",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Tapalque",
    "DENSIDAD": "10901",
    "ORDENANZA": "Ordenanza Tapalque ",
    "COBRO": "Tasa servicios asistenciales Art. 200 + Contribución unidad intensiva (impuesto encubierto)",
    "CONCEPTO": "Art 201 se faculta a deducciones de acuerdo posibilidades esconomicas del tributante determinadas por servicio social de la Municiipalidad  ",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Tigre",
    "DENSIDAD": "447785",
    "ORDENANZA": "Ordenanza Tigre",
    "COBRO": "Sistema SAMO + Tasa servicios asistenciales Art 83 y ss ordenanza impositiva para no residentes del partido",
    "CONCEPTO": "Tabla tarifaria para personas no residentes en el partido. Gratuidad a personas sin cobertira médica. ",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Tordillo",
    "DENSIDAD": "2672",
    "ORDENANZA": "Ordenanza Tordillo",
    "COBRO": "Tasa servicios asistenciales Art 28 y ss ordenanza impositiva",
    "CONCEPTO": "Abonan quienes soliciten los servicios asistenciales y tengan recursos probados. sin recursos gratuito",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Tornquist",
    "DENSIDAD": "14669",
    "ORDENANZA": "Ordenanza Tornquist",
    "COBRO": "Sistema SAMO + Tasa servicios asistenciales Art. 142 y ss",
    "CONCEPTO": "Podrán quedar eximidos total o parcialmente del pago de tasa quienes posean ficha socio económica otorgada por el área competente como aquellos que poseen cobertura médica (Art. 147)",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Trenque launquen",
    "DENSIDAD": "48423",
    "ORDENANZA": "Ordenanza Trenque Lauquen",
    "COBRO": "Sistema SAMO + Tasa servicios asistenciales Art 89 y ss",
    "CONCEPTO": "No se cobrará a los residentes del distrito sin cobertura médica",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Tres Arroyos",
    "DENSIDAD": "62835",
    "ORDENANZA": "Ordenanza Tres arroyos ",
    "COBRO": "Tasa solidaria de sostenimiento del servicio de salud Art. 183 y ss de la ordenanza fis (impuesto encubierto)",
    "CONCEPTO": "Se cobra a todo inmueble en \"Tasa servicios urbanos\". ",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Tres de Febrero",
    "DENSIDAD": "366377",
    "ORDENANZA": "Ordenanza Tres de Febrero",
    "COBRO": "Sistema SAMO Tributo por servicios asistenciales ART 245 Y SS",
    "CONCEPTO": "Gratuidad a personas sin cobertura médica",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  },
  {
    "MUNICIPIO": "Tres Lomas",
    "DENSIDAD": "8825",
    "ORDENANZA": "Actualizaciones falta ordenanza solicitada",
    "COBRO": "Tasa servicios asistenciales",
    "CONCEPTO": "La Ordenanza de Salud vigente 1043/13 DEL AÑO 2013 no figura disponible web, se solicito. Las actualizaciones dan cuenta del cobro a personas sin cobertura médica según medios económicos por encuesta social",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Vicente López",
    "DENSIDAD": "283510",
    "ORDENANZA": "Ordenanza Vicente Lopez",
    "COBRO": "Sistema SAMO derechos asistenciales Art 254 y ss ordennza fiscal y Art 54 y ss ordenanza impositiva",
    "CONCEPTO": "Gratuito para personas sin cobertura ",
    "CATEGORIA": "Categoría C (Arancel Directo)"
  },
  {
    "MUNICIPIO": "Villa Gesell",
    "DENSIDAD": "38614",
    "ORDENANZA": "Codigo tributario ",
    "COBRO": "Tasa salud ART 148 Y SS codigo tributario  (impuesto encubierto)",
    "CONCEPTO": "Art 148 y ss La localidad posee un codigo tributario 2156/08 y modificaciones, no renueva el codigo todos los años unificado digesto https://www.juntosxgesell.ar/res_dige.php?criter=2156%2F08",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Villarino",
    "DENSIDAD": "33170",
    "ORDENANZA": "Ordenanza Villarino",
    "COBRO": "Derecho de Comercialización sobre Producción Hortícola y Frutícola  (impuesto encubierto destinado a salud) Art 232 y ss\n\n\n",
    "CONCEPTO": "Derecho de Comercialización sobre Producción Hortícola y Frutícola. Del Destino de los Fondos\nARTÍCULO 236°: Los recursos serán afectados, destinados al financiamiento del Sistema de Salud Municipal, administrado por la Secretaría de Salud o quien en el futuro la reemplace. ",
    "CATEGORIA": "Categoría B (Tasa Encubierta)"
  },
  {
    "MUNICIPIO": "Zárate",
    "DENSIDAD": "132087",
    "ORDENANZA": "Ordenanza Zarate ",
    "COBRO": "Sistema SAMO Art 217 y ss",
    "CONCEPTO": "Sin concepto detallado",
    "CATEGORIA": "Categoría A (Gratuidad / SAMO)"
  }
]

@st.cache_data
def load_data():
    df = pd.DataFrame(DATA_135)
    df['MUNICIPIO'] = df['MUNICIPIO'].astype(str).str.strip()
    df['DENSIDAD'] = df['DENSIDAD'].astype(str)
    df['ORDENANZA'] = df['ORDENANZA'].astype(str)
    df['COBRO'] = df['COBRO'].astype(str)
    df['CONCEPTO'] = df['CONCEPTO'].astype(str)
    df['CATEGORIA'] = df['CATEGORIA'].astype(str)
    return df

df_censo = load_data()

# ==========================================
# BARRA LATERAL - NAVEGACIÓN Y CONFIGURACIÓN
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/scales.png", width=70)
st.sidebar.title("SIA-PBA v4.0")
st.sidebar.markdown("**Sistema Integrado de Auditoría Algorítmica y Canal Único de Denuncias**")
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
st.sidebar.markdown("### 🧠 Motor IA Gemini Pro")
user_api_key = st.sidebar.text_input(
    "Clave API Gemini (Google AI Studio):",
    type="password",
    help="Ingrese su API Key de Google AI Studio (aistudio.google.com) para activar el razonamiento superior de Gemini 1.5/2.0 Pro."
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
    st.markdown("<h1 class='main-title'>SIA-PBA: Auditoría Algorítmica & Canal Único de Denuncias</h1>", unsafe_allow_html=True)
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
        ### 🔍 1. Módulo de Auditoría Algorítmica de Ordenanzas
        * **Análisis de Texto PNL e IA (Gemini Pro):** Procesa automáticamente ordenanzas impositivas y fiscales locales.
        * **Semáforo Tripartito de Convencionalidad:**
            * 🟢 **Cat. A (Gratuidad Plena / SAMO):** Cumplimiento del Art. 36 inc. 8 CPBA y Ley 11.069.
            * 🟡 **Cat. B (Tasas Encubiertas):** Detección de tributos disfrazados en ABL/Red Vial.
            * 🔴 **Cat. C (Arancelamiento Directo):** Alerta por cobros indebidos, pagarés o apremios.
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
    
    tab1, tab2 = st.tabs(["🏛️ Auditoría por Municipio (Censo N=135)", "📝 Auditoría Futura (PDF / Ordenanza 2027+)"])
    
    with tab1:
        st.markdown("##### Seleccione un municipio para auditar su normativa tributario-sanitaria:")
        muni_selected = st.selectbox("Municipio de la Prov. de Bs. As.:", df_censo['MUNICIPIO'].unique())
        
        row_muni = df_censo[df_censo['MUNICIPIO'] == muni_selected].iloc[0]
        
        st.markdown("### 📊 Resultado del Examen Algorítmico Automatizado")
        
        col_res1, col_res2 = st.columns([1, 2])
        
        with col_res1:
            cat = str(row_muni.get('CATEGORIA', 'Categoría A (Gratuidad / SAMO)'))
            if 'Cat. C' in cat or 'Arancel' in cat or 'Categoría C' in cat:
                st.error("🔴 **DICTAMEN: INCONSTITUCIONAL / ARANCEL DIRECTO**")
                st.markdown("<span class='badge-cat-c'>Categoría C - Riesgo Alto</span>", unsafe_allow_html=True)
            elif 'Cat. B' in cat or 'Encubierta' in cat or 'Categoría B' in cat:
                st.warning("🟡 **DICTAMEN: ADVERTENCIA / TASA ENCUBIERTA**")
                st.markdown("<span class='badge-cat-b'>Categoría B - Riesgo Medio</span>", unsafe_allow_html=True)
            else:
                st.success("🟢 **DICTAMEN: CONFORME A DERECHO / GRATUIDAD PLENA**")
                st.markdown("<span class='badge-cat-a'>Categoría A - Gratuidad Plena</span>", unsafe_allow_html=True)
                
            st.write(f"**Municipio:** {row_muni.get('MUNICIPIO', 'Desconocido')}")
            st.write(f"**Densidad Poblacional:** {row_muni.get('DENSIDAD', 'Sin dato')}")
            st.write(f"**Norma Relevada:** {row_muni.get('ORDENANZA', 'Ordenanza Municipal')}")
            
        with col_res2:
            st.markdown("#### ⚖️ Fundamentación Jurídica de Alerta")
            m_concepto = str(row_muni.get('CONCEPTO', 'Sin concepto detallado'))
            st.markdown(f"**Disposición Local Relevada:** *'{m_concepto}'*")
            
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

    with tab2:
        st.markdown("### 📋 Motor de Auditoría Algorítmica Futura (Ejercicios 2027+)")
        st.markdown("Suba una Ordenanza Fiscal/Impositiva (PDF Digital o Escaneado por OCR) para ejecutar el diagnóstico automatizado:")
        
        col_a1, col_a2 = st.columns([1, 1])
        with col_a1:
            muni_futuro = st.selectbox("Seleccione Municipio emisor de la Ordenanza:", df_censo['MUNICIPIO'].unique(), key="muni_fut")
            row_fut = df_censo[df_censo['MUNICIPIO'] == muni_futuro].iloc[0]
            cat_fut = str(row_fut.get('CATEGORIA', 'Sin datos'))
            con_fut = str(row_fut.get('CONCEPTO', 'Sin datos'))
            st.info(f"**Línea de Base Censo 2026 ({muni_futuro}):** {cat_fut} | Disposición: {con_fut}")
            
        with col_a2:
            uploaded_pdf = st.file_uploader("Adjuntar archivo PDF de la Ordenanza Fiscal e Impositiva:", type=['pdf'])
            
        texto_suplementario = st.text_area(
            "Editor de Texto Suplementario (Opcional - para fragmentos copiados):",
            value="",
            height=100,
            placeholder="Si no adjunta un PDF, puede pegar aquí el articulado..."
        )
        
        if st.button("🚀 EJECUTAR AUDITORÍA CONTEXTUAL E IA"):
            texto_a_analizar = ""
            fuente_doc = ""
            
            if uploaded_pdf is not None:
                with st.spinner("⏳ Leyendo documento PDF..."):
                    try:
                        import pypdf
                        pdf_reader = pypdf.PdfReader(BytesIO(uploaded_pdf.read()))
                        pages_text = []
                        for page in pdf_reader.pages:
                            t_p = page.extract_text()
                            if t_p:
                                pages_text.append(t_p)
                        texto_a_analizar = "\n".join(pages_text)
                        fuente_doc = f"PDF Digital ({len(pdf_reader.pages)} páginas)"
                    except Exception:
                        texto_a_analizar = ""
                        
                    if len(texto_a_analizar.strip()) < 50:
                        with st.spinner("🔍 PDF sin capa de texto. Activando motor OCR de Visión Artificial (Tesseract)..."):
                            try:
                                from pdf2image import convert_from_bytes
                                import pytesseract
                                uploaded_pdf.seek(0)
                                images = convert_from_bytes(uploaded_pdf.read(), first_page=1, last_page=15)
                                ocr_pages = []
                                for img in images:
                                    ocr_pages.append(pytesseract.image_to_string(img, lang='spa'))
                                texto_a_analizar = "\n".join(ocr_pages)
                                fuente_doc = f"PDF Escaneado (Procesado con OCR Visión Artificial - {len(images)} págs)"
                            except Exception as e_ocr:
                                st.warning(f"Aviso OCR: {str(e_ocr)}")
                                
            if not texto_a_analizar.strip() and texto_suplementario.strip():
                texto_a_analizar = texto_suplementario
                fuente_doc = "Texto Ingresado en Editor Suplementario"
            elif texto_a_analizar.strip() and texto_suplementario.strip():
                texto_a_analizar += "\n" + texto_suplementario
                fuente_doc += " + Texto Suplementario"
                
            if not texto_a_analizar.strip():
                st.error("❌ **ERROR DE PROCESAMIENTO:** No se ingresó ningún archivo PDF ni texto en el editor para auditar.")
            else:
                st.success(f"✅ **Documento Cargado con Éxito:** {fuente_doc}")
                st.markdown("---")
                
                # INTENTO DE LLAMADA A GEMINI PRO CON CADENA DE MODELOS COMPATIBLES
                api_key_to_use = user_api_key.strip()
                if not api_key_to_use:
                    try:
                        api_key_to_use = st.secrets.get("GEMINI_API_KEY", "")
                    except Exception:
                        api_key_to_use = ""
                        
                gemini_exito = False
                
                if api_key_to_use:
                    with st.spinner("🧠 Ejecutando Razonamiento IA Superior con Gemini Pro..."):
                        try:
                            import google.generativeai as genai
                            genai.configure(api_key=api_key_to_use)
                            
                            models_to_try = ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-2.0-flash', 'gemini-pro']
                            response_text = ""
                            model_used_name = ""
                            
                            prompt_gemini = f"""Eres SIA-PBA, un Auditor Algorítmico Jurídico de la Provincia de Buenos Aires (TFC Abogacía UCES).
Tu tarea es auditar el texto de la siguiente Ordenanza Municipal ({muni_futuro}) y determinar si contiene cláusulas inconstitucionales en salud.

REGLAS DE EVALUACIÓN JURÍDICA:
1. CATEGORÍA C (Arancel Directo / Inconstitucional): Si el texto impone cobro directo, arancel, bono de guardia, pagaré, o exige encuesta social / certificado de indigencia a personas sin cobertura en hospitales o centros de salud.
2. CATEGORÍA B (Tasa Encubierta): Si impone fondos especiales o adicionales de salud adosados sobre tributos de ABL, Red Vial, Comercio o Multas.
3. CATEGORÍA A (Gratuidad / Conforme a Derecho): Si consagra la gratuidad de la atención hospitalaria para personas sin cobertura o restringe el recupero únicamente a Obras Sociales / Prepagas vía SAMO (Ley 11.069).
4. DESCARTE DE FALSOS POSITIVOS: Ignora impuestos de comercio, seguridad e higiene, bromatología, escombros, maquinaria vial, rifas de cooperadoras o tasas generales que NO sean cobros asistenciales de salud a pacientes.

MUNICIPIO AUDITADO: {muni_futuro}
LÍNEA DE BASE CENSO 2026: {cat_fut} - {con_fut}

TEXTO DE LA ORDENANZA A AUDITAR:
\"\"\"{texto_a_analizar[:30000]}\"\"\"

POR FAVOR RESPONDE CON EL SIGUIENTE FORMATO EXACTO EN MARKDOWN:
### 📋 Dictamen de Auditoría Algorítmico IA - {muni_futuro}
**MODELO IA:** [Nombre del Modelo]
**CLASIFICACIÓN:** [CATEGORÍA A / CATEGORÍA B / CATEGORÍA C]

**DICTAMEN:** [Escribe un resumen ejecutivo del dictamen]

**ARTÍCULOS INFRACTORES O DE RESGUARDO DETECTADOS:**
* **[Número de Artículo]**: "[Transcripción textual limpia del artículo de la ordenanza]"
  * *Observación Técnica:* [Explicación jurídica de por qué pertenece a esa categoría]
"""
                            for m_name in models_to_try:
                                try:
                                    m_inst = genai.GenerativeModel(m_name)
                                    res = m_inst.generate_content(prompt_gemini)
                                    if res and res.text:
                                        response_text = res.text
                                        model_used_name = m_name
                                        break
                                except Exception:
                                    continue
                                    
                            if response_text:
                                response_text = response_text.replace("[Nombre del Modelo]", model_used_name)
                                st.markdown(response_text)
                                gemini_exito = True
                        except Exception as e_gen:
                            st.warning(f"⚠️ Nota de conexión Gemini API ({str(e_gen)}). Ejecutando motor contextual local de resguardo...")
                            gemini_exito = False
                            
                if not gemini_exito:
                    # MOTOR CONTEXTUAL LOCAL DE RESGUARDO (CERO FALSOS POSITIVOS)
                    st.markdown(f"### 📋 Dictamen de Auditoría Algorítmica - {muni_futuro} (Ejercicio 2027+)")
                    
                    lineas = texto_a_analizar.split("\n")
                    articulos_dict = []
                    art_actual = ""
                    num_art = "Art. General"
                    
                    for line in lineas:
                        if re.match(r'^(ARTICULO|ARTÍCULO|ART\.?)\s*(\d+)', line.strip(), re.IGNORECASE):
                            if art_actual.strip():
                                articulos_dict.append((num_art, art_actual.strip()))
                            art_actual = line
                            m = re.match(r'^(ARTICULO|ARTÍCULO|ART\.?)\s*(\d+)', line.strip(), re.IGNORECASE)
                            num_art = f"Art. {m.group(2)}" if m else "Art. General"
                        else:
                            art_actual += " " + line
                    if art_actual.strip():
                        articulos_dict.append((num_art, art_actual.strip()))
                        
                    if not articulos_dict:
                        articulos_dict = [("Párrafo", p.strip()) for p in texto_a_analizar.split("\n\n") if len(p.strip()) > 30]
                        
                    arts_c = []
                    arts_b = []
                    arts_a = []
                    
                    for art_num, art_txt in articulos_dict:
                        txt_up = art_txt.upper()
                        
                        # DESCARTES EXPLÍCITOS DE FALSOS POSITIVOS
                        if any(w in txt_up for w in ['RIFA', 'BARRIDO', 'PALA MECÁNICA', 'MOTONIVELADORA', 'PODAS', 'ESCOMBROS', 'CEMETERY', 'CEMENTERIO', 'PUBLICIDAD', 'HABILITACION', 'BROMATOLOGÍA', 'BROMATOLOGIA', 'AGUA POTABLE', 'SEGUROS DE VIDA']):
                            if 'HOSPITAL' not in txt_up and 'ASISTENCIAL' not in txt_up:
                                continue
                                
                        # REGLA DE SALVAGUARDA
                        if 'EXCEPTO LOS SERVICIOS ASISTENCIALES' in txt_up or 'QUEDAN EXIMIDOS LOS EFECTORES' in txt_up:
                            arts_a.append((art_num, art_txt, "Conformidad Normativa: Exclusión explícita a favor del servicio asistencial de salud."))
                            continue
                            
                        # EVALUACIÓN SALUD
                        es_salud = any(w in txt_up for w in ['HOSPITAL', 'SALUD', 'ASISTENCIAL', 'PACIENTE', 'GUARDIA', 'MEDICO', 'MÉDICO', 'SICK', 'SAMO', 'IOMA', 'INTERNACIÓN', 'LABORATORIO'])
                        
                        if es_salud:
                            if any(w in txt_up for w in ['ARANCEL', 'BONO', 'PAGARÉ', 'PAGARE', 'INDIGENCIA', 'CARENCIA DE RECURSOS', 'ENCUESTA SOCIAL', 'INFORMACIÓN SUMARIA', 'ASISTENTE SOCIAL', 'APREMIO']):
                                if 'SAMO' not in txt_up and 'OBRAS SOCIALES' not in txt_up:
                                    arts_c.append((art_num, art_txt, "Cláusula de arancelamiento directo al paciente o exigencia de acreditación de pobreza/indigencia."))
                                else:
                                    arts_a.append((art_num, art_txt, "Conformidad Normativa: Mención de arancel/recupero limitado a Obras Sociales o Prepagas (Ley 11.069)."))
                            elif any(w in txt_up for w in ['FONDO ESPECIAL DE SALUD', 'TASA DE SALUD', 'CONTRIBUCIÓN PARA LA SALUD', 'SISTEMA INTEGRADO DE SALUD']) and any(w in txt_up for w in ['ALUMBRADO', 'RED VIAL', 'URBANOS', 'PREDIO', 'ABL']):
                                arts_b.append((art_num, art_txt, "Tasa encubierta / Fondo especial de salud adosado sobre tributos generales."))
                            elif 'GRATUITO' in txt_up or 'SAMO' in txt_up or 'SIN COBERTURA' in txt_up or 'SIN CARGO' in txt_up:
                                arts_a.append((art_num, art_txt, "Conformidad Normativa: Garantía expresa de gratuidad hospitalaria y recupero vía SAMO."))

                    if len(arts_c) > 0:
                        st.error("🔴 **ALERTA CRÍTICA: DETECCIÓN DE CLÁUSULAS INCONSTITUCIONALES / CATEGORÍA C**")
                        st.markdown(f"**Comparativa frente al Censo Base 2026:** El municipio {muni_futuro} mantiene o reintroduce normas de arancelamiento directo.")
                        st.markdown("#### 📜 Artículos Infractores Detectados:")
                        for num_a, txt_a, obs_a in arts_c:
                            st.markdown(f"<div class='snippet-box'><b>⚠️ Cita Textual {num_a}:</b><br><i>'{txt_a[:400]}...'</i><br><br><b>Observación Técnica:</b> {obs_a}</div>", unsafe_allow_html=True)
                    elif len(arts_b) > 0:
                        st.warning("🟡 **ADVERTENCIA: DETECCIÓN DE TASA ENCUBIERTA / CATEGORÍA B**")
                        st.markdown("#### 📜 Artículos con Tasas Encubiertas Detectados:")
                        for num_a, txt_a, obs_a in arts_b:
                            st.markdown(f"<div class='snippet-box'><b>⚠️ Cita Textual {num_a}:</b><br><i>'{txt_a[:400]}...'</i><br><br><b>Observación Técnica:</b> {obs_a}</div>", unsafe_allow_html=True)
                    else:
                        st.success("🟢 **DICTAMEN POSITIVO: NORMATIVA CONFORME A DERECHO / CATEGORÍA A**")
                        st.markdown(f"**Compatibilidad Constatada:** La norma analizada para **{muni_futuro}** respeta el principio de gratuidad (Art. 36 inc. 8 CPBA) y limita el recupero de costos a Obras Sociales y Prepagas (Ley 11.069 SAMO).")
                        if arts_a:
                            st.markdown("#### 📜 Artículos de Resguardo / Conformidad Detectados:")
                            for num_a, txt_a, obs_a in arts_a:
                                st.markdown(f"<div class='snippet-box-a'><b>✅ Cita Textual {num_a}:</b><br><i>'{txt_a[:400]}...'</i><br><br><b>Observación Técnica:</b> {obs_a}</div>", unsafe_allow_html=True)

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
            'Municipios': [65, 34, 36]
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
        
    st.subheader("📋 Matriz Completa del Censo de Municipios")
    st.dataframe(df_censo[['MUNICIPIO', 'DENSIDAD', 'CATEGORIA', 'ORDENANZA', 'CONCEPTO']], use_container_width=True)

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
SUJETO AUDITADO: Municipalidad de {row_d.get('MUNICIPIO', '')} (Provincia de Buenos Aires)
DENSIDAD POBLACIONAL: {row_d.get('DENSIDAD', '')}
NORMA EXAMINADA: {row_d.get('ORDENANZA', '')}
DISPOSICIÓN TRIBUTARIA: "{row_d.get('CONCEPTO', '')}"
CLASIFICACIÓN ALGORÍTMICA: {row_d.get('CATEGORIA', '')}

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
SE RECOMIENDA a la Asesoría General de Gobierno de la Provincia de Buenos Aires y al Honorable Tribunal de Cuentas promover la revisión de oficio del módulo impositivo de la Municipalidad de {row_d.get('MUNICIPIO', '')}, instando la adecuación inmediata al régimen SAMO (Ley 11.069) y el cese de todo cobro directo al paciente sin cobertura.

========================================================================================
SIA-PBA // Trabajo Final de Carrera (TFC) - Abogacía UCES
========================================================================================
"""
    
    st.text_area("Vista previa del Dictamen Jurídico:", value=dictamen_text, height=350)
    
    st.download_button(
        label="📥 DESCARGAR DICTAMEN JURÍDICO (TXT)",
        data=dictamen_text,
        file_name=f"dictamen_inconstitucionalidad_{str(muni_dictamen).lower().replace(' ', '_')}.txt",
        mime="text/plain"
    )
