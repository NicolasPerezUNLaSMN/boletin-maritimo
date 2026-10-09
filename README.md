# meMAREAVI

**Marítima Elaboraciones: Módulo Argentino de Reportes, Emisiones y Avisos**  
**Servicio Meteorológico Nacional (SMN) · Centro Operativo de Pronóstico (COP) · METAREA VI**

Aplicación web local desarrollada en **Python + Streamlit** para integrar el pronóstico meteorológico exportado desde **PIMET**, la información de **olas** y de **hielos y témpanos** remitida por el **Servicio de Hidrografía Naval (SHN)**, y elaborar productos para navegantes: boletín METAREA VI en inglés y español, y siete productos NAVTEX (seis estaciones costeras y uno consolidado).

> **Estado del proyecto:** herramienta en desarrollo y validación operativa. El botón **Guardar emisión completa** archiva una copia local, pero **no envía** mensajes por correo, FTP ni SFTP. El futuro botón **ENVIAR** todavía no está implementado. Los productos deben revisarse antes de cualquier utilización oficial.

---

## 1. Requisitos previos

- **Windows 10/11** para pruebas locales o **Linux** para pruebas y despliegue en servidor (se documentan ambos procedimientos).
- **Python 3.11**, recomendado para reproducir el entorno de desarrollo actual.
- **Git**, para clonar el repositorio. Si recibiste el proyecto como ZIP, Git no es indispensable.
- Acceso a la red para instalar dependencias la primera vez.
- Archivos operativos de entrada: **XML de PIMET** (necesario); **TXT de olas** y **TXT de hielos/témpanos** del SHN (según disponibilidad).

### 1.1. Instalar Python en Windows si todavía no está instalado

1. Entrar en <https://www.python.org/downloads/> y descargar una versión de **Python 3.11.x** compatible con Windows.
2. Ejecutar el instalador y, si ofrece la opción, marcar **Add python.exe to PATH**. Completar la instalación.
3. Cerrar y volver a abrir PowerShell o la terminal de VS Code.
4. Comprobar la instalación:

   ```powershell
   py -3.11 --version
   py -3.11 -m pip --version
   ```

Si `py` no está disponible, probar `python --version` y `python -m pip --version`. Si Windows abre Microsoft Store en lugar de Python, revisar los *alias de ejecución de aplicaciones* de Windows y la instalación/PATH de Python.

### 1.2. Instalar Git si no está instalado

Descargarlo de <https://git-scm.com/downloads/win>, instalarlo y abrir una terminal nueva. Verificar:

```powershell
git --version
```

## 2. Obtener el código

### Opción A: clonar el repositorio Git

En PowerShell, elegir una carpeta de trabajo y ejecutar:

```powershell
cd "$HOME\Documents"
git clone <URL-DEL-REPOSITORIO>
cd <CARPETA-CREADA-POR-GIT>
```

**Importante:** reemplazar los dos valores entre `<>` por la URL real del repositorio institucional y el nombre de la carpeta creada. **No hay una URL de repositorio definida en esta documentación**, por lo que no se inventa una.

Si el repositorio es privado, Git puede solicitar credenciales o autenticación institucional. Consultar al administrador del repositorio.

### Opción B: ejecutar desde un ZIP

1. Descargar el ZIP del proyecto.
2. Extraerlo en una carpeta estable, por ejemplo `C:\proyectos\meMAREAVI`.
3. Abrir esa carpeta en PowerShell o en **Visual Studio Code** (*Archivo > Abrir carpeta*).
4. Verificar que en la carpeta actual existan **`app.py`** y **`requirements.txt`**.

> En los ejemplos siguientes, todos los comandos se ejecutan **desde la carpeta raíz del proyecto**, donde está `app.py`.

## 3. Crear y activar un entorno virtual (Windows / PowerShell)

El entorno virtual evita mezclar las bibliotecas de meMAREAVI con las de otros proyectos Python.

### 3.1. Crear el entorno (solo la primera vez)

