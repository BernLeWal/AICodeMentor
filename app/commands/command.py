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
        if command_type.lower() in ['sh', 'shell', 'bash', 'powershell', 'cmd']:
            self.type = Command.SHELL
        else:
            self.type = command_type
        self.cmds : list[str] = cmds

    def __str__(self):
        return f"{self.type}: {self.cmds}"
