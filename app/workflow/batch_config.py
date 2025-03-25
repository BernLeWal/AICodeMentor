#!/bin/python
"""
Configuration for the AI CodeMentor Batch-Processing Engine
"""
import os
import json

from app.workflow.workflow import Workflow
from app.workflow.workflow_writer import WorkflowWriter
from app.workflow.workflow_runner import WorkflowRunner

class BatchConfig:
    """Configuration for the AI CodeMentor Batch-Processing Engine"""
    def __init__(self):
        # SetUp
        self.setup_workflow_file = None # if given, the workflow file to setup the environment
        self.csv_file = None

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


    def open_csv_file(self, file_path: str = None) -> str:
        """Creates or appends to a CSV file for benchmarking results
        :param workflow_file: Path to the workflow file in Markdown format
        :return: Path to the CSV file
        """
        directory = os.path.abspath(WorkflowWriter.OUTPUT_DIR)
        if not os.path.exists(directory):
            os.makedirs(directory)
        directory = os.path.abspath(directory)
        if (self.csv_file is None) and (file_path is not None):
            csv_file_name = os.path.basename(file_path).replace(".wf.md","").replace(".cfg.json","")
            csv_file_name += ".csv"
            self.csv_file = os.path.join(directory, csv_file_name)

        if not os.path.exists(self.csv_file):
            with open(self.csv_file, "w", encoding="utf-8") as f:
                f.write("sourcefile;"+\
                        "cfg_model;cfg_temperature;cfg_top_p;cfg_f_penalty;cfg_p_penalty;"+\
                        "run_timestamp;run_duration_sec;" +\
                        "result_status;result_hash;result_length;"+\
                        "total_duration_sec;total_iterations;"+\
                        "total_prompt_tokens;total_completion_tokens;total_tokens;"+\
                        "total_prompt_chars;total_completion_chars;total_chars;"+\
                        "score_result_length;score_result_facts\n")
        return self.csv_file


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


    def score_workflow(self, workflow_runner:WorkflowRunner,
                    cfg_model:str, cfg_temp, cfg_top_p, cfg_f_penalty, cfg_p_penalty,
                    results:tuple[Workflow.Status, str]):
        """Scores the workflow results and writes to a CSV file"""
        with open(self.csv_file, "a", encoding="utf-8") as f:
            #workflow_file_basename = os.path.basename(workflow_file)
            f.write(f"{workflow_runner.workflow_file};")

            # Data of configuration
            f.write(f"{cfg_model};{cfg_temp};{cfg_top_p};{cfg_f_penalty};{cfg_p_penalty};")

            # Data of workflow run
            result_status, result_content  = results
            timestamp = workflow_runner.start_time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp};{workflow_runner.duration_sec};")

            # Data of results
            content_length_score = self.score_result_length(result_content)
            content_items_score = self.score_result_facts(result_content)

            f.write(f"{result_status};{hash(result_content)};{len(result_content)};")
            agent = workflow_runner.get_agent()
            if agent is not None:
                f.write(f"{agent.total_duration_sec};{agent.total_iterations};")
                f.write(f"{agent.total_prompt_tokens if agent.total_prompt_tokens is not None else ""};"+\
                        f"{agent.total_completion_tokens if agent.total_completion_tokens is not None else ""};"+\
                        f"{agent.total_tokens if agent.total_tokens is not None else ""};")
                f.write(f"{agent.total_prompt_chars};{agent.total_completion_chars};"+\
                        f"{agent.total_chars};")
                f.write(f"{content_length_score};{content_items_score}\n")
            else:
                f.write(";;;;;;;")
            f.flush()


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
        return bc


    @staticmethod
    def from_json_file(json_file_path : str):
        """Converts a JSON file to a BatchConfig object"""
        with open(json_file_path, "r", encoding="utf-8") as f:
            bc = BatchConfig.from_json(f.read())
            bc.open_csv_file(json_file_path)
            return bc

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
    ]
    cfg.expected_length = 200
    cfg.expected_facts = [
        "SearchText1",
        "SearchText2",
        ["SearchText3a or", "SearchText3b"],
        ]
    cfg.save_to_json_file("template.cfg.json")
