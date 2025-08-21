#!/bin/python
"""
AI CodeMentor - RESTful API Routing Endpoints
"""

import os
from flask import Flask, request, send_file
from app.api.files import register_file_routes
from app.api.workflow import register_workflow_routes
from app.api.log import register_log_routes
from app.api.auth import authorize, register_auth_routes
from app.api.frontend import register_frontend_routes

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

        # Register auth blueprint (adds /auth route)
        register_auth_routes(self.app)
        register_frontend_routes(self.app)

        # Standard utility routes
        self.app.add_url_rule("/health", "health_check", health_check)
        self.app.add_url_rule("/openapi.yaml", "openapi_spec", openapi_spec)

        # Domain specific routes
        register_file_routes(self.app)
        register_workflow_routes(self.app)
        register_log_routes(self.app)

        # Install *before_request* guard last so that every route is protected
        self.app.before_request(self._check_auth)


    def _check_auth(self):
        """
        Middleware function to check for authorization on all routes except health check.
        """
        # Whitelist unauthenticated paths (Swagger UI assets start with /docs/)
        whitelisted = [
            "/health",
            "/openapi.yaml",
            "/auth",
            "/docs",
            "/docs/",
            "/"
        ]
        if request.path in whitelisted or request.path.startswith("/docs/"):
            return None
        return authorize()
