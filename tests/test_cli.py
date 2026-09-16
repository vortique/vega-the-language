import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

# Allow this file to be run directly with ``python tests/test_cli.py``.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from click.testing import CliRunner

from cli.vegapy import cli


@contextmanager
def isolated_working_directory():
    previous_directory = Path.cwd()
    with tempfile.TemporaryDirectory() as directory:
        os.chdir(directory)
        try:
            yield
        finally:
            os.chdir(previous_directory)


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_read_only_prints_transpiled_python(self) -> None:
        with isolated_working_directory():
            source = Path("program.veg")
            source.write_text("sayisal x = 10\nyazdir x\n", encoding="utf-8")

            result = self.runner.invoke(cli, ["read", str(source)])

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertEqual(result.output, "_vega_x = 10\nprint(_vega_x)\n")
            self.assertFalse(Path(".vega").exists())

    def test_out_writes_python_and_does_not_run_it(self) -> None:
        with isolated_working_directory():
            source = Path("program.veg")
            source.write_text('yazdir "not executed"\n', encoding="utf-8")

            result = self.runner.invoke(cli, ["out", str(source)])

            output_path = Path(".vega/program.py")
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertEqual(result.output, f"{output_path}\n")
            self.assertEqual(
                output_path.read_text(encoding="utf-8"),
                "print('not executed')\n",
            )

    def test_run_writes_and_executes_python(self) -> None:
        with isolated_working_directory():
            source = Path("program.veg")
            source.write_text('yazdir "executed"\n', encoding="utf-8")

            with mock.patch("cli.vegapy.subprocess.run") as run:
                run.return_value = subprocess.CompletedProcess([], 0)
                result = self.runner.invoke(cli, ["run", str(source)])

            output_path = Path(".vega/program.py")
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertEqual(
                output_path.read_text(encoding="utf-8"),
                "print('executed')\n",
            )
            run.assert_called_once_with(
                [sys.executable, str(output_path)], check=False
            )

    def test_run_preserves_generated_program_exit_status(self) -> None:
        with isolated_working_directory():
            source = Path("program.veg")
            source.write_text('yazdir "executed"\n', encoding="utf-8")

            with mock.patch("cli.vegapy.subprocess.run") as run:
                run.return_value = subprocess.CompletedProcess([], 7)
                result = self.runner.invoke(cli, ["run", str(source)])

            self.assertEqual(result.exit_code, 7)

    def test_rejects_non_vega_files_without_creating_output(self) -> None:
        with isolated_working_directory():
            source = Path("program.txt")
            source.write_text("sayisal x = 10\n", encoding="utf-8")

            result = self.runner.invoke(cli, ["out", str(source)])

            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("must use the .veg extension", result.output)
            self.assertFalse(Path(".vega").exists())

    def test_reports_compile_errors_without_creating_output(self) -> None:
        with isolated_working_directory():
            source = Path("invalid.veg")
            source.write_text("yazdir =\n", encoding="utf-8")

            result = self.runner.invoke(cli, ["run", str(source)])

            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Expected an expression", result.output)
            self.assertFalse(Path(".vega").exists())


if __name__ == "__main__":
    unittest.main()
