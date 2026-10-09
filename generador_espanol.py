from __future__ import annotations
import re
from generador_boletin import datos_emision
from avisos import SISTEMAS_CON_PRESION

SISTEMAS = {
    "STRONG BARIC GRADIENT": "FUERTE GRADIENTE BARICO",
    "LOW": "DEPRESION",
    "HIGH": "ANTICICLON",
    "COLD FRONT": "FRENTE FRIO",
    "WARM FRONT": "FRENTE CALIDO",
    "OCCLUDED FRONT": "FRENTE OCLUIDO",
    "TROUGH": "VAGUADA",
    "RIDGE": "EJE DE CUÑA",
    "OTHER": "OTRO",
}
EVOL = {
    "DEEPENING": "PROFUNDIZANDOSE",
    "WEAKENING": "DEBILITANDOSE",
    "INTENSIFYING": "INTENSIFICANDOSE",
}
AREAS = {
    "RIO DE LA PLATA INTERIOR": "RIO DE LA PLATA INTERIOR",
    "RIO DE LA PLATA EXTERIOR": "RIO DE LA PLATA EXTERIOR",
    "RIO DE LA PLATA INTERMEDIO": "RIO DE LA PLATA INTERMEDIO",
    "MAR DEL PLATA": "COSTA MAR DEL PLATA",
    "BAHIA BLANCA": "RINCON BAHIA BLANCA",
    "VALDES": "COSTA PENINSULA DE VALDES",
    "SAN JORGE": "GOLFO DE SAN JORGE",
    "PATAGONIA SUR": "COSTA PATAGONIA SUR",
    "FIN DEL MUNDO": "COSTA FIN DEL MUNDO",
    "ZONA MALVINAS": "COSTA DE ISLAS MALVINAS",
}
REEMPLAZOS = [
    ("WITH GUST", "CON RAFAGAS"),
    ("VIS VERY POOR", "VIS MUY MALA"),
    ("VIS POOR", "VIS MALA"),
    ("VIS MOD", "VIS REGULAR"),
    ("VIS FAIR", "VIS REGULAR"),
    ("VIS GOOD", "VIS BUENA"),
    ("BECMG", "LUEGO"),
    ("NOSIG WX.", ""),
    ("ISOL RA", "LLUVIAS AISLADAS"),
    ("HVY RA", "LLUVIAS FUERTES"),
    ("SHRA", "CHAPARRONES"),
    ("RA", "LLUVIAS"),
    ("DZ", "LLOVIZNAS"),
    ("SN", "NEVADAS"),
    ("RASN", "LLUVIA Y NIEVE MEZCLADA"),
    ("FZFG", "NIEBLA ENGELANTE"),
    ("FG", "NIEBLA"),
    ("BR", "NEBLINA"),
]

def encabezado_es():
    fecha, hora, _ = datos_emision()
    return (
        f"WWST01 SABM {fecha.day:02d}{hora}00\n\n"
        "1:31:06:01:00\n\n"
        "SEGURIDAD\n\n"
        "BOLETIN METEOROLOGICO PARA NAVEGANTES - METAREA 6 -\n\n"
        f"{fecha:%d-%m-%Y}, {hora}:00 UTC.\n\n"
        "SERVICIO METEOROLOGICO NACIONAL\n\n"
        "INFORMACION DE HIELOS MARINOS Y TEMPANOS SUMINISTRADA POR EL SHN, "
        "PRESION EN HPA, ESCALA BEAUFORT PARA VIENTO."
    )

def aviso_es(a):
    p=[f"AVISO {a['id']}:", SISTEMAS.get(a["sistema"], a["sistema"])]
    if a.get("sistema") in SISTEMAS_CON_PRESION and a.get("presion"):
        p.append(f"{int(a['presion'])}HPA")
    pos=(a.get("posicion_inicial") or "").upper()
    if pos:
        p.extend(["EN", pos] if a.get("tipo_posicion")=="POINT" else [pos])
    mov=a.get("movimiento","")
    if mov and mov!="STATIONARY": p.extend(["MOV",mov])
    elif mov=="STATIONARY": p.append("ESTACIONARIO")
    if a.get("evolucion"): p.append(EVOL.get(a["evolucion"],a["evolucion"]))
    p.extend(["PROVOCA" if a.get("inicio_es_actual") else "PROVOCARA","VIENTO FUERZA",str(a["fuerza"])])
    if a.get("direccion_viento"): p.extend(["DEL SECTOR",a["direccion_viento"]])
    if a.get("con_rafagas",True): p.extend(["CON RAFAGAS"])
    areas=a.get("areas_afectadas",[])
    if areas: p.extend(["EN"," / ".join(areas)])
    if a.get("fin_ddhh"): p.extend(["HASTA EL",a["fin_ddhh"]])
    if a.get("texto_extra"): p.append(a["texto_extra"].upper())
    return " ".join(p)

def parte1_es(avisos):
    l=["1 PARTE AVISO DE TEMPORAL:"]
    l.extend(aviso_es(a) for a in avisos) if avisos else l.append("SIN AVISOS.")
    return "\n\n".join(l)

def situacion_es(s):
    p=[SISTEMAS.get(s["sistema"],s["sistema"])]
    if s.get("sistema") in SISTEMAS_CON_PRESION and s.get("presion"):
        p.append(f"{int(s['presion'])}HPA")
    if s.get("posicion_inicial"): p.append(s["posicion_inicial"].upper())
    mov=s.get("movimiento","")
    if mov and mov!="STATIONARY": p.extend(["MOV",mov])
    elif mov=="STATIONARY": p.append("ESTACIONARIO")
    if s.get("evolucion"): p.append(EVOL.get(s["evolucion"],s["evolucion"]))
    if s.get("posicion_final"): p.extend(["PREVISTO",s["posicion_final"].upper()])
    if s.get("fin_ddhh"): p.extend(["EL",s["fin_ddhh"]])
    if s.get("texto_extra"): p.append(s["texto_extra"].upper())
    return " ".join(p)

def parte2_es(situaciones,hora):
    l=[f"2 PARTE SINOPSIS GENERAL A LAS {hora}UTC"]
    l.extend(situacion_es(x) for x in situaciones) if situaciones else l.append("SIN SITUACION SINOPTICA SIGNIFICATIVA.")
    return "\n\n".join(l)

def parte3_es():
    fecha,hora,validez=datos_emision()
    return (
        f"3 PARTE PRONOSTICO DE LAS {hora}:00 UTC VALIDO HASTA LAS {hora}:00 UTC "
        f"DEL DIA {validez:%d-%m-%Y}\n\nZONAS COSTERAS:"
    )

def normalizar_hielos_es(texto):
    if not texto: return ""
    lineas=[x.strip() for x in texto.splitlines() if x.strip()]
    if lineas and lineas[0].upper().startswith("INFORME DE HIELOS MARINOS Y TEMPANOS"):
        grupo=lineas.pop(0).upper().replace("INFORME DE HIELOS MARINOS Y TEMPANOS","").strip()
        if grupo: lineas.insert(0,grupo)
    return " ".join(lineas)

def traducir_pronostico(texto):
    t=texto.upper()
    for a,b in REEMPLAZOS:
        t=t.replace(a,b)
    t=re.sub(r"\bAREA SUDESTE\b","AREA SUDESTE",t)
    t=re.sub(r"\bAREA SUDOESTE\b","AREA SUDOESTE",t)
    return " ".join(t.split())

def nombre_area_es(area):
    a=area.replace("OFFSHORE ","")
    return AREAS.get(a,a)
