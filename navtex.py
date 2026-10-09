"""Generación de borradores NAVTEX a partir de las áreas XML.

La asociación estación/área es configurable en ESTACIONES. No implica cobertura
radioeléctrica ni delimita por sí sola zonas oficiales de responsabilidad.
"""
from __future__ import annotations
from generador_boletin import datos_emision
from avisos import generar_warning
from situaciones import generar_situacion

ESTACIONES = {
    "BUENOS AIRES": ("RIO DE LA PLATA INTERIOR", "RIO DE LA PLATA INTERMEDIO", "RIO DE LA PLATA EXTERIOR"),
    "BAHIA BLANCA": ("OFFSHORE BAHIA BLANCA",),
    "MAR DEL PLATA": ("OFFSHORE MAR DEL PLATA",),
    "COMODORO RIVADAVIA": ("OFFSHORE SAN JORGE",),
    "RIO GALLEGOS": ("OFFSHORE PATAGONIA SUR",),
    "USHUAIA": ("OFFSHORE FIN DEL MUNDO",),
}

def _forecast(info):
    return " ".join(str(info.get(k) or "").strip() for k in ("viento", "tiempo", "visibilidad") if info.get(k)).strip()

def _aplica(obj, areas):
    # Si no se declaró afectación, no se presupone que afecta a una estación.
    return bool(set(obj.get("areas_afectadas", [])) & set(areas))

def generar_navtex(boletin, avisos, situaciones, estaciones=None, todas_las_areas=False):
    fecha, hora, hasta = datos_emision()
    if todas_las_areas:
        areas = list(boletin)
        seleccion = {a: (a,) for a in areas}
    else:
        nombres = list(estaciones or ESTACIONES)
        seleccion = {e: ESTACIONES[e] for e in nombres}
        areas = [a for e in nombres for a in ESTACIONES[e]]
    # Conservar el orden de los avisos del operador; filtrar únicamente por áreas explícitas.
    avisos_sel = [a for a in avisos if _aplica(a, areas)]
    situaciones_sel = [s for s in situaciones if _aplica(s, areas)]
    bloques = [
        f"WWST03 SABM {fecha.day:02d}{hora}00",
        "WEATHER BULLETIN FOR NAVTEX STATIONS - METAREA 6 -",
        f"{fecha:%B} {fecha.day:02d}, {hora}:00UTC".upper(),
        "NATIONAL WEATHER SERVICE",
        "SEA ICE AND ICEBERGS ISSUED BY SHN",
        "PRESSURE HPA",
        "BEAUFORT SCALE WINDS.",
    ]
    bloques.extend(generar_warning(a) for a in avisos_sel)
    if not avisos_sel: bloques.append("NO WARNINGS")
    bloques.append("GENERAL SINOPSIS:")
    bloques.extend(generar_situacion(s) for s in situaciones_sel)
    if not situaciones_sel: bloques.append("NO COASTAL SYNOPTIC SITUATIONS REPORTED.")
    bloques.extend([
        f"FORECAST ISSUED {hora}:00 UTC VALID UNTIL {hora}:00 UTC {hasta:%Y-%m-%d}",
        "NAVTEX STATIONS FCST:",
    ])
    for estacion, zona in seleccion.items():
        textos = [_forecast(boletin[a]) for a in zona if a in boletin]
        textos = [t for t in textos if t]
        if not textos:
            bloques.append(f"{estacion}: FORECAST DATA NOT AVAILABLE.")
        elif len(textos) == 1:
            bloques.append(f"{estacion}: {textos[0]}")
        else:
            # Nunca descartar subáreas distintas ni fusionar pronósticos incompatibles.
            bloques.append(f"{estacion}:")
            for a in zona:
                if a in boletin:
                    bloques.append(f"{a}: {_forecast(boletin[a])}")
    bloques.extend(["-----------------------------------------------------------------", "NNNN="])
    return "\n".join(bloques) + "\n"
