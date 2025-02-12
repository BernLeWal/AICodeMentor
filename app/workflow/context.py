"""
This module contains the context for the interpreted workflow.
"""

import logging
import os
from enum import Enum
from dotenv import load_dotenv
from app.workflow.workflow import Workflow
from app.agents.agent import AIAgent
from app.commands.executor import CommandExecutor


load_dotenv()

# Setup logging framework
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                        format=os.getenv('LOGFORMAT', 'pretty'))
logger = logging.getLogger(__name__)


class Context:
    """The context for the interpreted workflow"""

    class InternalVariable(Enum):
        """Internal variables enumeration"""
        STATUS = 0
        RESULT = 1

        def __str__(self):
            return self.name



    def __init__(self, workflow : Workflow,
                 agent : AIAgent = None, command_executor : CommandExecutor = None):
        self.workflow = workflow
        self.agent : AIAgent = agent   # will be set from outside
        self.command_executor : CommandExecutor = command_executor  # will be set from outside

        self.status : Workflow.Status = Workflow.Status.CREATED
        self.result : str = None

        self.variables : dict = {}
        for key,value in workflow.params.items():
            self.variables[key] = value



    def get_value(self, name: str, default_value: str = None)->str:
        """Get the value of the variable with the given name"""
        if name is None or len(name) == 0:
            return default_value

        # Check for constants:
        if name.startswith("'") and name.endswith("'"):
            return name[1:-1]
        if len(name) > 100:
            return default_value # that is obviously a constant, not a variable

        # Find in internal (hard-coded) variables:
        if name == self.InternalVariable.STATUS.name:
            return self.status.name
        if name == self.InternalVariable.RESULT.name or name == "CONTENT":
            if self.result is None:
                return ""   # variable found, but result is empty
            return self.result

        # Find in variables:
        if name in self.variables:
            return self.variables[name]

        # Find in prompts:
        if name in self.workflow.prompts:
            return self.workflow.prompts[name].content

        # Find in environment variables:
        if name in os.environ:
            return os.environ[name]
        # Not found:
        if default_value is None:
            # it should have been a variable, so log a warning
            logger.warning("Variable %s not found!", name)
        return default_value


    def set_value(self, name: str, value: str)->None:
        """Set the value of the variable with the given name"""
        if name is None or len(name) == 0:
            logger.warning("Variable name for value='%s' is not set!", value)
            return

        # Check for constants:
        if name.startswith("'") and name.endswith("'"):
            logger.warning("Constant %s cannot be set to %s!", name, value)
            return
        if len(name) > 100:
            logger.warning("Variable name '%s' is too long!", name)
            return

        # Try set in internal (hard-coded) variables:
        if name == self.InternalVariable.STATUS.name:
            if value in Workflow.Status.__members__:
                self.status = Workflow.Status[value]
            else:
                logger.warning("Value '%s' is not a valid STATUS!", value)
            return
        if name == self.InternalVariable.RESULT.name or name == "CONTENT":
            self.result = value
            return

        # Set in variables:
        self.variables[name] = value
