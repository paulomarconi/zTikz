# zTikz

zTikz is a graphical WYSIWYG editor for TikZ built with Python and PyQt6 inspired in [TikzEdt](http://www.tikzedt.org/). It provides a real-time, interactive overlay on top of the compiled PDF preview, allowing you to visually draw and edit TikZ shapes while seamlessly updating the underlying LaTeX code in real-time.

<p align="center">
  <img src="zTikz/resources/icons/app_icon.svg" alt="zTikz" />
</p>

## Features

- **Real-Time LaTeX Compilation:** Instantly see your TikZ code compiled as you type.
- **Graphical WYSIWYG Editing:** Click, drag, and draw directly over your compiled document.
- **Supported Shapes:** Visually draw rectangles, circles, ellipses, arcs, paths, smooth curves, and nodes.
- **ANTLR4-Powered Parsing:** Advanced real-time TikZ code parsing allows robust round-tripping between text edits and graphical edits.
- **Code Editor:** Features a syntax-highlighted code editor, zoom functionality, and comment toggling.
- **Snippets Library:** Insert pre-defined TikZ snippets quickly with a visual thumbnail gallery.
- **Exporting:** Easily export your finished TikZ drawings to PNG, PDF, or SVG formats.

## Prerequisites

To run zTikz, you need a few system dependencies installed:

1. Python 3.10+ on Windows, Linux or macOS
2. pdflatex: a working LaTeX distribution with the `tikz`, `pgfplots`, `circuitikz` and `preview` packages:
   - Windows: [MiKTeX](https://miktex.org/) or [TeX Live](https://tug.org/texlive/)
   - macOS: [MacTeX](https://tug.org/mactex/) (`/Library/TeX/texbin`)
   - Linux: TeX Live from your package manager (for example `texlive-latex-extra` and `texlive-pictures` on Debian/Ubuntu)

zTikz finds pdflatex on your `PATH` and in the usual TeX install folders. If yours is somewhere else, or the app was started from a launcher that doesn't see your `PATH`, set it under Settings.

PDF rendering is handled by PyMuPDF, which is installed automatically with the Python dependencies; no separate Poppler installation is needed.

## Where zTikz keeps its files

Nothing is written inside the installed package, so it also works from a read-only or system-wide install.

| What | Where |
|---|---|
| Your preamble (edited in the Preamble tab) | Windows: `%LOCALAPPDATA%\zTikz` · Linux: `~/.local/share/zTikz` · macOS: `~/Library/Application Support/zTikz` |
| Compilation output | a private temporary folder (`ztikz-…`) created for each running session and removed on exit |
| Settings | the platform's standard settings store (registry, `~/.config` or `~/Library/Preferences`) |

Set the `ZTIKZ_DATA_DIR` environment variable to keep the preamble in a different folder (for example for a portable install). "Restore Preamble" brings back the default shipped with the app.

## Installation

The project is structured as a standard Python package. You can install it locally using `pip`:

```bash
# Clone the repository
git clone https://github.com/paulomarconi/ztikz.git
cd ztikz

# Install the application and its dependencies
pip install .
```

For development, install it in editable mode:
```bash
pip install -e .
```

## Running the Application

Once installed, you can launch the editor from anywhere in your terminal using the generated command:

```bash
ztikz
```

Alternatively, you can run the module directly via Python:

```bash
python -m zTikz.main
```

## Running the tests

```bash
python -m unittest discover -s tests -v
```

The GUI tests run headless (Qt's `offscreen` platform) and use their own temporary data folder and settings, so they never touch your real preamble or settings. Tests that need pdflatex are skipped if it isn't installed.

## Key Libraries

- PyQt6: The modern GUI framework driving the interface.
- ANTLR4: Robust lexer and parser for the TikZ grammar.
- PyMuPDF: Fast conversion from PDF to rasterised PNG previews.

## Author

Paulo Loma Marconi.  
Website: [paulomarconi.github.io](https://paulomarconi.github.io)
