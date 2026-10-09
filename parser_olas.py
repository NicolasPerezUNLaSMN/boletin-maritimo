import re


def es_nombre_area(linea):
    """
    Determina si una línea corresponde al nombre de un área.
    """

    if not linea:
        return False

    linea = linea.strip()

    if re.match(r"^\d{6}\s*-\s*\d{6}\s*UTC$", linea):
        return False

    if linea.startswith("WARNING"):
        return False

    if linea.startswith("PRONOSTICO"):
        return False

    palabras_prohibidas = [
        "UTC",
        "MOVING",
        "BUILDING",
        "DECAYING",
        "TEMPORARY",
        "SLIGHTLY",
        "LITTLE CHANGE",
        "WITHOUT",
        "IN THE",
        "AT ",
    ]

    for palabra in palabras_prohibidas:
        if palabra in linea:
            return False

    return linea == linea.upper()


def parse_boletin(archivo):
    """
    Lee un TXT subido por Streamlit y devuelve la estructura del boletín.
    """

    if hasattr(archivo, "seek"):
        archivo.seek(0)

    contenido = archivo.read()

    if isinstance(contenido, bytes):
        contenido = contenido.decode("utf-8", errors="replace")

    lineas = contenido.splitlines()

    datos = {
        "encabezado": "",
        "areas": [],
    }

    area_actual = None
    periodo_actual = None

    for linea in lineas:
        linea = linea.strip()

        if not linea:
            continue

        if linea.startswith("PRONOSTICO"):
            datos["encabezado"] = linea
            continue

        if es_nombre_area(linea):
            area_actual = {
                "nombre": linea,
                "periodos": [],
            }

            datos["areas"].append(area_actual)
            periodo_actual = None
            continue

        if re.match(r"^\d{6}\s*-\s*\d{6}\s*UTC$", linea):
            periodo_actual = {
                "periodo": linea,
                "mensajes": [],
            }

            if area_actual is not None:
                area_actual["periodos"].append(periodo_actual)

            continue

        if area_actual is None or periodo_actual is None:
            continue

        if linea.startswith("WARNING:"):
            periodo_actual["mensajes"].append(
                {
                    "tipo": "warning",
                    "texto": linea.replace("WARNING:", "", 1).strip(),
                }
            )
        else:
            periodo_actual["mensajes"].append(
                {
                    "tipo": "forecast",
                    "texto": linea,
                }
            )

    return datos


def olas_por_area(datos_olas):
    """
    Devuelve:
    {
        "AREA DRAKE": "texto completo de olas",
        ...
    }
    """

    resultado = {}

    for area in datos_olas["areas"]:
        nombre = area["nombre"].upper().strip()
        fragmentos = []

        for periodo in area["periodos"]:
            for mensaje in periodo["mensajes"]:
                texto = mensaje["texto"].strip()

                if mensaje["tipo"] == "warning":
                    fragmentos.append(f"WARNING: {texto}")
                else:
                    fragmentos.append(texto)

        resultado[nombre] = " ".join(fragmentos).strip()

    return resultado