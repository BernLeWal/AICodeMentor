#!/bin/python
"""
AI CodeMentor - RESTful API
automatically analyse, feedback and grade source-code project submissions using AI agents
"""

import logging
import os
import sys
from dotenv import load_dotenv
from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint
from app.api.routing import ApiRouter


class AICodeMentorServer:
    """
    Main server class for the AI CodeMentor application.
    This class initializes the Flask application, configures logging,
    and registers API routes.
    """
    def __init__(self):
        self.app = Flask(__name__)
        self.configure_logging()
        self.register_routes()
        self.register_swagger_ui()

    def configure_logging(self):
        """
        Configure logging for the application.
        It sets the logging level and format based on environment variables.
        If no handlers are set, it initializes the logging configuration.
        """
        if not logging.getLogger().hasHandlers():
            load_dotenv()
            logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                                format=os.getenv('LOGFORMAT', '%(message)s'))
            logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
        logging.info("Logging is configured.")

    def register_routes(self):
        """
        Register all API routes with the Flask application.
        This method sets up the routing for the application, including
        health check and file management routes.
        """
        ApiRouter(self.app)

    def register_swagger_ui(self):
        """
        Register Swagger UI for API documentation.
        This method sets up the Swagger UI blueprint and registers it
        with the Flask application.
        """
        swaggerui_blueprint = get_swaggerui_blueprint(
            '/docs',
            '/openapi.yaml',
            config={'app_name': "AICodeMentor API"}
        )
        self.app.register_blueprint(swaggerui_blueprint, url_prefix='/docs')

    def run(self, host="0.0.0.0", port=5000):
        """
        Run the Flask application.
        """
        logging.info("Starting AICodeMentor server on %s:%d", host,port)
        self.app.run(host=host, port=port)


if __name__ == '__main__':
    server = AICodeMentorServer()
    server.run()
