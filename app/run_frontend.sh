#!/bin/bash
# Arranca el frontend Vite React
export PATH="$HOME/.local/share/fnm:$PATH"
eval "$(~/.local/share/fnm/fnm env 2>/dev/null)"
cd "$(dirname "$0")/frontend"
echo "🚀 Iniciando frontend en http://localhost:5173"
~/.local/share/fnm/fnm exec --using=20 -- npm run dev
