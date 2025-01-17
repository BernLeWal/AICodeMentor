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
        SET = 10
        ASSIGN = 11
        CHECK = 12
        PROMPT = 21
        EXECUTE = 22
        CALL = 23
        SUCCESS = 1
        FAILED = 2

        def __str__(self):
            return self.name


    class Succeeded(Enum):
        """Activity succeeded enumeration"""
        YES = 'YES',
        TRUE = 'TRUE',
        OK = 'OK',
        SUCCESS = 'SUCCESS',

        def __str__(self):
            return self.name


    class Failed(Enum):
        """Activity failed enumeration"""
        NO = 'NO',
        FALSE = 'FALSE',
        ERROR = 'ERROR',
        FAILED = 'FAILED',
        ELSE = 'ELSE',
        FAIL = 'FAIL',
        OTHER = 'OTHER'

        def __str__(self):
            return self.name


    def __init__(self, kind: Kind, name: str, expression: str = None):
        self.kind : Activity.Kind = kind
        self.name : str = name
        self.expression : str = expression

        self.next : Activity = None
        self.other : Activity = None
        self.hits : int = 0


    def __str__(self):
        next_name = ''
        if self.next is not None:
            next_name = self.next.name
        other_name = ''
        if self.other is not None:
            other_name = self.other.name
        return f"Activity(kind={self.kind}, name={self.name}, expr='{self.expression}', " +\
            f"next={next_name}, other={other_name}, hits={self.hits} )"


    @staticmethod
    def parse_kind(kind: str) -> Kind:
        """Parse the kind of activity"""
        if kind.upper() not in Activity.Kind.__members__:
            return None
        return Activity.Kind[kind.upper()]
