#!/bin/python
"""
Workflow module
"""

from enum import Enum

# --- app/workflow/workflow.py ---
class Workflow:
    """The base class for all Workflow implementations"""

    class Status(Enum):
        """Workflow status enumeration"""
        CREATED = -1
        DOING = 0
        SUCCESS = 1
        FAILED = 2


    def __init__(self, name: str, interpreter=None, parent=None):
        self.name = name
        self.status : Workflow.Status = Workflow.Status.CREATED
        self.result : str = None
        self.parent : Workflow = parent  # parent workflow
        self.interpreter = interpreter  # WorkflowInterpreter instance


    def __str__(self):
        return f"Workflow(name={self.name}, status={self.status}, result={self.result})"
