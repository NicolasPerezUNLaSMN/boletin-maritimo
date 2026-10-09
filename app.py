from __future__ import annotations
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import streamlit as st

from navtex import ESTACIONES, generar_navtex
from archivo_historico import guardar_emision, listar_emisiones, leer_emision, empaquetar_emision
import io
import zipfile
import json
from parser_hielos import leer_reporte_hielos
from mapeo_areas import unir_meteorologia_y_olas
from parser_viento import generar_boletin_meteorologico, generar_pronostico, leer_xml
from parser_olas import olas_por_area, parse_boletin
from avisos import (
    TIPOS_SISTEMA as TIPOS_AVISO, SISTEMAS_CON_PRESION, EVOLUCIONES as EVOL_AVISO,
    MOVIMIENTOS as MOV_AVISO, DIRECCIONES_VIENTO, BEAUFORT, etiqueta_sistema, etiqueta_evolucion, generar_warning, cargar_datos,
    configurar_ultimo_id, crear_aviso, actualizar_aviso, cesar_aviso, avisos_vigentes
)
from situaciones import TIPOS_SISTEMA as TIPOS_SIT, EVOLUCIONES as EVOL_SIT, MOVIMIENTOS as MOV_SIT, generar_situacion
from coordenadas import normalizar_posicion
from generador_boletin import (
    generar_encabezado_boletin, generar_parte_1, generar_parte_2,
    generar_encabezado_parte_3, normalizar_hielos
)
from generador_espanol import (
    encabezado_es, parte1_es, parte2_es, parte3_es, normalizar_hielos_es,
    traducir_pronostico, nombre_area_es
)

st.set_page_config(page_title="meMAREAVI | SMN", page_icon="🌊", layout="wide")
st.markdown("""
<style>
:root { --marino:#103D58; --celeste:#6BD4E4; }
.block-container {padding-top: 1.5rem;}
.memarea-header {background:linear-gradient(110deg,#103D58 0%,#14536D 70%,#1A6E88 100%);color:white;
    padding:42px 30px 28px;border-radius:17px;margin-bottom:17px;box-shadow:0 5px 18px rgba(8,45,67,.14)}
.memarea-brand {font-size:clamp(2.0rem,4vw,3.1rem);font-weight:800;letter-spacing:-1px;line-height:1.15}
 .memarea-brand .accent {color:#6BD4E4}
.memarea-brand {display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.memarea-symbol {width:54px;height:54px;flex:none;display:inline-block}
.memarea-symbol svg {width:100%;height:100%;display:block}
.memarea-wordmark {white-space:nowrap}
.memarea-full {font-size:1rem;color:#E4F5F8;margin-top:9px;font-weight:500}
.memarea-sub {font-size:.83rem;color:#B9D9E3;margin-top:8px}
[data-testid="stSidebar"] {border-right:3px solid #6BD4E4;}
[data-testid="stSidebar"] a {text-decoration:none;}
</style>
<div class="memarea-header">
  <div class="memarea-brand">
    <span class="memarea-symbol" aria-hidden="true">
      <svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" role="img">
        <circle cx="43" cy="19" r="10" fill="#F5D779"/>
        <path d="M8 37 Q20 24 32 37 T56 37" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>
        <path d="M8 49 Q20 36 32 49 T56 49" fill="none" stroke="#6BD4E4" stroke-width="5" stroke-linecap="round"/>
      </svg>
    </span>
    <span class="memarea-wordmark"><span class="accent">me</span>MAREA<span class="accent">VI</span></span>
  </div>
  <div class="memarea-full">Marítima Elaboraciones: Módulo Argentino de Reportes, Emisiones y Avisos</div>
  <div class="memarea-sub">Servicio Meteorológico Nacional · Centro Operativo de Pronóstico (COP) · METAREA VI</div>
</div>
""", unsafe_allow_html=True)
with st.sidebar:
    st.markdown("### 🌊 meMAREAVI")
    st.caption("Elaboración de boletines marítimos · SMN / COP")
    with st.expander("🔗 Enlaces operativos", expanded=True):
        st.markdown("[🌐 OMM · METAREA VI](https://wwmiws.wmo.int/index.php/metareas/display/6)")
        st.markdown("[🌊 SMN · Zonas costeras](https://www.smn.gob.ar/zonas_costeras)")
        st.markdown("[🛰️ Iridium · GMDSS](https://gmdss.iridium.com/#/)")
        st.markdown("[📡 Inmarsat · MSDS](https://msds.inmarsat.com/msds/)")
