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
        print(f"**{command.output}##")
        self.assertEqual(result, 0)
        lines = self.executor.current_output.split("\n")
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[0].find("Hello, World!") >= 0)

    def test_multiple_commands(self):
        """Test executing multiple commands"""
        command = Command(Command.SHELL, ["VAR=PersistentShell", "echo \"$VAR\""])
        result = self.executor.execute(command)
        print(f"**{command.output}##")
        self.assertEqual(result, 0)
        lines = self.executor.current_output.split("\n")
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[0].find("PersistentShell") >= 0)

if __name__ == "__main__":
    unittest.main()
