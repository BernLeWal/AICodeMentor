#!/bin/python
"""
Class to parse commands from agent outputs
"""
import logging
import os
from dotenv import load_dotenv
from app.commands.command import Command, CommandFactory


# Setup logging framework
load_dotenv()
logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                    format=os.getenv('LOGFORMAT', 'pretty'))
logger = logging.getLogger(__name__)


class Parser:
    """
    Class to parse commands from agent outputs
    """
    def parse(self, agent_msg: str) -> list[Command]:
        """
        Parse the output string and return a list of Command objects

        :param output: The output string from the agent
        :return: A list of Command objects
        """
        commands : list[Command] = []
        current_code_block : str = None
        current_code_lines : list[str] = []
        for line in agent_msg.splitlines():
            if current_code_block is None:
                line = line.strip()
            if line.startswith("```"):
                if current_code_block is None:
                    # Start of code block
                    current_code_block = Command.parse_command_type(line.replace("```", ""))
                else:
                    # End of code block
                    new_command = CommandFactory.try_create_command(
                        current_code_block, current_code_lines)
                    if new_command is not None:
                        commands.append(new_command)
                    current_code_lines = []
                    current_code_block = None
            else:
                if current_code_block==Command.SHELL:
                    # Inside code SHELL block:
                    # create one Command instance per line
                    if len(line) > 0:
                        if line.endswith("\\"):
                            current_code_lines.append(line[:-1])
                            current_code_lines.append(" ")
                        else:
                            current_code_lines.append(line)
                            new_command = CommandFactory.try_create_command(
                                current_code_block, current_code_lines)
                            if new_command is not None:
                                commands.append(new_command)
                            current_code_lines = []
                elif current_code_block is not None:
                    # Inside code block
                    if len(line) > 0:
                        current_code_lines.append(line)
        return commands


if __name__ == "__main__":
    main_parser = Parser()
    # define a multi-line agent message
    MAIN_AGENT_MESSAGE = "```bash\n" + \
        "git --version && \\\n" + \
        "git ls-remote https://github.com\n" + \
        "# Check if git commands are installed\n" + \
        "git --version && echo \"Git is installed\" || echo \"Git is not installed\"\n" + \
        "\n" + \
        "# Check if GitHub is reachable\n" + \
        "ping -c 4 github.com\n" + \
        "```\n"
    # Print the parsed commands
    for command in main_parser.parse(MAIN_AGENT_MESSAGE):
        print(command)
