from __future__ import annotations

import xml.etree.ElementTree as ET

import streamlit as st

from parser_viento import generar_pronostico, leer_xml


st.set_page_config(
    page_title="Boletín Marítimo",
    page_icon="🌊",
    layout="wide",
)

st.title("🌊 Boletín Marítimo")
st.subheader("Prueba del pronóstico desde XML")

archivo_xml = st.file_uploader(
    "Subir XML del pronóstico",
    type=["xml"],
)

if archivo_xml is not None:
    try:
        datos = leer_xml(archivo_xml)
        texto = generar_pronostico(datos)

        st.success(
            f"XML procesado correctamente. Áreas encontradas: {len(datos)}"
        )

        st.text_area(
            "Pronóstico generado",
            value=texto,
            height=600,
        )

        st.download_button(
            label="Descargar pronóstico TXT",
            data=texto,
            file_name="pronostico_metarea.txt",
            mime="text/plain",
        )

    except ET.ParseError as error:
        st.error(f"El archivo no es un XML válido: {error}")

    except Exception as error:
        st.exception(error)