```powershell
py -3.11 -m venv .venv
```

Si el lanzador `py` no existe pero Python funciona, usar `python -m venv .venv`.

### 3.2. Activarlo (cada vez que se abre una terminal nueva)

```powershell
.\.venv\Scripts\Activate.ps1
```

La terminal normalmente mostrará `(.venv)` al comienzo de la línea. Confirmar que el intérprete sea el esperado:

```powershell
python --version
python -m pip --version
```

### 3.3. Si PowerShell no permite activar scripts

Puede aparecer el error **“running scripts is disabled on this system”**. Para permitir la activación **solo en la sesión actual**:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

El cambio de `Process` desaparece al cerrar esa ventana. No hace falta usar permisos de administrador para este alcance. **En equipos institucionales, respetar las políticas de seguridad de TI**: si están restringidas, no intentar sortearlas y consultar a Infraestructura.

Alternativa que **no requiere activar** el entorno virtual:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Otra alternativa es abrir **Símbolo del sistema (CMD)** y ejecutar `\.venv\Scripts\activate.bat` (sin la barra inicial, es decir, `.venv\Scripts\activate.bat`).

## 4. Instalar las dependencias

Con el entorno activado, ejecutar:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

La instalación inicial puede demorar algunos minutos. `requirements.txt` es el listado de bibliotecas de esta versión; no hace falta instalarlas una por una.

Si falla la instalación por proxy o certificados de la red institucional, consultar al área de infraestructura antes de modificar la configuración de seguridad.

## 5. Iniciar la aplicación

Con el entorno activado y ubicados en la carpeta raíz:

```powershell
python -m streamlit run app.py
```

Streamlit mostrará una dirección local, normalmente **http://localhost:8501**, y puede abrir automáticamente el navegador. Si no lo hace, copiar la dirección indicada en la terminal.

- **Detener:** volver a la terminal y presionar `Ctrl + C`.
- **Cerrar el entorno virtual:** ejecutar `deactivate`.
- **Volver a usarlo otro día:** abrir terminal en el proyecto → activar `.venv` → ejecutar `python -m streamlit run app.py`. No es necesario recrear el entorno ni reinstalar dependencias en cada inicio.
- **Actualizar el repositorio:** con los cambios locales respaldados, ejecutar `git pull` y, si cambió `requirements.txt`, volver a ejecutar `python -m pip install -r requirements.txt`.

### Comandos rápidos para un segundo inicio

```powershell
cd C:\proyectos\meMAREAVI
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```

Adaptar la ruta a la carpeta real del proyecto.

---


## 6. Instalación y ejecución en Linux (Ubuntu/Debian)

Esta sección es **alternativa a los pasos 1–5 de Windows**. Sirve para una PC Linux o un servidor de pruebas. Se supone una distribución Ubuntu/Debian con `apt`, un usuario con permisos `sudo` para instalar paquetes y un repositorio institucional cuya URL deberá proporcionar DPS. Para Rocky/AlmaLinux/RHEL cambian los comandos de instalación de paquetes.

### 6.1. Instalar Python, entorno virtual y Git

Abrir una terminal y verificar primero las versiones disponibles:

```bash
python3 --version
git --version
```

Si faltan Python o Git, instalar los paquetes:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
```

**Compatibilidad:** la versión de referencia del desarrollo es **Python 3.11**. El comando anterior instala la versión que provee la distribución, que puede ser distinta. Si no es 3.11, comprobar la compatibilidad de `requirements.txt` antes de pasar a producción. No reemplazar el Python del sistema ni forzar repositorios de terceros sin autorización de Infraestructura. Si el servidor dispone de `python3.11`, usarlo en los comandos siguientes.

### 6.2. Clonar el repositorio

```bash
mkdir -p ~/aplicaciones
cd ~/aplicaciones
git clone <URL-DEL-REPOSITORIO>
cd <CARPETA-DEL-REPOSITORIO>
ls app.py requirements.txt
```

Reemplazar los valores entre `<>` por los reales; la URL institucional todavía no está documentada. Si se recibe un ZIP, extraerlo y abrir su carpeta raíz, donde se encuentran `app.py` y `requirements.txt`.

### 6.3. Crear y activar el entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
python --version
```

