from __future__ import annotations
import re

PATRON = re.compile(r"^\s*(\d{1,2})(?:[°º\s]*)?([NS])\s+(\d{1,3})(?:[°º\s]*)?([EW])\s*$", re.I)

def normalizar_punto(texto):
    """Normaliza una coordenada a DD{N/S} DDD{E/W}, p.ej. 46S 042W."""
    m = PATRON.match((texto or "").strip())
    if not m:
        raise ValueError("Usá el formato: 46S 042W (latitud N/S y longitud E/W).")
    lat, ns, lon, ew = int(m.group(1)), m.group(2).upper(), int(m.group(3)), m.group(4).upper()
    if lat > 90 or lon > 180:
        raise ValueError("Latitud debe ser 0–90 y longitud 0–180.")
    return f"{lat:02d}{ns} {lon:03d}{ew}"

def normalizar_poligono(texto):
    """Acepta puntos separados por ; o salto de línea y exige al menos 3 puntos distintos."""
    crudos = [p.strip() for p in re.split(r"[;\n]+", texto or "") if p.strip()]
    puntos = [normalizar_punto(p) for p in crudos]
    if len(puntos) < 3:
        raise ValueError("Un polígono necesita al menos 3 puntos.")
    if len(set(puntos)) < 3:
        raise ValueError("El polígono necesita al menos 3 puntos distintos.")
    return " ".join(puntos)

def normalizar_posicion(tipo, texto):
    if tipo == "POINT":
        return normalizar_punto(texto)
    if tipo == "POLYGON":
        return normalizar_poligono(texto)
    return (texto or "").strip().upper()