st.caption("Integración de PIMET, olas y hielos del SHN · Generación METAREA VI y NAVTEX · Archivo de emisiones")

if "situaciones" not in st.session_state:
    st.session_state.situaciones = []
if "editar_aviso" not in st.session_state:
    st.session_state.editar_aviso = None
if "mensaje_aviso" not in st.session_state:
    st.session_state.mensaje_aviso = ""
if "reset_aviso" not in st.session_state:
    st.session_state.reset_aviso = 0
if "mensaje_situacion" not in st.session_state:
    st.session_state.mensaje_situacion = ""

datos_hielos = {"ingles": "", "espanol": ""}
datos_viento, datos_olas, boletin_meteorologico, boletin_final = {}, {}, {}, {}
texto_viento = ""

st.subheader("Fuentes")
c1, c2, c3 = st.columns(3)
with c1:
    archivo_xml = st.file_uploader(
        "Subir XML meteorológico", type=["xml"], key="archivo_xml",
        help="Este XML se envía desde PIMET al buzón de pronóstico. Primero completar todo PIMET y luego descargar el XML recibido por correo."
    )
    st.caption("📌 PIMET → buzón de pronóstico. Completar PIMET antes de descargar el XML.")
with c2:
    archivo_olas = st.file_uploader(
        "Subir TXT de olas", type=["txt"], key="archivo_olas",
        help="Este TXT llega todas las mañanas al buzón de pronóstico, enviado por el Servicio de Hidrografía Naval (SHN). Si no está disponible, el boletín puede emitirse igualmente indicando que no hay datos de olas."
    )
    st.caption("📌 Llega cada mañana al buzón de pronóstico, enviado por SHN.")
with c3:
    archivo_hielos = st.file_uploader(
        "Subir TXT de hielos y témpanos", type=["txt"], key="archivo_hielos",
        help="Este TXT llega al buzón de pronóstico. Si todavía no llegó el correspondiente al día, utilizar el informe más reciente disponible."
    )
    st.caption("📌 Buzón de pronóstico. Usar siempre el informe más reciente disponible.")

if archivo_xml is not None:
    try:
        datos_viento = leer_xml(archivo_xml)
        boletin_meteorologico = generar_boletin_meteorologico(datos_viento)
        texto_viento = generar_pronostico(datos_viento)
        st.success(f"XML procesado. Áreas: {len(datos_viento)}")
    except ET.ParseError as e:
        st.error(f"XML inválido: {e}")
    except Exception as e:
        st.exception(e)

if archivo_olas is not None:
    try:
        datos_olas = olas_por_area(parse_boletin(archivo_olas))
        st.success(f"TXT de olas procesado. Áreas: {len(datos_olas)}")
    except Exception as e:
        st.exception(e)

if archivo_hielos is not None:
    try:
        datos_hielos = leer_reporte_hielos(archivo_hielos)
        st.success("TXT de hielos procesado.")
    except Exception as e:
        st.exception(e)

if boletin_meteorologico:
    boletin_final = unir_meteorologia_y_olas(boletin_meteorologico, datos_olas)

areas_xml = list(boletin_meteorologico.keys())
zona_arg = ZoneInfo("America/Argentina/Buenos_Aires")
hoy = datetime.now(zona_arg).date()
fecha_max = hoy + timedelta(days=2)

tabs = st.tabs(["🌬️ Meteorología", "🌊 Olas", "🧊 Hielos", "⚠️ Avisos", "🌀 Situación", "📄 Boletín final", "📡 NAVTEX", "🗃️ Archivo y datos"])
tab_viento, tab_olas, tab_hielos, tab_avisos, tab_sit, tab_final, tab_navtex, tab_archivo = tabs

with tab_viento:
    if boletin_meteorologico:
        for area, info in boletin_meteorologico.items():
            with st.expander(area):
                st.write(info)
        st.text_area("Texto meteorológico", texto_viento, height=500)
    else:
        st.info("Subí un XML meteorológico.")