Para usar específicamente Python 3.11, cuando esté instalado:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

En Linux **no se utiliza `Activate.ps1` ni `Set-ExecutionPolicy`**. Si el shell informa `Permission denied`, no es necesario hacer ejecutable el script: se activa con `source`. Si `venv` falla por falta de `ensurepip`, instalar el paquete `python3-venv` correspondiente a la versión del intérprete.

### 6.4. Instalar dependencias

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si la instalación falla por restricciones de red, proxy o certificados institucionales, resolverlo con Infraestructura; no desactivar la validación TLS como solución permanente.

### 6.5. Ejecutar localmente en Linux

```bash
python -m streamlit run app.py
```

Abrir **http://localhost:8501** en el navegador de la misma máquina. Para detener, presionar `Ctrl+C`. Para salir del entorno: `deactivate`.

En sesiones posteriores:

```bash
cd ~/aplicaciones/<CARPETA-DEL-REPOSITORIO>
source .venv/bin/activate
python -m streamlit run app.py
```

**Sin activar el entorno:** también se puede ejecutar `./.venv/bin/python -m streamlit run app.py`.

### 6.6. Prueba desde otra PC de la red interna

Para una **prueba controlada**, con autorización de Infraestructura y reglas de firewall adecuadas, se puede escuchar en la interfaz de red del servidor:

```bash
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Desde otra PC de la misma red, ingresar a `http://IP-INTERNA-DEL-SERVIDOR:8501`. `0.0.0.0` significa *escuchar en todas las interfaces*, **no** es una URL de acceso. **No publicar el puerto 8501 directamente en Internet**: Streamlit no aporta por sí solo el esquema institucional de autenticación, HTTPS y control de acceso requerido para producción.

### 6.7. Persistencia y permisos en Linux

La versión actual guarda las emisiones en `data/emisiones/` y los avisos en `data/avisos.json`, relativos a la carpeta del proyecto. Por eso:

- Ejecutar la aplicación con un **usuario de servicio sin privilegios de administrador**, con permisos de escritura en `data/`.
- No ejecutar Streamlit con `sudo` o como `root`.
- Mantener `data/` en un almacenamiento **persistente** y con copias de seguridad. **No** incluir datos operativos ni credenciales en el repositorio Git.
- En esta versión, `data/emisiones/` está excluida de Git, pero se debe revisar el resto de `data/` antes de cada `git add` o publicación del repositorio.
- Si se actualiza o reemplaza la carpeta del proyecto, **respaldar `data/` antes** y restaurarla en la ubicación que leerá la nueva instancia. La aplicación todavía no permite configurar su ruta mediante una variable de entorno.

Ejemplo para verificar el almacenamiento después de guardar una emisión:

```bash
find data/emisiones -maxdepth 2 -type f | head -30
du -sh data/
```

### 6.8. Servidor institucional: recomendaciones antes de producción

Para un despliegue estable se recomienda ejecutar meMAREAVI como **servicio administrado** (por ejemplo, `systemd`) detrás de un **proxy inverso HTTPS** (Nginx/Apache) con autenticación y acceso limitado a la red institucional o VPN. El servicio debería reiniciarse automáticamente ante fallas y registrar logs consultables por Infraestructura.

**No se entrega todavía una unidad `systemd` ni una configuración de Nginx lista para producción**, porque deben definirse el usuario de servicio, directorios finales, dominio interno, certificados, política de autenticación, proxy y respaldos del SMN. La versión actual tampoco está dockerizada: Docker se considera una siguiente etapa, no un requisito para probarla en Linux.

