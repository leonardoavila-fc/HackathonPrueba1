#!/usr/bin/env python3
"""Instalador del entorno del hackathon.

Instala TODO dentro de la carpeta del proyecto (uv, Python, .venv, Node portátil, node_modules).
No usa sudo, no toca el PATH global y no instala nada en el sistema.
Solo usa la librería estándar de Python.

Uso:
  setup.sh                      pregunta el nombre del proyecto, lo crea e instala
  setup.sh --name mi-proyecto   igual, sin preguntar
  setup.sh --check              solo valida lo instalado
  setup.sh --entregar           valida, revisa el README, compila y genera el .zip de entrega
"""
import argparse
import datetime
import getpass
import traceback
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

for _f in (sys.stdout, sys.stderr):
    try:
        _f.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

INFRA_DIR = Path(__file__).resolve().parent             # carpeta .hackathon/
SCRIPT_DIR = INFRA_DIR.parent                           # raíz de la plantilla o del proyecto
MARKER = ".hackathon/proyecto"                          # marca que identifica una carpeta de proyecto
DEFAULT_NAME = "hackathon-unam"
COPY_IGNORE = {".git", ".venv", ".tools", ".cache", "node_modules", "dist", "__pycache__", "setup.log", "setup-log.txt", ".bootstrap"}


class SetupError(Exception):
    """Error con mensaje claro: qué falló y qué hacer."""

    def __init__(self, que, que_hacer=""):
        super().__init__(que)
        self.que, self.que_hacer = que, que_hacer


# ---------------------------------------------------------------- registro y mensajes
_buffer = []        # líneas de log antes de saber dónde vive el proyecto
_logfile = None


def log(texto):
    linea = f"{datetime.datetime.now():%H:%M:%S} {texto}"
    if _logfile:
        with open(_logfile, "a", encoding="utf-8") as f:
            f.write(linea + "\n")
    else:
        _buffer.append(linea)


def set_logfile(path):
    global _logfile
    _logfile = path
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"\n===== setup {datetime.datetime.now():%Y-%m-%d %H:%M:%S} =====\n")
        f.write("\n".join(_buffer) + ("\n" if _buffer else ""))
    _buffer.clear()


def cmd_setup(args=""):
    """Comando para volver a correr el script, según el sistema (en Windows funciona en CMD y PowerShell)."""
    base = r".\.hackathon\setup.cmd" if os.name == "nt" else "sh .hackathon/setup.sh"
    return f"{base} {args}".strip()


def say(texto=""):
    print(texto, flush=True)
    log(texto)


def paso(n, total, titulo):
    say(f"\n[{n}/{total}] {titulo}")


# ---------------------------------------------------------------- sistema
def detectar_sistema():
    s = platform.system().lower()
    so = {"darwin": "macos", "linux": "linux", "windows": "windows"}.get(s)
    if not so:
        raise SetupError(f"Sistema operativo no soportado: {platform.system()}", "Usa macOS, Linux o Windows 10/11.")
    m = platform.machine().lower()
    arq = "arm64" if m in ("arm64", "aarch64") else "x64" if m in ("x86_64", "amd64") else None
    if so == "macos" and arq == "x64":
        # Python bajo Rosetta en un Mac Apple Silicon reporta x86_64
        r = subprocess.run(["sysctl", "-n", "hw.optional.arm64"], capture_output=True, text=True)
        if r.stdout.strip() == "1":
            arq = "arm64"
    if not arq:
        raise SetupError(f"Arquitectura no soportada: {platform.machine()}", "Se soportan x64 y ARM64.")
    return so, arq


class Proyecto:
    """Rutas del proyecto y variables de entorno aisladas."""

    def __init__(self, raiz, so, arq, stack):
        self.raiz, self.so, self.arq, self.stack = Path(raiz), so, arq, stack
        win = so == "windows"
        self.infra = self.raiz / ".hackathon"
        self.tools = self.infra / ".tools"
        self.cache = self.infra / ".cache"
        self.uv_dir = self.tools / "uv"
        self.uv = self.uv_dir / ("uv.exe" if win else "uv")
        self.py_dir = self.tools / "python"
        self.venv = self.raiz / ".venv"
        self.venv_py = self.venv / ("Scripts/python.exe" if win else "bin/python")
        self.node_dir = self.tools / "node"
        self.node_bin = self.node_dir if win else self.node_dir / "bin"
        self.node = self.node_bin / ("node.exe" if win else "node")
        self.npm = self.node_bin / ("npm.cmd" if win else "npm")
        self.dash = self.raiz / stack["dashboard_dir"]

    def env(self):
        e = dict(os.environ)
        for k in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV", "UV_INDEX_URL", "PIP_INDEX_URL", "PIP_EXTRA_INDEX_URL",
                  "UV_EXTRA_INDEX_URL", "NODE_OPTIONS", "NODE_PATH"):
            e.pop(k, None)
        e.update({
            "UV_CACHE_DIR": str(self.cache / "uv"),
            "UV_PYTHON_INSTALL_DIR": str(self.py_dir),
            "UV_UNMANAGED_INSTALL": str(self.uv_dir),
            "UV_NO_MODIFY_PATH": "1",
            "UV_NO_CONFIG": "1",
            "UV_PYTHON_PREFERENCE": "only-managed",
            "UV_DEFAULT_INDEX": "https://pypi.org/simple",
            "UV_NO_PROGRESS": "1",
            "npm_config_cache": str(self.cache / "npm"),
            "npm_config_userconfig": str(self.cache / "npmrc-usuario"),
            "npm_config_globalconfig": str(self.cache / "npmrc-global"),
            "npm_config_registry": "https://registry.npmjs.org/",
            "npm_config_update_notifier": "false",
            "npm_config_fund": "false",
            "npm_config_audit": "false",
        })
        e["PATH"] = os.pathsep.join([str(self.node_bin), str(self.uv_dir), e.get("PATH", "")])
        return e


