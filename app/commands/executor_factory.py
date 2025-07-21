#!/bin/python
"""
The factory class for creating CommandExecutor instances
"""
import logging
import os
from dotenv import load_dotenv
from app.commands.executor import CommandExecutor
from app.commands.shell_executor import ShellCommandExecutor
from app.commands.ssh_executor import SSHCommandExecutor


# Setup logging framework
if not logging.getLogger().hasHandlers():
    load_dotenv()
    logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                        format=os.getenv('LOGFORMAT', '%(message)s'))
logger = logging.getLogger(__name__)


class ExecutorFactory:
    """
    The factory class for creating CommandExecutor instances
    """

    @staticmethod
    def create_executor() -> CommandExecutor:
        """
        Creates a CommandExecutor instance of the specified type.
        """

        ssh_host = os.getenv("SHELLBOX_HOST")
        if ssh_host:
            return SSHCommandExecutor()

        return ShellCommandExecutor()