**Punto operativo importante:** antes de habilitar varios usuarios simultáneos, revisar la numeración y modificación concurrente de avisos, la persistencia de situaciones y la política de guardado. Un servidor Linux no resuelve automáticamente esos problemas.

---

## 7. Flujo operativo: cómo elaborar el boletín

**Secuencia recomendada:** preparar PIMET → obtener archivos de la casilla de pronóstico → cargar fuentes → revisar datos → crear/actualizar avisos → incorporar situaciones sinópticas → revisar METAREA y NAVTEX → descargar y **guardar** la emisión.

### Paso 1. Completar el pronóstico en PIMET

1. Ingresar a **PIMET** con el acceso habitual del COP.
2. Completar y revisar los pronósticos de las áreas correspondientes al producto marítimo.
3. **Enviar el producto desde PIMET**, de acuerdo con el procedimiento operativo vigente.
4. Obtener del **buzón de pronóstico** el **XML meteorológico** resultante y guardarlo localmente.

> No se describe una secuencia exacta de botones internos de PIMET porque no forma parte de esta aplicación y debe confirmarse con su procedimiento vigente. Lo indispensable para meMAREAVI es disponer del XML exportado con los pronósticos completos.

### Paso 2. Descargar olas y hielos desde el correo

En el **correo de pronóstico**, localizar los mensajes del **Servicio de Hidrografía Naval (SHN)** y descargar:

- **TXT de olas:** el archivo correspondiente al producto/período a elaborar.
- **TXT de hielos y témpanos:** utilizar el informe **más reciente disponible**, según el procedimiento operativo.