with tab_olas:
    if datos_olas:
        for area, txt in datos_olas.items():
            with st.expander(area):
                st.write(txt)
    else:
        st.info("Subí el TXT de olas.")

with tab_hielos:
    if datos_hielos["ingles"]:
        st.text_area("Informe en inglés", datos_hielos["ingles"], height=300)
        st.text_area("Informe en español", datos_hielos["espanol"], height=300)
    else:
        st.info("Subí el TXT de hielos y témpanos.")

with tab_avisos:
    st.subheader("Avisos de temporal")
    if st.session_state.mensaje_aviso:
        st.success(st.session_state.mensaje_aviso)
        st.session_state.mensaje_aviso = ""
    datos = cargar_datos()
    with st.expander("Configuración de numeración"):
        ultimo = st.number_input("Último ID utilizado (el próximo será +1)", min_value=-1, value=int(datos["ultimo_id"]), step=1)
        if st.button("Guardar numeración"):
            configurar_ultimo_id(ultimo)
            st.success("Numeración actualizada.")

    vigentes = avisos_vigentes()
    st.markdown("### Avisos vigentes")
    if not vigentes:
        st.info("No hay avisos vigentes.")
    for a in vigentes:
        c1, c2, c3 = st.columns([5,1,1])
        c1.code(generar_warning(a), language=None)
        if c2.button("Editar", key=f"edit_{a['id']}"):
            st.session_state.editar_aviso = a["id"]
            st.rerun()
        if c3.button("Cesar", key=f"stop_{a['id']}"):
            cesar_aviso(a["id"])
            st.rerun()

    edit_id = st.session_state.editar_aviso
    existente = next((a for a in vigentes if a["id"] == edit_id), None)
    st.markdown("### " + (f"Modificar WARNING {edit_id}" if existente else "Nuevo aviso"))
    def val(campo, defecto=""):
        return existente.get(campo, defecto) if existente else defecto

    sistema_default = val("sistema", TIPOS_AVISO[0])
    sistema = st.selectbox("Sistema que origina el aviso", TIPOS_AVISO,
                           index=TIPOS_AVISO.index(sistema_default) if sistema_default in TIPOS_AVISO else 0,
                           format_func=etiqueta_sistema,
                           key=f"av_sistema_{st.session_state.reset_aviso}")
    presion = None
    if sistema in SISTEMAS_CON_PRESION:
        presion = st.number_input("Presión central (hPa)", min_value=850, max_value=1100,
                                  value=int(val("presion", 1000) or 1000), key=f"av_presion_{st.session_state.reset_aviso}")

    tipo_pos = st.radio("Posición inicial", ["AREA", "POINT", "POLYGON"],
                        format_func=lambda x: {"AREA":"Área del pronóstico","POINT":"Punto","POLYGON":"Polígono"}[x],
                        horizontal=True, key=f"av_tipo_{st.session_state.reset_aviso}")
    posicion = ""
    if tipo_pos == "AREA":
        pos_areas = st.multiselect("Área(s) de posición inicial", areas_xml, key=f"av_posareas_{st.session_state.reset_aviso}",
                                   default=[x for x in val("posicion_inicial","").split(" / ") if x in areas_xml])
        posicion = " / ".join(pos_areas)
        if not areas_xml:
            st.warning("Primero subí el XML para seleccionar áreas.")
    elif tipo_pos == "POINT":
        posicion = st.text_input("Punto (formato único: 46S 042W)", val("posicion_inicial"), key=f"av_point_{st.session_state.reset_aviso}")
    else:
        posicion = st.text_area("Polígono: un punto por línea o separado por ; (ej. 35S 055W)",
                                val("posicion_inicial"), key=f"av_poly_{st.session_state.reset_aviso}")
        st.caption("Se validan N/S, E/W, rangos geográficos y un mínimo de 3 puntos distintos.")

    movimiento = st.selectbox("Movimiento", MOV_AVISO, key=f"av_mov_{st.session_state.reset_aviso}",
                              index=MOV_AVISO.index(val("movimiento")) if val("movimiento") in MOV_AVISO else 0)
    evolucion = st.selectbox("Evolución", EVOL_AVISO, key=f"av_evol_{st.session_state.reset_aviso}",
                             index=EVOL_AVISO.index(val("evolucion")) if val("evolucion") in EVOL_AVISO else 0)

    fuerza = st.selectbox("Fuerza Beaufort", list(BEAUFORT), key=f"av_force_{st.session_state.reset_aviso}",
                          format_func=lambda n: f"{n} - {BEAUFORT[n]}",
                          index=max(0, min(4, int(val("fuerza",8))-8)))
    direccion = st.selectbox("Dirección del temporal", DIRECCIONES_VIENTO, key=f"av_dir_{st.session_state.reset_aviso}",
                             index=DIRECCIONES_VIENTO.index(val("direccion_viento","W")) if val("direccion_viento","W") in DIRECCIONES_VIENTO else 6)
    rafagas = st.checkbox("Con ráfagas (WITH GUST)", key=f"av_gust_{st.session_state.reset_aviso}", value=bool(val("con_rafagas", True)))

    areas_afectadas = st.multiselect("Áreas afectadas", areas_xml, key=f"av_areas_{st.session_state.reset_aviso}",
                                     default=[a for a in val("areas_afectadas",[]) if a in areas_xml])
    if not areas_xml:
        st.warning("Las áreas afectadas se habilitan al cargar el XML.")

    cfi, chi = st.columns(2)
    fecha_inicio = cfi.date_input("Inicio", value=hoy, min_value=hoy, max_value=fecha_max, key=f"av_di_{st.session_state.reset_aviso}")
    hora_inicio = chi.selectbox("Hora inicio UTC", list(range(24)), key=f"av_hi_{st.session_state.reset_aviso}", format_func=lambda h: f"{h:02d}:00")
    cff, chf = st.columns(2)
    fecha_fin = cff.date_input("Fin", value=hoy + timedelta(days=1), min_value=hoy, max_value=fecha_max, key=f"av_df_{st.session_state.reset_aviso}")
    hora_fin = chf.selectbox("Hora fin UTC", list(range(24)), key=f"av_hf_{st.session_state.reset_aviso}", format_func=lambda h: f"{h:02d}:00")

    extra = st.text_input("Texto adicional opcional en inglés", val("texto_extra"), key=f"av_extra_{st.session_state.reset_aviso}")
    if st.button("Guardar aviso", type="primary"):
        try:
            if not areas_afectadas:
                raise ValueError("Seleccioná al menos un área afectada. Este campo es obligatorio.")
            posicion_norm = normalizar_posicion(tipo_pos, posicion)
            inicio_dt = datetime.combine(fecha_inicio, datetime.min.time()).replace(hour=hora_inicio, tzinfo=zona_arg)
            ahora = datetime.now(zona_arg)
            inicio_actual = inicio_dt <= ahora
            fin_ddhh = f"{fecha_fin.day:02d}/{hora_fin:02d}00"
            payload = {
                "sistema": sistema, "presion": presion, "tipo_posicion": tipo_pos,
                "posicion_inicial": posicion_norm, "movimiento": movimiento, "evolucion": evolucion,
                "fuerza": fuerza, "direccion_viento": direccion, "con_rafagas": rafagas,
                "areas_afectadas": areas_afectadas, "inicio_es_actual": inicio_actual,
                "inicio_iso": inicio_dt.isoformat(), "fin_ddhh": fin_ddhh, "texto_extra": extra,
            }
            if existente:
                guardado = actualizar_aviso(existente["id"], payload)
                st.session_state.mensaje_aviso = f"WARNING {guardado['id']} actualizado correctamente."
                st.session_state.editar_aviso = None
            else:
                guardado = crear_aviso(payload)
                st.session_state.mensaje_aviso = f"WARNING {guardado['id']} guardado correctamente."
            st.session_state.reset_aviso += 1
            st.toast(st.session_state.mensaje_aviso, icon="✅")
            st.rerun()
        except ValueError as e:
            st.error(str(e))

    if existente and st.button("Cancelar edición"):
        st.session_state.editar_aviso = None
        st.rerun()

