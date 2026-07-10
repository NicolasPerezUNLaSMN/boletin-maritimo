from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import BinaryIO


HORAS = [12, 18, 24, 30, 36]

WW = {
    3: "CLR",
    13: "FEW CLD",
    19: "SCT CLD",
    25: "PTLY CLDY",
    37: "BKN",
    43: "OVC",
    51: "WINDY",
    61: "BR",
    67: "FG",
    69: "FZFG",
    71: "DZ",
    72: "ISOL RA",
    73: "RA",
    74: "SHRA",
    76: "ISOL TS",
    77: "RASN",
    79: "SN",
    80: "SHRA",
    81: "SHRA",
    82: "HVY SHRA",
    85: "HVY RA",
    89: "HVY TS",
    92: "BLSN",
    94: "BS",
    96: "DRSN"
}

WW_NUBOSIDAD = {3, 13, 19, 25, 37, 43}

DIRECCIONES = {
    "N":0,
    "NNE":22.5,
    "NE":45,
    "ENE":67.5,
    "E":90,
    "ESE":112.5,
    "SE":135,
    "SSE":157.5,
    "S":180,
    "SSW":202.5,
    "SW":225,
    "WSW":247.5,
    "W":270,
    "WNW":292.5,
    "NW":315,
    "NNW":337.5
}

ABREV = {
    "BECOMING": "BECMG",
    "VEERING": "VEER",
    "BACKING": "BACK",
    "INCREASING": "INCR",
    "DECREASING": "DECR",
    "GUST": "G",
     "THEN": "THEN"
}


ORDEN_AREAS = [

    "RIO DE LA PLATA INTERIOR",
    "RIO DE LA PLATA EXTERIOR",
    "RIO DE LA PLATA INTERMEDIO",

    "OFFSHORE RIO DE LA PLATA",
    "OFFSHORE MAR DEL PLATA",
    "OFFSHORE BAHIA BLANCA",
    "OFFSHORE VALDES",
    "OFFSHORE SAN JORGE",
    "OFFSHORE PATAGONIA SUR",
    "OFFSHORE FIN DEL MUNDO",

    "ZONA MALVINAS",

    "AREA NORTE (N 40S E30W)",
    "AREA NORTE (N 40S E40 W30)",
    "AREA NORTE (N 40S W 40W)"
]




def texto_fenomeno(ww):

    if ww is None:
        return ""

    ww = int(ww)

    # Ignorar fenómenos que solo representan nubosidad
    if ww in WW_NUBOSIDAD:
        return ""

    return WW.get(ww, "")


def texto_visibilidad(vis):
    if vis is None:
        return ""

    vis = int(vis)

    if vis >= 10000:
        return "VIS GOOD"
    elif vis >= 5000:
        return "VIS MOD"
    elif vis >= 1000:
        return "VIS POOR"
    else:
        return "VIS VERY POOR"


def texto_viento_estado(p):
    direccion = p.get("direccion")

    viento = kt_a_beaufort(p.get("viento_kt"))
    rafaga = kt_a_beaufort(p.get("rafagas_kt", 0))

    texto = f"{direccion} {viento}"

    if rafaga > viento:
       texto += f" {ABREV['GUST']}{rafaga}"

    return texto


def es_veering(dir1, dir2):
    a = DIRECCIONES[dir1]
    b = DIRECCIONES[dir2]
    delta = (b - a) % 360
    return delta < 180


def evolucion_viento(pronos):
    partes = []
    previo = None
    texto_previo = None

    for h in HORAS:
        if h not in pronos:
            continue

        actual = pronos[h]
        texto_actual = texto_viento_estado(actual)

        # No repetir si no cambió nada
        if texto_actual == texto_previo:
            continue

        if previo is None:
            partes.append(texto_actual)
        else:
            cambios = []

            if actual["direccion"] != previo["direccion"]:
                if es_veering(previo["direccion"], actual["direccion"]):
                    cambios.append(ABREV["VEERING"])
                else:
                    cambios.append(ABREV["BACKING"])

            if actual["viento_kt"] > previo["viento_kt"]:
                cambios.append(ABREV["INCREASING"])
            elif actual["viento_kt"] < previo["viento_kt"]:
                cambios.append(ABREV["DECREASING"])

            cambios.append(texto_actual)
            partes.append(" ".join(cambios))

        previo = actual
        texto_previo = texto_actual

    return f" {ABREV['THEN']} ".join(partes) + "."


