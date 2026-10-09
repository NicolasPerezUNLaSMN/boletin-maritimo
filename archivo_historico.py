"""Archivo local de emisiones: cada guardado crea una versión inmutable.
No expone HTTP; los JSON son exportables para una futura API.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json, hashlib, uuid, zipfile, io

RAIZ = Path(__file__).parent / "data" / "emisiones"
TZ = ZoneInfo("America/Argentina/Buenos_Aires")

def guardar_emision(ingles, espanol, navtex, areas, avisos, situaciones, fuentes, hora_sinopsis):
    if not ingles or not espanol or not navtex or not areas:
        raise ValueError("Faltan datos para guardar una emisión completa")
    ahora = datetime.now(TZ)
    identificador = ahora.strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:8]
    carpeta = RAIZ / identificador
    carpeta.mkdir(parents=True, exist_ok=False)
    textos = {"metarea_ingles.txt": ingles, "metarea_espanol.txt": espanol}
    for estacion, texto in navtex.items():
        slug = estacion.lower().replace(" ", "_")
        textos[f"navtex_{slug}.txt"] = texto
    hashes = {}
    for nombre, texto in textos.items():
        contenido = texto.encode("utf-8")
        (carpeta / nombre).write_bytes(contenido)
        hashes[nombre] = hashlib.sha256(contenido).hexdigest()
    for etiqueta, archivo in fuentes.items():
        if archivo is not None:
            datos = archivo.getvalue()
            sufijo = Path(archivo.name).suffix.lower()
            nombre = f"fuente_{etiqueta}{sufijo}"
            (carpeta / nombre).write_bytes(datos)
            hashes[nombre] = hashlib.sha256(datos).hexdigest()
    meta = {
        "id": identificador, "guardado_local": ahora.isoformat(),
        "hora_sinopsis_utc": hora_sinopsis,
        "fuentes": {k: (v.name if v is not None else None) for k,v in fuentes.items()},
        "avisos": avisos, "situaciones": situaciones,
        "areas": areas, "navtex_estaciones": list(navtex),
        "sha256": hashes, "estado": "BORRADOR_GUARDADO",
    }
    (carpeta / "metadatos.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (carpeta / "areas.json").write_text(json.dumps({"id_emision":identificador,"areas":areas}, ensure_ascii=False, indent=2), encoding="utf-8")
    return identificador

def listar_emisiones():
    if not RAIZ.exists():return []
    salida=[]
    for carpeta in sorted(RAIZ.iterdir(), reverse=True):
        archivo=carpeta/"metadatos.json"
        if carpeta.is_dir() and archivo.is_file():
            try: salida.append(json.loads(archivo.read_text(encoding="utf-8")))
            except (ValueError,OSError): pass
    return salida

def leer_emision(identificador):
    if not identificador or any(c not in "0123456789T_abcdef" for c in identificador):
        raise ValueError("Identificador inválido")
    carpeta=RAIZ/identificador
    if not (carpeta/"metadatos.json").exists(): raise FileNotFoundError(identificador)
    return {f.name:f.read_bytes() for f in carpeta.iterdir() if f.is_file()}

def empaquetar_emision(identificador):
    memoria=io.BytesIO()
    with zipfile.ZipFile(memoria,"w",zipfile.ZIP_DEFLATED) as z:
        for nombre, datos in leer_emision(identificador).items():z.writestr(nombre,datos)
    return memoria.getvalue()
