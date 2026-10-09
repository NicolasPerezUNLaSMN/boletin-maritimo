def leer_reporte_hielos(archivo):
    """
    Lee el TXT de hielos y separa el bloque en inglés
    del bloque en español.
    """

    contenido = archivo.getvalue().decode(
        "utf-8",
        errors="replace",
    )

    marcador_espanol = (
        "INFORME DE HIELOS MARINOS Y TEMPANOS"
    )

    if marcador_espanol not in contenido:
        return {
            "ingles": contenido.strip(),
            "espanol": "",
        }

    texto_ingles, texto_espanol = contenido.split(
        marcador_espanol,
        1,
    )

    texto_espanol = (
        marcador_espanol
        + texto_espanol
    )

    # Eliminar la última línea del bloque inglés
    lineas_ingles = texto_ingles.strip().splitlines()
    if lineas_ingles:
        lineas_ingles.pop()
    texto_ingles = "\n".join(lineas_ingles)

    # Eliminar la última línea del bloque español
    lineas_espanol = texto_espanol.strip().splitlines()
    if lineas_espanol:
        lineas_espanol.pop()
    texto_espanol = "\n".join(lineas_espanol)

    return {
        "ingles": texto_ingles,
        "espanol": texto_espanol,
    }