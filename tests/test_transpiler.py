import sys
import unittest
from pathlib import Path

# Allow this file to be run directly with ``python tests/test_transpiler.py``.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.lexer import tokenize
from src.parser import parse
from src.transpiler import transpile


def transpile_source(source: str) -> str:
    return transpile(parse(tokenize(source)))


class TranspilerTests(unittest.TestCase):
    def test_transpiles_current_grammar(self) -> None:
        python = transpile_source(
            """sayisal x = 10
dize mesaj = "Merhaba"
x = veri "İsminiz?"
yazdir x
uzunluk "Merhaba dünya!"
liste myList = liste.yeni 1,x,3.14
myList.ekle "abc",3.14
"""
        )

        self.assertEqual(
            python,
            """_vega_x = 10
_vega_mesaj = 'Merhaba'
_vega_x = input('İsminiz?')
print(_vega_x)
len('Merhaba dünya!')
_vega_myList = [1, _vega_x, 3.14]
_vega_myList.extend(['abc', 3.14])
""",
        )

    def test_mangles_python_keywords_and_builtin_names(self) -> None:
        python = transpile_source(
            "sayisal class = 3\nsayisal print = class\nyazdir print"
        )

        self.assertEqual(
            python,
            "_vega_class = 3\n_vega_print = _vega_class\nprint(_vega_print)\n",
        )

    def test_empty_program_produces_empty_python(self) -> None:
        self.assertEqual(transpile_source("# only a comment\n"), "")

    def test_transpiles_new_language_features(self) -> None:
        python = transpile_source(
            """bool etkin = dogru
sayisal on = mutlak -10
eger on > 5
    yazdir "büyük"
ikincil on < 0
    yazdir "negatif"
degilse:
    yazdir "diğer"
belirle selam/dize mesaj/
    yazdir mesaj
selam/"Merhaba"/
dene:
    yazdir eksik
yakala:
    yazdir "Hata!"
"""
        )

        self.assertEqual(
            python,
            """_vega_etkin = True
_vega_on = abs(-10)
if (_vega_on > 5):
    print('büyük')
elif (_vega_on < 0):
    print('negatif')
else:
    print('diğer')
def _vega_selam(_vega_mesaj):
    print(_vega_mesaj)
_vega_selam('Merhaba')
try:
    print(_vega_eksik)
except Exception:
    print('Hata!')
""",
        )

    def test_new_language_features_execute_end_to_end(self) -> None:
        python = transpile_source(
            """bool etkin = dogru
sayisal on = mutlak -10
eger etkin
    yazdir on
degilse:
    yazdir 0
belirle selam/dize mesaj/
    yazdir mesaj
selam "Merhaba"
dene:
    yazdir eksik
yakala:
    yazdir "Hata!"
"""
        )
        output: list[object] = []

        exec(python, {"print": lambda value: output.append(value)})

        self.assertEqual(output, [10, "Merhaba", "Hata!"])

    def test_numeric_declaration_converts_user_input(self) -> None:
        python = transpile_source('sayisal sayi = veri "Sayı gir: "')
        prompts: list[str] = []
        namespace = {
            "input": lambda prompt: prompts.append(prompt) or "12",
        }

        exec(python, namespace)

        self.assertEqual(prompts, ["Sayı gir: "])
        self.assertEqual(namespace["_vega_sayi"], 12)

    def test_generated_python_executes_end_to_end(self) -> None:
        python = transpile_source(
            """sayisal size = uzunluk veri "Adınız?"
liste values = liste.yeni size
values.ekle 2,3
yazdir size
yazdir values
"""
        )
        prompts: list[str] = []
        output: list[object] = []
        namespace = {
            "input": lambda prompt: prompts.append(prompt) or "Vega",
            "print": lambda value: output.append(value),
        }

        exec(python, namespace)

        self.assertEqual(prompts, ["Adınız?"])
        self.assertEqual(output, [4, [4, 2, 3]])


if __name__ == "__main__":
    unittest.main()
