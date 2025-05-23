#!/bin/python
"""
RESTful API Authentication
"""

import os
from flask import request, jsonify

def authorize():
    """
    Middleware function to check for a valid token in the request headers.
    If the token is missing or invalid, return a 401 Unauthorized response.
    """
    token = request.headers.get("Authorization")
    expected_token = f"Bearer {os.getenv('SERVER_TOKEN', '')}"
    if token != expected_token:
        return jsonify({"error": "Unauthorized"}), 401
    return None
