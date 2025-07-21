#!/bin/python
"""
AI CodeMentor - RESTful API - Workflow Execution
"""
import logging
import os
from dotenv import load_dotenv
from flask import request, jsonify
from app.agents.agent_config import AIAgentConfig
from app.workflow.workflow_runner import WorkflowRunner
from app.workflow.workflow import Workflow

WORKFLOWS_DIR = os.getenv('WORKFLOWS_DIR', '../../workflows')


# Setup logging framework
if not logging.getLogger().hasHandlers():
    load_dotenv()
    logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                        format=os.getenv('LOGFORMAT', '%(message)s'))
logger = logging.getLogger(__name__)


def register_workflow_routes(app):
    """
    Register workflow execution routes with the Flask app.
    """
    @app.route("/api/workflow/<path:filepath>", methods=["GET"])
    def execute_workflow_get(filepath):
        dirpath = os.path.join(WORKFLOWS_DIR, os.path.dirname(filepath))
        filename = os.path.basename(filepath)
        full_path = os.path.join(dirpath, filename)
        logger.info("Execute: %s from %s", filepath, full_path)

        if os.path.exists(dirpath) and not os.path.isdir(full_path):
            key_values_dict = request.args.to_dict()
            logger.info("Parameters: %s", key_values_dict)
            runner = WorkflowRunner(full_path, key_values_dict)
            (main_status, main_result) = runner.run(AIAgentConfig())
            if main_status == Workflow.Status.SUCCESS:
                return main_result, 200
            else:
                return main_result, 500

        else:
            return "Error: Workflow not found", 404


    @app.route("/api/workflow/<path:filepath>", methods=["POST"])
    def execute_workflow_post(filepath):
        dirpath = os.path.join(WORKFLOWS_DIR, os.path.dirname(filepath))
        filename = os.path.basename(filepath)
        full_path = os.path.join(dirpath, filename)
        logger.info("Execute: %s from %s", filepath, full_path)

        if os.path.exists(dirpath) and not os.path.isdir(full_path):
            try:
                key_values_dict = request.get_json()
                logger.info("Parameters: %s", key_values_dict)
            except Exception:
                return jsonify({"error": "Invalid JSON"}), 400

            runner = WorkflowRunner(full_path, key_values_dict)
            (main_status, main_result) = runner.run(AIAgentConfig())
            if main_status == Workflow.Status.SUCCESS:
                return main_result, 200
            else:
                return main_result, 500
        else:
            return "Error: Workflow not found", 404