with tab_sit:
    st.subheader("Situación sinóptica")
    if st.session_state.mensaje_situacion:
        st.success(st.session_state.mensaje_situacion)
        st.session_state.mensaje_situacion = ""
    hora_sinopsis = st.radio("Hora UTC de la situación", ["00:00", "12:00"], horizontal=True, index=1)
    sistema_s = st.selectbox("Sistema / fenómeno", TIPOS_SIT, format_func=etiqueta_sistema, key="sit_sistema")
    presion_s = None
    if sistema_s in SISTEMAS_CON_PRESION:
        presion_s = st.number_input("Presión central (hPa)", min_value=850, max_value=1100, value=1000, key="sit_presion")

    st.markdown("#### Posición inicial")
    tipo_ini = st.radio("Tipo", ["AREA","POINT","POLYGON"], horizontal=True, key="sit_tipo_ini",
                        format_func=lambda x: {"AREA":"Área","POINT":"Punto","POLYGON":"Polígono"}[x])
    if tipo_ini == "AREA":
        ini_areas = st.multiselect("Área(s) inicial(es)", areas_xml, key="sit_ini_areas")
        pos_ini = " / ".join(ini_areas)
    elif tipo_ini == "POINT":
        pos_ini = st.text_input("Punto inicial (ej. 46S 042W)")
    else:
        pos_ini = st.text_area("Polígono inicial (puntos separados por ; o salto de línea)")

    movimiento_s = st.selectbox("Movimiento", MOV_SIT, key="sit_mov")
    evolucion_s = st.selectbox("Evolución", EVOL_SIT, format_func=etiqueta_evolucion, key="sit_evol")

    st.markdown("#### Posición final prevista (opcional)")
    usar_final = st.checkbox("Agregar posición final")
    tipo_fin = "AREA"
    pos_fin = ""
    fecha_s_fin, hora_s_fin = hoy + timedelta(days=1), 12
    if usar_final:
        tipo_fin = st.radio("Tipo final", ["AREA","POINT","POLYGON"], horizontal=True, key="sit_tipo_fin",
                            format_func=lambda x: {"AREA":"Área","POINT":"Punto","POLYGON":"Polígono"}[x])
        if tipo_fin == "AREA":
            fin_areas = st.multiselect("Área(s) final(es)", areas_xml, key="sit_fin_areas")
            pos_fin = " / ".join(fin_areas)
        elif tipo_fin == "POINT":
            pos_fin = st.text_input("Punto final (ej. 48S 035W)")
        else:
            pos_fin = st.text_area("Polígono final")
        csd, csh = st.columns(2)
        fecha_s_fin = csd.date_input("Fecha posición final", hoy + timedelta(days=1), min_value=hoy, max_value=fecha_max)
        hora_s_fin = csh.selectbox("Hora posición final UTC", list(range(24)), index=12, format_func=lambda h: f"{h:02d}:00")

    areas_sit = st.multiselect(
        "Áreas afectadas por esta situación (para filtrar NAVTEX)",
        areas_xml, key="sit_areas_afectadas",
        help="Seleccioná las áreas costeras alcanzadas. Sin áreas seleccionadas, la situación no se incluirá en los NAVTEX costeros."
    )
    extra_s = st.text_input("Otra información opcional (en inglés)")
    if st.button("Agregar a la situación", type="primary"):
        try:
            ini_norm = normalizar_posicion(tipo_ini, pos_ini)
            fin_norm = normalizar_posicion(tipo_fin, pos_fin) if usar_final else ""
            nueva_situacion = {
                "sistema": sistema_s, "presion": presion_s, "posicion_inicial": ini_norm,
                "movimiento": movimiento_s, "evolucion": evolucion_s,
                "posicion_final": fin_norm,
                "fin_ddhh": f"{fecha_s_fin.day:02d}/{hora_s_fin:02d}00" if usar_final else "",
                "texto_extra": extra_s, "areas_afectadas": areas_sit,
            }
            st.session_state.situaciones.append(nueva_situacion)
            st.session_state.mensaje_situacion = "Situación agregada correctamente."
            st.toast("Situación agregada correctamente.", icon="✅")
            st.rerun()
        except ValueError as e:
            st.error(str(e))

    for i, s in enumerate(st.session_state.situaciones):
        c1, c2 = st.columns([8,1])
        c1.code(generar_situacion(s), language=None)
        if c2.button("Eliminar", key=f"del_sit_{i}"):
            st.session_state.situaciones.pop(i)
            st.rerun()

