#!/bin/python
"""
UnitTests for WorkflowWriter
"""

import unittest
import os
from app.workflow.history import History
from app.workflow.writer import WorkflowWriter
from app.workflow.reader import WorkflowReader

class TestWorkflowWriter(unittest.TestCase):
    """UnitTests for WorkflowWriter"""

    MAIN_FILENAME = "sample-project-eval.wf.md"
    LOGFILES_DIR = os.path.abspath(WorkflowWriter.LOGFILES_DIR)

    def test_save_definition(self):
        """Test WorkflowWriter save_definition method"""
        main_workflow = WorkflowReader().load_from_mdfile(self.MAIN_FILENAME)

        main_writer = WorkflowWriter(main_workflow)
        main_writer.save_definition(
            filepath = os.path.basename(self.MAIN_FILENAME),
            directory = self.LOGFILES_DIR
        )

        abspath = os.path.join(self.LOGFILES_DIR, self.MAIN_FILENAME)
        self.assertTrue( os.path.exists(abspath) )
        os.remove(abspath)

    def test_save_history(self):
        """Test WorkflowWriter save_definition method"""
        main_workflow = WorkflowReader().load_from_mdfile(self.MAIN_FILENAME)

        main_writer = WorkflowWriter(main_workflow)
        main_writer.save_history(
            filepath = os.path.basename(self.MAIN_FILENAME).replace(".wf.md", ".wfh.md"),
            directory = self.LOGFILES_DIR,
            current_activity=main_workflow.start,
            context=None,
            history=History(self.LOGFILES_DIR)
        )

        abspath = os.path.join(self.LOGFILES_DIR, self.MAIN_FILENAME).replace(".wf.md", ".wfh.md")
        self.assertTrue( os.path.exists(abspath) )
        os.remove(abspath)

if __name__ == "__main__":
    unittest.main()
