#!/bin/python
"""
Activity, represents an action within a workflow
"""

from enum import Enum


class Activity:
    """The base class for all Activity implementations"""

    class Kind(Enum):
        """Activity kind enumeration"""
        START = 'Start'
        SET = 'Set'
        ASSIGN = 'Assign'
        CHECK = 'Check'
        PROMPT = 'Prompt'
        ASK = 'Ask'
        EXECUTE = 'Execute'
        CALL = 'Call'
        SUCCESS = 'SUCCESS'
        FAILED = 'FAILED'
        ON = 'ON'

        def __str__(self):
            return self.name


    class Succeeded(Enum):
        """Activity succeeded enumeration"""
        YES = 'YES'
        TRUE = 'TRUE'
        OK = 'OK'
        SUCCESS = 'SUCCESS'

        def __str__(self):
            return self.name


    class Failed(Enum):
        """Activity failed enumeration"""
        NO = 'NO'
        FALSE = 'FALSE'
        ERROR = 'ERROR'
        FAILED = 'FAILED'
        ELSE = 'ELSE'
        FAIL = 'FAIL'
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


    def accept(self, visitor):
        """Visit the activity"""
        # currently there is only one Activity class with the Kind as member
        # so dispatching is working with an if-else chain here
        # Note: when changed to inheritance, the dispatching will be done in the derived class
        if self.kind == Activity.Kind.START:
            visitor.visit_start(self)
        elif self.kind == Activity.Kind.SET:
            visitor.visit_set(self)
        elif self.kind == Activity.Kind.ASSIGN:
            visitor.visit_assign(self)
        elif self.kind == Activity.Kind.CHECK:
            visitor.visit_check(self)
        elif self.kind == Activity.Kind.PROMPT:
            visitor.visit_prompt(self)
        elif self.kind == Activity.Kind.ASK:
            visitor.visit_ask(self)
        elif self.kind == Activity.Kind.EXECUTE:
            visitor.visit_execute(self)
        elif self.kind == Activity.Kind.CALL:
            visitor.visit_call(self)
        elif self.kind == Activity.Kind.SUCCESS:
            visitor.visit_success(self)
        elif self.kind == Activity.Kind.FAILED:
            visitor.visit_failed(self)
        elif self.kind == Activity.Kind.ON:
            visitor.visit_on(self)


    @staticmethod
    def parse_kind(kind: str) -> Kind:
        """Parse the kind of activity"""
        if kind.upper() not in Activity.Kind.__members__:
            return None
        return Activity.Kind[kind.upper()]


class ActivityVisitor:
    """Activity visitor interface"""
    # to separate concrete functions based on activities from the activity class

    def visit_start(self, activity: Activity) -> None:
        """Visit the START activity"""

    def visit_set(self, activity: Activity) -> None:
        """Visit the SET activity"""

    def visit_assign(self, activity: Activity) -> None:
        """Visit the ASSIGN activity"""

    def visit_check(self, activity: Activity) -> None:
        """Visit the CHECK activity"""

    def visit_prompt(self, activity: Activity) -> None:
        """Visit the PROMPT activity"""

    def visit_ask(self, activity: Activity) -> None:
        """Visit the ASK activity"""

    def visit_execute(self, activity: Activity) -> None:
        """Visit the EXECUTE activity"""

    def visit_call(self, activity: Activity) -> None:
        """Visit the CALL activity"""

    def visit_success(self, activity: Activity) -> None:
        """Visit the SUCCESS activity"""

    def visit_failed(self, activity: Activity) -> None:
        """Visit the FAILED activity"""

    def visit_on(self, activity: Activity) -> None:
        """Visit the ON activity"""
