#!/bin/python
"""
AI CodeMentor - RESTful API Routing Endpoints
"""

import os
from flask import Flask, request, send_file
from app.api.files import register_file_routes
from app.api.workflow import register_workflow_routes
from app.api.auth import authorize

def health_check():
    """
    Health check endpoint to verify the server is running.
    """
    return {"status": "ok"}, 200

def openapi_spec():
    """
    Endpoint to serve the OpenAPI specification file.
    This file is used for API documentation and client generation.
    """
    spec_path = os.path.join(os.path.dirname(__file__), 'openapi.yaml')
    return send_file(spec_path, mimetype='application/yaml')


class ApiRouter:
    """
    API Router class to register all routes for the Flask application.
    """
    def __init__(self, app: Flask):
        self.app = app
        self.register_all_routes()

    def register_all_routes(self):
        """
        Register all API routes with the Flask app.
        """
        self.app.before_request(self.check_auth)
        self.app.add_url_rule("/health", "health_check", health_check)
        self.app.add_url_rule("/openapi.yaml", "openapi_spec", openapi_spec)
        register_file_routes(self.app)
        register_workflow_routes(self.app)

    def check_auth(self):
        """
        Middleware function to check for authorization on all routes except health check.
        """
        if request.path in ["/health", "/openapi.yaml", "/docs", "/docs/"] or request.path.startswith("/docs/"):
            return None
        return authorize()
