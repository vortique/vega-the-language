# Vega the Language

## Command-line interface

Install the project in a virtual environment:

```sh
python -m pip install -e .
```

Use the `vega` command with a `.veg` source file:

```sh
vega read examples/variables_and_printing.veg
vega out examples/variables_and_printing.veg
vega run examples/variables_and_printing.veg
```

- `read` prints the transpiled Python without creating a file.
- `out` writes the Python file to `.vega/<source-name>.py`.
- `run` writes the same file and executes it with the active Python interpreter.