def run(cmd, proy, cwd=None, titulo=None):
    """Ejecuta un comando, guarda toda la salida en setup.log y devuelve (código, salida)."""
    log("$ " + " ".join(str(c) for c in cmd))
    try:
        p = subprocess.run([str(c) for c in cmd], cwd=str(cwd or proy.raiz), env=proy.env(),
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
    except PermissionError as e:
        raise SetupError(f"No se pudo ejecutar {cmd[0]}: {e}",
                         "Probablemente un antivirus o la configuración de seguridad lo bloquea. "
                         "Permite la carpeta del proyecto en tu antivirus y vuelve a correr el script.")
    except OSError as e:
        raise SetupError(f"No se pudo ejecutar {cmd[0]}: {e}", "Vuelve a correr el script; si persiste, envía setup.log.")
    log(p.stdout.rstrip())
    return p.returncode, p.stdout


def run_ok(cmd, proy, que_fallo, que_hacer, cwd=None):
    codigo, salida = run(cmd, proy, cwd)
    if codigo != 0:
        cola = "\n".join(salida.strip().splitlines()[-15:])
        if re.search(r"No space left|ENOSPC|disk full", salida, re.I):
            que_hacer = "Te quedaste sin espacio en disco. Libera unos 2 GB y vuelve a correr el script."
        elif re.search(r"getaddrinfo|ENOTFOUND|Connection|timed out|network|dns|ECONNRESET|certificate", salida, re.I):
            que_hacer = ("Parece un problema de red (sin internet, wifi saturado, proxy o certificado). "
                         "Revisa tu conexión y vuelve a correr el script: continúa donde se quedó.")
        raise SetupError(f"{que_fallo}\n    Salida:\n      " + cola.replace("\n", "\n      "), que_hacer)
    return salida


# ---------------------------------------------------------------- utilidades
def descargar(url, destino, etiqueta):
    """Descarga con barra de progreso simple. Devuelve la ruta."""
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    tmp = destino.with_suffix(destino.suffix + ".part")
    log(f"descargando {url}")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'hackathon-setup/1.0 (curl-compatible)'})
        with urllib.request.urlopen(req, timeout=60) as r, open(tmp, "wb") as f:
            total = int(r.headers.get("Content-Length") or 0)
            leido, ultimo = 0, -1
            while True:
                bloque = r.read(1 << 20)
                if not bloque:
                    break
                f.write(bloque)
                leido += len(bloque)
                if total and sys.stdout.isatty():
                    pct = int(leido * 100 / total)
                    if pct != ultimo:
                        print(f"\r    {etiqueta}: {pct}%  ({leido >> 20} MB)", end="", flush=True)
                        ultimo = pct
            if sys.stdout.isatty() and total:
                print()
        os.replace(tmp, destino)
    except urllib.error.URLError as e:
        tmp.unlink(missing_ok=True)
        raise SetupError(f"No se pudo descargar {url}: {e.reason if hasattr(e, 'reason') else e}",
                         "Revisa tu conexión a internet (o proxy/VPN). Si el wifi está saturado, pide la instalación sin conexión a los organizadores.")
    except OSError as e:
        tmp.unlink(missing_ok=True)
        raise SetupError(f"Error escribiendo la descarga ({e})", "Revisa el espacio en disco y los permisos de la carpeta del proyecto.")
    return destino


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def extraer_sin_prefijo(archivo, destino):
    """Extrae un .tar.gz/.tar.xz/.zip quitando la carpeta raíz, validando rutas."""
    destino = Path(destino)
    tmp = destino.with_name(destino.name + ".tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    base = tmp.resolve()
    if str(archivo).endswith(".zip"):
        with zipfile.ZipFile(archivo) as z:
            for m in z.infolist():
                partes = Path(m.filename).parts[1:]
                if not partes:
                    continue
                t = (tmp.joinpath(*partes)).resolve()
                if base not in t.parents and t != base:
                    raise SetupError("El archivo descargado tiene rutas inseguras", "No continúes; avisa a los organizadores.")
                if m.is_dir():
                    t.mkdir(parents=True, exist_ok=True)
                else:
                    t.parent.mkdir(parents=True, exist_ok=True)
                    with z.open(m) as src, open(t, "wb") as out:
                        shutil.copyfileobj(src, out)
    else:
        with tarfile.open(archivo) as t_:
            for m in t_.getmembers():
                partes = Path(m.name).parts[1:]
                if not partes:
                    continue
                m.name = str(Path(*partes))
                t = (tmp / m.name).resolve()
                if base not in t.parents and t != base:
                    raise SetupError("El archivo descargado tiene rutas inseguras", "No continúes; avisa a los organizadores.")
                t_.extract(m, tmp, filter="tar") if hasattr(tarfile, "tar_filter") else t_.extract(m, tmp)
    shutil.rmtree(destino, ignore_errors=True)
    os.replace(tmp, destino)


def salida(cmd, proy):
    try:
        r = subprocess.run([str(c) for c in cmd], env=proy.env(), capture_output=True, text=True, timeout=120)
        return r.stdout.strip() if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


# ---------------------------------------------------------------- pasos de instalación
def instalar_uv(pr):
    esperado = pr.stack["uv"]
    def version():
        v = salida([pr.uv, "--version"], pr) if pr.uv.exists() else None
        return v.split()[1] if v else None
    if version() == esperado:
        say(f"    uv {esperado} ya instalado")
        return
    if pr.uv_dir.exists():
        say("    uv incompleto o de otra versión: se reinstala")
        shutil.rmtree(pr.uv_dir, ignore_errors=True)
    boot = os.environ.get("HACKATHON_BOOTSTRAP_UV")      # uv que dejó el envoltorio
    if boot and Path(boot).exists():
        pr.uv_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(boot, pr.uv)
        os.chmod(pr.uv, 0o755)
        if version() == esperado:
            say(f"    uv {esperado} copiado desde el arranque")
            return
        shutil.rmtree(pr.uv_dir, ignore_errors=True)
    if pr.so == "windows":
        url = f"https://astral.sh/uv/{esperado}/install.ps1"
        inst = descargar(url, pr.cache / "downloads" / "uv-install.ps1", "instalador de uv")
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", inst]
    else:
        url = f"https://astral.sh/uv/{esperado}/install.sh"
        inst = descargar(url, pr.cache / "downloads" / "uv-install.sh", "instalador de uv")
        cmd = ["sh", inst]
    run_ok(cmd, pr, "Falló el instalador de uv", "Revisa tu conexión a internet y vuelve a correr el script.")
    if version() != esperado:
        raise SetupError(f"uv no quedó en la versión {esperado}", "Borra la carpeta .tools del proyecto y vuelve a correr el script.")
    say(f"    uv {esperado} instalado en .tools/uv")


def instalar_python(pr):
    v = pr.stack["python"]
    run_ok([pr.uv, "python", "install", v, "--no-bin", "--no-registry"], pr,
           f"No se pudo instalar Python {v}", "Revisa tu conexión a internet y vuelve a correr el script.")
    say(f"    Python {v} disponible en .tools/python")


def version_venv(pr):
    if not pr.venv_py.exists():
        return None
    return salida([pr.venv_py, "-c", "import sys;print('.'.join(map(str,sys.version_info[:3])))"], pr)


def crear_venv(pr):
    v = pr.stack["python"]
    actual = version_venv(pr)
    if actual == v:
        say(f"    .venv ya existe (Python {v})")
        return
    if pr.venv.exists():
        say(f"    .venv roto o de otra versión ({actual or 'no ejecuta'}): se reconstruye")
        shutil.rmtree(pr.venv, ignore_errors=True)
    run_ok([pr.uv, "venv", "--python", v, pr.venv], pr, "No se pudo crear .venv", "Borra la carpeta .venv y vuelve a correr.")
    say("    .venv creado")


def instalar_deps_python(pr):
    lock = pr.infra / pr.stack["python_lock"]
    if not lock.exists():
        raise SetupError(f"Falta {lock.name}", "Vuelve a descargar la plantilla del hackathon.")
    run_ok([pr.uv, "pip", "install", "--python", pr.venv_py, "--only-binary", ":all:", "--require-hashes", "-r", lock], pr,
           "No se pudieron instalar las dependencias de Python",
           "Revisa tu conexión y vuelve a correr el script. Si el error menciona una rueda (wheel) no disponible, envía setup.log.")
    say("    Dependencias de Python instaladas desde el archivo de bloqueo")


def nombre_node(pr):
    v = pr.stack["node"]
    ext = {"macos": "tar.gz", "linux": "tar.xz", "windows": "zip"}[pr.so]
    plat = {"macos": "darwin", "linux": "linux", "windows": "win"}[pr.so]
    return f"node-v{v}-{plat}-{pr.arq}.{ext}"


def instalar_node(pr):
    v = pr.stack["node"]
    sello = pr.node_dir / ".instalado"
    if pr.node.exists() and sello.exists() and sello.read_text().strip() == nombre_node(pr) and salida([pr.node, "--version"], pr) == f"v{v}":
        say(f"    Node v{v} ya instalado")
        return
    if pr.node_dir.exists():
        say("    Node incompleto o de otra versión: se reinstala")
        shutil.rmtree(pr.node_dir, ignore_errors=True)
    base = f"https://nodejs.org/dist/v{v}"
    nombre = nombre_node(pr)
    sumas = descargar(f"{base}/SHASUMS256.txt", pr.cache / "downloads" / "SHASUMS256.txt", "sumas de verificación")
    esperada = None
    for linea in sumas.read_text().splitlines():
        h, _, n = linea.partition("  ")
        if n.strip() == nombre:
            esperada = h.strip()
    if not esperada:
        raise SetupError(f"{nombre} no aparece en SHASUMS256.txt", "Avisa a los organizadores: sistema/arquitectura no soportados.")
    arch = pr.cache / "downloads" / nombre
    if not (arch.exists() and sha256(arch) == esperada):
        arch = descargar(f"{base}/{nombre}", arch, f"Node v{v}")
    real = sha256(arch)
    if real != esperada:
        arch.unlink(missing_ok=True)
        raise SetupError(f"La suma SHA-256 de {nombre} no coincide (esperada {esperada[:12]}…, real {real[:12]}…). Se borró la descarga.",
                         "No continúes con ese archivo. Vuelve a correr el script; si se repite, tu red o proxy está alterando la descarga: avisa a los organizadores.")
    say("    Suma SHA-256 verificada")
    extraer_sin_prefijo(arch, pr.node_dir)
    (pr.node_dir / ".instalado").write_text(nombre)
    if pr.so != "windows":
        for b in (pr.node_bin).iterdir():
            if not b.is_symlink():
                os.chmod(b, 0o755)
    if salida([pr.node, "--version"], pr) != f"v{v}":
        raise SetupError("Node se extrajo pero no se ejecuta", "Un antivirus podría estar bloqueándolo. Permite la carpeta del proyecto y reintenta.")
    say(f"    Node v{v} instalado en .tools/node")


def instalar_npm(pr):
    lock = pr.dash / "package-lock.json"
    if not lock.exists():
        raise SetupError("Falta dashboard/package-lock.json", "Vuelve a descargar la plantilla del hackathon.")
    sello = pr.dash / "node_modules" / ".lock-sha256"
    h = sha256(lock)
    if sello.exists() and sello.read_text().strip() == h:
        say("    node_modules ya coincide con package-lock.json")
        return
    pr.cache.mkdir(parents=True, exist_ok=True)
    for f in ("npmrc-usuario", "npmrc-global"):
        (pr.cache / f).touch()
    run_ok([pr.npm, "ci", "--ignore-scripts"], pr, "Falló npm ci", "Revisa tu conexión y vuelve a correr el script.", cwd=pr.dash)
    sello.write_text(h)
    say("    Dependencias del frontend instaladas con npm ci --ignore-scripts")


# ---------------------------------------------------------------- verificación
def leer_pins(path):
    """requirements.txt -> {nombre_normalizado: versión}"""
    pins = {}
    for l in Path(path).read_text().splitlines():
        m = re.match(r"^([A-Za-z0-9_.-]+)==([^\s#]+)", l.strip())
        if m:
            pins[re.sub(r"[-_.]+", "-", m.group(1)).lower()] = m.group(2)
    return pins


def instalados_python(pr):
    """Paquetes instalados en .venv -> {nombre_normalizado: versión}"""
    if not pr.venv_py.exists():
        return {}
    codigo = ("import json, importlib.metadata as m;"
              "print(json.dumps({d.metadata['Name'].lower().replace('_','-').replace('.','-'): d.version for d in m.distributions()}))")
    out = salida([pr.venv_py, "-c", codigo], pr)
    try:
        return json.loads(out) if out else {}
    except ValueError:
        return {}


def verificar(pr):
    """Devuelve lista de filas (pieza, esperado, encontrado, estado)."""
    filas = []

    def fila(pieza, esperado, encontrado, ok=None):
        ok = (esperado == encontrado) if ok is None else ok
        filas.append((pieza, esperado, encontrado or "no encontrado", "OK" if ok else ("FALTA" if not encontrado else "DISTINTA")))

    st = pr.stack
    v = salida([pr.uv, "--version"], pr) if pr.uv.exists() else None
    fila("uv", st["uv"], v.split()[1] if v else None)
    fila("Python (.venv)", st["python"], version_venv(pr))
    nv = salida([pr.node, "--version"], pr) if pr.node.exists() else None
    fila("Node", f"v{st['node']}", nv)
    npmv = salida([pr.npm, "--version"], pr) if pr.node.exists() else None
    fila("npm", f"{st['npm_major']}.x", npmv, ok=bool(npmv) and npmv.split(".")[0] == str(st["npm_major"]))

    # paquetes de Python de primer nivel
    pins = leer_pins(pr.infra / st["python_requirements"])
    inst = instalados_python(pr)
    malos = [f"{n} {inst.get(n, 'falta')}≠{v}" for n, v in pins.items() if inst.get(n) != v]
    filas.append(("Paquetes Python", f"{len(pins)} fijos", f"{len(pins) - len(malos)} coinciden", "OK" if not malos else "DISTINTA"))
    for m in malos:
        log("  paquete distinto: " + m)

    # paquetes npm de primer nivel (versión exacta en package.json)
    pj = json.loads((pr.dash / "package.json").read_text())
    todos = {**pj.get("dependencies", {}), **pj.get("devDependencies", {})}
    malos_n = []
    for n, v_ in todos.items():
        f = pr.dash / "node_modules" / n / "package.json"
        real = json.loads(f.read_text()).get("version") if f.exists() else None
        if real != v_:
            malos_n.append(f"{n} {real or 'falta'}≠{v_}")
    filas.append(("Paquetes npm", f"{len(todos)} fijos", f"{len(todos) - len(malos_n)} coinciden", "OK" if not malos_n else "DISTINTA"))
    for m in malos_n:
        log("  paquete npm distinto: " + m)

    # pruebas funcionales
    if pr.venv_py.exists():
        c = run([pr.uv, "pip", "check", "--python", pr.venv_py], pr)[0]
        filas.append(("pip check", "sin conflictos", "sin conflictos" if c == 0 else "con conflictos", "OK" if c == 0 else "DISTINTA"))
        c = run([pr.venv_py, "-c", "import pandas, numpy, fastapi, uvicorn, pydantic, strands, boto3, httpx"], pr)[0]
        filas.append(("Importar paquetes", "pandas, fastapi, pydantic, strands", "importan" if c == 0 else "fallan", "OK" if c == 0 else "FALTA"))
    return filas


def mostrar_tabla(filas):
    cols = ("Pieza", "Esperado", "Encontrado", "Estado")
    anchos = [max(len(str(r[i])) for r in [cols] + filas) for i in range(4)]
    linea = lambda r: "  " + "  ".join(str(r[i]).ljust(anchos[i]) for i in range(4))
    say(linea(cols))
    say("  " + "  ".join("-" * a for a in anchos))
    for r in filas:
        say(linea(r))
    return all(r[3] == "OK" for r in filas)


IGNORAR_PY = {"pip", "setuptools", "wheel", "pkg-resources", "distribute"}
EXT_CODIGO_DASH = (".ts", ".tsx", ".js", ".jsx", ".html")
README_MIN = 300   # caracteres; por debajo solo avisa


def desviaciones(pr):
    """Compara el proyecto contra el stack. Devuelve [(parte del stack, [detalles])]. Solo informa; no bloquea."""
    devs = []
    st = pr.stack
    pins = leer_pins(pr.infra / st["python_requirements"])
    lock = leer_pins(pr.infra / st["python_lock"])
    inst = instalados_python(pr)
    if inst:
        dist = [f"{n}: tienes {inst.get(n, 'nada')}, el stack pide {v}" for n, v in pins.items() if inst.get(n) != v]
        if dist:
            devs.append(("Python: paquetes con otra versión o faltantes", dist))
        extra = sorted(n for n in inst if n not in lock and n not in IGNORAR_PY)
        if extra:
            devs.append(("Python: paquetes que no son del stack", [f"{n} {inst[n]}" for n in extra]))
    refp = INFRA_DIR / "npm-pins.json"
    pjf = pr.dash / "package.json"
    if refp.exists() and pjf.exists():
        ref = json.loads(refp.read_text())
        pj = json.loads(pjf.read_text())
        act = {**pj.get("dependencies", {}), **pj.get("devDependencies", {})}
        dist = [f"{n}: tienes {act[n]}, el stack pide {v}" for n, v in ref.items() if n in act and act[n] != v]
        dist += [f"{n}: falta (el stack pide {v})" for n, v in ref.items() if n not in act]
        if dist:
            devs.append(("Frontend (npm): paquetes con otra versión o faltantes", dist))
        extra = sorted(n for n in act if n not in ref)
        if extra:
            devs.append(("Frontend (npm): paquetes que no son del stack", [f"{n} {act[n]}" for n in extra]))
    docker = []
    for base, dirs, files in os.walk(pr.raiz):
        dirs[:] = [d for d in dirs if d not in ENTREGA_EXCLUIR_DIRS and d != "dist"]
        for fn in files:
            if re.match(r"(?i)(dockerfile|docker-compose|compose\.ya?ml|procfile)", fn):
                docker.append(Path(base, fn).relative_to(pr.raiz).as_posix())
    if docker:
        devs.append(("Despliegue: archivos propios de contenedor o proceso (AWS usa su propia imagen)", sorted(docker)))
    contrato = []
    if pr.venv_py.exists():
        cod, sal = run([pr.venv_py, "-c",
                        "import backend.main as m;"
                        "assert hasattr(m,'app'), 'APP';"
                        "assert any(getattr(r,'path','')=='/health' for r in m.app.routes), 'HEALTH'"], pr)
        if cod != 0:
            if "APP" in sal:
                contrato.append("backend/main.py no expone la variable app (FastAPI)")
            elif "HEALTH" in sal:
                contrato.append("el backend no tiene la ruta GET /health")
    src = pr.dash / "src"
    if src.is_dir():
        locales = []
        for ruta in src.rglob("*"):
            if ruta.suffix in EXT_CODIGO_DASH and ruta.is_file():
                try:
                    t = ruta.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                if re.search(r"https?://(localhost|127\.0\.0\.1)", t):
                    locales.append(ruta.relative_to(pr.raiz).as_posix())
        if locales:
            contrato.append("el dashboard llama a localhost (usa rutas relativas como api/...): " + ", ".join(locales[:5]))
    if contrato:
        devs.append(("Contrato de despliegue", contrato))
    return devs


def mostrar_desviaciones(devs):
    if not devs:
        say("    El proyecto sigue el stack del evento")
        return
    say("    AVISO: tu proyecto se sale del stack del evento en estas partes:")
    for parte, detalles in devs:
        say(f"      * {parte}")
        for d in detalles[:10]:
            say(f"          - {d}")
        if len(detalles) > 10:
            say(f"          ... y {len(detalles) - 10} más (detalle completo en .hackathon/setup.log)")
        for d in detalles:
            log(f"  desviacion [{parte}] {d}")
    say("    Si fue a propósito: AWS no hospedará tu aplicación. Puedes publicarla por tu cuenta y bajo tu riesgo, o subir solo el código.")
    say("    Si NO fue a propósito: quita lo que sobra de tu código (y de package.json si es del frontend), borra la carpeta .venv")
    say(f"    y corre  {cmd_setup()}  para dejar el entorno igual al stack. Después vuelve a correr --check.")


def revisar_readme(pr):
    """Bloquea si no hay README.md o está vacío. Devuelve avisos (no bloquean). No evalúa el contenido."""
    cand = [p for p in pr.raiz.iterdir() if p.is_file() and p.name.lower() in ("readme.md", "readme.markdown", "readme.txt", "readme")]
    if not cand:
        raise SetupError("No encontré un README.md en la raíz de tu proyecto.",
                         "Escribe tu README.md (qué hallazgo encontraron, para quién es y cómo verlo) en la carpeta del proyecto y vuelve a correr --entregar. "
                         "Los jueces lo leen primero.")
    ruta = cand[0]
    texto = ruta.read_text(encoding="utf-8", errors="ignore").strip()
    if not texto:
        raise SetupError(f"{ruta.name} está vacío.", "Escribe tu README.md y vuelve a correr --entregar.")
    avisos = []
    if ruta.suffix.lower() not in (".md", ".markdown"):
        avisos.append(f"tu README se llama {ruta.name}; GitHub lo muestra mejor como README.md")
    if len(texto) < README_MIN:
        avisos.append(f"{ruta.name} es muy corto ({len(texto)} caracteres); los jueces lo leen primero")
    if not re.search(r"!\[|<img", texto):
        avisos.append(f"{ruta.name} no tiene ninguna imagen; los jueces piden un visual bien formateado")
    return avisos


# ---------------------------------------------------------------- entrega
ENTREGA_EXCLUIR_DIRS = {".venv", ".hackathon", "node_modules", ".git", ".cache", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
ENTREGA_EXCLUIR_ARCH = {".DS_Store", "Thumbs.db", "setup.log", "setup-log.txt", MARKER}
ENTREGA_AVISO_MB = 500   # solo avisa; nunca excluye datos
SECRETOS = [
    ("llave de AWS temporal (ASIA...)", re.compile(r"\bASIA[A-Z0-9]{16}\b")),
    ("llave de AWS de larga duración (AKIA...)", re.compile(r"\bAKIA[A-Z0-9]{16}\b")),
    ("token de sesión de AWS", re.compile(r"IQoJb3JpZ2lu[A-Za-z0-9+/=]{40,}")),
    ("llave secreta de AWS", re.compile(r"aws_secret_access_key\s*[=:]\s*['\"]?[A-Za-z0-9+/]{40}\b", re.I)),
    ("llave privada", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY")),
    ("token de GitHub", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("token de Slack", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("llave de API (sk-)", re.compile(r"\bsk-[A-Za-z0-9_-]{32,}\b")),
]
NOMBRES_SECRETOS = (".env", ".pem", ".key", ".p12", ".pfx")


def _mb(n):
    return f"{n / (1 << 20):.1f} MB"


def es_env(nombre):
    n = nombre.lower()
    return (n == ".env" or n.startswith(".env.")) and not n.endswith((".example", ".sample", ".template"))


def env_excluidos(pr):
    """Rutas (relativas) de los .env del proyecto que NO viajan en el zip."""
    out = []
    for base, dirs, files in os.walk(pr.raiz):
        dirs[:] = sorted(d for d in dirs if d not in ENTREGA_EXCLUIR_DIRS)
        out += [(Path(base) / f).relative_to(pr.raiz).as_posix() for f in sorted(files) if es_env(f)]
    return out


def listar_entrega(pr):
    """Devuelve la lista de (Path, arcname) a empaquetar. Los datos se incluyen siempre, sin importar el tamaño."""
    incluidos = []
    for base, dirs, files in os.walk(pr.raiz):
        dirs[:] = sorted(d for d in dirs if d not in ENTREGA_EXCLUIR_DIRS)
        for f in sorted(files):
            if f in ENTREGA_EXCLUIR_ARCH or es_env(f) or f.endswith((".pyc", ".pyo")) or re.fullmatch(r"entrega-.*\.zip", f):
                continue
            ruta = Path(base) / f
            if ruta.is_symlink() or not ruta.is_file():
                continue
            incluidos.append((ruta, ruta.relative_to(pr.raiz).as_posix()))
    return incluidos


def buscar_secretos(archivos):
    """Devuelve lista de (archivo, motivo). Nunca imprime el valor encontrado."""
    hallazgos = []
    for ruta, arc in archivos:
        nombre = ruta.name.lower()
        if (nombre == ".env" or nombre.startswith(".env.")) and not nombre.endswith((".example", ".sample", ".template")):
            hallazgos.append((arc, "archivo de variables de entorno (.env)"))
            continue
        if nombre.endswith(NOMBRES_SECRETOS[1:]) or nombre in ("credentials", "id_rsa", "id_ed25519"):
            hallazgos.append((arc, "archivo de llaves o credenciales"))
            continue
        if ruta.stat().st_size > 2 * (1 << 20):
            continue
        try:
            datos = ruta.read_bytes()
        except OSError:
            continue
        if b"\0" in datos[:4096]:
            continue
        texto = datos.decode("utf-8", errors="ignore")
        for etiqueta, rx in SECRETOS:
            if rx.search(texto):
                hallazgos.append((arc, etiqueta))
                break
    return hallazgos


RUTAS_ABS = [
    (re.compile(r"""\b(?:fetch|axios(?:\.\w+)?|EventSource|WebSocket)\s*\(\s*[`'"]/(?!/)"""), "llamada a la API con diagonal inicial"),
    (re.compile(r"""\.open\(\s*[`'"][A-Za-z]+[`'"]\s*,\s*[`'"]/(?!/)"""), "llamada a la API con diagonal inicial"),
    (re.compile(r"""\b(?:src|href)\s*=\s*[{]?\s*[`'"]/(?!/)"""), "src/href con diagonal inicial"),
    (re.compile(r"""url\(\s*[`'"]?/(?!/)"""), "url() con diagonal inicial"),
]


def hallazgos_rutas(pr):
    """Lista de rutas del dashboard que empiezan con '/' (archivo:línea y motivo)."""
    src = pr.dash / "src"
    out = []
    if not src.exists():
        return out
    for ruta in sorted(src.rglob("*")):
        if not ruta.is_file() or ruta.suffix.lower() not in (".ts", ".tsx", ".js", ".jsx", ".css"):
            continue
        try:
            lineas = ruta.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for n, linea in enumerate(lineas, 1):
            if linea.lstrip().startswith(("//", "*", "/*")):
                continue
            for rx, motivo in RUTAS_ABS:
                if rx.search(linea):
                    out.append(f"{ruta.relative_to(pr.raiz).as_posix()}:{n}  ({motivo})  {linea.strip()[:90]}")
                    break
    return out


def detalle_rutas(hallazgos):
    return "\n      ".join(hallazgos[:10]) + (f"\n      ... y {len(hallazgos) - 10} más" if len(hallazgos) > 10 else "")


MENSAJE_RUTAS = "El dashboard usa rutas que empiezan con '/'. Tu app se publica en una subruta y esas llamadas darían 404:"
ARREGLO_RUTAS = "Quita la diagonal inicial (por ejemplo fetch('api/datos') en vez de fetch('/api/datos'))"


def revisar_rutas(pr):
    """--entregar: bloquea si hay rutas del dashboard que empiezan con '/'."""
    h = hallazgos_rutas(pr)
    if h:
        raise SetupError(f"{MENSAJE_RUTAS}\n      {detalle_rutas(h)}", f"{ARREGLO_RUTAS} y vuelve a correr --entregar.")
    say("    Rutas del dashboard OK (ninguna empieza con '/')")


def entregar(pr):
    """Compila, valida, avisa de credenciales y empaqueta el proyecto en un .zip."""
    total = 7
    inicio = datetime.datetime.now()
    nombre = pr.raiz.name
    paso(1, total, "Validando el entorno")
    filas = verificar(pr)
    if not mostrar_tabla(filas):
        mostrar_desviaciones(desviaciones(pr))
        raise SetupError("El entorno no coincide con el stack del evento.",
                         f"Corre  {cmd_setup()}  para repararlo y vuelve a intentar.")

    paso(2, total, "Revisando el README y el stack")
    avisos = []
    for av in revisar_readme(pr):
        avisos.append(av)
        say(f"    AVISO: {av}")
    if not avisos:
        say("    README encontrado")
    devs = desviaciones(pr)
    mostrar_desviaciones(devs)
    if devs:
        avisos.append(f"el proyecto se sale del stack en {len(devs)} parte(s) (ver sección Desviaciones del stack)")
    revisar_rutas(pr)

    paso(3, total, "Compilando el dashboard (vite build)")
    vite = pr.dash / "node_modules" / "vite" / "bin" / "vite.js"
    if not vite.exists():
        raise SetupError("Falta vite en dashboard/node_modules.", "Corre el instalador otra vez para repararlo.")
    cod, sal = run([pr.node, vite, "build"], pr, cwd=pr.dash)
    if cod != 0:
        util = [l for l in sal.splitlines() if l.strip() and not re.match(r"\s+at ", l)]
        cola = "\n      ".join(util[:10])
        raise SetupError(f"El dashboard no compila:\n      {cola}",
                         "Corrige el error de arriba (indica el archivo y la línea) y vuelve a correr --entregar.")
    say("    Dashboard compilado en dashboard/dist")
    tsc = pr.dash / "node_modules" / "typescript" / "bin" / "tsc"
    if tsc.exists():
        cod, sal = run([pr.node, tsc, "--noEmit", "-p", pr.dash], pr)
        n = len(re.findall(r"error TS\d+", sal))
        if cod != 0:
            avisos.append(f"TypeScript reporta {n} error(es) de tipos. No bloquea la entrega; detalle en .hackathon/setup.log")
            say(f"    AVISO: {avisos[-1]}")

    paso(4, total, "Comprobando el backend (sintaxis e importación)")
    cod, sal = run([pr.venv_py, "-m", "compileall", "-q", "backend"], pr)
    if cod != 0:
        cola = "\n      ".join(sal.strip().splitlines()[-10:])
        raise SetupError(f"El backend tiene errores de sintaxis:\n      {cola}", "Corrige el archivo indicado y vuelve a correr --entregar.")
    cod, sal = run([pr.venv_py, "-c", "import backend.main"], pr)
    if cod != 0:
        cola = "\n      ".join(sal.strip().splitlines()[-10:])
        raise SetupError(f"El backend no se puede importar:\n      {cola}",
                         "Corrige el error (falta un paquete, un import mal escrito o código al importar) y vuelve a correr --entregar.")
    say("    Backend OK (backend.main se importa sin errores)")

    paso(5, total, "Buscando llaves y credenciales en tus archivos")
    for e in env_excluidos(pr):
        say(f"    {e} NO se incluye en el .zip (las llaves de desarrollo no viajan; el despliegue usa su propio rol)")
    incluidos = listar_entrega(pr)
    hallazgos = buscar_secretos(incluidos)
    if hallazgos:
        say("    AVISO: encontré posibles credenciales. NO se bloquea la entrega (pueden ser llaves temporales del workshop),")
        say("    pero los organizadores las reemplazarán por las de la cuenta de despliegue:")
        for a, m in hallazgos[:15]:
            say(f"      - {a}: {m}")
        avisos.append(f"{len(hallazgos)} archivo(s) con posibles credenciales (ver sección Credenciales detectadas)")
    else:
        say("    Sin credenciales a la vista")

    paso(6, total, "Empaquetando")
    sello = inicio.strftime("%Y%m%d-%H%M")
    destino = pr.raiz.parent / f"entrega-{nombre}-{sello}.zip"
    informe = construir_informe(pr, nombre, inicio, incluidos, hallazgos, avisos, devs)
    try:
        with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for ruta, arc in incluidos:
                z.write(ruta, f"{nombre}/{arc}")
            z.writestr(f"{nombre}/ENTREGA.md", informe)
    except OSError as e:
        destino.unlink(missing_ok=True)
        raise SetupError(f"No se pudo crear el .zip: {e}", "Revisa el espacio en disco y los permisos de la carpeta que contiene tu proyecto.")
    (pr.infra / "ENTREGA.md").write_text(informe, encoding="utf-8")

    paso(7, total, "Verificando el .zip")
    with zipfile.ZipFile(destino) as z:
        if z.testzip() is not None:
            destino.unlink(missing_ok=True)
            raise SetupError("El .zip quedó dañado.", "Vuelve a correr --entregar.")
        nombres = z.namelist()
    prohibidos = [n for n in nombres if any(f"/{d}/" in "/" + n for d in (".venv", "node_modules", ".hackathon"))]
    if prohibidos:
        destino.unlink(missing_ok=True)
        raise SetupError("El .zip incluyó carpetas que no deben ir.", "Avisa a los organizadores y envía setup.log.")
    say(f"    {len(nombres)} archivos, {_mb(destino.stat().st_size)}")
    if destino.stat().st_size > ENTREGA_AVISO_MB * (1 << 20):
        say(f"    AVISO: el .zip pesa más de {ENTREGA_AVISO_MB} MB; confirma con los organizadores que se puede subir.")
    say(f"\nLISTO. Sube este archivo:\n  {destino}")
    return 0


def construir_informe(pr, nombre, inicio, incluidos, hallazgos, avisos, devs=()):
    v = pr.stack
    tam = sum(r.stat().st_size for r, _ in incluidos)
    l = [f"# Entrega: {nombre}", "",
         f"- Generado: {inicio.strftime('%Y-%m-%d %H:%M')} ({pr.so} {pr.arq})",
         f"- Stack verificado: Python {v['python']}, Node {v['node']}, uv {v['uv']}",
         "- Dashboard compilado: sí (dashboard/dist)",
         "- Backend: se importa sin errores",
         f"- Archivos incluidos: {len(incluidos)} ({_mb(tam)} sin comprimir)",
         "- Desviaciones del stack: " + (f"si ({len(devs)})" if devs else "ninguna"), ""]
    if avisos:
        l += ["## Avisos"] + [f"- {a}" for a in avisos] + [""]
    if devs:
        l += ["## Desviaciones del stack (AWS no hospeda proyectos fuera del stack)"]
        for parte, detalles in devs:
            l += [f"- {parte}"] + [f"  - {d}" for d in detalles]
        l += [""]
    if hallazgos:
        l += ["## Credenciales detectadas (reemplazar en la cuenta de despliegue)",
              "Se detectaron por patrón; el valor no se imprime aquí. Las ASIA... son temporales y ya pueden haber caducado.",
              "Si están escritas en el código, cámbialas por el rol IAM de la cuenta o por variables de entorno."] + [f"- {a}: {m}" for a, m in hallazgos] + [""]
    l += ["## Cómo ejecutarlo", "Ver INSTALACION.md del evento. Backend: `uvicorn backend.main:app`. Dashboard: `cd dashboard && npm ci && npm run dev`.", ""]
    return "\n".join(l)


# ---------------------------------------------------------------- proyecto
def validar_nombre(n):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,39}", n or ""):
        raise SetupError(f"Nombre de proyecto no válido: '{n}'",
                         "Usa solo letras sin acentos, números, guion y guion bajo (máx. 40), sin espacios. Ejemplo: hackathon-unam")


def avisar_ruta(ruta, so):
    s = str(ruta)
    if not s.isascii() or " " in s or len(s) > 80:
        aviso = "La ruta tiene espacios, acentos o es larga; algunas herramientas pueden fallar."
        if so == "windows":
            aviso += " En Windows se recomienda una ruta corta como C:\\hackathon."
        say("    AVISO: " + aviso)


def instalar_reglas(pr):
    """Copia las reglas de Kiro a .kiro/steering/rules.md si el proyecto aún no las tiene (no pisa cambios del equipo)."""
    origen = INFRA_DIR / "rules.md"
    destino = pr.raiz / ".kiro" / "steering" / "rules.md"
    if destino.exists() or not origen.exists():
        return
    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origen, destino)
        say("    Reglas de Kiro instaladas en .kiro/steering/rules.md")
    except OSError as e:
        say(f"    AVISO: no se pudieron instalar las reglas de Kiro ({e}). No bloquea la instalación.")


ENV_EJEMPLO = """# Copia este archivo como .env y pega las llaves temporales del workshop (valen unas horas).
# .env no se versiona y NO se incluye en el .zip de entrega.
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=
AWS_REGION=us-east-1
"""


def instalar_env_ejemplo(pr):
    """Crea .env.example en la raíz del proyecto si no existe (no pisa nada)."""
    destino = pr.raiz / ".env.example"
    if destino.exists():
        return
    try:
        destino.write_text(ENV_EJEMPLO, encoding="utf-8")
    except OSError:
        pass


SCRIPT_VERSION = "2026-11-16"


def registrar_contexto(args, so, arq, raiz):
    """Escribe en setup.log los datos del equipo y del modo de ejecución (solo al log, no a pantalla)."""
    modo = "entregar" if args.entregar else "check" if args.check else "instalación"
    log(f"MODO: {modo}  |  versión del script: {SCRIPT_VERSION}  |  argumentos: {' '.join(sys.argv[1:]) or '(ninguno)'}")
    log(f"SISTEMA: {platform.platform()}  |  detectado: {so} {arq}  |  versión: {platform.version()}")
    if so == "windows":
        try:
            import ctypes
            log(f"WINDOWS: build {sys.getwindowsversion().build}  |  administrador: {bool(ctypes.windll.shell32.IsUserAnAdmin())}")
        except Exception as e:
            log(f"WINDOWS: no se pudo leer build/administrador ({e})")
    log(f"PYTHON: {platform.python_version()} ({sys.executable})")
    try:
        usuario = getpass.getuser()
    except Exception:
        usuario = "?"
    log(f"USUARIO: {usuario}  |  carpeta actual: {os.getcwd()}")
    log(f"PROYECTO: {raiz}  |  largo de ruta: {len(str(raiz))}  |  espacios: {' ' in str(raiz)}  |  no ASCII: {not str(raiz).isascii()}")
    try:
        libre = shutil.disk_usage(raiz).free / (1 << 30)
        log(f"DISCO LIBRE: {libre:.1f} GB")
    except OSError:
        pass
    log("PROXY: " + (", ".join(f"{k}=definido" for k in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy") if os.environ.get(k)) or "ninguno"))


def preparar_proyecto(args, so, arq):
    """Devuelve la raíz del proyecto, creándola desde la plantilla si hace falta."""
    if (SCRIPT_DIR / MARKER).exists():
        return SCRIPT_DIR            # ya estamos dentro de un proyecto
    if args.check or args.entregar:
        nombre = args.name or DEFAULT_NAME
        for padre in (Path(args.parent).resolve() if args.parent else Path.cwd(), SCRIPT_DIR.parent):
            if (padre / nombre / MARKER).exists():
                return padre / nombre
        raise SetupError("No encontré un proyecto instalado para validar.",
                         "Ejecuta --check desde dentro de la carpeta de tu proyecto, o pasa --name y --parent.")
    nombre = args.name
    if not nombre:
        if sys.stdin.isatty():
            nombre = input(f"Nombre del proyecto [{DEFAULT_NAME}]: ").strip() or DEFAULT_NAME
        else:
            nombre = DEFAULT_NAME
    validar_nombre(nombre)
    if args.parent:
        padre = Path(args.parent).resolve()
    else:
        padre = SCRIPT_DIR.parent   # siempre junto a la plantilla extraída
    destino = padre / nombre
    if destino.exists() and not (destino / MARKER).exists():
        if any(destino.iterdir()):
            raise SetupError(f"La carpeta {destino} ya existe y no es un proyecto del hackathon.", "Elige otro nombre con --name.")
    if (destino / MARKER).exists():
        say(f"    El proyecto {destino} ya existe: se reutiliza (se repara lo que falte)")
        return destino
    say(f"    Creando proyecto en: {destino}")
    avisar_ruta(destino, so)
    try:
        def ignorar(d, nombres):
            extra = {"setup.sh", "setup.cmd", "INSTALACION.md"} if Path(d) == SCRIPT_DIR else set()
            return [n for n in nombres if n in COPY_IGNORE or n in extra]
        shutil.copytree(SCRIPT_DIR, destino, ignore=ignorar, dirs_exist_ok=True)
        if (SCRIPT_DIR / "INSTALACION.md").exists():
            shutil.copy2(SCRIPT_DIR / "INSTALACION.md", destino / ".hackathon" / "INSTALACION.md")
        (destino / MARKER).write_text(f"creado {datetime.datetime.now().isoformat()}\n")
    except OSError as e:
        raise SetupError(f"No se pudo crear {destino}: {e}", "Revisa permisos y espacio en disco, o elige otra carpeta con --parent.")
    return destino


def main():
    ap = argparse.ArgumentParser(description="Instala y valida el entorno del hackathon (todo dentro de la carpeta del proyecto).")
    ap.add_argument("--check", action="store_true", help="solo valida lo instalado; no descarga ni instala")
    ap.add_argument("--entregar", action="store_true", help="valida, compila y genera el .zip de entrega")
    ap.add_argument("--name", help=f"nombre de la carpeta del proyecto (por defecto {DEFAULT_NAME})")
    ap.add_argument("--parent", help="carpeta donde crear el proyecto (por defecto, junto a la plantilla extraída)")
    ap.add_argument("--offline", metavar="CARPETA", help="instalar desde una carpeta local (aún no disponible)")
    args = ap.parse_args()
    if args.offline:
        raise SetupError("El modo --offline todavía no está implementado en esta versión.", "Usa la instalación normal con internet.")
    stack = json.loads((INFRA_DIR / "stack.json").read_text())
    so, arq = detectar_sistema()
    say(f"Sistema detectado: {so} {arq}  |  Python del arranque: {platform.python_version()}")
    raiz = preparar_proyecto(args, so, arq)
    (raiz / ".hackathon").mkdir(parents=True, exist_ok=True)
    set_logfile(raiz / ".hackathon" / "setup.log")
    registrar_contexto(args, so, arq, raiz)
    pr = Proyecto(raiz, so, arq, stack)
    say(f"Proyecto: {raiz}")
    if args.entregar:
        say("\nPreparando la entrega...")
        return entregar(pr)
    if args.check:
        say("\nValidando (no se descarga ni instala nada)...")
        ok = mostrar_tabla(verificar(pr))
        say("\nRevisando desviaciones del stack...")
        mostrar_desviaciones(desviaciones(pr))
        rutas = hallazgos_rutas(pr)
        if rutas:
            say(f"\nAVISO: {MENSAJE_RUTAS}\n      {detalle_rutas(rutas)}\n    {ARREGLO_RUTAS}. Si no lo corriges, --entregar se detendrá.")
        say("\nRESULTADO: " + ("TODO OK, puedes entregar." if ok and not rutas else "El entorno está bien, pero corrige las rutas de arriba antes de entregar." if ok else "HAY PROBLEMAS. Corre setup sin --check para repararlos y envía setup.log si persisten."))
        return 0 if ok else 1
    total = 8
    paso(1, total, "Preparando carpetas")
    for d in (pr.tools, pr.cache, pr.cache / "downloads"):
        d.mkdir(parents=True, exist_ok=True)
    instalar_reglas(pr)
    instalar_env_ejemplo(pr)
    paso(2, total, f"Instalando uv {stack['uv']}"); instalar_uv(pr)
    paso(3, total, f"Instalando Python {stack['python']} y creando .venv"); instalar_python(pr); crear_venv(pr)
    paso(4, total, "Instalando dependencias de Python (una sola resolución, solo ruedas)"); instalar_deps_python(pr)
    paso(5, total, f"Descargando Node {stack['node']} portátil y verificando SHA-256"); instalar_node(pr)
    paso(6, total, "Instalando dependencias del frontend (npm ci)"); instalar_npm(pr)
    paso(7, total, "Comprobando todo")
    ok = mostrar_tabla(verificar(pr))
    paso(8, total, "Resultado")
    if ok:
        say(f"\nTODO OK. Tu proyecto está en:\n  {raiz}\nTrabaja dentro de esa carpeta. Cuando termines, corre:  {cmd_setup('--entregar')}")
        return 0
    say("\nHAY PIEZAS CON PROBLEMAS (ver tabla). Vuelve a correr el script; si persiste, envía el archivo setup.log a soporte.")
    return 1


if __name__ == "__main__":
    codigo = 1
    try:
        codigo = main()
    except SetupError as e:
        say(f"\nERROR: {e.que}")
        if e.que_hacer:
            say(f"QUÉ HACER: {e.que_hacer}")
        codigo = 1
    except KeyboardInterrupt:
        say("\nCancelado. Puedes volver a correr el script: continúa donde se quedó.")
        codigo = 130
    except Exception as e:
        log("ERROR INESPERADO:\n" + traceback.format_exc())
        say(f"\nERROR INESPERADO: {type(e).__name__}: {e}")
        say("QUÉ HACER: vuelve a correr el script; si persiste, envía el archivo setup.log a soporte.")
        codigo = 1
    log(f"FIN con código de salida {codigo}")
    visible = None
    try:
        if _logfile:
            visible = _logfile.parent.parent / "setup-log.txt"
            shutil.copyfile(_logfile, visible)
        elif _buffer:
            visible = Path.cwd() / "setup-log.txt"
            visible.write_text("\n".join(_buffer) + "\n", encoding="utf-8")
    except Exception:
        visible = None
    if visible:
        print(f"\nRegistro técnico (si algo falla, envía este archivo a soporte):\n  {visible}", flush=True)
    sys.exit(codigo)
