# translations.py — Simple dictionary-based UI localization for zTikz
#
# Usage:
#   from translations import tr, set_language
#
#   set_language("Español")       # Switch to Spanish
#   print(tr("File"))             # -> "Archivo"
#   print(tr("New"))              # -> "Nuevo"
#
#   set_language("English")       # Switch back to English
#   print(tr("File"))             # -> "File"
#
# If a key is missing from the active language, the English fallback (the key itself) is returned.

_current_language = "English"

TRANSLATIONS = {
    "English": {},  # English is the fallback — keys ARE the English strings
    "Español": {
        # ── Menu bar ──
        "File": "Archivo",
        "Edit": "Editar",
        "View": "Ver",
        "Compilation": "Compilación",
        "Settings": "Configuración",
        "Help": "Ayuda",

        # ── File menu ──
        "New": "Nuevo",
        "Open": "Abrir",
        "Save": "Guardar",
        "Save As...": "Guardar como...",
        "Export": "Exportar",
        "Exit": "Salir",

        # ── Edit menu ──
        "Undo": "Deshacer",
        "Redo": "Rehacer",
        "Cut": "Cortar",
        "Copy": "Copiar",
        "Paste": "Pegar",
        "Find and Replace": "Buscar y Reemplazar",
        "Find Next": "Buscar siguiente",
        "Comment/Uncomment": "Comentar/Descomentar",

        # ── View menu ──
        "Show PDF in external viewer": "Mostrar PDF en visor externo",
        "Word Wrap": "Ajuste de línea",

        # ── Compilation menu ──
        "Compile": "Compilar",
        "Abort": "Abortar",
        "Auto compilation on code change": "Compilación automática al cambiar código",
        "Re-compile the Snippets thumbnails": "Recompilar miniaturas de Snippets",

        # ── Settings dialog ──
        "General": "General",
        "Path to pdfLaTeX:": "Ruta a pdfLaTeX:",
        "Path to external PDF viewer:": "Ruta al visor de PDF externo:",
        "Browse...": "Examinar...",
        "Reset Default": "Restablecer predeterminado",
        "Check for updates on startup": "Buscar actualizaciones al iniciar",
        "Language:": "Idioma:",
        "OK": "Aceptar",
        "Cancel": "Cancelar",

        # ── Help menu ──
        "Check for Updates": "Buscar actualizaciones",
        "About": "Acerca de",

        # ── About dialog ──
        "About zTikz": "Acerca de zTikz",
        "Version:": "Versión:",
        "Author:": "Autor:",
        "Website:": "Sitio web:",
        "Key Libraries:": "Librerías principales:",
        "GUI framework": "Marco de interfaz gráfica",
        "TikZ code parsing": "Análisis de código TikZ",
        "LaTeX compilation": "Compilación LaTeX",
        "PDF to PNG rendering": "Renderizado de PDF a PNG",
        "PDF processing backend": "Motor de procesamiento PDF",
        "Runtime": "Entorno de ejecución",

        # ── Find dialog ──
        "Find:": "Buscar:",
        "Replace:": "Reemplazar:",
        "Next": "Siguiente",
        "Previous": "Anterior",
        "Replace": "Reemplazar",
        "Replace All": "Reemplazar todo",

        # ── Toolbar tooltips ──
        "New": "Nuevo",
        "Open": "Abrir",
        "Save": "Guardar",
        "Export": "Exportar",
        "Compile": "Compilar",
        "Cancel/Abort compilation in case something goes wrong": "Cancelar/Abortar compilación en caso de error",
        "Auto compilation on code change": "Compilación automática al cambiar código",
        "Show PDF in external viewer": "Mostrar PDF en visor externo",
        "Toggle the editable overlay layer on top of the compiled preview": "Activar/desactivar la capa editable sobre la vista previa compilada",
        "Show/hide canvas grid": "Mostrar/ocultar cuadrícula del lienzo",
        "Show/hide reference points": "Mostrar/ocultar puntos de referencia",
        "Edit": "Editar",
        "Path Tool (double-click to finish)": "Herramienta de trazado (doble clic para terminar)",
        "Smooth Curve (double-click to finish)": "Curva suave (doble clic para terminar)",
        "Draw Rectangle": "Dibujar rectángulo",
        "Draw Circle": "Dibujar círculo",
        "Draw Ellipse": "Dibujar elipse",
        "Draw Arc": "Dibujar arco",

        # ── File navigation ──
        "Back": "Atrás",
        "Forward": "Adelante",
        "Up": "Arriba",
        "Refresh": "Actualizar",

        # ── Status / Output messages ──
        "No compiled PDF found. Compile first.": "No se encontró PDF compilado. Compile primero.",
        "Re-compiling snippet thumbnails...": "Recompilando miniaturas de snippets...",
        "zTikz loaded. Ready to compile.": "zTikz cargado. Listo para compilar.",
        "Compiling...": "Compilando...",
        "Compilation successful.": "Compilación exitosa.",
        "Compilation failed.": "Error de compilación.",
        "Compilation timed out.": "Tiempo de compilación agotado.",
        "Compilation cancelled by user.": "Compilación cancelada por el usuario.",
        "Temporary files located at:": "Archivos temporales ubicados en:",
        "tex file:": "Archivo tex:",
        "pdf file:": "Archivo pdf:",

        # ── Left Panel ──
        "Files": "Archivos",
        "Snippets": "Snippets",
        "Preamble": "Preámbulo",
        "Filter:": "Filtro:",
        "Output": "Salida",
    },
}


def set_language(lang: str):
    """Set the active UI language."""
    global _current_language
    _current_language = lang


def get_language() -> str:
    """Return the current UI language."""
    return _current_language


def tr(key: str) -> str:
    """Translate *key* to the active language. Returns *key* unchanged if no translation exists."""
    if _current_language == "English":
        return key
    return TRANSLATIONS.get(_current_language, {}).get(key, key)
