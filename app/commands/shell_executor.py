#!/bin/python
"""
Class to execute commands
"""
import logging
import subprocess
from app.commands.command import Command
from app.commands.executor import CommandExecutor

# Setup logging framework
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



class ShellCommandExecutor(CommandExecutor):
    """
    Class to execute shell commands
    """
    def execute(self, command: Command) -> str:
        """
        Execute the given shell command

        :param command: The Command object to execute
        :return: The result of the command execution
        """
        try:
            result = subprocess.run(command.cmds, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return e.stderr
