#!/bin/python
"""UnitTests for AIAgentConfig"""

# test/agents/test_AIAgent.py
import unittest
import os
import json
from app.agents.agent_config import AIAgentConfig


class TestAIAgentConfig(unittest.TestCase):
    """UnitTests for AIAgentConfig"""
    def setUp(self):
        self.config = AIAgentConfig()

    def test_load_from_environment(self):
        """Checks if the configuration is loaded from the environment"""
        os.environ['AI_API_KEY'] = 'test_api_key'
        os.environ['AI_ORGANIZATION_ID'] = 'test_org_id'
        os.environ['AI_MODEL_NAME'] = 'test_model_name'
        os.environ['AI_MAX_PROMPT_LENGTH'] = '200'

        self.config.load_from_environment()

        self.assertEqual(self.config.ai_api_key, 'test_api_key')
        self.assertEqual(self.config.ai_organization_id, 'test_org_id')
        self.assertEqual(self.config.ai_model_name, 'test_model_name')
        self.assertEqual(self.config.ai_max_prompt_length, 200)

    def test_load_from_jsonfile(self):
        """Checks if the configuration is loaded from a JSON file"""
        test_config = {
            "AI_API_KEY": "file_api_key",
            "AI_ORGANIZATION_ID": "file_org_id",
            "AI_MODEL_NAME": "file_model_name",
            "AI_MAX_PROMPT_LENGTH": 200
        }
        with open('test_config.json', 'w', encoding='utf-8') as f:
            json.dump(test_config, f)

        self.config.load_from_jsonfile('test_config.json')

        self.assertEqual(self.config.ai_api_key, 'file_api_key')
        self.assertEqual(self.config.ai_organization_id, 'file_org_id')
        self.assertEqual(self.config.ai_model_name, 'file_model_name')
        self.assertEqual(self.config.ai_max_prompt_length, 200)

        os.remove('test_config.json')

    def test_load_from_json(self):
        """Checks if the configuration is loaded from a JSON string"""
        json_data = json.dumps({
            "AI_API_KEY": "json_api_key",
            "AI_ORGANIZATION_ID": "json_org_id",
            "AI_MODEL_NAME": "json_model_name",
            "AI_MAX_PROMPT_LENGTH": 200
        })

        self.config.load_from_json(json_data)

        self.assertEqual(self.config.ai_api_key, 'json_api_key')
        self.assertEqual(self.config.ai_organization_id, 'json_org_id')
        self.assertEqual(self.config.ai_model_name, 'json_model_name')
        self.assertEqual(self.config.ai_max_prompt_length, 200)


if __name__ == "__main__":
    unittest.main()
