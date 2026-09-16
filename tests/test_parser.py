import sys
import unittest
from pathlib import Path

# Allow this file to be run directly with ``python tests/test_parser.py``.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ast_nodes import (
    Assignment,
    ExpressionStatement,
    Identifier,
    InputExpression,
    LengthExpression,
    ListDeclaration,
    ListExtendStatement,
    NumericDeclaration,
    PrintStatement,
    StringDeclaration,
)
from src.lexer import tokenize
from src.parser import ParserError, parse


class ParserTests(unittest.TestCase):
    def test_parses_current_grammar(self) -> None:
        program = parse(
            tokenize(
                """sayisal x = 10
dize mesaj = "Merhaba"
x = veri "İsminiz?"
yazdir x
uzunluk "Merhaba dünya!"
liste myList = liste.yeni 1,abc,3.14
myList.ekle "abc",3.14
"""
            )
        )

        self.assertEqual(len(program.statements), 7)
        self.assertIsInstance(program.statements[0], NumericDeclaration)
        self.assertIsInstance(program.statements[1], StringDeclaration)
        self.assertIsInstance(program.statements[2], Assignment)
        self.assertIsInstance(program.statements[3], PrintStatement)
        self.assertIsInstance(program.statements[4], ExpressionStatement)
        self.assertIsInstance(program.statements[5], ListDeclaration)
        self.assertIsInstance(program.statements[6], ListExtendStatement)

        declaration = program.statements[5]
        self.assertEqual(declaration.name, "myList")
        self.assertEqual(len(declaration.elements), 3)
        self.assertIsInstance(declaration.elements[1], Identifier)

    def test_prefix_expressions_are_composable(self) -> None:
        statement = parse(
            tokenize('sayisal n = uzunluk veri "Adınız?"')
        ).statements[0]

        self.assertIsInstance(statement, NumericDeclaration)
        self.assertIsInstance(statement.initializer, LengthExpression)
        self.assertIsInstance(statement.initializer.value, InputExpression)

    def test_string_declaration_accepts_input_expression(self) -> None:
        statement = parse(tokenize('dize ad = veri "Adınız?"')).statements[0]

        self.assertIsInstance(statement, StringDeclaration)
        self.assertIsInstance(statement.initializer, InputExpression)

    def test_comments_and_blank_lines_are_ignored(self) -> None:
        program = parse(tokenize("# açıklama\n\nyazdir \"ok\" # devam\n"))

        self.assertEqual(len(program.statements), 1)
        self.assertIsInstance(program.statements[0], PrintStatement)

    def test_rejects_empty_list(self) -> None:
        with self.assertRaisesRegex(ParserError, "Expected at least one list element"):
            parse(tokenize("liste xs = liste.yeni"))

    def test_rejects_empty_list_extension(self) -> None:
        with self.assertRaisesRegex(ParserError, "Expected at least one value"):
            parse(tokenize("xs.ekle"))

    def test_rejects_missing_comma(self) -> None:
        with self.assertRaisesRegex(ParserError, "Expected a newline after statement"):
            parse(tokenize("liste xs = liste.yeni 1 2"))

    def test_rejects_two_statements_on_one_line(self) -> None:
        with self.assertRaisesRegex(ParserError, "Expected a newline after statement"):
            parse(tokenize("sayisal x = 1 yazdir x"))

    def test_errors_include_source_location(self) -> None:
        with self.assertRaisesRegex(ParserError, r"line 2, column 8"):
            parse(tokenize("\nyazdir ="))


if __name__ == "__main__":
    unittest.main()
