
import unittest

from context import commands, definitions # type: ignore
from commands import google
from definitions import arguments_command

class GoogleCommandTest(unittest.TestCase):

    def setUp(self) -> None:
        self.instance = google.Google()

    def test_ineritance(self):
        self.assertIsInstance(self.instance, arguments_command.Usagi12WithArgumentsCommand)

    def test_single_letter_input(self):
        self.assertEqual(self.instance.redirect(["g"]), "https://www.google.com")

    def test_full_letter_input(self):
        self.assertEqual(self.instance.redirect(["google"]), "https://www.google.com")

    def test_single_letter_with_query(self):
        self.assertEqual(self.instance.redirect(["g", "hello", "world"]), "https://www.google.com/search?q=hello%20world")

    def test_full_letter_with_query(self):
        self.assertEqual(self.instance.redirect(["google", "hello", "world"]), "https://www.google.com/search?q=hello%20world")

    def test_unicode_query(self):
        self.assertEqual(self.instance.redirect(["g", "今日"]), "https://www.google.com/search?q=%E4%BB%8A%E6%97%A5")

    def test_ignore_case_short(self):
        self.assertEqual(self.instance.redirect(["G"]), "https://www.google.com")

    def test_ignore_case_full(self):
        self.assertEqual(self.instance.redirect(["gOoGlE"]), "https://www.google.com")

    def test_similar_but_not_a_query_short(self):
        for binding in self.instance.bindings:
            self.assertIsNone(binding.match("go"))

    def test_similar_but_not_a_query_long(self):
        for binding in self.instance.bindings:
            self.assertIsNone(binding.match("googled"))