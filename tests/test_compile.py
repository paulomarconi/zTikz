import glob
import os
import unittest
from unittest import mock

import qt_support
from qt_support import WindowTestCase, requires_pdflatex

from zTikz.utils.functions import _split_preamble, read_text_file


class SplitPreambleTests(unittest.TestCase):
    def setUp(self):
        qt_support.get_app()
        self.shipped = read_text_file(qt_support.DEFAULT_PREAMBLE_PATH)

    def test_static_part_holds_packages_and_no_placeholders(self):
        static, dynamic = _split_preamble(self.shipped)
        for wanted in ("amsmath", "pgfgantt", "calc"):
            self.assertIn(wanted, static)
        self.assertNotIn("%%", static)
        self.assertNotIn("pixelwidth", static)

    def test_dynamic_part_starts_at_page_size_setup(self):
        _, dynamic = _split_preamble(self.shipped)
        self.assertIn("pixelwidth", dynamic.split(r"\begin{document}")[0])
        self.assertTrue(dynamic.rstrip().endswith(r"\end{document}"))

    def test_without_begin_document_it_cannot_be_split(self):
        self.assertIsNone(_split_preamble(r"\documentclass{article}"))

    def test_without_documentclass_it_cannot_be_split(self):
        self.assertIsNone(_split_preamble("\\usepackage{tikz}\n\\begin{document}\n\\end{document}"))

    def test_fully_static_preamble_splits_at_begin_document(self):
        static, _ = _split_preamble(
            "\\documentclass{article}\n\\usepackage{tikz}\n"
            "\\begin{document}\n%%TIKZ_CODE%%\n\\end{document}")
        self.assertTrue(static.endswith("\\usepackage{tikz}\n"))


@requires_pdflatex
class CompileErrorTests(WindowTestCase):
    """A failed pdflatex run must never look like a success or reuse a stale PDF."""

    def test_valid_code_compiles(self):
        out = self.compile_code(r"\draw (0,0) -- (1,1);")
        self.assertIn("Compilation successful", out)
        self.assertTrue(os.path.exists(os.path.join(self.window.temp_dir, "temp.pdf")))

    def test_total_failure_is_reported_with_latex_errors(self):
        self.compile_code(r"\draw (0,0) -- (1,1);")
        good_hash = self.window._last_compiled_hash
        temp_pdf = os.path.join(self.window.temp_dir, "temp.pdf")
        with open(temp_pdf, "rb") as f:
            good_pdf = f.read()

        out = self.compile_code(r"\draw (0,0) -- (1,1); \input{does_not_exist_zz}")

        self.assertNotIn("Compilation successful", out)
        self.assertIn("Compilation failed", out)
        self.assertIn("does_not_exist_zz", out)          # the LaTeX error text is surfaced
        self.assertEqual(self.window._last_compiled_hash, good_hash)
        # temp.pdf is the last GOOD result (it matches the preview and stays usable for Export and
        # Show PDF); the failed run's own files are not mistaken for it and are cleaned up.
        with open(temp_pdf, "rb") as f:
            self.assertEqual(f.read(), good_pdf)
        self.assertEqual(glob.glob(os.path.join(self.window.temp_dir, "build*")), [])
        self.assertTrue(os.path.exists(os.path.join(self.window.temp_dir, "temp.log")))   # the log to read

    def test_partial_output_is_shown_but_not_cached(self):
        self.compile_code(r"\draw (0,0) -- (1,1);")
        good_hash = self.window._last_compiled_hash

        out = self.compile_code(r"\draw (0,0) -- (1,1); \undefinedmacro \draw (1,0) -- (2,2);")

        self.assertNotIn("Compilation successful", out)
        self.assertIn("Compiled with errors", out)
        self.assertIn("Undefined control sequence", out)
        self.assertEqual(self.window._last_compiled_hash, good_hash)

    def test_recompiles_after_fixing_the_error(self):
        broken = r"\draw (0,0) -- (1,1); \undefinedmacro"
        self.compile_code(broken)
        self.assertIn("Compiled with errors", self.compile_code(broken))   # retried, not skipped
        self.assertIn("Compilation successful", self.compile_code(r"\draw (0,0) -- (1,1);"))


