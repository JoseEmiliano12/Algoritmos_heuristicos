# Instalación local de LaTeX

En el equipo revisado, `/srv` es la partición montada con más espacio libre (aproximadamente 313 GiB). El disco NTFS de 1.8 TB no está montado y no se conoce su espacio disponible. El script no monta ni formatea particiones.

Desde la raíz del proyecto, como usuario normal:

```bash
bash scripts/instalar_latex_local.sh --comprobar
bash scripts/instalar_latex_local.sh
```

No usar `sudo`. La instalación necesita conexión a Internet. El script usa el instalador oficial de TeX Live y coloca programas, paquetes, datos de usuario y temporales en `/srv/<usuario>`. Está preparado para el equipo Debian x86_64 revisado y verifica el montaje y el espacio disponible antes de instalar.

Incluye las colecciones necesarias para la plantilla, español y latexmk. Omite documentación y fuentes de los paquetes para ahorrar espacio. Comprueba los archivos requeridos y compila un documento de prueba. Conserva los registros y temporales en `/srv/<usuario>/.cache/instalacion-texlive` para diagnosticar errores.

Añade el entorno a `.profile`, `.bashrc` y `.zshrc` (respeta ZDOTDIR) y guarda copias previas de esos archivos en el directorio de la ejecución. Instala LaTeX Workshop si encuentra VS Code. La extensión permanece en el directorio habitual de VS Code; los pequeños cambios de configuración también permanecen en el directorio personal. La distribución TeX Live se instala íntegramente en `/srv`.

Al terminar, ejecutar el comando de activación que muestra el script, cerrar VS Code por completo y abrirlo desde la terminal con `code .`. Para generar el PDF:

```bash
cd "Plantilla d trabajo"
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

No hace falta ejecutar los comandos `apt install texlive...` propuestos previamente: esta instalación usa el gestor propio `tlmgr`. Las dependencias del instalador ya se encontraron en el equipo; si falta alguna, el script lo informa. No se realiza ninguna instalación durante `--comprobar`.

Se comprobó la sintaxis Bash y se ejecutó el modo de comprobación. La descarga e instalación completas quedan para cuando ejecutes el script. Una instalación incompleta sin `tlmgr` funcional no se sobrescribe automáticamente. Si una instalación de un año anterior no admite el repositorio actual, `tlmgr` informará del error; no se intenta una migración de versión automática.

Fuente oficial del formato de perfil y selección del directorio TEXDIR: https://tug.org/texlive/doc/install-tl.html
