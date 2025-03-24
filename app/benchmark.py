#!/bin/python
"""
AI CodeMentor Benchmarking Engine
Automate AI CodeMentor execution and collect data for benchmark analyses
"""
import logging
import os
import datetime
from dotenv import load_dotenv

from app.main import run
from app.agents.agent_config import AIAgentConfig
from app.workflow.workflow import Workflow
from app.workflow.workflow_writer import WorkflowWriter


# Setup logging framework
if not logging.getLogger().hasHandlers():
    load_dotenv()
    logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                        format=os.getenv('LOGFORMAT', 'pretty'))
logger = logging.getLogger(__name__)


def open_csv_file(workflow_file: str) -> str:
    """Creates or appends to a CSV file for benchmarking results
    :param workflow_file: Path to the workflow file in Markdown format
    :return: Path to the CSV file
    """
    directory = os.path.abspath(WorkflowWriter.OUTPUT_DIR)
    if not os.path.exists(directory):
        os.makedirs(directory)
    directory = os.path.abspath(directory)
    csv_file_name = os.path.basename(workflow_file.replace(".wf.md", ".csv"))
    csv_file_path = os.path.join(directory, csv_file_name)

    if not os.path.exists(csv_file_path):
        with open(csv_file_path, "w", encoding="utf-8") as f:
            f.write("sourcefile;"+\
                    "cfg_model;cfg_temperature;cfg_top_p;cfg_f_penalty;cfg_p_penalty;"+\
                    "run_timestamp;run_duration_sec;" +\
                    "result_status;result_length_score;result_facts_score\n")
    return csv_file_path


def run_workflow(workflow_file: str, key_values: dict) -> tuple[Workflow.Status, str, float]:
    """Runs a workflow and returns the results and status code
    :param workflow_file: Path to the workflow file in Markdown format
    :return: (status, result)
    """
    start_time = datetime.datetime.now()
    (main_status, main_result) = run(workflow_file, key_values)
    elapsed_time = datetime.datetime.now() - start_time

    return (main_status, main_result, elapsed_time.total_seconds())


def score_workflow(workflow_file:str,
                   cfg_model:str, cfg_temp, cfg_top_p, cfg_f_penalty, cfg_p_penalty,
                   results:tuple[Workflow.Status, str, float],
                   expected_length:int, expected_facts:list,
                   csv_file: str):
    """Scores the workflow results and writes to a CSV file"""
    with open(csv_file, "a", encoding="utf-8") as f:
        workflow_file_basename = os.path.basename(workflow_file)
        # Data of configuration

        # Data of workflow run
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Data of results
        result_status, result_content, duration_sec = results
        content_length_score = score_result_length(result_content, expected_length)
        content_items_score = score_result_facts(result_content, expected_facts)

        f.write(f"{workflow_file_basename};"+\
                f"{cfg_model};{cfg_temp};{cfg_top_p};{cfg_f_penalty};{cfg_p_penalty};"+\
                f"{timestamp};{duration_sec};" +\
                f"{result_status};{content_length_score};{content_items_score}\n")


def score_result_length(result: str, expected_length: int) -> int:
    """Scores the content length of the result
    :param result: The content to score
    :param expected_length: The expected length
    :return: The score
    """
    wc = len(result.split())    # word count
    el = expected_length
    result_length_score = ( wc if ( wc<=el ) else (2*el)-wc )*100/el
    if result_length_score < 0:
        result_length_score = 0
    return result_length_score


def score_result_facts(result: str, expected_facts: list) -> float:
    """Scores the content facts of the result
    :param result: The content to score
    :param expected_facts: The expected facts
    :return: The score
    """
    content_items_score = 0
    fact_score = 100 / len(expected_facts)
    for fact in expected_facts:
        if isinstance(fact, list):
            if any( f in result for f in fact ):
                content_items_score += fact_score
        elif fact in result:
            content_items_score += fact_score
    return content_items_score


if __name__ == "__main__":
    WORKFLOW_FILE = "workflows/benchmarks/summarize-sourcefile.wf.md"
    KEY_VALUES = {}
    EXPECTED_FACTS = [
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
    MODEL_NAMES = [
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


    # Add the benchmark results to a CSV file
    CSV_FILE = open_csv_file(WORKFLOW_FILE)

    for model_name in MODEL_NAMES:
        logger.info("- Running benchmark for model: %s", model_name)
        os.environ['AI_MODEL_NAME'] = model_name
        temp = AIAgentConfig.get_temperature()
        top_p = AIAgentConfig.get_top_p()
        f_penalty = AIAgentConfig.get_frequency_penalty()
        p_penalty = AIAgentConfig.get_presence_penalty()

        # Run the workflow
        RESULTS = run_workflow(WORKFLOW_FILE, KEY_VALUES)
        score_workflow(WORKFLOW_FILE,
                       model_name, temp, top_p, f_penalty, p_penalty,
                       RESULTS, 200, EXPECTED_FACTS,
                       CSV_FILE)
