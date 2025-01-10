#!/bin/python
"""
Workflow module
"""

# --- app/workflow/workflow.py ---
import logging

# Setup logging framework
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Workflow:
    """The base class for all Workflow implementations"""

    # Workflow status
    DOING = 0
    SUCCESS = 1
    FAILED = 2

    def __init__(self, name: str, interpreter=None, parent=None):
        self.name = name
        self.status : int = None
        self.result : str = None
        self.parent : Workflow = parent  # parent workflow
        self.interpreter = interpreter  # WorkflowInterpreter instance
        logger.debug("Workflow created: %s", self.__dict__)

    def __str__(self):
        return f"Workflow(name={self.name}, status={self.status}, result={self.result})"
