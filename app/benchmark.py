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
            f.write("sourcefile;timestamp;duration_sec;status;" +\
                    "result_length_score;result_facts_score\n")
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


def score_workflow(workflow_file:str, results:tuple[Workflow.Status, str, float],
                   expected_facts:list, csv_file: str):
    """Scores the workflow results and writes to a CSV file"""
    with open(csv_file, "a", encoding="utf-8") as f:
        workflow_file_basename = os.path.basename(workflow_file)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        main_status, main_result, duration_sec = results

        content_length_score = score_result_length(main_result, 100)

        content_items_score = score_result_facts(main_result, expected_facts)

        f.write(f"{workflow_file_basename};{timestamp};{duration_sec};{main_status};" +\
                f"{content_length_score};{content_items_score}\n")


def score_result_length(result: str, expected_length: int) -> int:
    """Scores the content length of the result
    :param result: The content to score
    :param expected_length: The expected length
    :return: The score
    """
    wc = len(result.split())    # word count
    result_length_score = wc if ( wc<=expected_length ) else ((2*expected_length)-wc)
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
        "web service",
        ["temperature", "weather"],
        "city",
        ["get weather","get city weather","get temperature","get city temperature"],
        ["add weather","add city weather","add temperature","add city temperature"],
        ["update weather","update city weather","update temperature","update city temperature"],
        [r"GET /city/{id}","POST /city/add",r"PUT /city/update/{id}"],
        ["Vienna","Prague","Berlin","Munich"],
        ["in-memory","list","records","data"],
        ]


    # Add the benchmark results to a CSV file
    CSV_FILE = open_csv_file(WORKFLOW_FILE)

    # Run the workflow
    RESULTS = run_workflow(WORKFLOW_FILE, KEY_VALUES)
    score_workflow(WORKFLOW_FILE, RESULTS, EXPECTED_FACTS, CSV_FILE)
