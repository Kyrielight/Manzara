import unittest

from re import Pattern
from typing import List

from src.definitions import arguments_command, base_command

class BaseCommandTest(unittest.TestCase):

    def test_no_impl_of_base_abstract_methods(self):
        with self.assertRaises(TypeError):
            _ = base_command.ManzaraBaseCommand()
    
    def test_no_impl_of_base_binding(self):
        with self.assertRaises(TypeError):
            class ManzaraBaseCommandNoBinding(base_command.ManzaraBaseCommand):
                def description(self) -> str:
                    return str()
            _ = ManzaraBaseCommandNoBinding()
            
    def test_no_impl_of_description_binding(self):

        with self.assertRaises(TypeError):
            class ManzaraBaseCommandNoDescription(base_command.ManzaraBaseCommand):
                def bindings(self) -> List[Pattern]:
                    return list()
            _ = ManzaraBaseCommandNoDescription()

    def test_impl_of_base_command(self):

        class ManzaraBaseCommandCorrect(base_command.ManzaraBaseCommand):
            def bindings(self) -> List[Pattern]:
                return list()
            def description(self) -> str:
                return str()
        self.assertIsInstance(ManzaraBaseCommandCorrect(), base_command.ManzaraBaseCommand)


class ArgumentsCommandTest(unittest.TestCase):

    def test_ensure_arguments_command_is_also_base(self):
        self.assertTrue(issubclass(arguments_command.ManzaraWithArgumentsCommand, base_command.ManzaraBaseCommand))

    def test_no_redirect_impl(self):
        with self.assertRaises(TypeError):
            class ManzaraWithArgumentsNoRedirect(arguments_command.ManzaraWithArgumentsCommand):
                def bindings(self) -> List[Pattern]:
                    return list()
                def description(self) -> str:
                    return str()
            _ = ManzaraWithArgumentsNoRedirect()
    
    def test_all_methods_impl(self):
        class ManzaraWithArgumentsCorrect(arguments_command.ManzaraWithArgumentsCommand):
                def bindings(self) -> List[Pattern]:
                    return list()
                def description(self) -> str:
                    return str()
                def redirect(self, args: List[str]) -> str:
                    return str()
        self.assertIsInstance(ManzaraWithArgumentsCorrect(), base_command.ManzaraBaseCommand)

    