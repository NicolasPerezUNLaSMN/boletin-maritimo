# meMAREAVI v11 — primera prueba con Docker (Windows y Linux)

Esta versión **no modifica la lógica meteorológica**: agrega los archivos de contenedorización a la v10. No está validada aún como emisión operativa oficial.

## 1. Windows — primera instalación

1. Instalar **Docker Desktop** desde https://www.docker.com/products/docker-desktop/ (usar backend WSL 2 cuando se solicite). Si Windows solicita habilitar WSL 2, abrir PowerShell como administrador y ejecutar `wsl --install`, reiniciar y completar la configuración. Verificar compatibilidad, virtualización y permisos de la PC.
2. Abrir Docker Desktop y esperar que el motor indique que está funcionando.
3. Descomprimir el ZIP en una carpeta propia, por ejemplo `C:\meMAREAVI-v11`. No ejecutar desde dentro del ZIP.
4. Abrir PowerShell **en esa carpeta**, donde están `Dockerfile`, `compose.yaml` y `app.py`.
5. Comprobar Docker:

   ```powershell
   docker --version
   docker compose version
   docker info
   ```

6. Construir y arrancar (la primera vez necesita Internet para descargar imagen y paquetes):

   ```powershell
   docker compose up -d --build
   ```

7. Abrir **http://localhost:8501** en el navegador. Revisar el estado:

   ```powershell
   docker compose ps
   docker compose logs -f
   ```

   Salir de la vista de logs con `Ctrl+C` (no detiene el contenedor).

8. Detener y reiniciar:

   ```powershell
   docker compose down
   docker compose up -d
   ```

**No hace falta instalar Python en Windows para usar Docker.** La aplicación y Python corren dentro del contenedor.

## 2. Linux — prueba en servidor

En Ubuntu/Debian instalar **Docker Engine y el plugin Compose** desde la documentación oficial: https://docs.docker.com/engine/install/ . Seguir la guía correspondiente a la distribución y la política institucional. Copiar o clonar el mismo proyecto en el servidor y ejecutar desde su directorio:

```bash
docker compose version
docker compose up -d --build
docker compose ps
docker compose logs --tail=100
```

Por defecto, el servicio se publica **solo en localhost** del host Linux (`127.0.0.1:8501`), por seguridad. Para acceso desde otras PCs de la red institucional se deberá configurar un proxy inverso HTTPS con autenticación y restricciones de red; no publicar el puerto sin esa protección.

**Permisos Linux:** el contenedor usa un usuario sin privilegios. La carpeta `./data` del host debe ser escribible por ese usuario. En caso de errores de permisos, Infraestructura debe ajustar propietario/ACL de `data/` al UID/GID del usuario del contenedor (consultar con `docker compose run --rm --entrypoint id memareavi`). No resolverlo ejecutando toda la aplicación como root.

## 3. Persistencia y respaldo

El montaje `./data:/app/data` hace que `data/avisos.json` y `data/emisiones/` vivan en el **host**, fuera del contenedor. Reiniciar o recrear el contenedor no los borra. **No eliminar `data/`** al actualizar versiones; respaldar esa carpeta antes de migraciones y de forma periódica. Los cambios en datos se comparten con cualquier ejecución local de la misma carpeta: **no abrir simultáneamente Streamlit local y Docker sobre el mismo `data/`** durante las pruebas.

Comprobar persistencia: guardar una emisión de prueba, ejecutar `docker compose down`, volver a ejecutar `docker compose up -d` y revisar que la emisión continúe en Archivo y datos.

## 4. Comandos útiles

```powershell
docker compose ps                    # estado
docker compose logs --tail=100       # últimos logs
docker compose restart               # reiniciar
docker compose down                  # detener y quitar contenedor (conserva ./data)
docker compose up -d --build         # reconstruir tras actualizar código
```

Si `localhost:8501` está ocupado por otro Streamlit, cerrar esa instancia antes de iniciar Docker. Si el contenedor no arranca, revisar `docker compose logs --tail=100`.

## 5. Límites de esta primera versión

- El guardado histórico sigue siendo **manual**; no existe todavía el botón operativo ENVIAR ni la distribución por correo/FTP.
- No hay autenticación ni controles de concurrencia robustos: usar en PC local o entorno de prueba controlado.
- `requirements-docker.txt` contiene la dependencia directa Streamlit, para evitar arrastrar al contenedor un `requirements.txt` generado en Windows con dependencias ajenas. Se debe validar y congelar el conjunto de dependencias antes de producción.
- La imagen se construye con `python:3.11-slim` para compatibilidad Windows (Docker Linux containers) y Linux.
- Para producción: revisión de seguridad, pruebas de integración, backups, proxy HTTPS, autenticación, monitoreo y validación por COP/Infraestructura.

## 6. Flujo funcional

Se mantiene el flujo descrito en `README.md`: cargar XML de PIMET y TXT de olas/hielos SHN, revisar pronósticos, gestionar avisos y situaciones, revisar METAREA/NAVTEX y guardar emisión completa.
