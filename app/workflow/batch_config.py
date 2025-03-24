#!/bin/python
"""
Configuration for the AI CodeMentor Batch-Processing Engine
"""
import os
import datetime
import json

from app.workflow.workflow import Workflow
from app.workflow.workflow_writer import WorkflowWriter

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
            csv_file_name = os.path.basename(file_path).replace(".wf.md","").replace(".cfg.json","") + ".csv"
            self.csv_file = os.path.join(directory, csv_file_name)

        if not os.path.exists(self.csv_file):
            with open(self.csv_file, "w", encoding="utf-8") as f:
                f.write("sourcefile;"+\
                        "cfg_model;cfg_temperature;cfg_top_p;cfg_f_penalty;cfg_p_penalty;"+\
                        "run_timestamp;run_duration_sec;" +\
                        "result_status;result_length_score;result_facts_score\n")
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


    def score_workflow(self, workflow_file:str,
                    cfg_model:str, cfg_temp, cfg_top_p, cfg_f_penalty, cfg_p_penalty,
                    results:tuple[Workflow.Status, str, float]):
        """Scores the workflow results and writes to a CSV file"""
        with open(self.csv_file, "a", encoding="utf-8") as f:
            #workflow_file_basename = os.path.basename(workflow_file)
            f.write(f"{workflow_file};")

            # Data of configuration
            f.write(f"{cfg_model};{cfg_temp};{cfg_top_p};{cfg_f_penalty};{cfg_p_penalty};")

            # Data of workflow run
            result_status, result_content, duration_sec = results
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp};{duration_sec};")

            # Data of results
            content_length_score = self.score_result_length(result_content)
            content_items_score = self.score_result_facts(result_content)

            f.write(f"{result_status};{content_length_score};{content_items_score}\n")
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