with tab_final:
    if boletin_final:
        avisos_actuales = avisos_vigentes()
        situaciones_actuales = st.session_state.situaciones
        hora_sin = hora_sinopsis if 'hora_sinopsis' in locals() else "12:00"

        # ---------------- INGLÉS ----------------
        bloques_en = [
            generar_encabezado_boletin(),
            generar_parte_1(avisos_actuales),
            generar_parte_2(situaciones_actuales, hora_sin),
        ]
        hielo_en = normalizar_hielos(datos_hielos["ingles"])
        if hielo_en:
            bloques_en.append(hielo_en)
        bloques_en.append(generar_encabezado_parte_3())

        # Si faltan olas: un único aviso general en PART 3.
        if not datos_olas:
            bloques_en.append("WAVE DATA NOT AVAILABLE FOR ANY AREA.")

        areas_en, oceanico = [], False
        for area, info in boletin_final.items():
            if area.startswith("AREA NORTE") and not oceanico:
                areas_en.append("OCEANIC AREAS:")
                oceanico = True
            partes = [info["viento"], info["tiempo"], info["visibilidad"]]
            if datos_olas and info["olas"]:
                partes.append(info["olas"])
            texto = " ".join(p.strip() for p in partes if p)
            areas_en.append(f"{area.replace('OFFSHORE ', '')}: {texto}")
        bloques_en.append("\n\n".join(areas_en))
        bloques_en.extend(["-----------------------------------------------------------------", "NNNN="])
        texto_final_en = "\n\n".join(bloques_en)

        # ---------------- ESPAÑOL ----------------
        bloques_es = [
            encabezado_es(),
            parte1_es(avisos_actuales),
            parte2_es(situaciones_actuales, hora_sin),
        ]
        hielo_es = normalizar_hielos_es(datos_hielos["espanol"])
        if hielo_es:
            bloques_es.append(hielo_es)
        bloques_es.append(parte3_es())
        if not datos_olas:
            bloques_es.append("DATOS DE OLAS NO DISPONIBLES PARA NINGUNA DE LAS AREAS.")

        areas_es, oceanico_es = [], False
        for area, info in boletin_final.items():
            if area.startswith("AREA NORTE") and not oceanico_es:
                areas_es.append("AREAS OCEANICAS:")
                oceanico_es = True
            partes = [info["viento"], info["tiempo"], info["visibilidad"]]
            if datos_olas and info["olas"]:
                partes.append(info["olas"])
            texto = traducir_pronostico(" ".join(p.strip() for p in partes if p))
            areas_es.append(f"{nombre_area_es(area)}: {texto}")
        bloques_es.append("\n\n".join(areas_es))
        bloques_es.extend(["-----------------------------------------------------------------", "NNNN="])
        texto_final_es = "\n\n".join(bloques_es)

        idioma = st.radio("Vista previa", ["Inglés", "Español"], horizontal=True)
        if idioma == "Inglés":
            st.text_area("Boletín final en inglés", texto_final_en, height=850)
        else:
            st.text_area("Boletín final en español", texto_final_es, height=850)

        c_en, c_es = st.columns(2)
        with c_en:
            st.download_button(
                "⬇️ Descargar boletín en inglés",
                texto_final_en,
                "boletin_metarea6_en.txt",
                "text/plain",
                use_container_width=True,
            )
        with c_es:
            st.download_button(
                "⬇️ Descargar boletín en español",
                texto_final_es,
                "boletin_metarea6_es.txt",
                "text/plain",
                use_container_width=True,
            )
    else:
        st.info("Subí el XML meteorológico para generar el boletín. El TXT de olas es opcional.")

