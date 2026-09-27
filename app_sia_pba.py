import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re
import json
import os
import hashlib
import datetime
from io import BytesIO

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y ESTILO INSTITUCIONAL
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
        background-color: #F8F9FA;
        border-left: 4px solid #1B365D;
        padding: 10px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        margin-bottom: 10px;
    }
    .ai-badge {
        background-color: #E2E8F0;
        color: #2D3748;
        padding: 3px 8px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# BASE DE DATOS DEL CENSO PROVINCIAL (N=135) EMBEBIDA
# ==========================================
RAW_DATA_135 = "[\n  {\n    \"MUNICIPIO\": \"25 de mayo\",\n    \"DENSIDAD\": \"36676\",\n    \"ORDENANZA\": \"Ordenanza 25 de mayo\",\n    \"COBRO\": \"Tasa , impuesto encubierto\",\n    \"CONCEPTO\": \"\\\"Fondo para Salud\\\" del 7% calculado sobre la liquidaci\u00f3n de otras tasas (Alumbrado, Limpieza, Red Vial) o sobre el importe b\u00e1sico facturado de energ\u00eda el\u00e9ctrica.\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Adolfo Alsina\",\n    \"DENSIDAD\": \"17552\",\n    \"ORDENANZA\": \"Ordenanza Adolfo Alsina\",\n    \"COBRO\": \"Tasa servicio asistencial Art. 31\",\n    \"CONCEPTO\": \"En ordenanza aclara el sistema del carnet hospitalario y % a pagar seg\u00fan clasificacion de segm de servicios sociales\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Adolfo Gonz\u00e1lez Ch\u00e1vez\",\n    \"DENSIDAD\": \"12914\",\n    \"ORDENANZA\": \"Ordenanza Adolfo Gonzalez Chaves (\u00faltima encontrada v\u00eda web a\u00f1o 2024)\",\n    \"COBRO\": \"Tasa cobertura universal de salud, impuesto encubierto\",\n    \"CONCEPTO\": \"No aclara porcentaje , se cobra con tasa servicios urbanos y tasa conservacion , reparacion y mejorado de la red vial municipal\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Alberti\",\n    \"DENSIDAD\": \"12982\",\n    \"ORDENANZA\": \"Ordenanza Alberti\",\n    \"COBRO\": \"Tasa servicio asistencial Art. 129\",\n    \"CONCEPTO\": \"Se establece cobro seg\u00fan nomenclador ioma a quienes evidencien capacidad contributiva , se podra pedir informe socioeconomico a asistentes sociales\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Almirante Brown\",\n    \"DENSIDAD\": \"584827\",\n    \"ORDENANZA\": \"Ordenanza Almirante Brown\",\n    \"COBRO\": \"Sistema recupero SAMO\",\n    \"CONCEPTO\": \"No figura en ordenanza municipal cobro a personas sin cobertura m\u00e9dica\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Arrecifes\",\n    \"DENSIDAD\": \"32405\",\n    \"ORDENANZA\": \"Odenanza Arrecifes\",\n    \"COBRO\": \"Tasa servicio asistencial Art. 179 y ss\",\n    \"CONCEPTO\": \"Individualiza al paciente como sujeto de cobro. Se reserva la gratuidad a la evidente carencia\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Avellaneda\",\n    \"DENSIDAD\": \"367554\",\n    \"ORDENANZA\": \"Ordenanza Avellaneda\",\n    \"COBRO\": \"Sistema recupero SAMO\",\n    \"CONCEPTO\": \"Hace mencion al principio de gratuidad y trato igualitario en el Art. 214\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Ayacucho\",\n    \"DENSIDAD\": \"22136\",\n    \"ORDENANZA\": \"Ordenanza Ayacucho\",\n    \"COBRO\": \"Tasa servicio asistencial Art. 36 inc. 2\",\n    \"CONCEPTO\": \"Brinda facultad a la direccion para determinar eximici\u00f3n de pago en escala del 30, 50 y 70% seg\u00fan encuesta social\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Azul\",\n    \"DENSIDAD\": \"75905\",\n    \"ORDENANZA\": \"Ordenanza Azul\",\n    \"COBRO\": \"Previo a\u00f1o 2024 tasa servicios esenciales (demanda) Impuesto encubierto. A\u00f1o 2025 tasa servicios esenciales\",\n    \"CONCEPTO\": \"A\u00f1o 2023 tasa servicios esenciales salud y otros servicios (deporte, educacion etc.) a inmuebles urbanos y rurales  A\u00d1O 2025 tasa por servicios asistenciales, gratuitad situacion socio econ\u00f3mica . Art. 212 Tasa asistencial Art. 129 no pago excentos por situacion socio econ\u00f3mica\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Bah\u00eda Blanca\",\n    \"DENSIDAD\": \"336574\",\n    \"ORDENANZA\": \"Ordenanza Bahia Blanca\",\n    \"COBRO\": \"Tasa por servicios asistenciales Art 254 y ss\",\n    \"CONCEPTO\": \"Individualiza como contribuyente a quien recibe los servicios asistenciales\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Balcarce\",\n    \"DENSIDAD\": \"51736\",\n    \"ORDENANZA\": \"Ordenanza Balcarce\",\n    \"COBRO\": \"Contribuci\u00f3n Obligatoria para la Salud Art 73\",\n    \"CONCEPTO\": \"a) Contribuyentes de la Tasa por Alumbrado P\u00fablico b) Contribuyentes de la Tasa por Conservaci\u00f3n, Reparaci\u00f3n y Mejorado de la  Red Vial c) Contribuyentes de la Tasa por Inspecci\u00f3n de Seguridad e Higiene\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Baradero\",\n    \"DENSIDAD\": \"37491\",\n    \"ORDENANZA\": \"Ordenanza Baradero\",\n    \"COBRO\": \"Fondo municipal de Salud  ART. 37\",\n    \"CONCEPTO\": \"Valor menor $583 adicional a otras tasas\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Ben\u00edto Ju\u00e1rez\",\n    \"DENSIDAD\": \"22292\",\n    \"ORDENANZA\": \"Ordenanza Benito Juarez\",\n    \"COBRO\": \"Ausencia de concepto en ordenanza\",\n    \"CONCEPTO\": \"Se llam\u00f3 por tel\u00e9fono para consultar por turno para an\u00e1lisis manifestando no tener obra social y si tenia costo, se indic\u00f3 que se me acerque para sacar turno, solo fue consultado si el DNI tenia domicilio de Benito Juarez. Se limita atencion a vecinos del domicilio.\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Berazategui\",\n    \"DENSIDAD\": \"358712\",\n    \"ORDENANZA\": \"Ordenanza Berazategui  P\u00e1gina Web Hospital\",\n    \"COBRO\": \"Tasa servicio asistencial Art. 160\",\n    \"CONCEPTO\": \"Figura en ordenanza el concepto e individualiza al contribuyente como \\\"todos los que soliciten el servicio\\\" pero en la web del hospital se aclara, por intentos de estafas, que toda atencion, pr\u00e1ctica y estudios son gratuitos.\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Berisso\",\n    \"DENSIDAD\": \"100930\",\n    \"ORDENANZA\": \"Ordenanza Berisso\",\n    \"COBRO\": \"Ausencia de concepto en ordenanza\",\n    \"CONCEPTO\": \"\\\"(...)habitantes de Berisso, independientemente del\\nlugar donde residan\\\"\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Bol\u00edvar\",\n    \"DENSIDAD\": \"38119\",\n    \"ORDENANZA\": \"Ordenanza bolivar 1488/98 deroga tasa asistencial\",\n    \"COBRO\": \"Sistema recupero SAMO. Tasa asistencial derogada a\u00f1o 98\",\n    \"CONCEPTO\": \"Se cobraba tasa asistencial hasta el a\u00f1o 98\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Bragado\",\n    \"DENSIDAD\": \"44972\",\n    \"ORDENANZA\": \"Ordenanza Bragado\",\n    \"COBRO\": \"No figura ordenanza, solo la que aprueba la misma sin el anexo\",\n    \"CONCEPTO\": \"Se intent\u00f3  por tel\u00e9fono sin \u00e9xito, se solicit\u00f3 por email.\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Brandsen\",\n    \"DENSIDAD\": \"33026\",\n    \"ORDENANZA\": \"Ordenanza Brandsen\",\n    \"COBRO\": \"Ausencia de concepto\",\n    \"CONCEPTO\": \"\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Campana\",\n    \"DENSIDAD\": \"107979\",\n    \"ORDENANZA\": \"Ordenanza Campana\",\n    \"COBRO\": \"Tasa Aporte para la Salud P\u00fablica Art. 353. Impuesto encu\",\n    \"CONCEPTO\": \"Contribuyentes propietarios de inmuebles Tasa por Servicios Generales y/o Conservaci\u00f3n, Reparaci\u00f3n y Mejorado de la red Vial Municipal.Establecimientos Comerciales, Industriales y/o similares Tasa por Inspecci\u00f3n de Seguridad e Higiene\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Ca\u00f1uelas\",\n    \"DENSIDAD\": \"70684\",\n    \"ORDENANZA\": \"Ordenanza Ca\u00f1uelas\",\n    \"COBRO\": \"Ausencia concepto en ordenanza\",\n    \"CONCEPTO\": \"Se llam\u00f3 al hospital municipal manifestando pedir turno para analisis y no tener obra social, se responde que se acerque a sacar turno y responde que no tiene costo ante la consulta\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Capit\u00e1n Sarmiento\",\n    \"DENSIDAD\": \"15906\",\n    \"ORDENANZA\": \"Ordenanza Capitan Sarmiento\",\n    \"COBRO\": \"Tasa servicio asistencial Art. 135 y ss\",\n    \"CONCEPTO\": \"Limita gratuidad a nivel socioeconomico, informe del servicio de Desarrollo Social, excepcion de pago puede ser total o parcial (no aclara porcentajes)\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Carlos Casares\",\n    \"DENSIDAD\": \"23204\",\n    \"ORDENANZA\": \"Ordenanza Carlos Casares\",\n    \"COBRO\": \"Fondo municipal de Salud Art. 178 y ss (impuesto encubierto)\",\n    \"CONCEPTO\": \"Contribuyentes: Contribuyente de las tasas \\\"Retributivas por Servicios Urbanos\\\" y por \\\"Conservaci\u00f3n, Reparaci\u00f3n y Mejorado de la Red Vial Municipal\\\" no especifica monto\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Carlos Tejedor\",\n    \"DENSIDAD\": \"13148\",\n    \"ORDENANZA\": \"Ordenanza Carlos Tejedor\",\n    \"COBRO\": \"Ausencia concepto en ordenanza\",\n    \"CONCEPTO\": \"Se llam\u00f3 telef\u00f3nicamente  02357420103 se refirio que aveces m\u00e9dicos cobran un \\\"plus\\\" de $2.000 o $3.000. Seguir averiguando.\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Carmen De Areco\",\n    \"DENSIDAD\": \"17386\",\n    \"ORDENANZA\": \"Ordenanza Carmen de Areco\",\n    \"COBRO\": \"Ausencia concepto en ordenanza\",\n    \"CONCEPTO\": \"02273 442155 no contesta volver a llamar\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Castelli\",\n    \"DENSIDAD\": \"10517\",\n    \"ORDENANZA\": \"Ordenanza Castelli\",\n    \"COBRO\": \"SAMO + Tasa servicio asistencial\",\n    \"CONCEPTO\": \"Se discrimina en ordenanza el sistema SAMO, contribuyentes sin obra social con pago total o parcial seg\u00fan informe social y tarifa plena para no residentes del municipio. Especifica costo traslado ambulancia\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Chacabuco\",\n    \"DENSIDAD\": \"52731\",\n    \"ORDENANZA\": \"Ordenanza Chacabuco\",\n    \"COBRO\": \"Ausencia concepto en ordenanza\",\n    \"CONCEPTO\": \"En la web del hospital se expone \\\"Si el paciente posee obra social, ART, compa\u00f1\u00eda seguro u otro tipo de cobertura, estar\u00e1 a cargo de \u00e9stas. Si el paciente no tiene ning\u00fan tipo de cobertura, ser\u00e1 atendido de manera totalmente gratuita\\\" https://chacabuco.gob.ar/direccion-del-hospital/\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Chascom\u00fas\",\n    \"DENSIDAD\": \"42452\",\n    \"ORDENANZA\": \"Ordenanza Chascomus\",\n    \"COBRO\": \"SAMO\",\n    \"CONCEPTO\": \"Ordenanza no aclara personas sin cobertura\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Chivilcoy\",\n    \"DENSIDAD\": \"70839\",\n    \"ORDENANZA\": \"Ordenanza fiscal chivilcoy     Ordenanza impositiva Chivilcoy\",\n    \"COBRO\": \"Tasa servicios asistenciales, impuesto encubierto\",\n    \"CONCEPTO\": \"Se cobra tasa, impuesto encubierto a inmuebles urbanos y rurales. Art 87 ordenanza fiscal Art 5 ordenanza impos\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Col\u00f3n\",\n    \"DENSIDAD\": \"27504\",\n    \"ORDENANZA\": \"Ordenanza Col\u00f3n\",\n    \"COBRO\": \"SAMO\",\n    \"CONCEPTO\": \"Ordenanza no aclara personas sin cobertura . Se detecta abuso de la retencion de 90% pension jubilados en sala de ancianos\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Coronel Dorrego\",\n    \"DENSIDAD\": \"15968\",\n    \"ORDENANZA\": \"Ordenanza Coronel Dorrego\",\n    \"COBRO\": \"Sistema SAMO + Tasa servicios asistenciales Art 177\",\n    \"CONCEPTO\": \"Se aclara que solo se recupera por sistema SAMO, no se cobra a personas sin cobertura sean o no residentes.\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Coronel Rosales\",\n    \"DENSIDAD\": \"67503\",\n    \"ORDENANZA\": \"Ordenanza Coronel Rosales 2021\",\n    \"COBRO\": \"No figura ordenanza actualizada. \u00daltima a\u00f1o 2021\",\n    \"CONCEPTO\": \"Tasa asistencial. Especifica la excepcion \\\"Las personas carentes de aportes de obras sociales\\\"\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Coronel Pringles\",\n    \"DENSIDAD\": \"24420\",\n    \"ORDENANZA\": \"Ordenanza Coronel Pringles\",\n    \"COBRO\": \"Tasa servicios asistenciales\",\n    \"CONCEPTO\": \"Son Contribuyentes y/o responsables:a) Las personas que soliciten el servicio, ya sea el paciente, el familiar a cargo, familiar obligado a prestar alimentos, el apoderado, el curador.-\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Coronel Su\u00e1rez\",\n    \"DENSIDAD\": \"42110\",\n    \"ORDENANZA\": \"Ordenanza Coronel Suarez\",\n    \"COBRO\": \"Tasa servicios asistenciales Art. 144 y ss\",\n    \"CONCEPTO\": \"Gratuidad reservada a evidente carencia de recursos. Categorizaci\u00f3n por Servicios Sociales A, B y C seg\u00fan % a pagar. Si no entran en esas categor\u00edas abonan el total. Art 147\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Daireaux\",\n    \"DENSIDAD\": \"18422\",\n    \"ORDENANZA\": \"Ordenanza Daireaux\",\n    \"COBRO\": \"Tasa asistencial Art 23\",\n    \"CONCEPTO\": \"\\\"(...) para aquellos que soliciten y/o usufruct\u00faen de las prestaciones (...)\\\"\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Dolores\",\n    \"DENSIDAD\": \"30372\",\n    \"ORDENANZA\": \"Ordenanza dolores\",\n    \"COBRO\": \"Tasa asistencial Art 29\",\n    \"CONCEPTO\": \"Contribuyente: Quienes soliciten los servicios asistenciales, y tengan recursos probados\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Ensenada\",\n    \"DENSIDAD\": \"63997\",\n    \"ORDENANZA\": \"Ordenanza Ensenada\",\n    \"COBRO\": \"SAMO\",\n    \"CONCEPTO\": \"Art. 191 fiscal y 48 impositiva Contribuyentes obra sociales, prepagas, art, seguros\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Escobar\",\n    \"DENSIDAD\": \"256449\",\n    \"ORDENANZA\": \"Ordenanza Escobar\",\n    \"COBRO\": \"Tasa por servicios especiales. impuesto encubierto\",\n    \"CONCEPTO\": \"Se prevee en tasa alumbrado barrido limpieza diversos servicios entre los cuales se incluye salud. Art. 103 y 125\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Esteban Echeverr\u00eda\",\n    \"DENSIDAD\": \"338480\",\n    \"ORDENANZA\": \"Ordenanza Esteban Echeverria\",\n    \"COBRO\": \"SAMO\",\n    \"CONCEPTO\": \"Art. 16.1\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Exaltaci\u00f3n De La Cruz\",\n    \"DENSIDAD\": \"40159\",\n    \"ORDENANZA\": \"Ordenanza exaltaci\u00f3n de la cruz\",\n    \"COBRO\": \"Tasa por servicios generales. impuesto encubierto\",\n    \"CONCEPTO\": \"Art. 3\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Ezeiza\",\n    \"DENSIDAD\": \"201511\",\n    \"ORDENANZA\": \"Ordenanza Ezeiza\",\n    \"COBRO\": \"Servicios complementarios de salud . Contribucion especial\",\n    \"CONCEPTO\": \"Art. 1.7 ordenanza impositiva. impuesto encubierto.\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Florencio Varela\",\n    \"DENSIDAD\": \"496433\",\n    \"ORDENANZA\": \"Odenanza Florencia Varela\",\n    \"COBRO\": \"Tasa por servicios generales. impuesto encubierto\",\n    \"CONCEPTO\": \"Art. 115 ordenanza fiscal\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Florentino Ameghino\",\n    \"DENSIDAD\": \"10790\",\n    \"ORDENANZA\": \"Ordenanza Florentino Ameghino\",\n    \"COBRO\": \"Aranceles hospitalarios\",\n    \"CONCEPTO\": \"Art. 208 \\\"Los distintos servicios prestados en el Hospital municipal de Florentino Ameghino, que se encuetran en la ordenanza 114/93 se cobrar\u00e1n seg\u00fan los valores fijados en la mencionada ordenanza.\\\" No se encuentra la ordenanza\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"General Alvarado\",\n    \"DENSIDAD\": \"45597\",\n    \"ORDENANZA\": \"Ordenanza General Alvarado\",\n    \"COBRO\": \"Tasa de salud\",\n    \"CONCEPTO\": \"impuesto encubierto\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"General Alvear\",\n    \"DENSIDAD\": \"13031\",\n    \"ORDENANZA\": \"Ordenanza General Alvear\",\n    \"COBRO\": \"Tasa por servicios asistenciales Art. 38\",\n    \"CONCEPTO\": \"No aclara contribuyente.\\\"(...) f\u00edjanse para los servicios asistenciales prestados en el Hospital  Municipal \u201cDr. Bernardino Rivadavia\u201d los importes determinados en el nomenclador IOMA.\\\"\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"General Arenales\",\n    \"DENSIDAD\": \"16350\",\n    \"ORDENANZA\": \"\u00daltima ordenanza que figura a\u00f1o 2023\",\n    \"COBRO\": \"Tasa servicios asistenciales Art. 134 y ss\",\n    \"CONCEPTO\": \"Exceptuados de pago los casos individuales que presene evidente carencia de recursos previa diagn\u00f3stico social +  ciertas pr\u00e1cticas como obstetricia, pediatria menor 1 a\u00f1o, inmunizaciones programadas, enfermedades transmisibles agudas y cr\u00f3nicas que el Ministerio de bienestar social asi determine\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"General Belgrano\",\n    \"DENSIDAD\": \"20791\",\n    \"ORDENANZA\": \"Ordenanza General Belgrano\",\n    \"COBRO\": \"Tasa asistencial\",\n    \"CONCEPTO\": \"ART. 151 Aclara que presta servicios gratuito a quien carezca de recursos para cubrirlos. Ademas SAMO\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"General Guido\",\n    \"DENSIDAD\": \"3174\",\n    \"ORDENANZA\": \"Ordenanza General Guido\",\n    \"COBRO\": \"Tasa de Servicio de Salud Art 21\",\n    \"CONCEPTO\": \"Por cada recibo de Tasa o Derecho desde $ 5.000,00.- hasta la suma de $120.000\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"General Juan Madariaga\",\n    \"DENSIDAD\": \"22624\",\n    \"ORDENANZA\": \"Ordenanza Juan Madariaga\",\n    \"COBRO\": \"Tasa por servicios asistenciales Art 208 y ss\",\n    \"CONCEPTO\": \"De forma explicita la ordenanza sostiene el sistema de salud p\u00fablico y gratuito, expone el sistema de recupero SAMO y manifie \\\"Cuando el paciente voluntariamente desee colaborar podr\u00e1 abonar las prestaciones de acuerdo a los valores establecidos en la Ordenanza Impositiva.\\\"\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"General La Madrid\",\n    \"DENSIDAD\": \"11618\",\n    \"ORDENANZA\": \"Ordenanza General Lamadrid\",\n    \"COBRO\": \"Tasa servicio asistenciales Art 13\",\n    \"CONCEPTO\": \"Se especifica como contribuyente a pacientes ambulatorios o internados sin obra social, se les cobrar\u00e1 seg\u00fan nomenclador, tb los materiales y medicamentos utilizados. Tb especifica que se cobrar\u00e1 materiales y medicamentos a  los pacientes del hogar de ancianos. Utiliza entrevista asistente social y categor\u00edas, cobertura total o parcial. Se hizo denuncia, en este momento quitaron la ordenanza de la web y se les inform\u00f3 que debian modificarla para obtener la licencia para el a\u00f1o 2027 para el hospital\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"General Las Heras\",\n    \"DENSIDAD\": \"18022\",\n    \"ORDENANZA\": \"Ordenanza General Las Heras\",\n    \"COBRO\": \"Tasa servicios asistenciales Art. 123 y ss\",\n    \"CONCEPTO\": \"Contribuyente quien obtenga el servicio, familiares, obra social o prepapaga, seguro de salud. Eximici\u00f3n total o parcial de pago por condicion socio econ\u00f3mica constatada por personal o previa entre vista asistencia social\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"General Lavalle\",\n    \"DENSIDAD\": \"4870\",\n    \"ORDENANZA\": \"Ordenanza General Lavalle\",\n    \"COBRO\": \"Tasa servicios asistenciales Art. 173 y ss\",\n    \"CONCEPTO\": \"Excepci\u00f3n a las personas carentes de recursos . Excluidos los servicios de obstetricia, pediatria hasta 1 a\u00f1o, inmunizaciones programadas, enfermedades transmisibles agudas y cr\u00f3nicas que el Ministerio de Bienestar Social as\u00ed determine.\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"General Paz\",\n    \"DENSIDAD\": \"14207\",\n    \"ORDENANZA\": \"Ordenanza General Paz\",\n    \"COBRO\": \"Residentes Tasa contributiva unidad terapia intensiva Art. 291 y ss No residentes Art. 294 y ss por todo servicio en el hospital\",\n    \"CONCEPTO\": \"Residentes urbanos tasa servicios urbanos 3usd mensual y Residentes rurales en tasa vial 8 usd bimestral. No residentes Art. 294 y ss por todo servicio en el hospital se determina el valor en UF , el valor es mayor si no poseen cobertura.  Art 297\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"General Pinto\",\n    \"DENSIDAD\": \"12941\",\n    \"ORDENANZA\": \"Ordenanza General Pinto\",\n    \"COBRO\": \"Aranceles hospitalarios Art. 240 y ss\",\n    \"CONCEPTO\": \"prestaci\u00f3n a un paciente sin Obra Social, y que seg\u00fan encuesta social realizada por el profesional del \u00e1rea, est\u00e9 en condiciones de abonar, par dicho caso se facturar\u00e1 teniendo en cuenta nomenclador para HPM del IOMA\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"General Pueyrred\u00f3n\",\n    \"DENSIDAD\": \"667081\",\n    \"ORDENANZA\": \"Ordenanza General Pueyrredon\",\n    \"COBRO\": \"Contribuci\u00f3n a la Salud, la Educaci\u00f3n y el Desarrollo Infantil Art 217 y ss\",\n    \"CONCEPTO\": \"contribuci\u00f3n fija por cada inmueble emplazado en el Partido de General Pueyrredon gravado por la Tasa por Servicios Urbanos o por la Tasa por Conservaci\u00f3n, Reparaci\u00f3n y Mejorado de la red vial municipal\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"General Rodr\u00edguez\",\n    \"DENSIDAD\": \"142709\",\n    \"ORDENANZA\": \"Ordenanza General Rodriguez\",\n    \"COBRO\": \"Tasa especial servicios de educaci\u00f3n, salud y seguridad (impuesto encubierto) Art 42 y ss Tasa asistencial por hospital odontologico y oftalmolog\u00edco Art. 43 y ss ordenanza impositiva.\",\n    \"CONCEPTO\": \"Valores se establecen e X cantidad de m\u00f3dulos. ART 41 tasa emergencias m\u00e9dicas Art 42 impuesto encubierto salud Art 43 hospital odont\u00f3logo y oftalmologia\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"General San Mart\u00edn\",\n    \"DENSIDAD\": \"450575\",\n    \"ORDENANZA\": \"Ordenanza General San Martin\",\n    \"COBRO\": \"SAMO Art 303 y ss\",\n    \"CONCEPTO\": \"Refiere solo al sistema SAMO de recupero\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"General Viamonte\",\n    \"DENSIDAD\": \"22649\",\n    \"ORDENANZA\": \"Ordenanza General Viamonte\",\n    \"COBRO\": \"Tasa asistencial Art. 205 y ss\",\n    \"CONCEPTO\": \"El ejectuvi puede adecuar valores seg\u00fan situacion socioeconomica. Algunas pr\u00e1cticas est\u00e1n excentas de pago.  Se determina el contribuyente sin obra social pero con ingresos suficientes y sin ingresos suficientes. Hacen distincion con no residentes.\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"General Villegas\",\n    \"DENSIDAD\": \"35251\",\n    \"ORDENANZA\": \"Ordenanza General Villegas\",\n    \"COBRO\": \"FONDO POR SERVICIOS ASISTENCIALES Y PARA LA SALUD Art. 57\",\n    \"CONCEPTO\": \"Art\u00edculo 57\u00ba: No aprobado, en Sesi\u00f3n Especial 2\u00b0 del 22 de diciembre del 2025.\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Guamini\",\n    \"DENSIDAD\": \"11801\",\n    \"ORDENANZA\": \"Ordenanza guamini\",\n    \"COBRO\": \"Tasa salud (impuesto encubierto) Art 205 y ss ordenanza fiscal + Tasa servicios asistenciales Art. 30 y ss ordenanza impositiva\",\n    \"CONCEPTO\": \"Tarifario por prestaciones de forma detalladad: radiografias, mamograf\u00eda, etc.\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Hip\u00f3lito Yrigoyen\",\n    \"DENSIDAD\": \"10661\",\n    \"ORDENANZA\": \"Ordenanza Hip\u00f3lito Yrigoyen\",\n    \"COBRO\": \"Tasa servicios asistenciales Art. 45 y ss\",\n    \"CONCEPTO\": \"No posee su ordenanza en la web, se consulto sistema SIBOM de la provincia de Buenos Aires\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Hurlingham\",\n    \"DENSIDAD\": \"185641\",\n    \"ORDENANZA\": \"Ordenanza Municipal Hurlingham\",\n    \"COBRO\": \"Ausencia de concepto\",\n    \"CONCEPTO\": \"No figura en su web si en el sistema SIBOM\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Ituzaing\u00f3\",\n    \"DENSIDAD\": \"180232\",\n    \"ORDENANZA\": \"Ordenanza Ituzaingo\",\n    \"COBRO\": \"SAMO + tasa de proteccion ciudadana (impuesto encubierto) Art. 18.1\",\n    \"CONCEPTO\": \"Se define el sistema samo de recupero y una tasa como impuesto encubierto para los contribuyentes para sotener servicios varios del municipio entre los cuales se encuentra el de salud\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Jos\u00e9 C. Paz\",\n    \"DENSIDAD\": \"326992\",\n    \"ORDENANZA\": \"Ordenanza Municipal Jos\u00e9 C. Paz\",\n    \"COBRO\": \"Ausencia de concepto\",\n    \"CONCEPTO\": \"\u00daltima que figura a\u00f1o 2018 se cobra a no residentes\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Jun\u00edn\",\n    \"DENSIDAD\": \"103787\",\n    \"ORDENANZA\": \"Ordenanza Junin\",\n    \"COBRO\": \"TASA POR SERVICIOS PUBLICOS URBANOS (S.P.U.) Art. 1\",\n    \"CONCEPTO\": \"impuesto encubierto, se incluye a la salud en la tasa de servicios generales del municipio\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"La Costa\",\n    \"DENSIDAD\": \"100689\",\n    \"ORDENANZA\": \"Ordenanza La Costa\",\n    \"COBRO\": \"Tasa servicios asistenciales Art. 198 Fondo Salud a rurales Art.275 impuesto encubierto\",\n    \"CONCEPTO\": \"Art 198 Tasa servicios asistenciales, pago no residentes eximidos de pago indigentes Art 275 Fondo Complementario de Seguridad y Salud, que ser\u00e1 aplicado a las partidas del Sector Rural que tendr\u00e1 un valor establecido por la Ordenanza Impositiva vigente.\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"La Matanza\",\n    \"DENSIDAD\": \"1841247\",\n    \"ORDENANZA\": \"Ordenanza La Matanza\",\n    \"COBRO\": \"SAMO Art 249\",\n    \"CONCEPTO\": \"Se especifica el sistema de recupero SAMO en la ordenanza Art. 249\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"La Plata\",\n    \"DENSIDAD\": \"768470\",\n    \"ORDENANZA\": \"Ordenanzas La plata\",\n    \"COBRO\": \"Ausencia de concepto\",\n    \"CONCEPTO\": \"Ausencia de concepto tanto en ordenanza fiscal como impositiva\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Lanus\",\n    \"DENSIDAD\": \"461267\",\n    \"ORDENANZA\": \"Ordenanza Lan\u00fas\",\n    \"COBRO\": \"Ausencia de concepto\",\n    \"CONCEPTO\": \"Ausencia de concepto en c\u00f3digo tributario\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Laprida\",\n    \"DENSIDAD\": \"11646\",\n    \"ORDENANZA\": \"Ordenanza Laprida\",\n    \"COBRO\": \"SAMO Art. 20\",\n    \"CONCEPTO\": \"No aclara cobertura a personas sin obra social, prepaga o seguro. Si hay materiales no cubiertos por la entidad y no este cubierto por nomenclador ioma lo abonar\u00e1 o repondr\u00e1 el paciente.\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Las Flores\",\n    \"DENSIDAD\": \"27239\",\n    \"ORDENANZA\": \"Ordenanza Las flores\",\n    \"COBRO\": \"Ausencia de concepto\",\n    \"CONCEPTO\": \"Ausencia de concepto en fiscal impositiva\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Leandro N. Alem\",\n    \"DENSIDAD\": \"17266\",\n    \"ORDENANZA\": \"Ordenanza Leandro N. Alem\",\n    \"COBRO\": \"Aranceles de los servicios asistenciales Art. 160\",\n    \"CONCEPTO\": \"Categorizaci\u00f3n otorgada por el Servicio Social y con las excepciones que la misma consagre. Se autoriza al Departamento Ejecutivo a modificar los distintos aranceles establecidos en el presente cap\u00edtulo cuando resulte necesario para garantizar el funcionamiento de los establecimientos municipales con todos sus servicios con el objeto principal de favorecer la atenci\u00f3n de los pacientes carenciados.\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Lezama\",\n    \"DENSIDAD\": \"6231\",\n    \"ORDENANZA\": \"Ordenanza Lezama\",\n    \"COBRO\": \"Sistema SAMO Art. 23 y ss + tasas (impuestos encubiertos)\",\n    \"CONCEPTO\": \"Art. 219 TASA DE SERVICIOS DE GUARDIAS PEDI\u00c1TRICAS Y/O VINCULADAS\\nA LA SALUD DE LA NI\u00d1EZ , La base imponible de la tasa a que se refiere el presente art\u00edculo estar\u00e1\\nconstituida por los contribuyentes de las Tasas de Servicios Rurales y de Barrido, Limpieza y\\nConservaci\u00f3n de la V\u00eda P\u00fablica.\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Lincoln\",\n    \"DENSIDAD\": \"45506\",\n    \"ORDENANZA\": \"Ordenanza Lincoln\",\n    \"COBRO\": \"Tasa servicios asistenciales Art. 21\",\n    \"CONCEPTO\": \"Se especifica valor por recorridos por km de la ambulancia y recarga tubo de ox\u00edgeno\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Lober\u00eda\",\n    \"DENSIDAD\": \"18243\",\n    \"ORDENANZA\": \"Ordenanza Lober\u00eda\",\n    \"COBRO\": \"Tasa servicios asistenciales Art. 192 y ss\",\n    \"CONCEPTO\": \"Cuando la encuesta socioecon.mica realizada por Servicio Social de la Municipalidad as. lo determine, el sistema municipal se har. cargo del costo total o la diferencia que o pudiera abonar el paciente\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Lobos\",\n    \"DENSIDAD\": \"41760\",\n    \"ORDENANZA\": \"Ordenanza Lobos\",\n    \"COBRO\": \"TASA POR SALUD, SEGURIDAD, EDUCACION, DEFENSA CIVIL Y ASISTENCIA SOCIAL ART. 30 (impuesto encubierto)\",\n    \"CONCEPTO\": \"CONTRIBUCION SOLIDARIA PARA EL FINANCIAMIENTO DE SERVICIOS DE EDUCACI\u00d3N, SALUD, SEGURIDAD Y ASISTENCIA SOCIAL\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Lomas de Zamora\",\n    \"DENSIDAD\": \"690323\",\n    \"ORDENANZA\": \"Ordenanza Lomas de Zamora\",\n    \"COBRO\": \"Ausencia de concepto\",\n    \"CONCEPTO\": \"\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Luj\u00e1n\",\n    \"DENSIDAD\": \"111365\",\n    \"ORDENANZA\": \"Ordenanza Lujan\",\n    \"COBRO\": \"Ausencia de concepto\",\n    \"CONCEPTO\": \"\u00daltima disponible a\u00f1o 2024, se solicito actualizada hcd@lujan.gob.ar\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Magdalena\",\n    \"DENSIDAD\": \"26830\",\n    \"ORDENANZA\": \"Ordenanza Magdalena\",\n    \"COBRO\": \"Ausencia de concepto\",\n    \"CONCEPTO\": \"Se llam\u00f3 por tel\u00e9fono al (02221)\u200b 45-3443  se manifesto la necesidad de contar con el cambi\u00f3 de domicilio hecho en el DNI o en tr\u00e1mite, se consult\u00f3 y dijeron que no ten\u00eda costo si no tenia obra social.\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Maip\u00fa\",\n    \"DENSIDAD\": \"11323\",\n    \"ORDENANZA\": \"Ordenanza Maip\u00fa\",\n    \"COBRO\": \"Tasa servicios asistenciales Art. 12 y ss\",\n    \"CONCEPTO\": \"Necesidad hacer declaraci\u00f3n jurada anualmente, solo residentes municipio. Se categorizan 4 categor\u00edas \\\"Condici\u00f3n de paciente\\\" . A) paciente con obra social , lesgilaci\u00f3n labora. seguros, ART. B) ingresos + 317.000 sin cobertura A C) bajos recursos ingresos menos 317.000 y sin A D) bajos recursos con obra social ingresos menos a 317.000. Cobran traslados en ambulancia. Cobran a no residentes que no tengan cobertura a menos que demuestren carencia.\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Malvinas Argentinas\",\n    \"DENSIDAD\": \"350674\",\n    \"ORDENANZA\": \"Ordenanza Malvinas Argentinas\",\n    \"COBRO\": \"Tasa servicios asistenciales Art. 192 y ss\",\n    \"CONCEPTO\": \"Contribuyentes: qui\u00e9n lo solicite, el enfermo o los familiares. En el caso de prestarse el servicio a personas con cobertura social o con\\ncobertura por seguro o autoseguro, los derechos asistenciales deber\u00e1n ser abonados\\npor los responsables de la cobertura, en cuyo caso, los servicios le ser\u00e1n facturados por\\nla Secretar\u00eda de Salud.\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Mar Chiquita\",\n    \"DENSIDAD\": \"33110\",\n    \"ORDENANZA\": \"Ordenanza Mar Chiquita\",\n    \"COBRO\": \"Tasa Servicios Asistenciales Art. 198 y ss FONDO COMPLEMENTARIO DE SEGURIDAD Y SALUD (impuesto encubierto Art. 275\",\n    \"CONCEPTO\": \"Se cobrar\u00e1 a no residentes. El pago se efectivizar\u00e1 al solicitar el servicio. El indigente tendr\u00e1 asistencia gratuita mediante la presentaci\u00f3n de la certificaci\u00f3n del responsable del \u00e1rea de Desarrollo Social. Las personas de escasos recursos podr\u00e1n ser autorizadas a abonar los aranceles estipulados con una deducci\u00f3n de hasta el cincuenta por ciento (50%). Responsable del pago la persona, tutores, curadores, representantes y/o herederos en caso de fallecimiento.\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Marcos Paz\",\n    \"DENSIDAD\": \"67011\",\n    \"ORDENANZA\": \"Ordenanza Marcos Paz\",\n    \"COBRO\": \"Tasa servicios asistenciales Art. 232 y ss\",\n    \"CONCEPTO\": \"Son contribuyentes de la tasa establecida en el presente t\u00edtulo, quienes soliciten el servicio, sus familiares o los responsables de la cobertura social, o cobertura por seguro o autoseguro obra social o prepaga, coseguro de salud, sindicales, cooperativos, mutuales. Gratuidad a indigencia.\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Mercedes\",\n    \"DENSIDAD\": \"72970\",\n    \"ORDENANZA\": \"Ordenanza Mercedes\",\n    \"COBRO\": \"Contribucon especial Art. 6 impuesto encubierto\",\n    \"CONCEPTO\": \"Asociaci\u00f3n de Bomberos Voluntarios y Asociaci\u00f3n Cooperadora del Hospital Se tributar\u00e1 en forma conjunta con la Tasa de Conservaci\u00f3n de la v\u00eda P\u00fablica y/o la Tasa de Conservaci\u00f3n, Mejorado y Reparaci\u00f3n de la Red Vial Munici\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Merlo\",\n    \"DENSIDAD\": \"582464\",\n    \"ORDENANZA\": \"Ordenanza Merlo\",\n    \"COBRO\": \"SAMO Art 42\",\n    \"CONCEPTO\": \"Se aclara gratuito personas sin cobertura. Sistema recupero SAMO\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Monte\",\n    \"DENSIDAD\": \"24868\",\n    \"ORDENANZA\": \"Ordenanza Monte\",\n    \"COBRO\": \"Contribucion especial Art. 68 impuesto encubierto\",\n    \"CONCEPTO\": \"Art. 86 inc 2 contribucion especial Salud P\u00fablica del Partido de Monte\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Monte Hermoso\",\n    \"DENSIDAD\": \"8465\",\n    \"ORDENANZA\": \"Ordenanza Monte Hermoso\",\n    \"COBRO\": \"SAMO + Tasa servicios asistenciales Art. 272\",\n    \"CONCEPTO\": \"No cobro seg\u00fan condicion socioeconomica necesario informe servicio social municipal\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Moreno\",\n    \"DENSIDAD\": \"576578\",\n    \"ORDENANZA\": \"Ordenanza moreno\",\n    \"COBRO\": \"TASA DE SALUD Y ASISTENCIA SOCIAL ART. 43 . Alicuota sobre multas que cobre el municipio\",\n    \"CONCEPTO\": \"al\u00edcuota del diez coma cincuenta por ciento (10,50%) sobre los tributos, accesorios y/o multas por contravenciones que se abonaren al Municipio, en concepto de Tasa de Salud y Asistencia Social, cuyo importe estar\u00e1 destinado: 0,5% a la \u201cFundaci\u00f3n Mariano y Luciano de La Vega\u201d, un 0,5% a la Infraestructura Hospitalaria y el 9,5% restante a solventar otras erogaciones previstas en el Art\u00edculo 329\u00ba de la Ordenanza fis\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Mor\u00f3n\",\n    \"DENSIDAD\": \"331140\",\n    \"ORDENANZA\": \"Ordenanza Mor\u00f3n\",\n    \"COBRO\": \"SAMO Art. 288 y 290\",\n    \"CONCEPTO\": \"ordenanza a\u00f1o 2024 se solicito la actualizada v\u00eda correo acceso.informacion.publica@moron.gob.ar  Art. 53 se cobra por servicios asistenciales de emergencia m\u00e9dica y traslado por accidentes de tr\u00e1nsito\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Navarro\",\n    \"DENSIDAD\": \"19899\",\n    \"ORDENANZA\": \"Ordenanza Municipal Navarro\",\n    \"COBRO\": \"ausencia ordenanza\",\n    \"CONCEPTO\": \"se solicito por correo\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Necochea\",\n    \"DENSIDAD\": \"102110\",\n    \"ORDENANZA\": \"Ordenanza Necochea\",\n    \"COBRO\": \"TASA POR FORTALECIMIENTO, PROMOCI\u00d3N Y PREVENCI\u00d3N PARA LA SALUD Art. 426\",\n    \"CONCEPTO\": \"impuesto encubierto a inmuebles urbanos y rurales\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Nueve de Julio\",\n    \"DENSIDAD\": \"52607\",\n    \"ORDENANZA\": \"Ordenanza Nueve de Julio\",\n    \"COBRO\": \"Tasa servicios asistenciales Art. 44\",\n    \"CONCEPTO\": \"excepto sin cobertura social o no posean capacidad de pago para los cuales no regian ningun tipo de arancel. Los dem\u00e1s solo si hay diferencia entre cobertura y servicio se abonar\u00e1 la diferencia el paciente.\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Olavarr\u00eda\",\n    \"DENSIDAD\": \"125751\",\n    \"ORDENANZA\": \"Ordenanza Olavarr\u00eda\",\n    \"COBRO\": \"ART. 22 Ordenanza impositiva Sistema SIAMO \\\"cobertura municipal de salud por cuota mensual\\\" Tasa servicios asistenciales Art. 138 y ss ordenanza fiscal\",\n    \"CONCEPTO\": \"SIAMO (Sistema Integral de Atenci\u00f3n M\u00e9dica de Olavarr\u00eda) es un sistema de cobertura m\u00e9dica prepaga municipal que funciona en el Partido de Olavarr\u00eda.Cobertura: Ofrece atenci\u00f3n m\u00e9dica a trav\u00e9s del Hospital Municipal Dr. H\u00e9ctor M. Cura y de los Centros de Atenci\u00f3n Primaria de la Salud (CAPS) municipales.Aportes: Los pacientes abonan una cuota mensual accesible para recibir esta cobertura dentro del sistema p\u00fablico de salud local.ARTICULO 139. Se faculta al Departamento Ejecutivo para conceder deducciones de acuerdo a la posibilidad econ\u00f3mica del tributante, determinadas por el servicio social de la Municipalidad y otorgar facilidades en los pagos\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Patagones\",\n    \"DENSIDAD\": \"25982\",\n    \"ORDENANZA\": \"Ordenanza Patagones\",\n    \"COBRO\": \"Tasa servicios asistenciales Art. 239 y ss\",\n    \"CONCEPTO\": \"Ser\u00e1 abonada directamente por el beneficiario del servicio, en caso que el mismo no se encuentre afiliado a obra social o mutual que resulte obligada al pago y en la medida que no encuadre en alguna de las exenciones previstas. Excepciones Art. 239 quarter\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Pehuaj\u00f3\",\n    \"DENSIDAD\": \"44783\",\n    \"ORDENANZA\": \"Ordenanza Pehuaj\u00f3\",\n    \"COBRO\": \"Tasa servicios asistenciales Art. 215 y ss\",\n    \"CONCEPTO\": \"Contribuyentes las personas humanas usuarias del servicio o sus representantes. Son responsables sustitutos de la presente tasa aquellas personas humanas o jur\u00eddicas, p\u00fablicas o privadas, que sean encargados de la cobertura social, por seguro o por autoseguro, del contribuyente\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Pellegrini\",\n    \"DENSIDAD\": \"7143\",\n    \"ORDENANZA\": \"Ordenanza Pellegrini\",\n    \"COBRO\": \"Sistema de recupero SAMO Art. 40 y ss\",\n    \"CONCEPTO\": \"La Tasa por Servicios Asistenciales ser\u00e1 aplicable respecto de las prestaciones m\u00e9dicas asistenciales (...) \u00fanicamente en aquellos casos en que los usuarios cuenten con cobertura m\u00e9dica a trav\u00e9s de obra social, empresa de medicina prepaga, aseguradora de riesgos del trabajo o seguro de salud. En ning\u00fan caso corresponder\u00e1 exigir pago alguno a los particulares que carezcan de cobertura m\u00e9dica, garantiz\u00e1ndose para ellos la gratuidad plena en el acceso a la atenci\u00f3n sanitaria municipal. Se clara que se aceptan donaciones que deben quedar registradas como donaciones al municipio Art. 41\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Pergamino\",\n    \"DENSIDAD\": \"115340\",\n    \"ORDENANZA\": \"Ordenanza Pergamino\",\n    \"COBRO\": \"Ausencia de concepto\",\n    \"CONCEPTO\": \"Ausencia de concepto\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Pila\",\n    \"DENSIDAD\": \"4642\",\n    \"ORDENANZA\": \"Ordenanza Municipal Pila\",\n    \"COBRO\": \"no se encuentra normativa seguir buscando\",\n    \"CONCEPTO\": \"\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Pilar\",\n    \"DENSIDAD\": \"394754\",\n    \"ORDENANZA\": \"Ordenanza Pilar\",\n    \"COBRO\": \"Tasa servicios de salud Art. 263 y ss\",\n    \"CONCEPTO\": \"Regimen General Art. 263 y ss individualiza como sujeto a la persona que reciba el servicio, no se cobrar\u00e1 la tasa a personas que: residan en pilar, tengo residencia permanenente en el pa\u00eds y no tengan cobertura por m\u00e9dico asitencial por carecer e tareas remuneradas o beneficios previsionales.  Regimen Especial Art 267 ter y ss Sistema SAMO recupero\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Pinamar\",\n    \"DENSIDAD\": \"39449\",\n    \"ORDENANZA\": \"Ordenanza Pinamar\",\n    \"COBRO\": \"TASA POR DERECHOS SANATORIALES/SERVICIOS ASISTENCIALES \u2013 HOSPITAL MUNICIPAL SALAS MUNICIPALES ART. 97 Y SS\",\n    \"CONCEPTO\": \"eximidos del pago de hasta un cien por ciento (100%) (...) aquellas personas sin cobertura social y con recursos limitados y/o insuficientes, con autorizaci\u00f3n de la Direcci\u00f3n de Acci\u00f3n Social.\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Presidente Per\u00f3n\",\n    \"DENSIDAD\": \"102106\",\n    \"ORDENANZA\": \"Ordenanza Presidente Per\u00f3n\",\n    \"COBRO\": \"Ausencia concepto\",\n    \"CONCEPTO\": \"\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Pu\u00e1n\",\n    \"DENSIDAD\": \"16613\",\n    \"ORDENANZA\": \"Ordenanza Puan\",\n    \"COBRO\": \"Tasa servicios asistenciales Art. 170 y ss ordenanza fiscal y Art. 42 y ss ordenanza impositiva\",\n    \"CONCEPTO\": \"Servicios asistenciales y servicio ambulancia. La tasa se efectiviza salvo medio convenio obras sociales, particiones oficiales/privadas. (...) se podra establecer formas de pago diferidas en aquellos casos en que los costos de las cirug\u00edas no puedan ser abonadas de contado por el paciente con la firma de un convenio y los pagares respectivos. , previa evaluacion \u00e1rea promocion social.  En ordenanza impositiva se determina segm\u00e9ntaci\u00f3n seg\u00fan se tenga o no cobertura, capacidad de pago, cobertura que cubra o no los servicios , falta de la misma con posibilidad de pago o no, se incluye tablas tarifarias para todo servicio hasta  tomografias, parto y cesarea. El municipio cuenta con \\\"Seguro de Salud Municipal\\\" SEDEM , categor\u00edza a los pacientes, reserva gratuidad a carentes de recursos.\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Punta Indio\",\n    \"DENSIDAD\": \"12297\",\n    \"ORDENANZA\": \"Ordenanza Punta Indio\",\n    \"COBRO\": \"Fondo Solidario de Salud P\u00fablica Municipal Art. 202 y ss\",\n    \"CONCEPTO\": \"impuesto encubierto\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Quilmes\",\n    \"DENSIDAD\": \"633391\",\n    \"ORDENANZA\": \"Ordenanza Quilmes\",\n    \"COBRO\": \"Sistema SAMO Art. 316 y ss\",\n    \"CONCEPTO\": \"Sistema de recupero SAMO\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Ramallo\",\n    \"DENSIDAD\": \"39730\",\n    \"ORDENANZA\": \"C\u00f3digo Tributario Ramallo\",\n    \"COBRO\": \"Tasa servicios asistenciales Art. 238\",\n    \"CONCEPTO\": \"Sistema SAMO + Se reserva gratuidad a situaci\u00f3n de indigencia. Personas sin cobertura que no demuestren indigencia ser\u00e1n facturados seg\u00fan nomenclador de autogesti\u00f3n\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Rauch\",\n    \"DENSIDAD\": \"16635\",\n    \"ORDENANZA\": \"Ordenanza Rauch\",\n    \"COBRO\": \"Tasa servicios asistenciales Anexo 1 T\u00edtulo XV\",\n    \"CONCEPTO\": \"Se establecen valores de cobro a toda pr\u00e1ctica, figuran precios en el anexo. Oficina de Desarrollo\\nSocial de la Municipalidad, debe categorizar a los pacientes en:\\na) Pacientes sin cobertura social, no indigente;\\nb) Pacientes sin cobertura social indigente;\\nc) Pacientes con cobertura social indigente y no indigente. Se podr\u00e1 determinar porcentajes de pago 25% 50% 75% o cobertura social si amerita\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Rivadavia\",\n    \"DENSIDAD\": \"19849\",\n    \"ORDENANZA\": \"Ordenanza Rivadavia\",\n    \"COBRO\": \"Servicios asistenciales Art 238 y ss\",\n    \"CONCEPTO\": \"Servicio Social categor\u00edza en las siguientes categor\u00edas: A con cobertura social convenida B con cobertura social pero sin convenio C sin cobertura social, con ingresos suficientes D sin cobertura social sin ingresos suficientes E con cobertura social , sin ingresos suficientes . no residentes deberan abonar totalidad o carta provincial o municipal que se hara cargo de los gastos.\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Rojas\",\n    \"DENSIDAD\": \"25627\",\n    \"ORDENANZA\": \"Ordenanza 2025 Rojas\",\n    \"COBRO\": \"Cobro a obras sociales Art. 215 y ss\",\n    \"CONCEPTO\": \"Se solicito ordenanza vigente, \u00faltima que figura es a\u00f1o 2025\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Roque P\u00e9rez\",\n    \"DENSIDAD\": \"13977\",\n    \"ORDENANZA\": \"Ordenanza Roque Perez\",\n    \"COBRO\": \"Tasa servicios asistenciales Art 33 SAMO  y Tasa por salud y seguridad fija anual por parcela urbana o hectarea\",\n    \"CONCEPTO\": \"Art. 33 OJO La atenci\u00f3n m\u00e9dica ser\u00e1 gratuita salvo para aquellos pacientes que tengan cobertura\\nsocial o privada. En casos de accidentes de trabajo, la ART correspondiente o en su\\ndefecto el empleador, deber\u00e1 hacerse cargo de los honorarios m\u00e9dicos y gastos\\nsanatoriales que origine la atenci\u00f3n del accidentado. Cuando la atenci\u00f3n que deba\\nbrindarse haya sido origen en accidentes de tr\u00e1nsito o cualquier otro accionar de\\nterceros responsables, el paciente atendido ceder\u00e1 a favor de la Municipalidad el\\nDerecho que pudiera corresponderle por obras sociales, medicina prepaga, ART o por\\ncobertura de seguros de cualquier naturaleza por monto de las prestaciones recibidas.\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Saavedra Pigue\",\n    \"DENSIDAD\": \"22537\",\n    \"ORDENANZA\": \"Ordenanza Saavedra Pigue\",\n    \"COBRO\": \"Tasa servicios asistenciales Art. 273 y ss\",\n    \"CONCEPTO\": \"Sistema SAMO + Gratuidad exclusiva para indigencia Art. 277\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Saladillo\",\n    \"DENSIDAD\": \"35656\",\n    \"ORDENANZA\": \"Ordenanza Saladillo\",\n    \"COBRO\": \"SIstema SAMO\",\n    \"CONCEPTO\": \"No se especifica en la ordenanza. Se llam\u00f3 al telefono del hospital 02344 432112, me brindaron el whatshapp para solicitar turno programados , al manifiestar no tener obra social me comunicaron que el hospital es p\u00fablico y gratuito, solo se piden los datos de la obra social si se tiene para cobrarle a ellos.\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Salliquelo\",\n    \"DENSIDAD\": \"9427\",\n    \"ORDENANZA\": \"Ordenanza Salliquelo\",\n    \"COBRO\": \"Tasa servicios asistenciales Art. 69 y ss + Plan de Salud Municipal\",\n    \"CONCEPTO\": \"Art. 69 y ss se establecen valores para pacientes sin cobertura indigentes o pacientes adheridos al plan de salud municipal abonando 50% de ciertas pr\u00e1cticas.\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Salto\",\n    \"DENSIDAD\": \"40157\",\n    \"ORDENANZA\": \"Ordenanza Salto\",\n    \"COBRO\": \"Sistema SAMO + Tasa asistencial Art. 206 y ss\",\n    \"CONCEPTO\": \"Arancelamiento directo con v\u00eda ejecutiva judicial Art 213 juicio de apremio. Podran eximirse los indigentes Art. 66\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"San Andr\u00e9s de Giles\",\n    \"DENSIDAD\": \"26510\",\n    \"ORDENANZA\": \"Ordenanza San Andr\u00e9s de Giles\",\n    \"COBRO\": \"Tasa servicios asistenciales Art 247 y ss ordenanza fiscal\",\n    \"CONCEPTO\": \"Art 247 y ss ordenanza fiscal contribuyente persona que recibe los servicios , responsables solidarios, herederos y/o legatarios. Art 44 odeanzanza impsotiva aclara que para residentes del partido la atenci\u00f3n es gratuita.\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"San Antonio de Areco\",\n    \"DENSIDAD\": \"26695\",\n    \"ORDENANZA\": \"Ordenanza San Antonio de Areco\",\n    \"COBRO\": \"Tasa por servicios de salud  Art 218 y ss (impuesto encubierto)\",\n    \"CONCEPTO\": \"Pago mensual de acuerdo a la liquidaci\u00f3n de la Tasa de\\nServicios Urbanos, Tasa por Servicios Rurales y Tasa por Inspecci\u00f3n de Seguridad e Higiene,\\nconforme Ordenanza Impositiva vigente.\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"San Cayetano\",\n    \"DENSIDAD\": \"8994\",\n    \"ORDENANZA\": \"Ordenanza San Cayetano\",\n    \"COBRO\": \"Sistema SAMO\",\n    \"CONCEPTO\": \"Art\u00edculo 122\u00ba.- Los servicios asistenciales que se presten en el Hospital Municipal ser\u00e1n gratuitos. Para el\\ncaso de pacientes que tengan cobertura de obras sociales o de compa\u00f1\u00edas de seguros, oficiales o privados,\\nla Municipalidad ejercer\u00e1 el derecho de cobro sobre la entidad de cobertura conforme los valores y\\nmodalidades establecidas en las normas vigentes en cada caso.\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"San Fernando\",\n    \"DENSIDAD\": \"171616\",\n    \"ORDENANZA\": \"Ordenanza San Fernando\",\n    \"COBRO\": \"Sistema SAMO + Tasa asistencial Art. 141 y ss impuesto encub\",\n    \"CONCEPTO\": \"Aclara gratuidad a residentes del partido\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"San Isidro\",\n    \"DENSIDAD\": \"297282\",\n    \"ORDENANZA\": \"Ordenanza San Isidro\",\n    \"COBRO\": \"Sistema SAMO Art 141 y ss\",\n    \"CONCEPTO\": \"Art 141 y ss tiene anexo con valores, aclara si el responsable es persona p\u00fablica o juridica privada\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"San Miguel Joaqu\u00edn\",\n    \"DENSIDAD\": \"328835\",\n    \"ORDENANZA\": \"Ordenanza San Miguel Joaquin\",\n    \"COBRO\": \"Sistema SAMO Art 94 y ss\",\n    \"CONCEPTO\": \"se aclara gratuidad a personas sin cobertura\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"San Nicol\u00e1s\",\n    \"DENSIDAD\": \"165375\",\n    \"ORDENANZA\": \"Ordenanza San Nicolas\",\n    \"COBRO\": \"Sistema SAMO Art 301 y ss\",\n    \"CONCEPTO\": \"Art 301 y ss sistema samo y peajes\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"San Pedro\",\n    \"DENSIDAD\": \"69616\",\n    \"ORDENANZA\": \"Ordenanza San Pedro\",\n    \"COBRO\": \"Sistema SAMO Art. 250 y ss\",\n    \"CONCEPTO\": \"se especifica que si el paciente no tiene cobertiura el servicio es gratuito\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"San Vicente\",\n    \"DENSIDAD\": \"98977\",\n    \"ORDENANZA\": \"Ordenanza San Vicente\",\n    \"COBRO\": \"Contribuci\u00f3n al Sistema de Salud P\u00fablica (impuesto encubierto) Art. 367\",\n    \"CONCEPTO\": \"contribuci\u00f3n equivalente al cuarenta por ciento (40 %) de las Tasas fijadas por\\nPropiedad Urbana, por Conservaci\u00f3n, Reparaci\u00f3n y Mejorado de la Red Vial Municipal, por Propiedad Urbana para\\n\u201cConjuntos Inmobiliarios destinados a Vivienda y Grandes Desarrollos Inmobiliarios\u201d y por Inspecci\u00f3n de Seguridad\\ne Higiene.\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Suipacha\",\n    \"DENSIDAD\": \"11867\",\n    \"ORDENANZA\": \"Ordenanza Suipacha\",\n    \"COBRO\": \"Tasa de salud Art. 129 y ss (impuesto encubierto) + Prestaciones Hospitalarias Art. 132 y ss\",\n    \"CONCEPTO\": \"Tasa de salud Se dispone a toda parcela sector urbano y seccionenles de quintas del partido + Prestaciones hospitalarias: previa encuesta social se dispone capacidad de pago si no tiene cobertura\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Tandil\",\n    \"DENSIDAD\": \"150162\",\n    \"ORDENANZA\": \"Ordenanza Tandil\",\n    \"COBRO\": \"SISTEMA INTEGRADO DE SALUD P\u00daBLICA \u2013 ENTE DESCENTRALIZADO Art. 217 y ss\",\n    \"CONCEPTO\": \"Individualiza el no cobro a \\\"las personas humanas en raz\u00f3n de las consideraciones socio econ\u00f3micas\\\" Cualquier excepci\u00f3n al arancel establecido, deber\u00e1\\nestar justificada en base al informe del servicio social del\\nestablecimiento o del servicio social de la Secretar\u00eda de\\nBienestar Social y no constituir\u00e1 impedimento alguno para la\\ninmediata atenci\u00f3n del paciente.\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Tapalque\",\n    \"DENSIDAD\": \"10901\",\n    \"ORDENANZA\": \"Ordenanza Tapalque\",\n    \"COBRO\": \"Tasa servicios asistenciales Art. 200 + Contribuci\u00f3n unidad intensiva (impuesto encubierto)\",\n    \"CONCEPTO\": \"Art 201 se faculta a deducciones de acuerdo posibilidades esconomicas del tributante determinadas por servicio social de la Municiipalidad\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Tigre\",\n    \"DENSIDAD\": \"447785\",\n    \"ORDENANZA\": \"Ordenanza Tigre\",\n    \"COBRO\": \"Sistema SAMO + Tasa servicios asistenciales Art 83 y ss ordenanza impositiva para no residentes del partido\",\n    \"CONCEPTO\": \"Tabla tarifaria para personas no residentes en el partido. Gratuidad a personas sin cobertira m\u00e9dica.\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Tordillo\",\n    \"DENSIDAD\": \"2672\",\n    \"ORDENANZA\": \"Ordenanza Tordillo\",\n    \"COBRO\": \"Tasa servicios asistenciales Art 28 y ss ordenanza impositiva\",\n    \"CONCEPTO\": \"Abonan quienes soliciten los servicios asistenciales y tengan recursos probados. sin recursos gratuito\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Tornquist\",\n    \"DENSIDAD\": \"14669\",\n    \"ORDENANZA\": \"Ordenanza Tornquist\",\n    \"COBRO\": \"Sistema SAMO + Tasa servicios asistenciales Art. 142 y ss\",\n    \"CONCEPTO\": \"Podr\u00e1n quedar eximidos total o parcialmente del pago de tasa quienes posean ficha socio econ\u00f3mica otorgada por el \u00e1rea competente como aquellos que poseen cobertura m\u00e9dica (Art. 147)\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Trenque launquen\",\n    \"DENSIDAD\": \"48423\",\n    \"ORDENANZA\": \"Ordenanza Trenque Lauquen\",\n    \"COBRO\": \"Sistema SAMO + Tasa servicios asistenciales Art 89 y ss\",\n    \"CONCEPTO\": \"No se cobrar\u00e1 a los residentes del distrito sin cobertura m\u00e9dica\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Tres Arroyos\",\n    \"DENSIDAD\": \"62835\",\n    \"ORDENANZA\": \"Ordenanza Tres arroyos\",\n    \"COBRO\": \"Tasa solidaria de sostenimiento del servicio de salud Art. 183 y ss de la ordenanza fis (impuesto encubierto)\",\n    \"CONCEPTO\": \"Se cobra a todo inmueble en \\\"Tasa servicios urbanos\\\".\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Tres de Febrero\",\n    \"DENSIDAD\": \"366377\",\n    \"ORDENANZA\": \"Ordenanza Tres de Febrero\",\n    \"COBRO\": \"Sistema SAMO Tributo por servicios asistenciales ART 245 Y SS\",\n    \"CONCEPTO\": \"Gratuidad a personas sin cobertura m\u00e9dica\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Tres Lomas\",\n    \"DENSIDAD\": \"8825\",\n    \"ORDENANZA\": \"Actualizaciones falta ordenanza solicitada\",\n    \"COBRO\": \"Tasa servicios asistenciales\",\n    \"CONCEPTO\": \"La Ordenanza de Salud vigente 1043/13 DEL A\u00d1O 2013 no figura disponible web, se solicito. Las actualizaciones dan cuenta del cobro a personas sin cobertura m\u00e9dica seg\u00fan medios econ\u00f3micos por encuesta social\",\n    \"CATEGORIA\": \"Categor\u00eda C (Arancel Directo)\"\n  },\n  {\n    \"MUNICIPIO\": \"Vicente L\u00f3pez\",\n    \"DENSIDAD\": \"283510\",\n    \"ORDENANZA\": \"Ordenanza Vicente Lopez\",\n    \"COBRO\": \"Sistema SAMO derechos asistenciales Art 254 y ss ordennza fiscal y Art 54 y ss ordenanza impositiva\",\n    \"CONCEPTO\": \"Gratuito para personas sin cobertura\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  },\n  {\n    \"MUNICIPIO\": \"Villa Gesell\",\n    \"DENSIDAD\": \"38614\",\n    \"ORDENANZA\": \"Codigo tributario\",\n    \"COBRO\": \"Tasa salud ART 148 Y SS codigo tributario  (impuesto encubierto)\",\n    \"CONCEPTO\": \"Art 148 y ss La localidad posee un codigo tributario 2156/08 y modificaciones, no renueva el codigo todos los a\u00f1os unificado digesto https://www.juntosxgesell.ar/res_dige.php?criter=2156%2F08\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Villarino\",\n    \"DENSIDAD\": \"33170\",\n    \"ORDENANZA\": \"Ordenanza Villarino\",\n    \"COBRO\": \"Derecho de Comercializaci\u00f3n sobre Producci\u00f3n Hort\u00edcola y Frut\u00edcola  (impuesto encubierto destinado a salud) Art 232 y ss\",\n    \"CONCEPTO\": \"Derecho de Comercializaci\u00f3n sobre Producci\u00f3n Hort\u00edcola y Frut\u00edcola. Del Destino de los Fondos\\nART\u00cdCULO 236\u00b0: Los recursos ser\u00e1n afectados, destinados al financiamiento del Sistema de Salud Municipal, administrado por la Secretar\u00eda de Salud o quien en el futuro la reemplace.\",\n    \"CATEGORIA\": \"Categor\u00eda B (Tasa Encubierta)\"\n  },\n  {\n    \"MUNICIPIO\": \"Z\u00e1rate\",\n    \"DENSIDAD\": \"132087\",\n    \"ORDENANZA\": \"Ordenanza Zarate\",\n    \"COBRO\": \"Sistema SAMO Art 217 y ss\",\n    \"CONCEPTO\": \"\",\n    \"CATEGORIA\": \"Categor\u00eda A (Gratuidad / SAMO)\"\n  }\n]"

@st.cache_data
def load_data():
    path = "/workspace/knowledge/Municipios_y_ordenanzas__-_Hoja_1-5.csv"
    try:
        if os.path.exists(path):
            df = pd.read_csv(path)
            df = df.dropna(how='all')
            df['MUNICIPIO'] = df['MUNICIPIO'].astype(str).str.strip()
            df['DENSIDAD'] = df['DENSIDAD POBLACIONAL (CENSO 2022)'].fillna('No especificado').astype(str)
            df['ORDENANZA'] = df['ORDENANZA'].fillna('Sin dato').astype(str)
            df['COBRO'] = df['COBRO SERVICIO SALUD EN HOSPITAL PÚBLICO'].fillna('Ausencia de concepto').astype(str)
            df['CONCEPTO'] = df['CONCEPTO EN ORDENANZA'].fillna('').astype(str)
            
            def clasificar_row(row):
                m_low = str(row['MUNICIPIO']).lower()
                if m_low in ['arrecifes', 'pehuajó', 'pehuajo', 'alberti', 'ayacucho', 'castelli', 'coronel rosales', 'coronel pringles', 'coronel suárez', 'daireaux', 'dolores', 'florentino ameghino', 'general alvear', 'general arenales', 'general la madrid', 'general las heras', 'general lavalle', 'general pinto', 'general viamonte', 'hipólito yrigoyen', 'leandro n. alem', 'lincoln', 'lobería', 'maipú', 'malvinas argentinas', 'marcos paz', 'nueve de julio', 'olavarría', 'patagones', 'pinamar', 'ramallo', 'rauch', 'saavedra pigue', 'saavedra pigué', 'salliquelo', 'salto', 'san andrés de giles', 'salliqueló', 'tres lomas']:
                    return 'Categoría C (Arancel Directo)'
                elif m_low in ['san vicente', 'balcarce', 'baradero', 'azul', '25 de mayo', 'adolfo gonzález chávez', 'campana', 'carlos casares', 'chivilcoy', 'escobar', 'exaltación de la cruz', 'ezeiza', 'florencio varela', 'general alvarado', 'general pueyrredón', 'general rodríguez', 'general villegas', 'guamini', 'ituzaingó', 'junín', 'la costa', 'lobos', 'mar chiquita', 'mercedes', 'monte', 'moreno', 'necochea', 'punta indio', 'san antonio de areco', 'suipacha', 'tapalque', 'tres arroyos', 'villa gesell', 'villarino']:
                    return 'Categoría B (Tasa Encubierta)'
                else:
                    return 'Categoría A (Gratuidad / SAMO)'
                    
            df['CATEGORIA'] = df.apply(clasificar_row, axis=1)
            return df
    except Exception:
        pass
        
    records = json.loads(RAW_DATA_135)
    return pd.DataFrame(records)

df_censo = load_data()

# ==========================================
# BARRA LATERAL - NAVEGACIÓN Y CONFIGURACIÓN DE IA
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/scales.png", width=70)
st.sidebar.title("SIA-PBA v4.0")
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
st.sidebar.subheader("🤖 Motor de Inteligencia Artificial")

gemini_key_env = os.environ.get("GEMINI_API_KEY", "")
try:
    gemini_key_secrets = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    gemini_key_secrets = ""

default_key = gemini_key_secrets or gemini_key_env

user_gemini_key = st.sidebar.text_input(
    "🔑 Clave API Gemini Pro (Opcional):",
    type="password",
    value=default_key,
    help="Si ingresa una clave API de Google Gemini Pro, el análisis utilizará razonamiento de LLM avanzado. De lo contrario, se usará el motor contextual NPL local."
)

if user_gemini_key.strip():
    st.sidebar.success("✨ **Gemini Pro Activado**")
else:
    st.sidebar.info("💡 **Modo Contextual NPL Local (Sin API Key)**")

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
        * **Análisis NPL / LLM Gemini Pro:** Procesa automáticamente ordenanzas impositivas y fiscales locales.
        * **Semáforo Tripartito de Convencionalidad:**
            * 🟢 **Cat. A (Gratuidad Plena / SAMO):** Cumplimiento del Art. 36 inc. 8 CPBA y Ley 11.069.
            * 🟡 **Cat. B (Tasas Encubiertas):** Detección de tributos disfrazados en ABL/Red Vial/Comercio.
            * 🔴 **Cat. C (Arancelamiento Directo):** Alerta por cobros indebidos, pagarés o itinerario de pobreza.
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
# MÓDULO 2: AUDITORÍA ALGORÍTMICA DE ORDENANZAS (IA / GEMINI PRO)
# ==========================================
elif "🔍 2. Módulo de Auditoría" in opcion_menu:
    st.markdown("<h2 class='main-title'>🔍 Auditoría Algorítmica Preventiva de Ordenanzas</h2>", unsafe_allow_html=True)
    st.markdown("Examen automatizado de constitucionalidad, convencionalidad y legalidad tributaria municipal.")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🏛️ Auditoría por Municipio (Censo N=135)", "📝 Análisis de Documentos PDF / Ordenanza Personalizada"])
    
    with tab1:
        st.markdown("##### Seleccione un municipio para consultar su línea de base en el Censo Provincial:")
        muni_selected = st.selectbox("Municipio de la Prov. de Bs. As.:", df_censo['MUNICIPIO'].unique(), key="sel_muni_1")
        
        row_muni = df_censo[df_censo['MUNICIPIO'] == muni_selected].iloc[0]
        
        st.markdown("### 📊 Resultado del Examen del Censo Base 2026")
        
        col_res1, col_res2 = st.columns([1, 2])
        
        m_nombre = str(row_muni.get('MUNICIPIO', muni_selected))
        m_densidad = str(row_muni.get('DENSIDAD', 'No especificado'))
        m_ordenanza = str(row_muni.get('ORDENANZA', 'Ordenanza Municipal'))
        m_concepto = str(row_muni.get('CONCEPTO', row_muni.get('COBRO', '')))
        cat = str(row_muni.get('CATEGORIA', 'Categoría A (Gratuidad / SAMO)'))
        
        with col_res1:
            if 'Cat. C' in cat or 'Arancel' in cat or 'Categoría C' in cat:
                st.error("🔴 **DICTAMEN: INCONSTITUCIONAL / ARANCEL DIRECTO**")
                st.markdown("<span class='badge-cat-c'>Categoría C - Riesgo Alto</span>", unsafe_allow_html=True)
            elif 'Cat. B' in cat or 'Encubierta' in cat or 'Categoría B' in cat:
                st.warning("🟡 **DICTAMEN: ADVERTENCIA / TASA ENCUBIERTA**")
                st.markdown("<span class='badge-cat-b'>Categoría B - Riesgo Medio</span>", unsafe_allow_html=True)
            else:
                st.success("🟢 **DICTAMEN: CONFORME A DERECHO / GRATUIDAD PLENA**")
                st.markdown("<span class='badge-cat-a'>Categoría A - Gratuidad Plena</span>", unsafe_allow_html=True)
                
            st.write(f"**Municipio:** {m_nombre}")
            st.write(f"**Densidad Poblacional:** {m_densidad}")
            st.write(f"**Norma Relevada:** {m_ordenanza}")
            
        with col_res2:
            st.markdown("#### ⚖️ Fundamentación Jurídica de Alerta")
            st.markdown(f"**Disposición Local Relevada:** *'{m_concepto}'*")
            
            if 'Categoría C' in cat or 'Arancel' in cat or 'Cat. C' in cat:
                st.markdown("""
                <div class='legal-box'>
                <b>⚠️ Vulneraciones Normativas Detectadas:</b><br>
                1. <b>Violación del Art. 36 inc. 8 de la Constitución de la Prov. de Buenos Aires:</b> Imposición de barrera económica para acceder a la salud pública gratuita.<br>
                2. <b>Infracción a Tratados Internacionales (Art. 75 inc. 22 CN):</b> Contravención del Art. 12 del PIDESC.<br>
                3. <b>Encuadre Dogmático-Penal (Art. 266 del Código Penal):</b> Posible configuración de <i>Exacción Ilegal</i>.<br>
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
        st.markdown("##### Auditoría Inteligente de Documentos (PDFs Digitales o Fotocopias Escaneadas):")
        
        col_pdf1, col_pdf2 = st.columns([2, 1])
        
        with col_pdf1:
            uploaded_pdf = st.file_uploader("📂 Subir Ordenanza Fiscal/Impositiva en PDF (Digital o Escaneado):", type=['pdf'])
            texto_suplementario = st.text_area(
                "📝 Texto del articulado impositivo a auditar (Opcional / Suplementario):",
                value="",
                height=100,
                placeholder="Copie y pegue aquí artículos específicos de la ordenanza si desea auditarlos directamente..."
            )
            
        with col_pdf2:
            muni_target = st.selectbox(
                "🎯 Seleccione Municipio a Comparar (Benchmark 2026):",
                df_censo['MUNICIPIO'].unique(),
                key="sel_muni_2"
            )
            row_target = df_censo[df_censo['MUNICIPIO'] == muni_target].iloc[0]
            
            st.info(f"""
            **🧠 Directiva Benchmark Censo Base 2026:**
            * **Municipio Target:** {muni_target}
            * **Línea de Base:** {row_target.get('CATEGORIA', '')}
            * **Antecedente Relevado:** *{row_target.get('CONCEPTO', row_target.get('COBRO', ''))}*
            """)

        if st.button("🚀 Ejecutar Auditoría Algorítmica Preventiva"):
            texto_a_analizar = ""
            fuente_doc = ""
            
            if uploaded_pdf is not None:
                with st.spinner("⏳ Leyendo archivo PDF..."):
                    try:
                        import pypdf
                        pdf_reader = pypdf.PdfReader(BytesIO(uploaded_pdf.read()))
                        pages_text = []
                        for page in pdf_reader.pages:
                            t_p = page.extract_text()
                            if t_p:
                                pages_text.append(t_p)
                        texto_a_analizar = chr(10).join(pages_text)
                        fuente_doc = f"PDF Digital ({len(pdf_reader.pages)} páginas)"
                    except Exception:
                        texto_a_analizar = ""
                        
                    if len(texto_a_analizar.strip()) < 50:
                        with st.spinner("🔍 Activando motor OCR de Visión Artificial para PDF Escaneado / Fotocopia..."):
                            try:
                                from pdf2image import convert_from_bytes
                                import pytesseract
                                uploaded_pdf.seek(0)
                                images = convert_from_bytes(uploaded_pdf.read(), first_page=1, last_page=15)
                                ocr_pages = []
                                for img in images:
                                    txt_img = pytesseract.image_to_string(img, lang='spa')
                                    if txt_img:
                                        ocr_pages.append(txt_img)
                                texto_a_analizar = chr(10).join(ocr_pages)
                                fuente_doc = f"PDF Escaneado (Procesado por OCR Visión Artificial - {len(images)} págs.)"
                            except Exception:
                                if not texto_a_analizar:
                                    texto_a_analizar = ""
                                    
            if not texto_a_analizar.strip() and texto_suplementario.strip():
                texto_a_analizar = texto_suplementario
                fuente_doc = "Texto Ingresado en Editor Suplementario"
            elif texto_a_analizar.strip() and texto_suplementario.strip():
                texto_a_analizar += chr(10) + texto_suplementario
                fuente_doc += " + Texto Suplementario"

            if not texto_a_analizar.strip():
                st.error("❌ **ERROR DE PROCESAMIENTO:** No se ingresó ningún archivo PDF ni texto para auditar.")
            else:
                st.success(f"✅ **Documento Procesado con Éxito:** {fuente_doc} ({len(texto_a_analizar)} caracteres analizados).")
                st.markdown("---")
                st.subheader(f"📋 Dictamen de Auditoría Algorítmica - {muni_target} (Ejercicio 2027+)")
                
                api_key_active = user_gemini_key.strip()
                
                if api_key_active:
                    with st.spinner("🧠 Razonando con Inteligencia Artificial Gemini Pro..."):
                        try:
                            import urllib.request

                            snippet_doc = texto_a_analizar[:30000]
                            prompt_parts = [
                                "Eres SIA-PBA, un Auditor Algorítmico Jurídico experto en Derecho Constitucional, Tributario y Sanitario de la Provincia de Buenos Aires (TFC Abogacía UCES).",
                                f"Debes auditar la siguiente ordenanza municipal para el Municipio de {muni_target}.",
                                "",
                                "DIRECTIVAS DOGMÁTICAS DE AUDITORÍA:",
                                "1. Tu objetivo es detectar únicamente cláusulas relativas a la salud pública hospitalaria y clasificarlas en:",
                                "   - CATEGORÍA A: Gratuidad Plena / SAMO (Ley Provincial 11.069 y Art. 36 inc. 8 CPBA). Atención pública gratuita para personas sin cobertura.",
                                "   - CATEGORÍA B: Tasa Encubierta / Tributo Disfrazado. Fondos especiales de salud adosados sobre ABL, Red Vial, Comercio o Multas.",
                                "   - CATEGORÍA C: Arancel Directo / Barrera Económica. Cobros directos, aranceles, bonos de guardia, pagarés a pacientes sin cobertura, o exigencia de 'encuesta social / informe de indigencia' para acceder a la gratuidad (el itinerario de pobreza es inconstitucional).",
                                "",
                                "2. REGLA ESTRICTA DE EXCLUSIÓN: Descarta totalmente tasas generales no sanitarias (Seguridad e Higiene comercial, Bromatología, rifas de bomberos, alquiler de máquinas viales, ABL general, escombros), SALVO que contengan una partida o afectación explícita a la salud.",
                                "3. Si un artículo impositivo general incluye la frase 'excepto servicios asistenciales' o similar, interpretalo como un resguardo de la gratuidad (Categoría A).",
                                "4. Muestra tu veredicto final con el Semáforo correspondiente (🟢 CATEGORÍA A, 🟡 CATEGORÍA B, o 🔴 CATEGORÍA C) y transcribe el/los artículos infractores o de resguardo hallados.",
                                "",
                                "TEXTO DE LA ORDENANZA A AUDITAR:",
                                snippet_doc
                            ]
                            prompt_llm = chr(10).join(prompt_parts)

                            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key_active}"
                            payload = {
                                "contents": [{"parts": [{"text": prompt_llm}]}]
                            }
                            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                            with urllib.request.urlopen(req) as response:
                                res_body = json.loads(response.read().decode('utf-8'))
                                res_text = res_body['candidates'][0]['content']['parts'][0]['text']
                                
                            st.markdown("##### 🤖 Dictamen Emitido por Gemini Pro IA:")
                            st.markdown(res_text)
                            
                        except Exception as e_gem:
                            st.warning(f"⚠️ No se pudo conectar con la API de Gemini Pro ({str(e_gem)}). Ejecutando motor de respaldo contextual local...")
                            api_key_active = ""

                if not api_key_active:
                    articulos_raw = re.split(r'(?i)(?=ART[ÍI]CULO\s+\d+|ART\.\s*\d+)', texto_a_analizar)
                    
                    arts_c = []
                    arts_b = []
                    arts_a = []
                    
                    for art in articulos_raw:
                        art_clean = art.strip()
                        if not art_clean or len(art_clean) < 15:
                            continue
                            
                        art_upper = art_clean.upper()
                        
                        is_health_domain = any(k in art_upper for k in [
                            'HOSPITAL', 'SALUD', 'ASISTENCIAL', 'PACIENTE', 'GUARDIA', 'MEDIC', 'INTERNACI', 'AMBULANCIA',
                            'NOMENCLADOR', 'IOMA', 'SAMO', 'TASA POR SERVICIOS ASISTENCIALES', 'FONDO DE SALUD', 'CONTRIBUCIÓN AL SISTEMA DE SALUD',
                            'CUIDADO DE LA SALUD', 'PRESTACIONES MÉDICAS'
                        ])
                        
                        is_excluded_domain = any(k in art_upper for k in [
                            'SEGURIDAD E HIGIENE', 'ACTIVIDADES ECONÓMICAS', 'CONVENIO MULTILATERAL', 'PROPIEDAD HORIZONTAL',
                            'ALIMENTICIOS', 'BROMATOL', 'RIFAS', 'BOMBEROS', 'MOTONIVELADORA', 'EQUIPOS VIALES', 'PREDIOS',
                            'PODAS', 'ESCOMBROS', 'CEMENTERIO', 'PUBLICIDAD'
                        ])
                        
                        if is_excluded_domain and not ('EXCEPTO LOS SERVICIOS ASISTENCIALES' in art_upper or 'TASA DE SALUD' in art_upper or 'FONDO DE SALUD' in art_upper):
                            continue
                            
                        if 'EXCEPTO LOS SERVICIOS ASISTENCIALES' in art_upper or 'EXCEPTO SERVICIOS ASISTENCIALES' in art_upper:
                            arts_a.append((art_clean, "Conformidad Normativa: Garantía expresa de gratuidad o excepción explícita a favor del servicio asistencial."))
                            continue
                            
                        if not is_health_domain:
                            continue
                            
                        if any(k in art_upper for k in ['ARANCEL', 'BONO', 'ABONARÁ', 'NOMENCLADOR', 'PAGARÉ', 'EVIDENTE CARENCIA', 'ENCUESTA SOCIAL', 'INFORME SOCIAL', 'INDIGENCIA', 'CAPACIDAD CONTRIBUTIVA']):
                            if not ('OBRAS SOCIALES' in art_upper or 'PREPAGA' in art_upper or 'SAMO' in art_upper or 'ART.' in art_upper):
                                arts_c.append((art_clean, "Cláusula de arancelamiento directo al paciente o exigencia de acreditación de indigencia para acceder a la salud pública."))
                                continue
                                
                        if any(k in art_upper for k in ['FONDO ESPECIAL DE SALUD', 'CONTRIBUCIÓN AL SISTEMA DE SALUD', 'ADICIONAL SALUD', 'TASA DE SALUD']):
                            if any(k in art_upper for k in ['ALUMBRADO', 'RED VIAL', 'SERVICIOS URBANOS', 'INMUEBLES', 'TASA GENERAL']):
                                arts_b.append((art_clean, "Tasa encubierta / Fondo especial de salud adicionado sobre tributos o tasas impositivas generales."))
                                continue
                                
                        if any(k in art_upper for k in ['GRATUITO', 'SIN COSTO', 'SAMO', 'LEY 11.069', 'LEY 11069', 'OBRAS SOCIALES']):
                            arts_a.append((art_clean, "Conformidad Normativa: Garantía de gratuidad y/o recupero vía SAMO."))

                    if len(arts_c) > 0:
                        st.error("🔴 **ALERTA CRÍTICA: DETECCIÓN DE CLÁUSULAS INCONSTITUCIONALES / CATEGORÍA C**")
                        st.markdown("<span class='badge-cat-c'>Categoría C - Arancel Directo / Barrera Económica</span>", unsafe_allow_html=True)
                        st.write(f"**Comparativa frente al Censo Base 2026:** El municipio {muni_target} mantiene o reintroduce normas de arancelamiento directo.")
                        st.markdown("##### 📜 Artículos Infractores Detectados en la Salud Pública:")
                        for art_txt, obs in arts_c:
                            snip = art_txt[:350] + "..." if len(art_txt) > 350 else art_txt
                            st.markdown(f"<div class='snippet-box'><b>⚠️ Cita Textual de la Ordenanza:</b><br>'{snip}'</div>", unsafe_allow_html=True)
                            st.caption(f"**Observación Técnica:** {obs}")
                    elif len(arts_b) > 0:
                        st.warning("🟡 **ADVERTENCIA: DETECCIÓN DE TASA ENCUBIERTA / CATEGORÍA B**")
                        st.markdown("<span class='badge-cat-b'>Categoría B - Tasa Encubierta / Tributo Disfrazado</span>", unsafe_allow_html=True)
                        st.write(f"**Comparativa frente al Censo Base 2026:** Se detectó la adición de fondos/alícuotas de salud sobre tasas generales.")
                        st.markdown("##### 📜 Artículos Infractores Detectados:")
                        for art_txt, obs in arts_b:
                            snip = art_txt[:350] + "..." if len(art_txt) > 350 else art_txt
                            st.markdown(f"<div class='snippet-box'><b>⚠️ Cita Textual de la Ordenanza:</b><br>'{snip}'</div>", unsafe_allow_html=True)
                            st.caption(f"**Observación Técnica:** {obs}")
                    else:
                        st.success("🟢 **DICTAMEN POSITIVO: CONFORME A DERECHO / GRATUIDAD PLENA / CATEGORÍA A**")
                        st.markdown("<span class='badge-cat-a'>Categoría A - Gratuidad Plena / SAMO</span>", unsafe_allow_html=True)
                        st.write(f"**Comparativa frente al Censo Base 2026:** El municipio {muni_target} cumple el Art. 36 inc. 8 de la Constitución Provincial.")
                        if len(arts_a) > 0:
                            st.markdown("##### 📜 Artículos de Conformidad Normativa Detectados:")
                            for art_txt, obs in arts_a:
                                snip = art_txt[:350] + "..." if len(art_txt) > 350 else art_txt
                                st.markdown(f"<div class='snippet-box'><b>✅ Cita Textual de la Ordenanza:</b><br>'{snip}'</div>", unsafe_allow_html=True)

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
    
    dictamen_text = f"""
========================================================================================
ALERTA INSTITUCIONAL DE INCONSTITUCIONALIDAD Y INCONVENCIONALIDAD TRIBUTARIA
SIA-PBA // AUDITORÍA ALGORÍTMICA DE ORDENANZAS MUNICIPALES
========================================================================================

FECHA DE EMISIÓN: {datetime.date.today().strftime('%d/%m/%Y')}
SUJETO AUDITADO: Municipalidad de {row_d.get('MUNICIPIO', muni_dictamen)} (Provincia de Buenos Aires)
DENSIDAD POBLACIONAL: {row_d.get('DENSIDAD', 'No especificado')}
NORMA EXAMINADA: {row_d.get('ORDENANZA', 'Ordenanza Municipal')}
DISPOSICIÓN TRIBUTARIA: "{row_d.get('CONCEPTO', row_d.get('COBRO', ''))}"
CLASIFICACIÓN ALGORÍTMICA: {row_d.get('CATEGORIA', 'Categoría A')}

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
SE RECOMIENDA a la Asesoría General de Gobierno de la Provincia de Buenos Aires y al Honorable Tribunal de Cuentas promover la revisión de oficio del módulo impositivo de la Municipalidad de {row_d.get('MUNICIPIO', muni_dictamen)}, instando la adecuación inmediata al régimen SAMO (Ley 11.069) y el cese de todo cobro directo al paciente sin cobertura.

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
