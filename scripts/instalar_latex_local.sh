#!/usr/bin/env bash
# Instalación por usuario para este equipo Debian. No ejecutar con sudo.
# Documentación: https://tug.org/texlive/doc/install-tl.html
set -Eeuo pipefail

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
trap 'printf "La instalación se interrumpió en la línea %s. Revisa el mensaje anterior.\n" "$LINENO" >&2' ERR

mode=install
case "${1:-}" in
  --comprobar) mode=check ;;
  --help|-h)
    printf '%s\n' 'Uso: bash scripts/instalar_latex_local.sh [--comprobar]' \
      'Instala TeX Live en /srv/<usuario>/.local/texlive y LaTeX Workshop.' \
      '--comprobar: muestra destino y requisitos sin escribir ni descargar.'
    exit 0 ;;
  '') ;;
  *) fail "Opción desconocida: $1" ;;
esac
[[ $# -le 1 ]] || fail 'Demasiados argumentos.'
[[ $EUID -ne 0 ]] || fail 'Ejecuta este script con tu usuario normal, sin sudo.'

for tool in perl tar xz curl df findmnt mktemp uname id find grep; do
  command -v "$tool" >/dev/null || fail "Falta $tool. Instala las dependencias: sudo apt install perl tar xz-utils curl ca-certificates util-linux"
done
[[ $(uname -m) == x86_64 ]] || fail 'Este script está preparado para el equipo x86_64 revisado.'

latex_user=$(id -un)
latex_parent="/srv/$latex_user"
latex_root="$latex_parent/.local/texlive"
latex_work="$latex_parent/.cache/instalacion-texlive"
latex_bin="$latex_root/bin/x86_64-linux"
# Un espejo directo evita depender de la redirección geográfica de CTAN.
latex_repo='https://mirrors.rit.edu/CTAN/systems/texlive/tlnet'
latex_mirrors=(
  "$latex_repo"
  'https://mirrors.ibiblio.org/CTAN/systems/texlive/tlnet'
  'https://mirror.ctan.org/systems/texlive/tlnet'
)
latex_ca='/etc/ssl/certs/ca-certificates.crt'
[[ -r "$latex_ca" ]] || fail 'Falta el almacén de certificados. Ejecuta: sudo apt install --reinstall ca-certificates'

[[ -d "$latex_parent" && -O "$latex_parent" ]] || fail "No existe un directorio propio en $latex_parent. No se cambiarán permisos ni particiones."
latex_mount=$(findmnt -n -o TARGET -T "$latex_parent")
[[ "$latex_mount" == /srv ]] || fail "Se esperaba la partición /srv, pero el destino está en $latex_mount."
latex_fs=$(findmnt -n -o FSTYPE -T "$latex_parent")
case "$latex_fs" in ext4|ext3|xfs|btrfs) ;; *) fail "Sistema de archivos inesperado: $latex_fs" ;; esac
latex_options=$(findmnt -n -o OPTIONS -T "$latex_parent")
[[ ",$latex_options," != *,noexec,* ]] || fail '/srv está montado con noexec; no se podrán ejecutar los programas.'
latex_free=$(df -B1 --output=avail "$latex_parent" | tail -n 1 | tr -d ' ')
(( latex_free >= 4 * 1024 * 1024 * 1024 )) || fail 'Se requieren al menos 4 GiB libres como margen para esta instalación.'
printf 'Destino: %s\nPartición: %s (%s)\nEspacio libre: %s GiB\nTemporales: %s\n' \
  "$latex_root" "$latex_mount" "$latex_fs" "$((latex_free / 1024 / 1024 / 1024))" "$latex_work"
if [[ "$mode" == check ]]; then
  printf '%s\n' 'Comprobación terminada. No se ha instalado ni modificado nada.'
  exit 0
fi
[[ -w "$latex_parent" ]] || fail "$latex_parent no permite escritura. Ejecuta desde tu terminal normal y comprueba los permisos."

mkdir -p "$latex_work"
# Descargas, cachés y temporales permanecen en la partición /srv.
export TMPDIR="$latex_work"
# Los descargadores de TeX Live utilizan el mismo almacén del sistema.
export CURL_CA_BUNDLE="$latex_ca"
export SSL_CERT_FILE="$latex_ca"
latex_session=$(mktemp -d "$latex_work/sesion.XXXXXX")
printf 'Registro y archivos de esta ejecución: %s\n' "$latex_session"

if [[ ! -x "$latex_bin/tlmgr" ]]; then
  if [[ -d "$latex_root" ]] && [[ -n $(find "$latex_root" -mindepth 1 -maxdepth 1 -print -quit) ]]; then
    fail "Hay una instalación incompleta o distinta en $latex_root. Se conserva sin sobrescribirla; revisa esa carpeta antes de reintentar."
  fi
  latex_downloaded=0
  for latex_candidate in "${latex_mirrors[@]}"; do
    printf 'Descargando desde %s\n' "$latex_candidate"
    if curl --fail --location --retry 2 --connect-timeout 20 --max-time 180 \
      --cacert "$latex_ca" --proto '=https' --proto-redir '=https' \
      "$latex_candidate/install-tl-unx.tar.gz" -o "$latex_session/install-tl.tar.gz"; then
      latex_repo="$latex_candidate"
      latex_downloaded=1
      break
    fi
    printf '%s\n' 'Ese servidor falló; se intentará otro manteniendo la verificación HTTPS.' >&2
  done
  if [[ "$latex_downloaded" != 1 ]]; then
    fail 'No se pudo descargar desde los espejos. Comprueba la fecha del equipo y ejecuta: sudo apt install --reinstall ca-certificates && sudo update-ca-certificates. Después reintenta. Si tu red usa una CA propia, debe estar instalada en el almacén del sistema.'
  fi
  tar -xzf "$latex_session/install-tl.tar.gz" -C "$latex_session"
  latex_installer=$(find "$latex_session" -mindepth 2 -maxdepth 2 -type f -name install-tl -print -quit)
  [[ -n "$latex_installer" ]] || fail 'No se encontró install-tl en el archivo descargado.'
  cat > "$latex_session/texlive.profile" <<PROFILE