# Los textos se generan una sola vez por rerun, con los mismos datos que la vista final.
navs = {}
if boletin_meteorologico:
    avisos_nav = avisos_vigentes()
    situaciones_nav = st.session_state.situaciones
    navs = {nombre: generar_navtex(boletin_meteorologico, avisos_nav, situaciones_nav, estaciones=[nombre]) for nombre in ESTACIONES}
    navs["TODAS LAS ESTACIONES COSTERAS"] = generar_navtex(boletin_meteorologico, avisos_nav, situaciones_nav, estaciones=list(ESTACIONES))

with tab_navtex:
    st.subheader("NAVTEX costeros — vista completa")
    st.caption("Se muestran todas las estaciones sin selector. Los textos son borradores que deben validarse antes de su emisión.")
    with st.expander("Asociación de estaciones y áreas"):
        for nombre, zonas in ESTACIONES.items():
            st.write(f"**{nombre}:** {', '.join(zonas)}")
    if not navs:
        st.info("Cargá el XML meteorológico para generar los NAVTEX.")
    else:
        for nombre, texto_nav in navs.items():
            st.markdown(f"#### {nombre}")
            # Sin key persistente: el texto mostrado siempre corresponde a la estación.
            st.code(texto_nav, language=None)
            st.download_button("⬇️ Descargar " + nombre, texto_nav,
                f"navtex_{nombre.lower().replace(' ', '_')}.txt", "text/plain",
                key=f"desc_nav_{nombre}")
            st.divider()
        memoria = io.BytesIO()
        with zipfile.ZipFile(memoria, "w", zipfile.ZIP_DEFLATED) as paquete:
            for nombre, texto_nav in navs.items():
                paquete.writestr(f"navtex_{nombre.lower().replace(' ', '_')}.txt", texto_nav)
        st.download_button("⬇️ Descargar los 7 NAVTEX (ZIP)", memoria.getvalue(),
            "navtex_costeros.zip", "application/zip")