def evolucion_tiempo(pronos):

    partes = []
    previo = None

    for h in HORAS:

        if h not in pronos:
            continue

        actual = texto_fenomeno(pronos[h].get("ww"))

        if not actual:
            continue

        if actual == previo:
            continue

        partes.append(actual)
        previo = actual

    if not partes:
        return "NOSIG WX."

    return f" {ABREV['BECOMING']} ".join(partes) + "."


def evolucion_visibilidad(pronos):
    partes = []
    previo = None

    for h in HORAS:
        if h not in pronos:
            continue

        actual = texto_visibilidad(pronos[h].get("visibilidad"))

        if not actual:
            continue

        if actual == previo:
            continue

        partes.append(actual)
        previo = actual

    return f" {ABREV['BECOMING']} ".join(partes) + "."


def evolucion_viento(pronos):

    partes = []

    previo = None

    for h in HORAS:

        if h not in pronos:
            continue

        actual = pronos[h]

        direccion = actual["direccion"]
        viento = actual["viento_kt"]
        rafaga = actual.get("rafagas_kt", 0)

        texto = f"{direccion} {viento}KT"

        if rafaga > viento:
            texto += f" GUST {rafaga}KT"

        if previo is None:
            partes.append(texto)

        else:

            cambios = []

            # Dirección
            if direccion != previo["direccion"]:

                if es_veering(previo["direccion"], direccion):
                    cambios.append("VEERING")

                else:
                    cambios.append("BACKING")

            # Intensidad
            if viento > previo["viento_kt"]:
                cambios.append("INCREASING")

            elif viento < previo["viento_kt"]:
                cambios.append("DECREASING")

            cambios.append(texto)

            partes.append(" ".join(cambios))

        previo = actual

    return " THEN ".join(partes) + "."





def texto_visibilidad(vis):

    if vis is None:
        return ""

    if vis >= 10000:
        return "VIS GOOD"

    elif vis >= 5000:
        return "VIS FAIR"

    elif vis >= 2000:
        return "VIS MOD"

    elif vis >= 1000:
        return "VIS POOR"

    else:
        return "VIS VERY POOR"
    

def texto_viento(dir, viento, rafaga=None):

    texto = f"{dir} {viento}KT"

    if rafaga is not None and rafaga > viento:
        texto += f" GUST {rafaga}KT"

    return texto


def texto_fenomeno(ww):

    return WW.get(ww, "")

def texto_visibilidad(vis):

    if vis is None:
        return ""

    if vis >= 10000:
        return "VIS GOOD"

    elif vis >= 5000:
        return "VIS FAIR"

    elif vis >= 2000:
        return "VIS MOD"

    elif vis >= 1000:
        return "VIS POOR"

    else:
        return "VIS VERY POOR"
    

def generar_linea(datos):

    partes = []

    # viento
    partes.append(
        texto_viento(
            datos["direccion"],
            datos["viento_kt"],
            datos.get("rafagas_kt", 0)
        )
    )

    # fenómeno
    fenomeno = texto_fenomeno(datos.get("ww"))

    if fenomeno:
        partes.append(fenomeno)

    # visibilidad
    vis = texto_visibilidad(datos.get("visibilidad"))

    if vis:
        partes.append(vis)

    return ", ".join(partes) + "."

def buscar_valor(parametro, unidad_buscada):
    """
    Devuelve un diccionario:
    hora -> valor
    para la unidad solicitada.
    """

    datos = {}

    # Busca todos los nodos que tengan un valor
    for nodo in parametro.iter():

        # Hora
        hora = nodo.attrib.get("time") \
            or nodo.attrib.get("date") \
            or nodo.attrib.get("from")

        # Unidad
        unidad = nodo.attrib.get("units") \
            or nodo.attrib.get("unit")

        # Valor
        valor = nodo.attrib.get("value")

        if valor is None and nodo.text:
            valor = nodo.text.strip()

        if unidad == unidad_buscada and hora is not None:

            datos[hora] = valor

    return datos


def buscar_cardinal(parametro):

    datos = {}

    for nodo in parametro.iter():

        hora = nodo.attrib.get("time") \
            or nodo.attrib.get("date") \
            or nodo.attrib.get("from")

        unidad = nodo.attrib.get("units") \
            or nodo.attrib.get("unit")

        valor = nodo.attrib.get("value")

        if valor is None and nodo.text:
            valor = nodo.text.strip()

        if unidad == "CARD" and hora is not None:

            datos[hora] = valor

    return datos

