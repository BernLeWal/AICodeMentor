#!/bin/python
"""
WorkflowRunner class to run the AI CodeMentor Workflow
"""

import datetime
import os
from app.workflow.workflow import Workflow
from app.workflow.workflow_reader import WorkflowReader
from app.workflow.workflow_writer import WorkflowWriter
from app.workflow.interpreter import WorkflowInterpreter
from app.workflow.context import Context
from app.workflow.batch_config import BatchConfig
from app.agents.agent_factory import AIAgentFactory
from app.commands.shell_executor import ShellCommandExecutor
from app.agents.agent_config import AIAgentConfig


class WorkflowRunner:
    """
    WorkflowRunner class to run the AI CodeMentor Workflow
    """
    def __init__(self, workflow_file, key_values):
        self.workflow_file = workflow_file
        self.key_values = key_values

        # export stats as csv-file
        self.csv_file = None
        self.results_dir = None
        self.counter = 1

        # recorded run stats
        self.start_time = None
        self.duration_sec = 0

        self.context:Context = None


    def run(self, config:AIAgentConfig) -> tuple[Workflow.Status, str]:
        """
        Run the AI CodeMentor Workflow
        """
        self.start_time = datetime.datetime.now()
        main_workflow = WorkflowReader().load_from_mdfile(self.workflow_file, ".")
        print(f"Running workflow: {main_workflow.name} (from file {main_workflow.filepath}) "+\
            f"using AI-model {AIAgentConfig.get_model_name()} ")
        if self.key_values:
            print("with parameters:")
            for kv in self.key_values:
                key, value = kv.split("=")
                print(f"  - {key}={value}\n")
                main_workflow.params[key] = value

        main_interpreter = WorkflowInterpreter(main_workflow)

        ## run the workflow
        self.context = Context(main_workflow,
                               AIAgentFactory.create_agent(config),
                               ShellCommandExecutor())
        results = main_interpreter.run(self.context)
        self.duration_sec = (datetime.datetime.now() - self.start_time).total_seconds()
        return results


    def get_agent(self):
        """Returns the agent used in the workflow"""
        if not self.context:
            return None
        return self.context.agent


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

            self.results_dir = os.path.join(directory, csv_file_name.replace(".csv","_results"))
            if not os.path.exists(self.results_dir):
                os.makedirs(self.results_dir)

        if not os.path.exists(self.csv_file):
            with open(self.csv_file, "w", encoding="utf-8") as f:
                f.write("nr;sourcefile;"+\
                        "cfg_model;cfg_temperature;cfg_top_p;cfg_f_penalty;cfg_p_penalty;"+\
                        "run_timestamp;run_duration_sec;" +\
                        "result_status;result_file;result_length;"+\
                        "total_duration_sec;total_iterations;"+\
                        "total_prompt_tokens;total_completion_tokens;total_tokens;"+\
                        "total_prompt_chars;total_completion_chars;total_chars;"+\
                        "score_result_length;score_result_facts\n")
        else:
            with open(self.csv_file, "r", encoding="utf-8") as f:
                self.counter = len(f.readlines())

        return self.csv_file


    def write_stats_to_csv(self, results:tuple[Workflow.Status, str],
                       cfg:BatchConfig):
        """Scores the workflow results and writes to a CSV file"""
        csv_file_from = cfg.config_file if cfg.config_file is not None else self.workflow_file
        self.open_csv_file(csv_file_from)

        with open(self.csv_file, "a", encoding="utf-8") as f:
            f.write(f"{self.counter};"+\
                    f"{self.workflow_file};")

            # Data of configuration
            agent = self.get_agent()
            if agent is not None:
                f.write(f"{agent.model_name};"+\
                        f"{agent.temperature};"+\
                        f"{agent.top_p};"+\
                        f"{agent.frequency_penalty};"+\
                        f"{agent.presence_penalty};")
            else:
                f.write(";;;;;")

            # Data of workflow run
            result_status, result_content  = results
            timestamp = self.start_time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp};"+\
                    f"{self.duration_sec};")

            # Data of results
            f.write(f"{result_status};")
            result_file_name = os.path.join(self.results_dir,
                                            f"{self.counter}__{agent.model_name}.md")
            with open(result_file_name, "w", encoding="utf-8") as rf:
                rf.write(result_content)
            f.write(f"{os.path.basename(result_file_name)};"+\
                    f"{len(result_content)};")

            if agent is not None:
                f.write(f"{agent.total_duration_sec};"+\
                        f"{agent.total_iterations};")
                f.write(f"{agent.total_prompt_tokens if agent.total_prompt_tokens is not None else ""};"+\
                        f"{agent.total_completion_tokens if agent.total_completion_tokens is not None else ""};"+\
                        f"{agent.total_tokens if agent.total_tokens is not None else ""};")
                f.write(f"{agent.total_prompt_chars};"+\
                        f"{agent.total_completion_chars};"+\
                        f"{agent.total_chars};")
            else:
                f.write(";;;;;;;;")

            # Scoring
            content_length_score = cfg.score_result_length(result_content)
            f.write(f"{content_length_score};")
            content_items_score = cfg.score_result_facts(result_content)
            f.write(f"{content_items_score};")

            f.write("\n")
            f.flush()
            self.counter += 1
