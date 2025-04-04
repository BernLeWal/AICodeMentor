"""
Workflow module
"""

from enum import Enum
from app.workflow.activity import Activity


# --- app/workflow/workflow.py ---
class Workflow:
    """The base class for all Workflow implementations"""

    instance_count = 0

    class Status(Enum):
        """Workflow status enumeration"""
        CREATED = -1
        DOING = 0
        SUCCESS = 1
        FAILED = 2

        def __str__(self):
            return self.name


    def __init__(self, filepath: str, parent=None):
        self.filepath = filepath
        self.directory = None
        self.name = filepath.replace('.md', '')
        self.parent : Workflow = parent  # parent workflow
        self.description : str = ''
        Workflow.instance_count += 1
        self.instance_nr = Workflow.instance_count

        self.params : dict = {}
        self.prompts : dict = {}  # prompt_id -> Prompt instance
        self.activities : dict = {}  # activity_name -> Activity instance

        self.start : Activity = None
        self.on_failed : Activity = None
        self.on_success : Activity = None


    def __str__(self):
        return f"Workflow(name={self.name})"
