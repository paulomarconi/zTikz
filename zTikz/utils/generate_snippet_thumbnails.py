import os
import json
import subprocess
import re
import shutil
import fitz  # PyMuPDF

def sanitize_filename(name):
    # Keep only alphanumeric characters and safe punctuation
    clean_name = re.sub(r'[^\w\-_\. ]', '_', name)
    return clean_name.replace(' ', '_').lower()

def generate_thumbnails():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    resources_dir = os.path.join(os.path.dirname(base_dir), 'resources')
    snippets_path = os.path.join(resources_dir, 'snippets.json')
    icons_dir = os.path.join(resources_dir, 'snippets_icons')
    temp_dir = os.path.join(resources_dir, 'temp_icons')
    
    os.makedirs(icons_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)
    
    with open(snippets_path, 'r', encoding='utf-8') as f:
        snippets_data = json.load(f)
        
    preamble = r"""\documentclass{article}
\usepackage[active,tightpage,pdftex]{preview}
\usepackage{tikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepackage{circuitikz}
\usetikzlibrary{arrows, arrows.meta, decorations.pathmorphing, shapes.geometric, shapes.multipart, positioning, automata, er, mindmap, backgrounds, shadows, fadings, trees, matrix, graphs, intersections, decorations.text}

\setlength{\PreviewBorder}{2pt}
\PreviewEnvironment{tikzpicture}
\begin{document}
\begin{tikzpicture}
"""
    postamble = r"""
\end{tikzpicture}
\end{document}
"""

    total_snippets = sum(len(items) for items in snippets_data.values())
    processed = 0

    for category, items in snippets_data.items():
        for item in items:
            processed += 1
            name = item['name']
            code = item['code']
            filename = sanitize_filename(name)
            png_path = os.path.join(icons_dir, f"{filename}.png")
            
            if os.path.exists(png_path):
                print(f"[{processed}/{total_snippets}] Skipping {name}, already exists.")
                continue
                
            print(f"[{processed}/{total_snippets}] Generating thumbnail for {name}...")
            
            # Special handling for mindmaps, pgfplots, etc. if they already include their own environments
            tex_code = code
            if "\\begin{axis}" in code:
                # We don't need a wrapper around axis if we don't want to, but pgfplots works inside tikzpicture
                pass
            
            tex_file = os.path.join(temp_dir, "temp.tex")
            pdf_file = os.path.join(temp_dir, "temp.pdf")
            
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(preamble + tex_code + postamble)
                
            try:
                subprocess.run(
                    ["pdflatex", "-no-shell-escape", "-interaction=nonstopmode", "-output-directory", temp_dir, tex_file],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15
                )
                
                if os.path.exists(pdf_file):
                    doc = fitz.open(pdf_file)
                    try:
                        if doc.page_count:
                            # Qt scales the icon via setIconSize; the preview package already crops it tight.
                            scale = 300 / 72  # 300 DPI
                            doc[0].get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=True).save(png_path)
                        else:
                            print(f"Failed to convert PDF to PNG for {name}")
                    finally:
                        doc.close()
                else:
                    print(f"PDF not generated for {name}")
            except Exception as e:
                print(f"Error compiling {name}: {e}")
                
    # Clean up temp dir
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("Done generating thumbnails.")

if __name__ == "__main__":
    generate_thumbnails()
