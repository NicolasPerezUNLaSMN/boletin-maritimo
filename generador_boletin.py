from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from avisos import generar_warning
from situaciones import generar_situacion

def datos_emision(ahora=None):
    zona = ZoneInfo("America/Argentina/Buenos_Aires")
    ahora = ahora or datetime.now(zona)
    if ahora.hour < 19:
        fecha = ahora
        hora = "12"
    else:
        fecha = ahora + timedelta(days=1)
        hora = "00"
    return fecha, hora, fecha + timedelta(days=1)

def generar_encabezado_boletin():
    fecha, hora, _ = datos_emision()
    grupo = f"{fecha.day:02d}{hora}00"
    return (
        f"WWST02 SABM {grupo}\n\n"
        "1:31:06:01:00\n\n"
        "SECURITE\n\n"
        "WEATHER BULLETIN FOR SHIPPING - METAREA 6-\n\n"
        f"{fecha:%Y-%m-%d}, {hora}:00 UTC.\n\n"
        "NATIONAL WEATHER SERVICE\n\n"
        "SEA ICE AND ICEBERGS ISSUED BY SHN PRESSURE HPA BEAUFORT SCALE WINDS."
    )

def generar_parte_1(avisos):
    lineas = ["PART 1 GALE WARNING:"]
    if avisos:
        lineas.extend(generar_warning(a) for a in avisos)
    else:
        lineas.append("NO WARNINGS.")
    return "\n\n".join(lineas)

def generar_parte_2(situaciones, hora_sinopsis="12:00"):
    lineas = [f"PART 2 GENERAL SYNOPSIS AT {hora_sinopsis}UTC"]
    if situaciones:
        lineas.extend(generar_situacion(s) for s in situaciones)
    else:
        lineas.append("NO SIGNIFICANT SYNOPTIC SITUATION.")
    return "\n\n".join(lineas)

def generar_encabezado_parte_3():
    _, hora, validez = datos_emision()
    return (
        f"PART 3 FORECAST ISSUED {hora}:00 UTC "
        f"VALID UNTIL {hora}:00 UTC {validez:%Y-%m-%d}\n\n"
        "COASTAL AREAS:"
    )

def normalizar_hielos(texto):
    if not texto:
        return ""
    lineas = [x.strip() for x in texto.splitlines() if x.strip()]
    if lineas and lineas[0].upper().startswith("SEA ICE AND ICEBERGS REPORT"):
        cab = lineas.pop(0)
        # preserve issuance group, drop title
        grupo = cab.upper().replace("SEA ICE AND ICEBERGS REPORT", "").strip()
        if grupo:
            lineas.insert(0, grupo)
    return " ".join(lineas)