def kt_a_beaufort(kt):

    kt = float(kt)

    if kt < 1:
        return 0
    elif kt < 4:
        return 1
    elif kt < 7:
        return 2
    elif kt < 11:
        return 3
    elif kt < 17:
        return 4
    elif kt < 22:
        return 5
    elif kt < 28:
        return 6
    elif kt < 34:
        return 7
    elif kt < 41:
        return 8
    elif kt < 48:
        return 9
    elif kt < 56:
        return 10
    elif kt < 64:
        return 11
    else:
        return 12


def leer_xml(archivo: str | BinaryIO) -> dict:
    """
    Lee el XML meteorológico desde una ruta o un archivo subido
    por Streamlit y devuelve los datos organizados por área y horizonte.
    """

    if hasattr(archivo, "seek"):
        archivo.seek(0)


    tree = ET.parse(archivo)
    root = tree.getroot()

    resultado = {}

    # Acá continúa tu parser estable de Colab...

    for area in root.findall(".//area"):

        nombre = area.findtext("name")

        if not nombre:
            continue

        resultado[nombre] = {}

        for parametro in area.findall("parameter"):

            pid = parametro.attrib["id"]

            for timerange in parametro.findall("timerange"):

                h = int(timerange.attrib["h"])

                if h not in resultado[nombre]:
                     resultado[nombre][h] = {}

                # Dirección
                if pid == "wd":

                    for value in timerange.findall("value"):

                        if value.attrib.get("unit") == "CARD":
                            resultado[nombre][h]["direccion"] = value.text

                # Viento
                elif pid == "ws":

                    for value in timerange.findall("value"):

                        if value.attrib.get("unit") == "Kt":
                            resultado[nombre][h]["viento_kt"] = int(float(value.text))

                # Rafagas
                elif pid == "gust":

                    for value in timerange.findall("value"):

                        if value.attrib.get("unit") == "Kt":
                            resultado[nombre][h]["rafagas_kt"] = int(float(value.text))

                # Probabilidad
                elif pid == "proba_rain":

                    valor = timerange.find("value")

                    if valor is not None:
                        resultado[nombre][h]["probabilidad"] = int(float(valor.text))

                # Tiempo presente
                elif pid == "ww":

                   valor = timerange.find("value")

                   if valor is not None:

                      resultado[nombre][h]["ww"] = int(valor.text)


                elif pid == "visibility":

                  valor = timerange.find("value")

                  if valor is not None:

                    resultado[nombre][h]["visibilidad"] = int(float(valor.text))


    # Mostrar los IDs de parámetros del primer área
    primera_area = root.find(".//area")

    print("Parámetros encontrados:")
    for parametro in primera_area.findall("parameter"):
      print("-", parametro.attrib["id"])
    return resultado


def generar_pronostico(datos):

    salida = []
    areas = []
    usadas = set()

    def agregar_area(area):
        if area in datos and area not in usadas:
            areas.append(area)
            usadas.add(area)

    # 1) Áreas fijas
    for area_orden in ORDEN_AREAS:
        for area_real in datos:
            if area_real.upper() == area_orden.upper():
                agregar_area(area_real)

    # 2) Grupos dinámicos
    for prefijo in [
        "AREA CENTRO ESTE",
        "AREA CENTRO OESTE",
        "AREA SUDESTE",
        "AREA SUDOESTE",
        "AREA DRAKE"
    ]:
        grupo = [
            area for area in datos
            if area.upper().startswith(prefijo)
            and area not in usadas
        ]

        grupo = sorted(grupo, key=lambda x: x.upper())

        for area in grupo:
            agregar_area(area)

    # 3) Por si quedó alguna área afuera
    for area in datos:
        agregar_area(area)

    # Generar texto
    for area in areas:

        pronos = datos[area]

        viento = evolucion_viento(pronos)
        tiempo = evolucion_tiempo(pronos)
        visibilidad = evolucion_visibilidad(pronos)

        partes = [p for p in [viento, tiempo, visibilidad] if p]

        salida.append(f"{area.upper()}: " + " ".join(partes))

    return "\n\n".join(salida)