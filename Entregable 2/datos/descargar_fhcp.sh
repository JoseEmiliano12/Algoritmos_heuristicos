#!/usr/bin/env bash
# Descarga el FHCP Challenge Set completo (1001 grafos + soluciones oficiales .tou) en
# datos/fhcp_completo/ (ignorado por git, ~92 MB descomprimido). Requiere curl y 7z (p7zip).
# Uso desde la raíz del repositorio:  bash datos/descargar_fhcp.sh
set -euo pipefail
BASE="https://sites.flinders.edu.au/flinders-hamiltonian-cycle-project/wp-content/uploads/sites/18/2020/01"
DESTINO="datos/fhcp_completo"
mkdir -p "$DESTINO"
for archivo in FHCPCS.7z FHCPCS_sols.7z; do
  curl -fL -o "$DESTINO/$archivo" "$BASE/$archivo"
  7z x -y -o"$DESTINO" "$DESTINO/$archivo" > /dev/null
  rm "$DESTINO/$archivo"
done
echo "Listo: $(ls "$DESTINO"/*.hcp | wc -l) grafos en $DESTINO"
