#!/bin/python
"""
Configuration for the AI CodeMentor Batch-Processing Engine
"""
import os
import logging
from dotenv import load_dotenv
from app.workflow.batch_config import BatchConfig
from app.agents.agent_config import AIAgentConfig
from app.workflow.workflow_runner import WorkflowRunner


load_dotenv()

# Setup logging framework
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                        format=os.getenv('LOGFORMAT', '%(message)s'))
logger = logging.getLogger(__name__)


class BatchRunner:
    """Batch runner for the AI CodeMentor Batch-Processing Engine"""
    def __init__(self, cfg: BatchConfig):
        self.cfg = cfg


    def run_workflow(self, workflow_file:str, key_values:dict, agent_config:AIAgentConfig):
        """Runs a workflow and collects benchmarking data"""
        workflow_runner = WorkflowRunner(workflow_file, key_values)

        # Run the workflow
        results = workflow_runner.run(agent_config)

        # Add the benchmark results to a CSV file
        workflow_runner.write_stats_to_csv(results, self.cfg)


    def run_workflow_configs(self, workflow_file: str):
        """Runs a workflow in all config variations"""

        for _ in range(self.cfg.repeats):
            for model_name in self.cfg.ai_model_names or [AIAgentConfig.get_model_name()]:
                logger.info("- Running benchmark for model: %s", model_name)
                os.environ['AI_MODEL_NAME'] = model_name

                for temp in self.cfg.ai_temperature_values or [AIAgentConfig.get_temperature()]:
                    os.environ['AI_TEMPERATURE'] = str(temp)

                    for top_p in self.cfg.ai_top_p_values or [AIAgentConfig.get_top_p()]:
                        os.environ['AI_TOP_P'] = str(top_p)

                        for f_penalty in self.cfg.ai_f_penalty_values or [AIAgentConfig.get_frequency_penalty()]:
                            os.environ['AI_FREQUENCY_PENALTY'] = str(f_penalty)

                            for p_penalty in self.cfg.ai_p_penalty_values or [AIAgentConfig.get_presence_penalty()]:
                                os.environ['AI_PRESENCE_PENALTY'] = str(p_penalty)

                                ac = AIAgentConfig(model_name)
                                if isinstance(self.cfg.key_values, list):
                                    for key_values in self.cfg.key_values:
                                        self.run_workflow(workflow_file, key_values, ac)
                                else:
                                    self.run_workflow(workflow_file, self.cfg.key_values, ac)


    def run(self):
        """Runs a batch of workflows and collects benchmarking data"""
        main_key_values = {}
        if isinstance(self.cfg.key_values, list) and len(self.cfg.key_values) > 0:
            main_key_values = self.cfg.key_values[0]
        else:
            main_key_values = self.cfg.key_values

        if self.cfg.setup_workflow_file is not None:
            logger.info("Setting up the environment...")
            WorkflowRunner(self.cfg.setup_workflow_file, main_key_values).run(AIAgentConfig())

        if self.cfg.workflow_files is None:
            logger.error("No workflow files given!")
            return
        # if workflow_files is a list of string then process all files each
        if isinstance(self.cfg.workflow_files, list):
            for workflow_file in self.cfg.workflow_files:
                self.run_workflow_configs(workflow_file)
        else:
            self.run_workflow_configs(self.cfg.workflow_files)

        if self.cfg.cleanup_workflow_file is not None:
            logger.info("Cleaning up the environment...")
            load_dotenv()   # reload the environment variables
            WorkflowRunner(self.cfg.cleanup_workflow_file, main_key_values).run(AIAgentConfig())
