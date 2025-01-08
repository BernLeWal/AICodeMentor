#!/bin/python
"""UnitTests for ShellCommandExecutor"""

import unittest
from app.commands.shell_executor import ShellCommandExecutor
from app.commands.command import Command

class TestShellCommandExecutor(unittest.TestCase):
    """UnitTests for ShellCommandExecutor"""

    def setUp(self):
        self.executor = ShellCommandExecutor()

    def test_single_command(self):
        """Test executing a single command"""
        command = Command(Command.SHELL, ["echo \"Hello, World!\""])
        result = self.executor.execute(command)
        self.assertEqual(result, 0)
        lines = self.executor.current_output.split("\n")
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[1].find("Hello, World!") >= 0)

    def test_multiple_commands(self):
        """Test executing multiple commands"""
        command = Command(Command.SHELL, ["set VAR=PersistentShell", "echo %VAR%"])
        result = self.executor.execute(command)
        self.assertEqual(result, 0)
        lines = self.executor.current_output.split("\n")
        self.assertEqual(len(lines), 3)
        self.assertTrue(lines[2].find("PersistentShell") >= 0)

if __name__ == "__main__":
    unittest.main()
