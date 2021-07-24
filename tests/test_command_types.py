import unittest

from re import Pattern
from typing import Tuple

from context import definitions # type: ignore
from definitions import arguments_command, base_command

class BaseCommandTest(unittest.TestCase):

    def test_no_impl_of_base_abstract_methods(self):
        with self.assertRaises(TypeError):
            _ = base_command.Usagi12BaseCommand()
    
    def test_no_impl_of_base_binding(self):
        with self.assertRaises(TypeError):
            class Usagi12BaseCommandNoBinding(base_command.Usagi12BaseCommand):
                def description(self) -> str:
                    return str()
            _ = Usagi12BaseCommandNoBinding()
            
    def test_no_impl_of_description_binding(self):

        with self.assertRaises(TypeError):
            class Usagi12BaseCommandNoDescription(base_command.Usagi12BaseCommand):
                def bindings(self) -> Tuple[Pattern]:
                    return list()
            _ = Usagi12BaseCommandNoDescription()

    def test_impl_of_base_command(self):

        class Usagi12BaseCommandCorrect(base_command.Usagi12BaseCommand):
            def bindings(self) -> Tuple[Pattern]:
                return list()
            def description(self) -> str:
                return str()
        self.assertIsInstance(Usagi12BaseCommandCorrect(), base_command.Usagi12BaseCommand)


class ArgumentsCommandTest(unittest.TestCase):

    def test_ensure_arguments_command_is_also_base(self):
        self.assertTrue(issubclass(arguments_command.Usagi12WithArgumentsCommand, base_command.Usagi12BaseCommand))

    def test_no_redirect_impl(self):
        with self.assertRaises(TypeError):
            class Usagi12WithArgumentsNoRedirect(arguments_command.Usagi12WithArgumentsCommand):
                def bindings(self) -> Tuple[Pattern]:
                    return list()
                def description(self) -> str:
                    return str()
            _ = Usagi12WithArgumentsNoRedirect()
    
    def test_all_methods_impl(self):
        class Usagi12WithArgumentsCorrect(arguments_command.Usagi12WithArgumentsCommand):
                def bindings(self) -> Tuple[Pattern]:
                    return list()
                def description(self) -> str:
                    return str()
                def redirect(self, args: Tuple[str]) -> str:
                    return str()
        self.assertIsInstance(Usagi12WithArgumentsCorrect(), base_command.Usagi12BaseCommand)

    