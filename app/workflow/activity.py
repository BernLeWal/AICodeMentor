#!/bin/python
"""
Activity, represents an action within a workflow
"""

from enum import Enum


class Activity:
    """The base class for all Activity implementations"""

    class Kind(Enum):
        """Activity kind enumeration"""
        START = 0
        PROMPT = 1
        EXECUTE = 2
        CHECK_STATUS = 3
        CHECK_RESULT = 4
        SUCCESS = 5
        FAILED = 6

        def __str__(self):
            return self.name


    def __init__(self, kind: Kind, name: str, expression: str = None):
        self.kind : Activity.Kind = kind
        self.name : str = name
        self.expression : str = expression

        self.next : Activity = None
        self.other : Activity = None
        self.hits : int = 0