Guardar ambos archivos en una carpeta identificable por fecha/hora de emisión, por ejemplo `Documentos\PronosticoMaritimo\2026-10-09_12UTC\`. No modificar manualmente la estructura de los TXT sin verificar que el parser los interprete correctamente.

### Paso 3. Cargar las fuentes en meMAREAVI

En la parte superior de la aplicación, en **Fuentes**, usar los tres campos de carga (se puede **arrastrar y soltar** cada archivo sobre su recuadro, o presionar **Upload**):

| Campo | Archivo | Necesidad |
|---|---|---|
| **Subir XML meteorológico** | XML exportado desde PIMET | **Obligatorio** para generar los pronósticos |
| **Subir TXT de olas** | TXT recibido del SHN | Opcional técnicamente; cargarlo cuando esté disponible |
| **Subir TXT de hielos y témpanos** | TXT recibido del SHN | Cargar el más reciente disponible |

La carga de un archivo **no equivale a guardar una emisión** en el histórico. Antes de continuar, comprobar que la aplicación haya interpretado correctamente los archivos.

### Paso 4. Revisar las tres pestañas de fuentes

- **Meteorología:** controlar áreas, viento, tiempo significativo y visibilidad importados desde PIMET.
- **Olas:** revisar la información de olas interpretada desde el TXT del SHN y su correspondencia con las áreas.
- **Hielos:** comprobar los bloques disponibles del informe de hielos y témpanos, en inglés y español.

Si falta el TXT de olas, la aplicación puede seguir generando el boletín e indicará que no hay datos de olas disponibles. **La ausencia de datos no debe confundirse con un pronóstico válido de calma**. Revisar el resultado antes de emitir.

### Paso 5. Crear, editar o cesar avisos de temporal

Abrir la pestaña **⚠️ Avisos**:

1. Revisar la lista de **avisos vigentes**.
2. Si corresponde un aviso nuevo, completar el formulario **Nuevo aviso**: sistema, posición inicial (área, punto o polígono), movimiento, evolución, fuerza Beaufort, dirección del viento, período de validez, áreas afectadas y demás campos disponibles.
3. Seleccionar las **áreas afectadas** del XML: son importantes para determinar en qué productos NAVTEX costeros debe aparecer el aviso.
4. Guardar el aviso y verificar el texto generado.
5. Para un aviso ya existente, utilizar **Editar** y actualizar los datos; si corresponde finalizarlo, utilizar **Cesar**.
6. Verificar la **numeración de avisos** en la sección *Configuración de numeración* cuando sea necesario, especialmente al iniciar una operación o migrar el sistema.

**Persistencia:** los avisos se mantienen en `data/avisos.json`. No dependen solamente de la sesión del navegador. Antes de cambiar o reinstalar la aplicación, respaldar ese archivo.

### Paso 6. Incorporar situaciones sinópticas

Abrir la pestaña **🌀 Situación**:

1. Elegir la hora de referencia **00:00 o 12:00 UTC**.
2. Seleccionar el sistema o fenómeno; completar presión central si corresponde.
3. Indicar posición inicial, movimiento y evolución.
4. Opcionalmente, indicar posición final prevista y su fecha/hora.
5. Seleccionar las **áreas afectadas por la situación** cuando deba incorporarse a determinados NAVTEX costeros.
6. Presionar **Agregar a la situación** y revisar el texto. Si se agregó una situación incorrecta, utilizar **Eliminar** y volver a crearla.

**Atención:** las situaciones de esta versión se administran en la **sesión activa de Streamlit**. Para conservarlas como parte de una emisión histórica, guardar la emisión completa antes de cerrar la sesión. No asumir que se recuperarán automáticamente al reiniciar la aplicación.

### Paso 7. Revisar los productos finales

En **📄 Boletín final**:

- Alternar la vista previa **Inglés / Español**.
- Revisar fecha/hora UTC, avisos, sinopsis, hielos, pronósticos por área, olas y terminología.
- Descargar por separado el boletín **METAREA VI en inglés** y **en español**.

En **📡 NAVTEX**:

- Revisar los **seis productos por estación costera**.
- Revisar **TODAS LAS ESTACIONES COSTERAS**, el séptimo producto consolidado; **no incluye las áreas oceánicas**.
- Descargar los TXT individuales o el ZIP con los siete productos.
- Confirmar que los avisos y situaciones incluidos correspondan a las áreas de cada estación.

> La asociación estación/área y las abreviaturas NAVTEX deben validarse con los procedimientos operativos antes de utilizarse en una emisión oficial.

### Paso 8. Guardar la emisión completa

En **🗃️ Archivo y datos**, presionar **💾 Guardar emisión completa**.

La aplicación guarda una **instantánea** de los productos generados y de los insumos cargados: boletines en ambos idiomas, siete NAVTEX, pronósticos por área (`areas.json`), metadatos, avisos y situaciones, y copias de los archivos fuente disponibles.

- **El guardado es manual.** Descargar un TXT o ZIP **no** guarda automáticamente la emisión.
- **Cada pulsación genera una carpeta nueva**; no sobrescribe el histórico anterior. Evitar pulsaciones repetidas innecesarias.
- El archivo histórico se conserva en el **disco del equipo o servidor donde corre Streamlit**, no en el equipo del usuario que accede desde otro navegador.
- En la misma pestaña se pueden consultar emisiones anteriores, descargar una emisión completa y explorar datos por área en JSON.

**ENVIAR (futuro):** se prevé un botón para confirmar la emisión, archivarla automáticamente y luego distribuirla por correo y FTP/SFTP, registrando éxito/error y permitiendo reintentos. **Ese botón y esos envíos no existen todavía en la versión documentada.** Por ahora, la transmisión operativa —si corresponde— debe seguir el circuito autorizado vigente del COP.

---

## 8. Qué contiene el archivo histórico

Estructura ilustrativa (los nombres de archivos fuente pueden variar según lo cargado):

```text
data/
├── avisos.json
└── emisiones/
    └── <identificador-de-emision>/
        ├── metarea_ingles.txt
        ├── metarea_espanol.txt
        ├── navtex_*.txt
        ├── areas.json
        ├── metadatos.json
        └── fuente_*.xml / fuente_*.txt  (si fueron cargados)
