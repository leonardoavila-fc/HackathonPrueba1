#!/bin/sh
# Envoltorio macOS / Linux: localiza un Python mínimo y ejecuta setup.py.
# Si no hay Python utilizable, descarga uv (versión fija) y uv provee Python. No usa sudo.
AQUI="$(cd "$(dirname "$0")" && pwd)"
UV_VERSION="$(sed -n 's/.*"uv": *"\([^"]*\)".*/\1/p' "$AQUI/stack.json")"
PY_VERSION="$(sed -n 's/.*"python": *"\([^"]*\)".*/\1/p' "$AQUI/stack.json")"

usable() {  # Python 3.8+ real (en macOS sin herramientas de Xcode /usr/bin/python3 es un aviso, no se usa)
  [ "$(uname)" = "Darwin" ] && [ "$1" = "/usr/bin/python3" ] && ! xcode-select -p >/dev/null 2>&1 && return 1
  "$1" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1
}

for c in "$AQUI/../.venv/bin/python" python3 python; do
  P="$(command -v "$c" 2>/dev/null)" && usable "$P" && exec "$P" "$AQUI/setup.py" "$@"
done

echo "No encontré Python 3.8+. Descargo uv $UV_VERSION dentro de esta carpeta para obtenerlo..."
BOOT="$AQUI/.bootstrap"
mkdir -p "$BOOT"
curl -LsSf "https://astral.sh/uv/$UV_VERSION/install.sh" -o "$BOOT/install.sh" || { echo "ERROR: sin internet. Revisa tu conexión y reintenta."; exit 1; }
UV_UNMANAGED_INSTALL="$BOOT/uv" UV_NO_MODIFY_PATH=1 sh "$BOOT/install.sh" || exit 1
export HACKATHON_BOOTSTRAP_UV="$BOOT/uv/uv"
UV_PYTHON_INSTALL_DIR="$BOOT/python" UV_CACHE_DIR="$BOOT/cache" UV_NO_CONFIG=1 \
  exec "$BOOT/uv/uv" run --no-project --managed-python --python "$PY_VERSION" python "$AQUI/setup.py" "$@"
