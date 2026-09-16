"""Command-line interface for Vega the Language."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.lexer import LexerError, tokenize
from src.parser import ParserError, parse
from src.transpiler import transpile


VEGA_FILE = click.Path(
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    path_type=Path,
)


def _transpile_file(source_path: Path) -> str:
    if source_path.suffix.lower() != ".veg":
        raise click.BadParameter(
            "Vega source files must use the .veg extension",
            param_hint="SOURCE",
        )

    try:
        source = source_path.read_text(encoding="utf-8")
        return transpile(parse(tokenize(source)))
    except (OSError, UnicodeError) as error:
        raise click.ClickException(
            f"Could not read {source_path}: {error}"
        ) from error
    except (LexerError, ParserError) as error:
        raise click.ClickException(str(error)) from error


def _write_python(source_path: Path, python_code: str) -> Path:
    output_directory = Path(".vega")
    output_path = output_directory / f"{source_path.stem}.py"

    try:
        output_directory.mkdir(exist_ok=True)
        output_path.write_text(python_code, encoding="utf-8")
    except OSError as error:
        raise click.ClickException(
            f"Could not write {output_path}: {error}"
        ) from error

    return output_path


@click.group()
def cli() -> None:
    """Compile and run Vega source files."""


@cli.command("read")
@click.argument("source", type=VEGA_FILE)
def read_command(source: Path) -> None:
    """Print the transpiled Python for SOURCE without writing a file."""

    click.echo(_transpile_file(source), nl=False)


@cli.command("out")
@click.argument("source", type=VEGA_FILE)
def out_command(source: Path) -> None:
    """Write transpiled Python for SOURCE into the .vega directory."""

    output_path = _write_python(source, _transpile_file(source))
    click.echo(output_path)


@cli.command("run")
@click.argument("source", type=VEGA_FILE)
def run_command(source: Path) -> None:
    """Write and execute transpiled Python."""

    output_path = _write_python(source, _transpile_file(source))
    try:
        result = subprocess.run([sys.executable, str(output_path)], check=False)
    except OSError as error:
        raise click.ClickException(
            f"Could not run {output_path}: {error}"
        ) from error

    if result.returncode:
        raise click.exceptions.Exit(result.returncode)


if __name__ == "__main__":
    cli()
