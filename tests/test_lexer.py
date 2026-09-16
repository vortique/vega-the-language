import unittest
from pathlib import Path
import sys

# Allow this file to be run directly with python tests/test_lexer.py.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.lexer import LexerError, TokenType, tokenize


class LexerTests(unittest.TestCase):
    def test_variable_declaration(self) -> None:
        tokens = tokenize("sayisal x = 10")

        self.assertEqual(
            [token.type for token in tokens],
            [
                TokenType.SAYISAL,
                TokenType.IDENTIFIER,
                TokenType.EQUAL,
                TokenType.NUMBER,
                TokenType.EOF,
            ],
        )
        self.assertEqual(tokens[1].lexeme, "x")
        self.assertEqual(tokens[3].literal, 10)

    def test_string_declaration(self) -> None:
        tokens = tokenize('dize mesaj = "Merhaba, dünya!"')

        self.assertEqual(
            [token.type for token in tokens],
            [
                TokenType.DIZE,
                TokenType.IDENTIFIER,
                TokenType.EQUAL,
                TokenType.STRING,
                TokenType.EOF,
            ],
        )
        self.assertEqual(tokens[3].literal, "Merhaba, dünya!")

    def test_print_with_straight_quotes(self) -> None:
        tokens = tokenize('yazdir "Merhaba, dünya!"')

        self.assertEqual(tokens[0].type, TokenType.YAZDIR)
        self.assertEqual(tokens[1].type, TokenType.STRING)
        self.assertEqual(tokens[1].literal, "Merhaba, dünya!")

    def test_print_with_typographic_quotes(self) -> None:
        tokens = tokenize("yazdir “Hello, world!”")

        self.assertEqual(tokens[1].type, TokenType.STRING)
        self.assertEqual(tokens[1].literal, "Hello, world!")

    def test_comments_are_ignored_but_newlines_are_preserved(self) -> None:
        tokens = tokenize("# comment\nsayisal değer = 3.5 # trailing comment\n")

        self.assertEqual(
            [token.type for token in tokens],
            [
                TokenType.NEWLINE,
                TokenType.SAYISAL,
                TokenType.IDENTIFIER,
                TokenType.EQUAL,
                TokenType.NUMBER,
                TokenType.NEWLINE,
                TokenType.EOF,
            ],
        )
        self.assertEqual(tokens[4].literal, 3.5)
        self.assertEqual((tokens[1].line, tokens[1].column), (2, 1))

    def test_list_syntax_and_new_keywords(self) -> None:
        tokens = tokenize(
            "liste myList = liste.yeni 1,abc\nmyList.ekle veri \"Değer?\""
        )

        self.assertEqual(
            [token.type for token in tokens],
            [
                TokenType.LISTE,
                TokenType.IDENTIFIER,
                TokenType.EQUAL,
                TokenType.LISTE,
                TokenType.DOT,
                TokenType.YENI,
                TokenType.NUMBER,
                TokenType.COMMA,
                TokenType.IDENTIFIER,
                TokenType.NEWLINE,
                TokenType.IDENTIFIER,
                TokenType.DOT,
                TokenType.EKLE,
                TokenType.VERI,
                TokenType.STRING,
                TokenType.EOF,
            ],
        )

    def test_slash_is_not_vega_syntax(self) -> None:
        with self.assertRaisesRegex(LexerError, "Unexpected character '/'"):
            tokenize('myList.ekle "a" / myList.ekle "b"')

    def test_string_escapes(self) -> None:
        tokens = tokenize(r'yazdir "birinci\nikinci"')

        self.assertEqual(tokens[1].literal, "birinci\nikinci")

    def test_invalid_character_reports_location(self) -> None:
        with self.assertRaisesRegex(LexerError, r"line 2, column 1"):
            tokenize("sayisal x = 10\n@")

    def test_unterminated_string_reports_opening_location(self) -> None:
        with self.assertRaisesRegex(LexerError, r"line 1, column 8"):
            tokenize('yazdir "unfinished')


if __name__ == "__main__":
    unittest.main()
