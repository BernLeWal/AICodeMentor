#!/bin/python
"""
Classes to store and deal with history of Workflow activities proceeded
"""

import datetime
from app.workflow.workflow import Workflow


class HistoryRecord:
    """A record of an activity in the workflow history"""
    def __init__(self, activity_caption : str, status : Workflow.Status, result : str,
            timestamp = None):
        # set current datetime as self.timestamp
        if timestamp is not None:
            self.timestamp = timestamp
        else:
            self.timestamp = datetime.datetime.now()
        self.activity_caption = activity_caption
        self.status : Workflow.Status = status
        self.result : str = result


class History:
    """A history of Workflow activities"""
    def __init__(self, history_dir : str, max_record_length : int = 2000):
        self.history_dir : str = history_dir
        self.max_record_length : int = max_record_length

        self.records : list = []


    def add_record(self, caption: str, status: Workflow.Status, result: str) -> HistoryRecord:
        """Add a record to the history"""
        record = HistoryRecord(caption, status, result)
        self.records.append( record )
        return record
