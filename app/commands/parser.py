#!/bin/python
"""
Class to parse commands from agent outputs
"""
import logging
from app.commands.command import Command


# Setup logging framework
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Parser:
    """
    Class to parse commands from agent outputs
    """
    def parse(self, agent_msg: str) -> list['Command']:
        """
        Parse the output string and return a list of Command objects

        :param output: The output string from the agent
        :return: A list of Command objects
        """
        commands = []
        current_code_block = None
        current_code_lines = []
        for line in agent_msg.splitlines():
            if current_code_block is None:
                line.strip()
            if line.startswith("```"):
                if current_code_block is None:
                    # Start of code block
                    current_code_block = line.replace("```", "")
                else:
                    # End of code block
                    commands.append(Command(current_code_block, current_code_lines))
                    current_code_block = None
                    current_code_lines = []
            else:
                if current_code_block is not None:
                    # Inside code block
                    if len(line) > 0:
                        current_code_lines.append(line)
        return commands


if __name__ == "__main__":
    main_parser = Parser()
    # define a multi-line agent message
    MAIN_AGENT_MESSAGE = "```bash\n" + \
        "git --version && " + \
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
