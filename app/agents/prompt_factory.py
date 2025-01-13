"""Module for the Prompt class"""
import json
import os
from app.agents.prompt import Prompt, PromptDecoder

class PromptFactory:
    """
    Class for loading prompts from files
    """

    @staticmethod
    def load(file_path: str) -> list[Prompt]:
        """
        Load prompts from a file and automatically checks the file-type.
        Supported files: .json, .md and .txt

        :param file_path: The path to the file
        :return: A list of prompts
        """
        if file_path.endswith('.json'):
            return PromptFactory.load_from_jsonfile(file_path)
        if file_path.endswith('.md'):
            return PromptFactory.load_from_mdfile(file_path)
        if file_path.endswith('.txt'):
            return PromptFactory.load_from_textfile(file_path)

        raise ValueError(f"Unsupported file type: {file_path}")

    @staticmethod
    def load_from_jsonfile(file_path: str) -> list[Prompt]:
        """
        Load prompts from a file

        :param file_path: The path to the file
        :return: A list of prompts
        """
        abs_file_path = os.path.join(os.path.dirname(__file__), file_path)
        with open(abs_file_path, 'r', encoding='utf-8') as f:
            prompts = json.load(f, cls=PromptDecoder)
        return prompts

    @staticmethod
    def load_from_mdfile(file_path: str) -> list[Prompt]:
        """
        Load prompts from a .md file

        :param file_path: The path to the file
        :return: A list of prompts
        """
        abs_file_path = os.path.join(os.path.dirname(__file__), file_path)
        with open(abs_file_path, 'r', encoding='utf-8') as f:
            content = f.readlines()
        result = []
        current_content = ''
        current_role = Prompt.USER
        for line in content:
            line_strip = line.strip()
            if line_strip.startswith('## User'):
                if len(current_content) > 0:
                    result.append(Prompt(current_role, current_content))
                    current_content = ''
                current_role = Prompt.USER
            elif line_strip.startswith('## Assistant'):
                if len(current_content) > 0:
                    result.append(Prompt(current_role, current_content))
                    current_content = ''
                current_role = Prompt.ASSISTANT
            elif line_strip.startswith('## System'):
                if len(current_content) > 0:
                    result.append(Prompt(current_role, current_content))
                    current_content = ''
                current_role = Prompt.SYSTEM
            else:
                current_content += line
        if len(current_content) > 0:
            result.append(Prompt(current_role, current_content))
        return result

    @staticmethod
    def load_from_textfile(file_path: str) -> list[Prompt]:
        """
        Load prompts from a .txt or .md file

        :param file_path: The path to the file
        :return: A list of prompts
        """
        abs_file_path = os.path.join(os.path.dirname(__file__), file_path)
        with open(abs_file_path, 'r', encoding='utf-8') as f:
            content = f.readlines()
        result = []
        current_content = ''
        current_role = Prompt.USER
        for line in content:
            line = line.strip()
            if line.startswith('User:'):
                if len(current_content) > 0:
                    result.append(Prompt(current_role, current_content))
                current_role = Prompt.USER
                current_content = line.replace('User:', '')
            elif line.startswith('Assistant:'):
                if len(current_content) > 0:
                    result.append(Prompt(current_role, current_content))
                current_role = Prompt.ASSISTANT
                current_content = line.replace('Assistant:', '')
            elif line.startswith('System:'):
                if len(current_content) > 0:
                    result.append(Prompt(current_role, current_content))
                current_role = Prompt.SYSTEM
                current_content = line.replace('System:', '')
            else:
                current_content += line
        if len(current_content) > 0:
            result.append(Prompt(current_role, current_content))
        return result


    @staticmethod
    def write_textfile(file_path: str, content: str):
        """
        Write prompts to a .txt or .md file

        :param file_path: The path to the file
        :param content: The content to write
        """
        abs_file_path = os.path.join(os.path.dirname(__file__), file_path)
        with open(abs_file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def delete_file(file_path: str):
        """
        Delete a file

        :param file_path: The path to the file
        """
        abs_file_path = os.path.join(os.path.dirname(__file__), file_path)
        os.remove(abs_file_path)
