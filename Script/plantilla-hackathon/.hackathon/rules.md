# Reglas del proyecto: Hackathon NFL Big Data Bowl, UNAM

Estas reglas aplican a todo lo que generes en este proyecto. Si una petición las contradice, dilo y propón la alternativa dentro del stack.

Si el equipo declara explícitamente que se sale del stack, ignora todas las secciones de estas reglas: Stack fijo, Estructura y despliegue, IA opcional con servicios AWS y Entrega.

Estas reglas solo cubren el stack y el despliegue. El enfoque, el análisis, los datos y la calidad del trabajo son decisión del equipo.

## Stack fijo

| Capa | Versión |
|---|---|
| Python / uv | 3.12.12 / 0.11.19 |
| Backend | FastAPI 0.115.14, Uvicorn 0.34.3, Pydantic 2.11.7 |
| Datos | pandas 2.2.3, numpy 2.1.3 |
| Pruebas (opcionales) | pytest 8.3.5, httpx 0.28.1 |
| Node / npm | 22.23.1 / 10.x |
| Frontend | React 18.3.1, Vite 5.4.21, TypeScript 5.7.3, Tailwind CSS 3.4.19, Recharts 3.10.1 |
| IA (opcional) | strands-agents 1.64.0, boto3 1.44.0 |

- No agregues dependencias, no cambies versiones, no uses otros frameworks (Streamlit, Flask, Django, Next.js, Plotly Dash, notebooks como app, etc.) ni Docker. Si algo no se puede hacer con este stack, dilo y propón la alternativa dentro de él.
- Si el equipo decide salirse del stack, el equipo asume que AWS no hospedará su aplicación. Puede publicarla por su cuenta y bajo su propio riesgo, o no publicarla y subir solo el código. Avísale esto de forma breve antes de apartarte del stack, sin insistir.
- Python siempre dentro de `.venv`. Tailwind es la versión 3: no uses la sintaxis de Tailwind 4 (`@import "tailwindcss"`, `@theme`, `@tailwindcss/vite`).

## Estructura y despliegue

AWS hospeda la aplicación y la despliega tal cual, así que respeta este contrato:

- `backend/` contiene el código Python. `backend/main.py` expone `app` (FastAPI) con `GET /health` que responde `{"status": "ok"}`. Toda la API va bajo `/api/...`.
- `dashboard/` contiene el frontend. El build es `vite build` y genera `dashboard/dist`. El servidor sirve ese build y la API en la misma URL y puerto.
- El dashboard llama a la API con rutas relativas **sin diagonal inicial**: `fetch('api/<ruta>')`, nunca `fetch('/api/<ruta>')` (`<ruta>` es el nombre de tu endpoint). Tu app se publica en una subruta (`/evento/equipo/`) y con la diagonal inicial la llamada falla con 404. Esto aplica a toda ruta que escribas en el código del dashboard (imágenes, CSS, enlaces), no solo a `fetch`. Nunca uses `localhost`, `127.0.0.1` ni URLs absolutas.
- En desarrollo, Vite y Uvicorn corren por separado. Configura en `vite.config.ts` un proxy de `/api` hacia `http://localhost:8000`, y conserva `base: './'`.
- `data/` contiene los datos. Léelos con rutas relativas a la raíz del proyecto. Es solo lectura: no modifiques los archivos originales.
- El servidor es efímero: no dependas de escribir archivos en disco para que la app funcione. Calcula al arrancar o al responder.
- No cambies la estructura de carpetas ni muevas `.hackathon/`, `.venv/` ni `.kiro/`.

## IA opcional con servicios AWS

- La IA es opcional. Dentro del stack se usa solo Amazon Bedrock, con modelos Amazon Nova, mediante Strands Agents y boto3. Si el equipo prefiere otro proveedor (OpenAI, Gemini, etc.), aplica la regla de salirse del stack: AWS no lo hospeda y la llave del proveedor es responsabilidad del equipo.
- El hosting ya define `BEDROCK_MODEL_ID` y las credenciales vienen del rol: no uses llaves en el código. **No leas, no verifiques ni exijas `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` ni `AWS_SESSION_TOKEN`** (ni devuelvas un error si faltan) y no pases llaves a boto3: crea el cliente solo con la región, `boto3.client("bedrock-runtime", region_name=region)`. En AWS el rol de la tarea firma las llamadas; en tu computadora boto3 toma las llaves del `.env` por sí solo. Lee el modelo con `os.environ.get("BEDROCK_MODEL_ID", "us.amazon.nova-pro-v1:0")` y la región con `os.environ.get("AWS_REGION", "us-east-1")`. No pongas otros IDs de modelo.
- En tu computadora, las llamadas a Bedrock usan las llaves temporales del workshop, que van en un archivo `.env` en la raíz del proyecto (hay un `.env.example` para copiar) con `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` y `AWS_SESSION_TOKEN`. No agregues `python-dotenv` ni otra dependencia: al inicio de `backend/main.py`, antes de usar boto3, carga el `.env` con este código y nada más:
  ```python
  import os
  from pathlib import Path

  def cargar_env():
      f = Path(__file__).resolve().parent.parent / ".env"
      if f.exists():
          for linea in f.read_text(encoding="utf-8-sig").splitlines():
              linea = linea.strip()
              if linea and not linea.startswith("#") and "=" in linea:
                  k, v = linea.split("=", 1)
                  os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

  cargar_env()
  ```
- `.env` no se versiona y `--entregar` no lo incluye en el .zip. Nunca escribas llaves ni credenciales en el código ni en el README, y no imprimas ni registres credenciales. En el despliegue AWS asigna el rol y no se usan llaves.
- La app debe funcionar y mostrar su hallazgo principal aunque la IA falle o no esté disponible. La IA añade funciones, no sostiene el análisis.
- No crees ni llames otros servicios de AWS (S3, DynamoDB, Lambda, etc.). La infraestructura la pone AWS.

## Entrega

- Para verificar el entorno: `sh .hackathon/setup.sh --check`. Para generar el zip de entrega: `sh .hackathon/setup.sh --entregar`. En Windows: `.\.hackathon\setup.cmd --check` (o `--entregar`; en CMD omite el `.\` inicial).
