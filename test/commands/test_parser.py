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
        agent_msg = "```python\nprint('Hello, world!')"
        commands = self.parser.parse(agent_msg)
        self.assertEqual(len(commands), 0)

    def test_parse_mixed_content(self):
        """Test parsing mixed content with commands and text"""
        agent_msg = "Here is a command:\n```bash\nls -la\n```\nAnd some more text."
        commands = self.parser.parse(agent_msg)
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].type, Command.SHELL)
        self.assertEqual(commands[0].cmds, ["ls -la"])

    def test_parse_mutliline_commands(self):
        """Test parsing multiple commands with multiple lines"""
        agent_msg = "```bash\n" +\
            "git --version && \\\n" + \
            "git ls-remote https://github.com\n" +\
            "```\n"
        commands = self.parser.parse(agent_msg)
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].type, Command.SHELL)
        self.assertTrue(commands[0].cmds[0].startswith("git --version"))
        self.assertTrue(commands[0].cmds[0].endswith("github.com"))


    def test_parse_multiline_commands2(self):
        """Test parsing multiple commands with multiple lines"""
        agent_msg = "```bash\n# Check if git commands are installed\n" + \
            "git --version && \\\n# Check mvn version\nmvn --version\n```\n"
        commands = self.parser.parse(agent_msg)
        self.assertEqual(len(commands), 3)
        self.assertEqual(commands[0].type, Command.SHELL)
        self.assertEqual(commands[0].cmds, ["# Check if git commands are installed"])
        self.assertEqual(commands[1].type, Command.SHELL)
        self.assertEqual(commands[1].cmds, ["git --version &&   # Check mvn version"])
        self.assertEqual(commands[2].type, Command.SHELL)
        self.assertEqual(commands[2].cmds, ["mvn --version"])

    def test_parse_command_block(self):
        """Test parsing a command block"""
        agent_msg = "```bash\n" +\
            "for file in \".\"/*; do \n" + \
            "  if [ -d \"$file\" ]; then \n" +\
            "    echo \"$file is a directory.\" \n" +\
            "  else \n" +\
            "    echo \"$file is a file.\" \n" +\
            "  fi \n" +\
            "done\n" +\
            "```\n"
        commands = self.parser.parse(agent_msg)
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].type, Command.SHELL)
        self.assertTrue(commands[0].cmds[0].startswith("for file in"))
        self.assertTrue(commands[0].cmds[0].endswith("done"))


if __name__ == "__main__":
    unittest.main()
