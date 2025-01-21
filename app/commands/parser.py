#!/bin/python
"""
Class to parse commands from agent outputs
"""
import logging
import os
from dotenv import load_dotenv
from app.commands.command import Command, CommandFactory


# Setup logging framework
if not logging.getLogger().hasHandlers():
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
        collapse_next_line : bool = False
        is_code_block : bool = False
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
                        if len(current_code_lines) > 0 and not collapse_next_line:
                            if not line.startswith(" ") and not line.startswith("\t") \
                                and not is_code_block:
                                # previous line was the last line of a command
                                # --> create Command
                                new_command = CommandFactory.try_create_command(
                                    current_code_block, current_code_lines)
                                if new_command is not None:
                                    commands.append(new_command)
                                    current_code_lines = []

                        if line.endswith("\\"):
                            # collapse multi-line commands to one line
                            current_code_lines.append(line[:-1] + " ")
                            collapse_next_line = True
                        elif line.startswith(" ") or line.startswith("\t"):
                            # continuation of previous line
                            current_code_lines.append("\n" + line)
                            is_code_block = True
                        elif len(current_code_lines) > 0 \
                            and not collapse_next_line and not is_code_block:
                            # previous line was the last line of a multi-line command
                            # --> create Command
                            new_command = CommandFactory.try_create_command(
                                current_code_block, current_code_lines)
                            if new_command is not None:
                                commands.append(new_command)
                                current_code_lines = []
                            current_code_lines.append(line)
                        else:
                            current_code_lines.append(line)
                            collapse_next_line = False
                            is_code_block = False
                elif current_code_block is not None:
                    # Inside code block
                    if len(line) > 0:
                        current_code_lines.append(line)
        return commands


if __name__ == "__main__":
    main_parser = Parser()
    # define a multi-line agent message
    MAIN_AGENT_MESSAGE = "```bash\n" + \
        "# Check if git commands are installed\n" + \
        "git --version && echo \"Git is installed\" || echo \"Git is not installed\"\n" + \
        "\n" + \
        "# Check if GitHub is reachable\n" + \
        "ping -c 4 github.com\n" + \
        "```\n"
    # Print the parsed commands
    for command in main_parser.parse(MAIN_AGENT_MESSAGE):
        print(command)
