#!/bin/python
"""
AI CodeMentor
automatically analyse, feedback and grade source-code project submissions using AI agents
"""
import logging
import sys
import os
import argparse
from dotenv import load_dotenv

from app.version import __version__, __app_name__, __app_description__
from app.agents.agent_config import AIAgentConfig
from app.workflow.batch_config import BatchConfig
from app.workflow.workflow import Workflow
from app.workflow.workflow_runner import WorkflowRunner

# Setup logging framework
load_dotenv()
logfiles_dir = os.getenv('LOGFILES_DIR', './logs')
os.makedirs(logfiles_dir, exist_ok=True)
logfile_path = os.path.join(logfiles_dir, 'codementor.log')
if logging.getLogger().hasHandlers():
    logging.getLogger().handlers.clear()    #remove existing default handlers
logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                    format=os.getenv('LOGFORMAT', 'pretty'),
                    handlers=[
                        logging.FileHandler(logfile_path),
                        #logging.StreamHandler(sys.stdout)  # Optional: to also log to console
                    ])
logger = logging.getLogger(__name__)


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
                            agent_config = AIAgentConfig(model_name)
                            workflow_runner = WorkflowRunner(workflow_file, cfg.key_values)
                            results = workflow_runner.run(agent_config)

                            cfg.score_workflow(workflow_runner,results)


def run_batch(cfg: BatchConfig):
    """Runs a batch of workflows and collects benchmarking data"""
    if cfg.setup_workflow_file is not None:
        logger.info("Setting up the environment...")
        WorkflowRunner(cfg.setup_workflow_file, cfg.key_values).run(AIAgentConfig())

    if cfg.workflow_files is None:
        logger.error("No workflow files given!")
        return
    # if workflow_files is a list of string then process all files each
    if isinstance(cfg.workflow_files, list):
        for workflow_file in cfg.workflow_files:
            run_batch_workflow(cfg, workflow_file)
    else:
        run_batch_workflow(cfg, cfg.workflow_files)

    if cfg.cleanup_workflow_file is not None:
        logger.info("Cleaning up the environment...")
        load_dotenv()   # reload the environment variables
        WorkflowRunner(cfg.cleanup_workflow_file, cfg.key_values).run(AIAgentConfig())



if __name__ == "__main__":
    # For debugging, uncomment and set the following lines:
    #sys.argv.append("--help")

    # Scenario 1: workflow execution
    #sys.argv.append("--verbose")
    #sys.argv.append("workflows/sample-project-eval.wf.md")
    #sys.argv.append("REPO_URL=https://github.com/BernLeWal/fhtw-bif5-swkom-paperless.git")

    # Scenario 2: batch execution
    #sys.argv.append("--batch")
    #sys.argv.append("workflows/benchmarks/summarize-sourcefile.cfg.json")

    parser = argparse.ArgumentParser(
        description=f"{__app_name__} - {__app_description__}"
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"{__app_name__} V{__version__}",
        help="Show program's version number and exit"
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help="Write the log-output also to the console"
    )
    #parser.add_argument(
    #    '--server', '-s',
    #    action='store_true',
    #    help="Run the application as a server"
    #)
    parser.add_argument(
        '--batch', '-b',
        action='store_true',
        help="Run the application in batch mode"
    )
    parser.add_argument(
        'workflow_file',
        metavar='<workflow-file.md|batch-config.json>',
        type=str,
        help="Path to the workflow file (in Markdown format) "+\
            "or batch configuration file (in JSON format)"
    )
    parser.add_argument(
        'key_values',
        metavar='<key=value>',
        type=str,
        nargs='*',
        help="Optional key-value pairs to pass to the application"
    )

    args = parser.parse_args()
    if args.verbose: #or args.server:
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    #if args.server:
    #    from app.server import run_server
    #    run_server()
    #    sys.exit(1) # not implemented yet

    if args.batch:
        batch_cfg = BatchConfig.from_json_file(args.workflow_file)
        batch_cfg.key_values = args.key_values
        run_batch(batch_cfg)
        sys.exit(0)
    # else normal workflow execution
    runner = WorkflowRunner(args.workflow_file, args.key_values)
    (main_status, main_result) = runner.run(AIAgentConfig())
    if main_status == Workflow.Status.SUCCESS:
        print(f"Workflow completed with SUCCESS\n\n---\n{main_result}")
        sys.exit(0)
    else:
        print(f"Workflow completed with FAILED\n\n---\n{main_result}")
        sys.exit(1)
