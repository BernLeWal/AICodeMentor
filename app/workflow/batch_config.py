#!/bin/python
"""
Configuration for the AI CodeMentor Batch-Processing Engine
"""
import json


class BatchConfig:
    """Configuration for the AI CodeMentor Batch-Processing Engine"""
    def __init__(self):
        self.config_file = None
        # SetUp
        self.setup_workflow_file = None # if given, the workflow file to setup the environment

        # Workflows to run
        self.workflow_files = None
        self.key_values = {}
        self.repeats = 1

        # AIAgentConfigs
        self.ai_model_names = None
        self.ai_temperature_values = None
        self.ai_top_p_values = None
        self.ai_f_penalty_values = None
        self.ai_p_penalty_values = None

        # Expected results
        self.expected_length = None
        self.expected_facts = None

        # TearDown
        self.cleanup_workflow_file = None # if given, the workflow file to cleanup the environment


    def save_to_json_file(self, json_file_path : str):
        """Saves the configuration to a JSON file"""
        with open(json_file_path, "w", encoding="utf-8") as f:
            f.write(self.to_json())


    def to_json(self) -> str:
        """Converts the configuration to a JSON string"""
        return json.dumps(self.__dict__, indent=4)


    @staticmethod
    def from_json(json_str : str):
        """Converts a JSON string to a BatchConfig object"""
        bc = BatchConfig()
        bc.__dict__ = json.loads(json_str)
        bc.config_file = None
        return bc


    @staticmethod
    def from_json_file(json_file_path : str):
        """Converts a JSON file to a BatchConfig object"""
        with open(json_file_path, "r", encoding="utf-8") as f:
            bc = BatchConfig.from_json(f.read())
            bc.config_file = json_file_path
            return bc


    def score_result_length(self, result: str):
        """Scores the content length of the result
        :param result: The content to score
        :param expected_length: The expected length
        :return: The score
        """
        if self.expected_length is None:
            return ""
        wc = len(result.split())    # word count
        el = int(self.expected_length)
        result_length_score = ( wc if ( wc<=el ) else (2*el)-wc )*100/el
        if result_length_score < 0:
            result_length_score = 0
        return result_length_score


    def score_result_facts(self, result: str):
        """Scores the content facts of the result
        :param result: The content to score
        :param expected_facts: The expected facts
        :return: The score
        """
        if self.expected_facts is None:
            return ""

        content_items_score = 0
        fact_score = 100 / len(self.expected_facts)
        for fact in self.expected_facts:
            if isinstance(fact, list):
                if any( f in result for f in fact ):
                    content_items_score += fact_score
            elif fact in result:
                content_items_score += fact_score
        return content_items_score


if __name__ == "__main__":
    # Create a template for the batch-configuration
    cfg = BatchConfig()

    cfg.workflow_files = "<your_workflow_file.wf.md>"
    cfg.ai_model_names = [
        ## Platform OpenAI GPT Chat Models
        "gpt-4o",           #expensive
        "gpt-4o-mini",
        "gpt-4",            #expensive
        "gpt-4-turbo",
        "gpt-3.5-turbo",

        ## Platform OpenAI Reasoning Models
        "o3-mini",
        "o1-mini",
        "o1",               #expensive

        ## Google Gemini Models
        # see https://ai.google.dev/gemini-api/docs/models
        "gemini-2.0-flash",                         #expensive
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-2.0-flash-thinking-experimental",   #expensive

        ## Anthropic Claude Models
        "claude-3-7-sonnet-latest", #expensive
        "claude-3-5-haiku-latest",
        "claude-3-opus-latest", 
        "claude-3-5-sonnet-latest", #expensive
        "claude-3-haiku-20240307",
        #"claude-code-2.1",    # does this work?

        ## Huggingface Models
        "codellama/CodeLlama-7b-Instruct-hf",   #and all other CodeLlama models
    ]
    cfg.expected_length = 200
    cfg.expected_facts = [
        "SearchText1",
        "SearchText2",
        ["SearchText3a or", "SearchText3b"],
        ]
    cfg.save_to_json_file("template.cfg.json")