selected_scheme scheme-small
TEXDIR $latex_root
TEXMFLOCAL $latex_root/texmf-local
TEXMFSYSCONFIG $latex_root/texmf-config
TEXMFSYSVAR $latex_root/texmf-var
TEXMFHOME $latex_root/usuario/texmf
TEXMFCONFIG $latex_root/usuario/texmf-config
TEXMFVAR $latex_root/usuario/texmf-var
binary_x86_64-linux 1
instopt_adjustpath 0
instopt_adjustrepo 0
tlpdbopt_install_docfiles 0
tlpdbopt_install_srcfiles 0
PROFILE
  (
    cd "$latex_session"
    perl "$latex_installer" -no-interaction -profile "$latex_session/texlive.profile" -repository "$latex_repo"
  )
else
  printf '%s\n' 'Se reutilizará la instalación existente en el destino.'
fi

export PATH="$latex_bin:$PATH"
export TEXMFHOME="$latex_root/usuario/texmf"
export TEXMFCONFIG="$latex_root/usuario/texmf-config"
export TEXMFVAR="$latex_root/usuario/texmf-var"
"$latex_bin/tlmgr" --repository "$latex_repo" install collection-latexrecommended collection-latexextra \
  collection-pictures collection-science collection-langspanish \
  collection-fontsrecommended latexmk

# Validar dependencias concretas del documento antes de cambiar el inicio de shell.
for latex_package in spanish.ldf eso-pic.sty amsmath.sty amssymb.sty \
  booktabs.sty tabularx.sty adjustbox.sty enumitem.sty float.sty \
  tikz.sty algorithm.sty algpseudocode.sty hyperref.sty; do
  "$latex_bin/kpsewhich" "$latex_package" >/dev/null || fail "Falta el paquete $latex_package."
done
"$latex_bin/pdflatex" --version
"$latex_bin/latexmk" -v

# Compilación de prueba de los mismos paquetes, sin modificar el proyecto.
cat > "$latex_session/prueba.tex" <<'LATEX'
\documentclass{report}
\usepackage[T1]{fontenc}
\usepackage[spanish,es-noshorthands,es-tabla,es-nodecimaldot]{babel}
\usepackage{graphicx,eso-pic,amsmath,amssymb,array,booktabs,tabularx,adjustbox}
\usepackage{enumitem,float,tikz,algorithm,algpseudocode,hyperref}
\usetikzlibrary{arrows.meta,positioning}
\begin{document}
Instalación local: español, investigación y ecuaciones. $n\geq3$.
\end{document}
LATEX
"$latex_bin/latexmk" -pdf -interaction=nonstopmode -halt-on-error \
  -outdir="$latex_session" "$latex_session/prueba.tex"

# Archivo de entorno válido tanto para Bash como para Zsh.
{
  printf 'export PATH=%q:"$PATH"\n' "$latex_bin"
  printf 'export TEXMFHOME=%q\n' "$TEXMFHOME"
  printf 'export TEXMFCONFIG=%q\n' "$TEXMFCONFIG"
  printf 'export TEXMFVAR=%q\n' "$TEXMFVAR"
} > "$latex_root/entorno.sh"
printf -v latex_source_line '. %q' "$latex_root/entorno.sh"
for latex_rc in "$HOME/.profile" "$HOME/.bashrc" "${ZDOTDIR:-$HOME}/.zshrc"; do
  if ! grep -Fqx "$latex_source_line" "$latex_rc" 2>/dev/null; then
    if [[ -e "$latex_rc" ]]; then
      cp -p "$latex_rc" "$latex_session/$(basename "$latex_rc").anterior"
    fi
    printf '\n# TeX Live local en /srv\n%s\n' "$latex_source_line" >> "$latex_rc"
  fi
done

if command -v code >/dev/null; then
  if ! code --install-extension James-Yu.latex-workshop; then
    printf '%s\n' 'TeX Live funciona, pero falló la extensión. Reintenta: code --install-extension James-Yu.latex-workshop' >&2
  fi
else
  printf '%s\n' 'VS Code no está disponible. Puedes compilar desde la terminal.'
fi
printf '\nTeX Live instalado y probado. Activa esta terminal con:\n%s\n' "$latex_source_line"
printf '%s\n' 'Después cierra todas las ventanas de VS Code y ábrelo desde esa terminal con code .' \
  'Para compilar: cd "Plantilla d trabajo" y ejecutar latexmk -pdf main.tex'