with tab_archivo:
    st.subheader("Archivo histórico y datos por área")
    st.caption("El archivo se conserva en disco local en data/emisiones/. Guardar crea una nueva versión; no modifica las anteriores.")
    if boletin_final and navs:
        st.markdown("#### Guardar emisión actual")
        st.info("Se guardarán ambos boletines METAREA, los siete NAVTEX, los pronósticos por área, los avisos y situaciones, y copias de los archivos fuente cargados.")
        if st.button("💾 Guardar emisión completa", type="primary"):
            try:
                identificador = guardar_emision(
                    texto_final_en, texto_final_es, navs, boletin_final,
                    avisos_vigentes(), st.session_state.situaciones,
                    {"xml":archivo_xml,"olas":archivo_olas,"hielos":archivo_hielos},
                    hora_sinopsis if 'hora_sinopsis' in locals() else "12:00")
                st.session_state["ultima_emision"] = identificador
                st.toast("Emisión archivada correctamente", icon="✅")
            except (OSError, ValueError) as exc:
                st.error(f"No se pudo archivar: {exc}")
        if st.session_state.get("ultima_emision"):
            st.success("Última emisión guardada: " + st.session_state["ultima_emision"])
    else:
        st.info("Cargá un XML para habilitar el guardado de la emisión.")
    registros = listar_emisiones()
    st.markdown("#### Consultar emisiones anteriores")
    if registros:
        opciones = {r["id"]:r for r in registros}
        elegido = st.selectbox("Emisión archivada", list(opciones),
            format_func=lambda x: f"{opciones[x]['guardado_local']} — {x}")
        archivos = leer_emision(elegido)
        st.download_button("⬇️ Descargar emisión completa (ZIP)", empaquetar_emision(elegido),
            f"emision_{elegido}.zip", "application/zip")
        nombre_archivo = st.selectbox("Ver archivo guardado", sorted(archivos))
        if nombre_archivo.endswith((".txt", ".json", ".xml")):
            st.code(archivos[nombre_archivo].decode("utf-8", errors="replace"), language=None)
        st.download_button("⬇️ Descargar archivo seleccionado", archivos[nombre_archivo],
            nombre_archivo, "application/octet-stream")
        st.markdown("#### Datos estructurados para futura API")
        areas_archivadas = json.loads(archivos["areas.json"].decode("utf-8"))["areas"]
        area_consulta = st.selectbox("Consultar pronóstico de un área", list(areas_archivadas))
        st.json({"id_emision": elegido, "area":area_consulta, "pronostico":areas_archivadas[area_consulta]})
        st.download_button("⬇️ Exportar datos por área (JSON)", archivos["areas.json"],
            f"areas_{elegido}.json", "application/json")
    else:
        st.info("Todavía no hay emisiones archivadas.")
    st.caption("Esta solapa ofrece consultas y JSON exportables, no un endpoint HTTP público. Una API real requerirá un servicio independiente y control de acceso.")
