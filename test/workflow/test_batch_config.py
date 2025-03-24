#!/bin/python
"""
UnitTests for BatchConfig
"""

import os
import unittest
from app.workflow.batch_config import BatchConfig


class TestBatchConfig(unittest.TestCase):
    """UnitTests for BatchConfig"""

    def test_to_json(self):
        """Test BatchConfig to_json"""
        cfg = BatchConfig()

        cfg.workflow_files = "workflows/benchmarks/summarize-sourcefile.wf.md"
        cfg.ai_model_names = [
            ## Platform OpenAI GPT Chat Models
            #"gpt-4o",
            "gpt-4o-mini",
            #"gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo",

            ## Platform OpenAI Reasoning Models
            "o3-mini",
            "o1-mini",
            #"o1",
        ]
        cfg.expected_length = 200
        cfg.expected_facts = [
            "Java",
            "Spring Boot",
            ["REST", "RESTful"],
            ["web service","microservice","micro service"],
            ["temperature", "weather"],
            "city",
            ["get weather","get city weather","get temperature","get city temperature"],
            ["add weather","add city weather","add temperature","add city temperature"],
            ["update weather","update city weather","update temperature","update city temperature"],
            [r"GET /city/{id}","POST /city/add",r"PUT /city/update/{id}"],
            ["Vienna","Prague","Berlin","Munich"],
            ["in-memory","list","records","data"],
            ]
        file_name = "summarize-sourcefile.cfg.json"
        cfg.save_to_json_file(file_name)

        self.assertTrue(os.path.exists(file_name))
        os.remove(file_name)


if __name__ == "__main__":
    unittest.main()
