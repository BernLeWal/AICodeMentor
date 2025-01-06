#!/bin/python
"""UnitTests for Parser"""
import unittest
from app.commands.parser import Parser
from app.commands.command import Command

class TestParser(unittest.TestCase):
    """UnitTests for Parser"""

    def setUp(self):
        self.parser = Parser()

    def test_parse_single_command(self):
        """Test parsing a single command"""
        agent_msg = "```bash\nls -la\n```"
        commands = self.parser.parse(agent_msg)
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].type, Command.SHELL)
        self.assertEqual(commands[0].cmds, ["ls -la"])

    def test_parse_multiple_commands(self):
        """Test parsing multiple commands"""
        agent_msg = "```bash\nls -la\n```\n```python\nprint('Hello, world!')\n```"
        commands = self.parser.parse(agent_msg)
        self.assertEqual(len(commands), 2)
        self.assertEqual(commands[0].type, Command.SHELL)
        self.assertEqual(commands[0].cmds, ["ls -la"])
        self.assertEqual(commands[1].type, "python")
        self.assertEqual(commands[1].cmds, ["print('Hello, world!')"])

    def test_parse_no_commands(self):
        """Test parsing when there are no commands"""
        agent_msg = "This is a message without any commands."
        commands = self.parser.parse(agent_msg)
        self.assertEqual(len(commands), 0)

    def test_parse_incomplete_command(self):
        """Test parsing an incomplete command"""
        agent_msg = "```bash\nls -la"
        commands = self.parser.parse(agent_msg)
        self.assertEqual(len(commands), 0)

    def test_parse_mixed_content(self):
        """Test parsing mixed content with commands and text"""
        agent_msg = "Here is a command:\n```bash\nls -la\n```\nAnd some more text."
        commands = self.parser.parse(agent_msg)
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].type, Command.SHELL)
        self.assertEqual(commands[0].cmds, ["ls -la"])

if __name__ == "__main__":
    unittest.main()
