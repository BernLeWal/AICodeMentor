"""Module for the Prompt class"""
import json

class Prompt:
    """
    Class representing a chatgpt chat completion prompt
    :param role: The role of the prompt (system, user or assistant)
    :param content: The content of the prompt
    """

    # Static constant for the roles
    SYSTEM = 'system'
    USER = 'user'
    ASSISTANT = 'assistant'

    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content.strip()
        self.check()


    def check(self):
        """Check the prompt for validity"""
        allowed_roles = [self.SYSTEM, self.USER, self.ASSISTANT]
        if self.role not in allowed_roles:
            raise ValueError(f"role must be one of {allowed_roles}, not {self.role}")

    def to_dict(self):
        """Convert the Prompt to a dictionary, for JSON serialization"""
        return {
            'role': self.role,
            'content': self.content
        }

    def __str__(self):
        return f"{self.role}: {self.content}"


class PromptEncoder(json.JSONEncoder):
    """
    JSON encoder for the Prompt class
    """
    def default(self, o):
        """
        Default JSON serialization for objects that don't have a specialized
        serialization

        :param obj: The object to serialize
        :return: The serialized object
        """
        if isinstance(o, Prompt):
            return o.to_dict()
        return super().default(o)


class PromptDecoder(json.JSONDecoder):
    """
    JSON decoder for the Prompt class
    """
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.dict_to_object, *args, **kwargs)

    def dict_to_object(self, d):
        """
        Convert a dictionary to a Prompt object

        :param d: The dictionary to convert
        :return: The Prompt object
        """
        return Prompt(d['role'], d['content'])