@requires_pdflatex
class PreambleFormatTests(WindowTestCase):
    """Edits saved from the Preamble tab must reach the fast (precompiled format) path."""

    def setUp(self):
        super().setUp()
        self.original = qt_support.preserve_preamble(self)
        self.set_preamble(self.original)

    def set_preamble(self, text):
        self.window.preamble_editor.setPlainText(text)
        self.window.save_preamble()

    def assertFastPathSuccess(self, out):
        self.assertIn("Compilation successful", out)
        self.assertIn("fmt: yes", out)

    def test_packages_from_preamble_file_are_available(self):
        # amsmath (\dfrac) and calc are in preamble.tex but were not in the old hardcoded list.
        out = self.compile_code(r"\draw ($(0,0)!.5!(1,1)$) circle (1); \node at (2,2) {$\dfrac{1}{2}$};")
        self.assertFastPathSuccess(out)

    def test_editing_the_static_part_rebuilds_the_format(self):
        before = self.window._fmt_static_hash
        self.set_preamble(self.original.replace(
            r"\usepackage{pgfgantt}",
            "\\usepackage{pgfgantt}\n\\newcommand{\\zzmark}{HELLO}\n\\usepackage{xcolor}"))

        out = self.compile_code(r"\node {\zzmark}; \draw[color=red!50!blue] (0,0)--(1,0);")

        self.assertFastPathSuccess(out)
        self.assertNotEqual(self.window._fmt_static_hash, before)

    def test_editing_only_the_dynamic_part_reuses_the_format(self):
        self.compile_code(r"\draw (0,0)--(1,1);")            # make sure a format exists
        before = self.window._fmt_static_hash
        self.set_preamble(self.original.replace(
            r"\begin{document}", "\\tikzset{zzstyle/.style={blue,thick}}\n\\begin{document}"))

        out = self.compile_code(r"\draw[zzstyle] (0,0)--(1,1);")

        self.assertFastPathSuccess(out)
        self.assertEqual(self.window._fmt_static_hash, before)

    def test_broken_static_part_falls_back_and_reports_once(self):
        self.set_preamble(self.original.replace(
            r"\usepackage{pgfgantt}", "\\usepackage{pgfgantt}\n\\usepackage{nonexistentpkgzz}"))

        first = self.compile_code(r"\draw (0,0)--(1,1);")
        second = self.compile_code(r"\draw (0,0)--(2,2);")

        self.assertIn("Could not precompile", first)
        self.assertIn("nonexistentpkgzz", first)
        self.assertNotIn("Could not precompile", second)            # not retried / re-reported
        self.assertNotIn("fmt: yes", second)
        # An older format must not survive a failed rebuild.
        self.assertFalse(os.path.exists(os.path.join(self.window.temp_dir, "tikz_preamble.fmt")))

    def test_restoring_a_good_preamble_recovers_the_fast_path(self):
        self.set_preamble(self.original.replace(
            r"\usepackage{pgfgantt}", "\\usepackage{pgfgantt}\n\\usepackage{nonexistentpkgzz}"))
        self.compile_code(r"\draw (0,0)--(1,1);")

        self.set_preamble(self.original)
        out = self.compile_code(r"\draw (0,0)--(3,3);")

        self.assertFastPathSuccess(out)


@requires_pdflatex
class ShellEscapeTests(WindowTestCase):
    """pdflatex must never run with shell escape: opening an untrusted .tex compiles it."""

    def test_format_build_and_format_compile_disable_shell_escape(self):
        self.window._fmt_static_hash = None                   # force the format to be rebuilt
        self.window._fmt_failed_hash = None
        with qt_support.recorded_tex_runs() as runs:
            self.compile_code(r"\draw (0,0)--(1,1);")
        self.assertGreaterEqual(len(runs), 2)                 # the format build + the compile
        for run in runs:
            self.assertIn("-no-shell-escape", run["arguments"])

    def test_fallback_compile_without_a_format_disables_shell_escape(self):
        with mock.patch("zTikz.utils.functions._split_preamble", return_value=None), \
                qt_support.recorded_tex_runs() as runs:
            self.compile_code(r"\draw (0,0)--(2,2);")
        self.assertEqual(len(runs), 1)
        self.assertIn("-no-shell-escape", runs[0]["arguments"])

    def test_compilation_still_succeeds(self):
        self.assertIn("Compilation successful", self.compile_code(r"\draw (0,0)--(3,3);"))

    def test_thumbnail_generator_disables_shell_escape(self):
        import qt_support as support
        path = os.path.join(support.ROOT, "zTikz", "utils", "generate_snippet_thumbnails.py")
        with open(path, encoding="utf-8") as f:
            self.assertIn('"-no-shell-escape"', f.read())


class RestorePreambleTests(WindowTestCase):
    DEFAULT_PATH = qt_support.DEFAULT_PREAMBLE_PATH

    def setUp(self):
        super().setUp()
        qt_support.preserve_preamble(self)
        self.default = read_text_file(self.DEFAULT_PATH)

    def edit_preamble(self, text):
        self.window.preamble_editor.setPlainText(text)
        self.window.save_preamble()

    def test_default_file_is_a_usable_template(self):
        self.assertIn("%%TIKZ_CODE%%", self.default)
        self.assertIn("%%PIXEL_WIDTH%%", self.default)
        self.assertIsNotNone(_split_preamble(self.default))
        for wanted in ("amsmath", "calc", "pgfgantt"):   # what the old hardcoded default was missing
            self.assertIn(wanted, self.default)

    def test_restore_brings_back_the_shipped_default_and_saves_it(self):
        self.edit_preamble("% my experiment\n" + self.default)
        self.window.restore_preamble()
        self.assertEqual(self.window.preamble_editor.toPlainText(), self.default)
        self.assertEqual(read_text_file(qt_support.user_preamble_path()), self.default)
        self.assertEqual(self.window._get_cached_preamble(), self.default)

    def test_restore_does_not_modify_the_default_file(self):
        self.edit_preamble("% junk")
        self.window.restore_preamble()
        self.edit_preamble("% more junk")
        self.assertEqual(read_text_file(self.DEFAULT_PATH), self.default)

    def test_missing_default_reports_and_keeps_the_current_preamble(self):
        self.edit_preamble("% keep me\n" + self.default)
        with mock.patch("zTikz.utils.functions.read_text_file", side_effect=FileNotFoundError("gone")):
            self.window.restore_preamble()
        self.assertTrue(self.window.preamble_editor.toPlainText().startswith("% keep me"))
        self.assertIn("Could not read the default preamble", self.window.output.toPlainText())

    @requires_pdflatex
    def test_code_using_calc_and_amsmath_compiles_after_restore(self):
        # The old hardcoded default lacked amsmath and calc, so this failed after clicking Restore.
        broken = self.default.replace("\\usetikzlibrary{calc,intersections}", "")
        self.assertNotEqual(broken, self.default)            # guard: the edit must really remove calc
        self.edit_preamble(broken)
        self.window.restore_preamble()
        out = self.compile_code(r"\draw ($(0,0)!.5!(1,1)$) circle (1); \node at (2,2) {$\dfrac{1}{2}$};")
        self.assertIn("Compilation successful", out)


if __name__ == "__main__":
    unittest.main()
