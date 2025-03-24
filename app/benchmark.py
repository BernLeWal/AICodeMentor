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
from app.workflow.batch_config import BatchConfig


# Setup logging framework
if not logging.getLogger().hasHandlers():
    load_dotenv()
    logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                        format=os.getenv('LOGFORMAT', 'pretty'))
logger = logging.getLogger(__name__)


def run_workflow(workflow_file: str, key_values: dict) -> tuple[Workflow.Status, str, float]:
    """Runs a workflow and returns the results and status code
    :param workflow_file: Path to the workflow file in Markdown format
    :return: (status, result)
    """
    start_time = datetime.datetime.now()
    (main_status, main_result) = run(workflow_file, key_values)
    elapsed_time = datetime.datetime.now() - start_time

    return (main_status, main_result, elapsed_time.total_seconds())



def run_workflow_file(cfg: BatchConfig, workflow_file: str):
    """Runs a workflow and collects benchmarking data"""
    # Add the benchmark results to a CSV file
    cfg.open_csv_file(workflow_file)

    for _ in range(cfg.repeats):
        for model_name in cfg.ai_model_names or [AIAgentConfig.get_model_name()]:
            logger.info("- Running benchmark for model: %s", model_name)
            os.environ['AI_MODEL_NAME'] = model_name

            for temp in cfg.ai_temperature_values or [AIAgentConfig.get_temperature()]:
                os.environ['AI_TEMPERATURE'] = str(temp)

                for top_p in cfg.ai_top_p_values or [AIAgentConfig.get_top_p()]:
                    os.environ['AI_TOP_P'] = str(top_p)

                    for f_penalty in cfg.ai_f_penalty_values or [AIAgentConfig.get_frequency_penalty()]:
                        os.environ['AI_FREQUENCY_PENALTY'] = str(f_penalty)

                        for p_penalty in cfg.ai_p_penalty_values or [AIAgentConfig.get_presence_penalty()]:
                            os.environ['AI_PRESENCE_PENALTY'] = str(p_penalty)

                            # Run the workflow
                            results = run_workflow(workflow_file, cfg.key_values)

                            cfg.score_workflow(workflow_file,
                                        model_name, temp, top_p, f_penalty, p_penalty,
                                        results)



def run_batch(cfg: BatchConfig):
    """Runs a batch of workflows and collects benchmarking data"""
    if cfg.setup_workflow_file is not None:
        logger.info("Setting up the environment...")
        run_workflow(cfg.setup_workflow_file, cfg.key_values)

    if cfg.workflow_files is None:
        logger.error("No workflow files given!")
        return
    # if workflow_files is a list of string then process all files each
    if isinstance(cfg.workflow_files, list):
        for workflow_file in cfg.workflow_files:
            run_workflow_file(cfg, workflow_file)
    else:
        run_workflow_file(cfg, cfg.workflow_files)


if __name__ == "__main__":
    CFG = BatchConfig()

    CFG.workflow_files = "workflows/benchmarks/summarize-sourcefile.wf.md"
    CFG.ai_model_names = [
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
    CFG.expected_length = 200
    CFG.expected_facts = [
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

    run_batch(CFG)
