from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
ARCHIVO_AVISOS = DATA_DIR / "avisos.json"

TIPOS_SISTEMA = [
    "STRONG BARIC GRADIENT", "LOW", "COLD FRONT", "WARM FRONT",
    "OCCLUDED FRONT", "TROUGH", "HIGH", "RIDGE", "OTHER",
]
SISTEMAS_CON_PRESION = {"LOW", "HIGH"}

TRADUCCIONES_SISTEMA = {
    "STRONG BARIC GRADIENT": "Fuerte gradiente bárico",
    "LOW": "Baja / depresión",
    "COLD FRONT": "Frente frío",
    "WARM FRONT": "Frente cálido",
    "OCCLUDED FRONT": "Frente ocluido",
    "TROUGH": "Vaguada",
    "HIGH": "Alta / anticiclón",
    "RIDGE": "Cuña",
    "OTHER": "Otro",
}

def etiqueta_sistema(valor):
    return f"{valor} - {TRADUCCIONES_SISTEMA.get(valor, valor)}"

EVOLUCIONES = ["", "DEEPENING", "WEAKENING", "INTENSIFYING"]
TRADUCCIONES_EVOLUCION = {
    "": "Sin evolución indicada",
    "DEEPENING": "Profundizándose",
    "WEAKENING": "Debilitándose",
    "INTENSIFYING": "Intensificándose",
}
def etiqueta_evolucion(valor):
    return f"{valor} - {TRADUCCIONES_EVOLUCION[valor]}" if valor else TRADUCCIONES_EVOLUCION[valor]
MOVIMIENTOS = ["", "N", "NE", "E", "SE", "S", "SW", "W", "NW", "STATIONARY"]
DIRECCIONES_VIENTO = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
BEAUFORT = {
    8: "Temporal",
    9: "Temporal fuerte",
    10: "Temporal duro",
    11: "Temporal muy duro",
    12: "Huracán",
}

def _base():
    return {"anio": datetime.now().year, "ultimo_id": -1, "avisos": []}

def cargar_datos():
    DATA_DIR.mkdir(exist_ok=True)
    if not ARCHIVO_AVISOS.exists():
        return _base()
    try:
        datos = json.loads(ARCHIVO_AVISOS.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _base()
    if datos.get("anio") != datetime.now().year:
        return _base()
    datos.setdefault("ultimo_id", -1)
    datos.setdefault("avisos", [])
    return datos

def guardar_datos(datos):
    DATA_DIR.mkdir(exist_ok=True)
    ARCHIVO_AVISOS.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")

def configurar_ultimo_id(valor):
    datos = cargar_datos()
    datos["ultimo_id"] = int(valor)
    guardar_datos(datos)

def crear_aviso(aviso):
    datos = cargar_datos()
    nuevo_id = datos["ultimo_id"] + 1
    aviso = dict(aviso)
    aviso.update({"id": nuevo_id, "anio": datos["anio"], "estado": "VIGENTE"})
    datos["ultimo_id"] = nuevo_id
    datos["avisos"].append(aviso)
    guardar_datos(datos)
    return aviso

def actualizar_aviso(aviso_id, cambios):
    datos = cargar_datos()
    for aviso in datos["avisos"]:
        if aviso["id"] == aviso_id:
            aviso.update(cambios)
            guardar_datos(datos)
            return aviso
    return None

def cesar_aviso(aviso_id):
    return actualizar_aviso(aviso_id, {"estado": "CESADO"})

def avisos_vigentes():
    return [a for a in cargar_datos()["avisos"] if a.get("estado") == "VIGENTE"]

def texto_posicion(tipo, valor):
    valor = (valor or "").strip().upper()
    if not valor:
        return ""
    if tipo == "POINT":
        return f"AT {valor}"
    return valor

def generar_warning(aviso):
    partes = [f"WARNING {aviso['id']}:", aviso["sistema"]]
    if aviso.get("sistema") in SISTEMAS_CON_PRESION and aviso.get("presion"):
        partes.append(f"{int(aviso['presion'])}HPA")

    pos = texto_posicion(aviso.get("tipo_posicion", "AREA"), aviso.get("posicion_inicial"))
    if pos:
        partes.append(pos)

    mov = aviso.get("movimiento", "")
    if mov and mov != "STATIONARY":
        partes.extend(["MOV", mov])
    elif mov == "STATIONARY":
        partes.append("STATIONARY")

    if aviso.get("evolucion"):
        partes.append(aviso["evolucion"])

    verbo = "PROVOKES" if aviso.get("inicio_es_actual", False) else "WILL PROVOKE"
    partes.extend([verbo, "WINDS FORCE", str(aviso["fuerza"])])

    if aviso.get("direccion_viento"):
        partes.extend(["FROM SECTOR", aviso["direccion_viento"]])
    if aviso.get("con_rafagas", True):
        partes.extend(["WITH GUST"])

    areas = aviso.get("areas_afectadas", [])
    if areas:
        partes.extend(["IN", " / ".join(a.upper() for a in areas)])

    if aviso.get("fin_ddhh"):
        partes.extend(["UNTIL", aviso["fin_ddhh"]])

    if aviso.get("texto_extra"):
        partes.append(aviso["texto_extra"].strip().upper())

    return " ".join(partes)
