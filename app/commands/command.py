"""
Class representing a command
"""

class Command:
    """
    Class representing a command
    """

    # Static constant for the command-types
    SHELL = 'sh'

    def __init__(self, command_type: str, cmds: list[str]):
        self.type = Command.parse_command_type(command_type)
        self.cmds : list[str] = cmds
        self.exit_code : int = None
        self.output : str = None

    def __str__(self):
        return f"{self.type}: {self.cmds}"


    @staticmethod
    def parse_command_type(command_type: str) -> str:
        """Parse the command type from a string"""
        if command_type.lower() in ['sh', 'shell', 'bash', 'powershell', 'cmd']:
            return Command.SHELL
        return command_type



class CommandFactory:
    """
    Factory class to create Command objects
    """

    @staticmethod
    def try_create_command(command_type: str, cmds: list[str]) -> Command:
        """
        Create a Command object

        :param command_type: The type of command
        :param cmds: The list of commands
        :return: A Command object
        """
        command_type = Command.parse_command_type(command_type)
        if command_type is None:
            return None

        if len(cmds) == 0:
            return None

        if command_type == Command.SHELL:
            # If the command type is SHELL, join the commands into a single command
            cmds = [" ".join(cmds)]
            if len(cmds[0]) == 0:
                return None
        return Command(command_type, cmds)
