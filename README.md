# meMAREAVI — identidad visual actualizada

## Ejecución

Activar el entorno virtual e iniciar `streamlit run app.py`.

## NAVTEX

La pestaña NAVTEX muestra los seis boletines costeros y el general, uno debajo de otro, con descargas individuales y ZIP conjunto. Se mantiene la asociación estación/área de `navtex.py` (requiere validación operacional).

## Archivo histórico

En **Archivo y datos** se guarda explícitamente una **instantánea completa** de la emisión: METAREA inglés/español, siete NAVTEX, `areas.json`, `metadatos.json` (avisos y situaciones), y copias de los archivos fuente que estén cargados. Se crea una carpeta inmutable por guardado en `data/emisiones/<id>/`.

El botón **Guardar emisión completa** no transmite ni publica boletines: archiva borradores. Cada clic crea una nueva versión. Las descargas individuales no archivan automáticamente. Los archivos se guardan en el equipo/servidor donde se ejecuta Streamlit, **no en el navegador**. Realizar copias de seguridad periódicas de `data/`, incluyendo `data/avisos.json`.

## Volumen de almacenamiento y dimensionamiento para despliegue

### Supuestos de cálculo (estimación inicial, octubre de 2026)

- Tamaño observado de una carpeta completa de emisión en `data/emisiones/<id>/`: **390–400 KB** aproximadamente, incluyendo TXT, JSON y copias de las fuentes cargadas.
- Frecuencia operativa prevista: **dos emisiones diarias** (00 y 12 UTC).
- Se supone **un guardado por emisión** y 365 días de operación al año. Si se guardan borradores, correcciones o reemisiones, cada guardado crea otra carpeta y aumenta el consumo.
- Cálculos aproximados en unidades decimales (1 MB = 1.000 KB; 1 GB = 1.000 MB). No incluyen el espacio ocupado por el sistema, dependencias, registros, respaldos ni otros archivos ajenos a cada emisión.

| Período | Emisiones | Almacenamiento estimado |
|---|---:|---:|
| Una emisión | 1 | 390–400 KB |
| Un día | 2 | 780–800 KB |
| 30 días | 60 | 23,4–24 MB |
| Un año (365 días) | 730 | 284,7–292 MB |
| Cinco años | 3.650 | 1,42–1,46 GB |
| Diez años | 7.300 | 2,85–2,92 GB |

**Conclusión preliminar:** el archivo histórico tiene una demanda de almacenamiento reducida. Como reserva de planificación se pueden prever **10 GB de espacio disponible para las emisiones**, con capacidad de ampliación, **además** del espacio para aplicación, sistema, logs y copias de seguridad. No es una exigencia técnica mínima ni reemplaza la medición en el entorno definitivo.

### Aspectos a considerar en producción

- **Persistencia real:** montar `data/` en un volumen duradero del servidor; evitar almacenamiento efímero de contenedores o despliegues que se reinicialicen.
- **Respaldo y recuperación:** incluir `data/emisiones/` y `data/avisos.json` en copias de seguridad programadas; probar periódicamente la restauración. El almacenamiento requerido por las copias se calcula por separado.
- **Versiones:** cada pulsación de «Guardar emisión completa» genera una carpeta nueva, incluso para una misma hora sinóptica. Registrar y diferenciar borradores, correcciones y emisiones enviadas cuando se implemente **ENVIAR**.
- **Crecimiento:** controlar periódicamente el tamaño real de cada carpeta, el número de emisiones y el espacio libre; recalcular la proyección si cambian los XML/TXT o se agregan adjuntos.
- **Concurrencia y retención:** antes de un despliegue multiusuario definir permisos, escritura segura, política de retención, auditoría y eventual migración a base de datos/almacenamiento de objetos.
- **Distribución futura:** el correo y FTP/SFTP pueden requerir registros, colas y reintentos adicionales; su volumen no está incluido en estas cifras.

## Consulta de datos / API futura

En la misma solapa se pueden explorar emisiones anteriores, consultar los pronósticos de cada área y descargar `areas.json`. Esto **no es un endpoint HTTP**. Para exponer un endpoint de verdad se recomienda implementar una API de solo lectura (p.ej. FastAPI) con autenticación, paginación, control de acceso y respaldo del archivo histórico.

## Pendientes operativos

- Validación de terminología y formato con pronosticadores.
- Validación de correspondencia oficial estación/área NAVTEX.
- Persistencia multiusuario/transaccional y política de retención.
- API HTTP con autorización y auditoría.
- Registro formal de aprobación/publicación separado del guardado de borradores.

## Nombre y enlaces
La aplicación se presenta como **meMAREAVI** (Marítima Elaboraciones: Módulo Argentino de Reportes, Emisiones y Avisos). Los enlaces operativos se encuentran en la barra lateral. El séptimo NAVTEX consolida únicamente las estaciones costeras, no todas las áreas oceánicas.

## Identidad visual

**meMAREAVI**: **me** = Marítima Elaboraciones; **MAREA** = Módulo Argentino de Reportes, Emisiones y Avisos; **VI** = METAREA VI. Colores institucionales propuestos: azul marino `#103D58`, celeste `#6BD4E4` y blanco.

El título, el encabezado, la barra lateral y el título de la pestaña del navegador reflejan la nueva identidad. El nombre es una propuesta de marca para el desarrollo, no una denominación oficial aprobada por el SMN.

El guardado histórico sigue siendo **manual** hasta implementar un flujo ENVIAR con archivado previo y registro de distribución.

## Ajustes visuales v10

Encabezado con mayor margen superior, isotipo SVG de sol y olas, nombre `meMAREAVI` sin espacios e íconos en los cuatro enlaces operativos de la barra lateral.
