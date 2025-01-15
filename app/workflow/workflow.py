"""
Workflow module
"""

from enum import Enum
from app.workflow.activity import Activity


# --- app/workflow/workflow.py ---
class Workflow:
    """The base class for all Workflow implementations"""

    class Status(Enum):
        """Workflow status enumeration"""
        CREATED = -1
        DOING = 0
        SUCCESS = 1
        FAILED = 2

        def __str__(self):
            return self.name


    def __init__(self, name: str, interpreter=None, parent=None):
        self.name = name
        self.interpreter = interpreter  # WorkflowInterpreter instance
        self.parent : Workflow = parent  # parent workflow
        self.description : str = ''

        self.status : Workflow.Status = Workflow.Status.CREATED
        self.result : str = None
        self.variables : dict = {}

        self.prompts : dict = {}  # prompt_id -> Prompt instance
        self.activities : dict = {}  # activity_name -> Activity instance
        self.start : Activity = None


    def __str__(self):
        return f"Workflow(name={self.name}, status={self.status}, result={self.result})"
