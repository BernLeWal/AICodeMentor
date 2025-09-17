#!/bin/python
"""Interprets and Creates Operations which are used in expressions"""

import re
from enum import Enum

class Operation(Enum):
    """Operation enumeration"""
    # String Operations:
    EQUALS = 0
    DIFFERS = 1
    CONTAINS = 2
    MATCHES = 3  # regex match

    # Numeric Operations:
    GREATER = 10
    GREATER_EQUAL = 11
    LESS = 12
    LESS_EQUAL = 13


    def __str__(self):
        return self.name


class OperationInterpreter:
    """Interprets and Creates Operations"""
    @staticmethod
    def parse_operation(operation: str) -> Operation | None:
        """Parse operation"""
        if operation.upper() in Operation.__members__:
            return Operation[operation.upper()]
        if operation == "==" or operation == "eq":
            return Operation.EQUALS
        if operation == "!=" or operation == "ne":
            return Operation.DIFFERS
        if operation == "<" or operation == "lt":
            return Operation.LESS
        if operation == ">" or operation == "gt":
            return Operation.GREATER
        if operation == "<=" or operation == "le":
            return Operation.LESS_EQUAL
        if operation == ">=" or operation == "ge":
            return Operation.GREATER_EQUAL
        return None


    @staticmethod
    def interpret_operation(operation: Operation, left: str, right: str) -> bool:
        """Interpret operation"""
        if operation == Operation.EQUALS:
            firstline = left.split("\n")[0].strip()
            return right.strip() == firstline
        if operation == Operation.DIFFERS:
            firstline = left.split("\n")[0].strip()
            return right.strip() != firstline
        if operation == Operation.CONTAINS:
            return right.strip() in left
        if operation == Operation.MATCHES:
            return re.search(right, left) is not None
        if operation == Operation.LESS:
            try:
                # numeric comparison
                n_left = float(left)
                n_right = float(right)
                return n_left < n_right
            except ValueError:
                # string comparison
                return left < right
        if operation == Operation.GREATER:
            try:
                # numeric comparison
                n_left = float(left)
                n_right = float(right)
                return n_left > n_right
            except ValueError:
                # string comparison
                return left > right
        if operation == Operation.LESS_EQUAL:
            try:
                # numeric comparison
                n_left = float(left)
                n_right = float(right)
                return n_left <= n_right
            except ValueError:
                # string comparison
                return left <= right
        if operation == Operation.GREATER_EQUAL:
            try:
                # numeric comparison
                n_left = float(left)
                n_right = float(right)
                return n_left >= n_right
            except ValueError:
                # string comparison
                return left >= right

        return False
