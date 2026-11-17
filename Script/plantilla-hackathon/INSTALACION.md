# Instalación del entorno del hackathon

Prepara tu laptop con el stack exacto del evento. **No requiere administrador** y **no toca lo que ya tengas instalado**:
todo queda dentro de la carpeta de tu proyecto. Para desinstalar, borra esa carpeta.

> **Importante:** el script crea una carpeta nueva con el nombre de tu proyecto. **Esa carpeta nueva es tu proyecto**;
> trabaja y entrega desde ahí, no desde la carpeta donde descomprimiste el zip.

## macOS y Linux
1. Descomprime el zip donde quieras trabajar (por ejemplo, tu carpeta de Documentos).
2. Abre una Terminal en esa carpeta y ejecuta:
   ```
   sh setup.sh
   ```
3. Escribe el nombre de tu proyecto (por defecto `hackathon-unam`; sin espacios ni acentos).
4. Espera a ver `TODO OK`. La primera vez descarga unos cientos de MB.

## Cómo queda tu proyecto
```
tu-proyecto/
  backend/      tu código Python (FastAPI)
  dashboard/    tu código del frontend (React)
  data/         datos del evento
  .venv/        Python del proyecto (no lo toques)
  .hackathon/   herramientas del evento (no lo toques)
```
Trabaja solo en `backend/`, `dashboard/` y `data/`. No hay carpeta de pruebas: pruébalo como prefieras.

## Windows
1. Descomprime el zip en una ruta corta, por ejemplo `C:\hackathon` (evita rutas muy largas).
2. Haz doble clic en `setup.cmd`. Si Windows muestra un aviso de SmartScreen, elige "Más información" y "Ejecutar de todos modos".
3. Escribe el nombre de tu proyecto (por defecto `hackathon-unam`) y espera a ver `TODO OK`.
4. Para validar antes de entregar, abre PowerShell o CMD dentro de tu proyecto y ejecuta (en CMD omite el `.\` inicial):
   ```
   .\.hackathon\setup.cmd --check
   ```

## Ver tu aplicación
Abre siempre `http://localhost:...` en el navegador, no `http://127.0.0.1:...`: en algunos sistemas el dashboard solo escucha en `localhost`.

## Cuando termines: generar tu entrega
Dentro de la carpeta de tu proyecto (macOS / Linux):
```
sh .hackathon/setup.sh --entregar
```
En Windows, en PowerShell o CMD dentro de tu proyecto (en CMD omite el `.\` inicial):
```
.\.hackathon\setup.cmd --entregar
```
El script valida tu entorno, **revisa que exista tu `README.md`**, compila el dashboard, revisa que el backend arranque, avisa si hay llaves o credenciales
y crea `entrega-<tu-proyecto>-<fecha>.zip` **junto a la carpeta de tu proyecto**. Ese `.zip` es lo que subes.

- Si encuentra una llave o credencial (por ejemplo las llaves temporales del workshop para Bedrock), **solo avisa** y sigue: las lista en pantalla y en `ENTREGA.md`. Los organizadores las reemplazarán por las de la cuenta de despliegue.
- Los archivos de datos se incluyen siempre, sin importar su tamaño (si renombraste o copiaste el dataset, va en el .zip). Solo se excluyen `.venv`, `node_modules`, `.git` y `.hackathon`.
- **README:** el README lo escribes tú, a mano. `--entregar` solo comprueba que `README.md` exista en la raíz y no esté vacío; si falta, se detiene. Avisa (sin detenerse) si es muy corto o no tiene imagen. No evalúa lo que dice.
- **Llaves del workshop:** en tu computadora van en un archivo `.env` en la raíz del proyecto (copia `.env.example`). `--entregar` **nunca** incluye los `.env` en el .zip; el despliegue usa su propio rol.
- **Reglas de Kiro:** al instalar se copia `.kiro/steering/rules.md` con las reglas del stack y el despliegue. Si ya existe, no se sobrescribe.
- **Stack:** `--check` y `--entregar` te dicen **qué parte** se sale del stack (versiones distintas, paquetes de Python o npm que no son del stack, archivos Docker, o rutas que no funcionarán en el hosting). Si no fue a propósito, quita lo que sobra, borra la carpeta `.venv` y corre `sh .hackathon/setup.sh` (Windows: `.\.hackathon\setup.cmd`) otra vez. Si fue a propósito, AWS no hospedará tu aplicación: puedes publicarla por tu cuenta, bajo tu riesgo, o subir solo el código.
- Si el dashboard no compila, el mensaje indica el archivo y la línea.
- Para solo validar el entorno sin generar nada: `sh .hackathon/setup.sh --check`.

## Versiones fijas (no las cambies)
Python 3.12.12, uv 0.11.19, Node 22.23.1, npm 10.x. Con otras versiones podrías no poder enviar tu proyecto.

## Problemas frecuentes
| Síntoma | Qué hacer |
|---|---|
| Sin internet / wifi saturado | Vuelve a correr `sh setup.sh` (desde la carpeta del zip) o `sh .hackathon/setup.sh` (desde tu proyecto): continúa donde se quedó. |
| "Suma SHA-256 no coincide" | Vuelve a correrlo. Si se repite, avisa a los organizadores. |
| Antivirus bloquea un programa | Permite la carpeta del proyecto en tu antivirus y reintenta. |
| Sin espacio en disco | Libera unos 2 GB y reintenta. |
| Nada funciona | Envía a soporte el archivo `setup-log.txt` que está en la carpeta de tu proyecto (se crea en cada ejecución: instalación, `--check` y `--entregar`; el script imprime su ruta al final). Es copia de `.hackathon/setup.log`. No contiene llaves ni contraseñas. |

El script nunca te pide llaves ni credenciales. No las compartas con nadie.
