"""UnitTests for PromptFactory"""
import unittest
import json
from app.agents.prompt_factory import PromptFactory
from app.agents.prompt import Prompt, PromptEncoder

class TestPromptFactory(unittest.TestCase):
    """UnitTests for PromptFactory"""

    def setUp(self):
        self.json_file_path = 'test_prompts.json'
        self.text_file_path = 'test_prompts.txt'
        self.md_file_path = 'test_prompts.md'

        self.prompts = [
            Prompt(Prompt.SYSTEM, "System prompt"),
            Prompt(Prompt.USER, "User prompt"),
            Prompt(Prompt.ASSISTANT, "Assistant response")
        ]

        PromptFactory.write_textfile(self.json_file_path,
            json.dumps([prompt.to_dict() for prompt in self.prompts], cls=PromptEncoder))

        PromptFactory.write_textfile(self.text_file_path,
            'System: System prompt\nUser: User prompt\nAssistant: Assistant response\n')

        PromptFactory.write_textfile(self.md_file_path,
            '## System\nSystem prompt\n\n## User\nUser prompt\n\n## Assistant\nAssistant response\n')

    def tearDown(self):
        PromptFactory.delete_file(self.json_file_path)
        PromptFactory.delete_file(self.text_file_path)
        PromptFactory.delete_file(self.md_file_path)

    def test_load_from_jsonfile(self):
        """Test loading prompts from a JSON file"""
        loaded_prompts = PromptFactory.load_from_jsonfile(self.json_file_path)
        self.assertEqual(len(loaded_prompts), len(self.prompts))
        for loaded_prompt, prompt in zip(loaded_prompts, self.prompts):
            self.assertEqual(loaded_prompt.role, prompt.role)
            self.assertEqual(loaded_prompt.content, prompt.content)

    def test_load_from_textfile(self):
        """Test loading prompts from a text file"""
        loaded_prompts = PromptFactory.load_from_textfile(self.text_file_path)
        self.assertEqual(len(loaded_prompts), len(self.prompts))
        for loaded_prompt, prompt in zip(loaded_prompts, self.prompts):
            self.assertEqual(loaded_prompt.role, prompt.role)
            self.assertEqual(loaded_prompt.content, prompt.content)

    def test_load_from_mdfile(self):
        """Test loading prompts from a markdown file"""
        loaded_prompts = PromptFactory.load_from_mdfile(self.md_file_path)
        self.assertEqual(len(loaded_prompts), len(self.prompts))
        for loaded_prompt, prompt in zip(loaded_prompts, self.prompts):
            self.assertEqual(loaded_prompt.role, prompt.role)
            self.assertEqual(loaded_prompt.content, prompt.content)

    def test_load_unsupported_file_type(self):
        """Test loading prompts from an unsupported file type"""
        with self.assertRaises(ValueError):
            PromptFactory.load('unsupported_file_type.xyz')

if __name__ == "__main__":
    unittest.main()
