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



def run_batch_workflow(cfg: BatchConfig, workflow_file: str):
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
            run_batch_workflow(cfg, workflow_file)
    else:
        run_batch_workflow(cfg, cfg.workflow_files)


if __name__ == "__main__":
    CFG = BatchConfig.from_json_file("workflows/benchmarks/summarize-sourcefile.cfg.json")

    run_batch(CFG)
