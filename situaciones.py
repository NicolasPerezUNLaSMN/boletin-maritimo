from __future__ import annotations
from avisos import SISTEMAS_CON_PRESION

TIPOS_SISTEMA = [
    "LOW", "HIGH", "STRONG BARIC GRADIENT", "COLD FRONT", "WARM FRONT",
    "OCCLUDED FRONT", "TROUGH", "RIDGE", "OTHER",
]
EVOLUCIONES = ["", "DEEPENING", "WEAKENING", "INTENSIFYING"]
MOVIMIENTOS = ["", "N", "NE", "E", "SE", "S", "SW", "W", "NW", "STATIONARY"]

def generar_situacion(s):
    partes = [s["sistema"]]
    if s.get("sistema") in SISTEMAS_CON_PRESION and s.get("presion"):
        partes.append(f"{int(s['presion'])}HPA")
    if s.get("posicion_inicial"):
        partes.append(s["posicion_inicial"].strip().upper())
    mov = s.get("movimiento", "")
    if mov and mov != "STATIONARY":
        partes.extend(["MOV", mov])
    elif mov == "STATIONARY":
        partes.append("STATIONARY")
    if s.get("evolucion"):
        partes.append(s["evolucion"])
    if s.get("posicion_final"):
        partes.extend(["EXPECTED", s["posicion_final"].strip().upper()])
    if s.get("fin_ddhh"):
        partes.extend(["BY", s["fin_ddhh"]])
    if s.get("texto_extra"):
        partes.append(s["texto_extra"].strip().upper())
    return " ".join(partes)