```

La carpeta `data/emisiones/` está excluida del control de versiones mediante `.gitignore`: **clonar o actualizar el repositorio no recupera automáticamente las emisiones históricas**. Definir un respaldo separado de `data/` y una política de permisos para el despliegue final.

`areas.json` permite consultar pronósticos estructurados desde la interfaz, pero **no constituye todavía una API o endpoint HTTP**.

## 9. Volumen de datos y dimensionamiento inicial

Estimación a octubre de 2026, basada en una medición aproximada de **390–400 KB por carpeta de emisión**, con dos emisiones diarias (00 y 12 UTC) y un guardado por emisión. Unidades decimales.

| Período | Cantidad | Volumen estimado |
|---|---:|---:|
| Emisión | 1 | 390–400 KB |
| Día | 2 | 780–800 KB |
| Mes de 30 días | 60 | 23,4–24 MB |
| Año de 365 días | 730 | 284,7–292 MB |
| Cinco años | 3.650 | 1,42–1,46 GB |
| Diez años | 7.300 | 2,85–2,92 GB |

**Sugerencia de planificación:** prever inicialmente **10 GB para el histórico**, ampliables, más espacio separado para el sistema, dependencias, registros y respaldos. No es un mínimo técnico obligatorio. Las reemisiones, correcciones, nuevas fuentes y copias de seguridad incrementarán el consumo.

Para producción se recomienda: volumen persistente (no efímero), respaldo periódico y restauración probada, control de permisos, supervisión de espacio disponible, retención documentada y evaluación de concurrencia/multiusuario.

## 10. Problemas frecuentes

| Problema | Qué comprobar |
|---|---|
| `python` / `py` no se reconoce | Instalación de Python 3.11, PATH y reapertura de la terminal |
| No se activa `.venv` | Revisar ruta; en PowerShell usar `Activate.ps1`; aplicar política **Process** solo si está permitido |
| `No module named streamlit` | Activar el entorno correcto e instalar `requirements.txt` |
| No abre la página | Comprobar que Streamlit sigue ejecutándose; usar la URL que imprime la terminal |
| Puerto 8501 ocupado | Streamlit puede ofrecer otro puerto; usar la URL mostrada |
| No aparecen áreas o pronósticos | Confirmar que se cargó un XML de PIMET válido y completo |
| Faltan olas/hielos | Verificar que se cargaron los TXT correctos y revisar las pestañas correspondientes |
| No aparece una situación en NAVTEX | Verificar que se hayan seleccionado las áreas costeras afectadas |
| No encuentro una emisión guardada | Revisar la pestaña Archivo y datos y la carpeta `data/emisiones/` del servidor que ejecuta Streamlit |
| Cambié de carpeta y perdí el histórico | El historial no viaja con Git; recuperar `data/` desde su copia de seguridad |

## 11. Enlaces operativos

También accesibles desde la barra lateral del aplicativo:

- **OMM — METAREA VI:** <https://wwmiws.wmo.int/index.php/metareas/display/6>
- **SMN — Zonas costeras:** <https://www.smn.gob.ar/zonas_costeras>
- **Iridium — GMDSS:** <https://gmdss.iridium.com/#/>
- **Inmarsat — MSDS:** <https://msds.inmarsat.com/msds/>

## 12. Pendientes antes del despliegue operativo definitivo

- Validación meteorológica de textos, traducciones, abreviaturas y cobertura NAVTEX.
- Definir URL del repositorio institucional y proceso de despliegue/versionado.
- Definir servidor, volumen persistente, respaldos, permisos y recuperación ante fallas.
- Resolver persistencia de situaciones y comportamiento con varios usuarios concurrentes.
- Implementar **ENVIAR**: aprobación, archivo automático, distribución por correo/FTP/SFTP, auditoría y reintentos.
- Definir si se necesita API HTTP de consulta y qué controles de acceso debe tener.

---

**Versión documentada:** meMAREAVI v10 (identidad visual), con procedimientos de instalación en Windows y Linux. Este README describe las funciones presentes en esa versión y distingue explícitamente las capacidades previstas para el futuro.
