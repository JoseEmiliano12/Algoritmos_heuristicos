#!/usr/bin/env bash
# Reanuda el FHCP completo y genera resúmenes/gráficas antes y después de correr.
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo"
python="$repo/.venv/bin/python"
if [[ ! -x "$python" ]]; then
  python=python3
fi
procesos="${1:-10}"
estado="scripts/challenge_1001_45.estado"
printf 'EN_CURSO\n' > "$estado"
printf '%s\n' "$$" > scripts/challenge_1001_45.pid

"$python" scripts/challenge.py --preparar
"$python" scripts/graficas_challenge.py

if "$python" scripts/challenge.py --procesos "$procesos"; then
  "$python" scripts/graficas_challenge.py
  printf 'COMPLETO\n' > "$estado"
else
  codigo=$?
  "$python" scripts/graficas_challenge.py || true
  printf 'INTERRUMPIDO (%s)\n' "$codigo" > "$estado"
  exit "$codigo"
fi
