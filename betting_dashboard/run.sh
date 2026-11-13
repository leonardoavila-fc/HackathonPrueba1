#!/bin/bash
# ── NFL Betting Dashboard — Servidor local ──────────────────────────────────
# Uso: bash run.sh
# Abre el dashboard en http://localhost:8888

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=8888

echo ""
echo "🏈  NFL 2017 — Betting Analytics Dashboard"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Regenerar datos si el CSV es más reciente que el JSON
CSV="$SCRIPT_DIR/../data/plays.csv"
JSON="$SCRIPT_DIR/data_betting.json"

if [ ! -f "$JSON" ] || [ "$CSV" -nt "$JSON" ]; then
  echo "⚙️  Generando datos desde plays.csv..."
  python3 "$SCRIPT_DIR/build_data.py"
  echo "✓  data_betting.json actualizado"
else
  echo "✓  data_betting.json ya está actualizado"
fi

echo ""
echo "🌐  Servidor corriendo en:  http://localhost:$PORT"
echo "    Abre esa URL en tu navegador"
echo "    Presiona Ctrl+C para detener"
echo ""

# Intentar abrir el navegador automáticamente
sleep 1 && (xdg-open "http://localhost:$PORT" 2>/dev/null || open "http://localhost:$PORT" 2>/dev/null) &

# Iniciar servidor
cd "$SCRIPT_DIR"
python3 -m http.server $PORT
