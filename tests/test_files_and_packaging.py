import ast
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import qt_support
from qt_support import ROOT, WindowTestCase, requires_pdflatex, open_dialog_returns

from zTikz.utils.functions import read_text_file

ACCENTED = "\\node at (0,0) {café ü 日本};\n"


class TempDirMixin:
    def make_temp_dir(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return tmp.name

    def write_bytes(self, name, data):
        path = os.path.join(self.tmp, name)
        with open(path, "wb") as f:
            f.write(data)
        return path


class ReadTextFileTests(TempDirMixin, unittest.TestCase):
    def setUp(self):
        self.tmp = self.make_temp_dir()

    def test_utf8(self):
        path = self.write_bytes("u.tex", ACCENTED.encode("utf-8"))
        self.assertEqual(read_text_file(path), ACCENTED)

    def test_utf8_bom_is_stripped(self):
        path = self.write_bytes("bom.tex", ACCENTED.encode("utf-8-sig"))
        self.assertEqual(read_text_file(path), ACCENTED)

    def test_legacy_cp1252_file_opens_without_crashing(self):
        path = self.write_bytes("legacy.tex", "\\node {café};\n".encode("cp1252"))
        self.assertEqual(read_text_file(path), "\\node {café};\n")


class FileRoundTripTests(TempDirMixin, WindowTestCase):
    def setUp(self):
        super().setUp()
        self.tmp = self.make_temp_dir()
        self.window.current_file_path = None
        self.window.editor.document().setModified(False)

    def test_save_writes_utf8(self):
        w = self.window
        w.editor.setPlainText(ACCENTED)
        w.current_file_path = os.path.join(self.tmp, "roundtrip.tex")
        w.save_file()
        with open(w.current_file_path, "rb") as f:
            self.assertEqual(f.read().decode("utf-8").replace("\r\n", "\n"), ACCENTED)

    def test_open_file_loads_accented_text(self):
        path = self.write_bytes("in.tex", ACCENTED.encode("utf-8"))
        with open_dialog_returns(path):
            self.window.open_file()
        self.assertEqual(self.window.editor.toPlainText(), ACCENTED)
        self.assertEqual(self.window.current_file_path, path)

    @requires_pdflatex
    def test_accented_code_compiles_and_temp_tex_is_utf8(self):
        out = self.compile_code("\\node at (0,0) {café ü};\n")     # pdflatex can't typeset CJK
        self.assertIn("Compilation successful", out)
        with open(os.path.join(self.window.temp_dir, "temp.tex"), encoding="utf-8") as f:
            self.assertIn("café", f.read())

    def test_preamble_is_saved_and_reloaded_as_utf8(self):
        original = qt_support.preserve_preamble(self)
        w = self.window
        w.preamble_editor.setPlainText(original + "\n% café 日本\n")
        w.save_preamble()
        with open(qt_support.user_preamble_path(), "rb") as f:
            self.assertIn("café".encode("utf-8"), f.read())
        self.assertIn("café 日本", w._get_cached_preamble())


class PackagingTests(unittest.TestCase):
    def read(self, *parts):
        with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
            return f.read()

    def project_text_files(self):
        for pattern in ("*.py", "*.md", "*.toml", "*.txt"):
            for path in glob.glob(os.path.join(ROOT, "**", pattern), recursive=True):
                relative = os.path.relpath(path, ROOT).split(os.sep)
                if relative[0] in ("build", "dist", "tests") or relative[0].endswith(".egg-info"):
                    continue
                yield path

    def test_requirements_txt_is_valid_pip_format(self):
        self.assertEqual(self.read("requirements.txt").split(),
                         ["PyQt6", "PyMuPDF", "antlr4-python3-runtime==4.13.2"])

    def test_no_pdf2image_or_poppler_dependency_left(self):
        offenders = []
        for path in self.project_text_files():
            with open(path, encoding="utf-8", errors="ignore") as f:
                text = f.read().lower()
            text = text.replace("no separate poppler installation is needed", "")   # README note
            if "pdf2image" in text or "poppler" in text:
                offenders.append(os.path.relpath(path, ROOT))
        self.assertEqual(offenders, [])

    def test_default_preamble_is_covered_by_the_packaging_globs(self):
        self.assertTrue(os.path.exists(os.path.join(ROOT, "zTikz", "resources", "preamble.default.tex")))
        self.assertIn('"*.tex"', self.read("pyproject.toml"))                      # wheel / pip install
        self.assertIn("('zTikz/resources/*.tex', 'zTikz/resources')", self.read("zTikz.spec"))  # PyInstaller

    def test_declared_python_version_matches_the_code(self):
        self.assertIn('requires-python = ">=3.10"', self.read("pyproject.toml"))
        for path in glob.glob(os.path.join(ROOT, "zTikz", "**", "*.py"), recursive=True):
            with open(path, encoding="utf-8") as f:
                source = f.read()
            ast.parse(source, filename=path, feature_version=(3, 10))     # raises on newer syntax
            for newer in ("tomllib", "typing import Self", "ExceptionGroup", "StrEnum"):
                self.assertNotIn(newer, source, path)


class RecompileSnippetsTests(WindowTestCase):
    def test_runs_with_the_current_interpreter(self):
        with mock.patch("subprocess.Popen") as popen:
            self.window.recompile_snippets()
        self.assertEqual(popen.call_args[0][0][0], sys.executable)

    def test_refuses_in_a_frozen_build(self):
        with mock.patch("subprocess.Popen") as popen, mock.patch.object(sys, "frozen", True, create=True):
            self.window.recompile_snippets()
        popen.assert_not_called()
        self.assertIn("from source", self.window.output.toPlainText())


@requires_pdflatex
class ThumbnailGeneratorTests(TempDirMixin, unittest.TestCase):
    def test_generates_transparent_pngs_with_pymupdf(self):
        import fitz
        base = self.make_temp_dir()
        os.makedirs(os.path.join(base, "utils"))
        os.makedirs(os.path.join(base, "resources"))
        shutil.copy(os.path.join(ROOT, "zTikz", "utils", "generate_snippet_thumbnails.py"),
                    os.path.join(base, "utils"))
        snippets = {"Demo": [
            {"name": "Diagonal line", "code": "\\draw[thick] (0,0) -- (1,1);"},
            {"name": "Filled circle", "code": "\\fill[red] (0,0) circle (0.5);"},
        ]}
        with open(os.path.join(base, "resources", "snippets.json"), "w", encoding="utf-8") as f:
            json.dump(snippets, f)

        result = subprocess.run([sys.executable, os.path.join(base, "utils", "generate_snippet_thumbnails.py")],
                                capture_output=True, text=True, timeout=180)

        self.assertEqual(result.returncode, 0, result.stderr)
        for name in ("diagonal_line.png", "filled_circle.png"):
            pix = fitz.Pixmap(os.path.join(base, "resources", "snippets_icons", name))
            self.assertTrue(pix.alpha, name)
            self.assertTrue(any(pix.samples[3::4]), f"{name} is fully transparent")


if __name__ == "__main__":
    unittest.main()
