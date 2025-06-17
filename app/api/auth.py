#!/bin/python
"""
RESTFul API Authentication helpers & routes (cookie + bearer header).
"""
import os
from typing import Optional

from flask import request, jsonify, Blueprint, make_response, Response

_SERVER_TOKEN: str = os.getenv("SERVER_TOKEN", "")


# --------------------------- low‑level helper ---------------------------------

def _extract_token() -> Optional[str]:
    """Return token from *Authorization* header or *auth_token* cookie (if present)."""
    # 1) Bearer header takes precedence
    hdr: Optional[str] = request.headers.get("Authorization")
    if hdr and hdr.startswith("Bearer "):
        return hdr.split(" ", 1)[1]

    # 2) Fallback to cookie
    return request.cookies.get("auth_token")


# --------------------------- middleware‑style check ---------------------------

def authorize() -> Optional[Response]:
    """
    Flask *before_request* hook. Returns a response *iff* the call is **unauthorised**.
    """
    token: Optional[str] = _extract_token()
    if token == _SERVER_TOKEN:
        return None  # authorised
    return jsonify({"error": "Unauthorized"}), 401


# --------------------------- /auth endpoint ----------------------------------

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/auth", methods=["GET"])
def login():
    """Simple login endpoint.

    Usage (once per browser session):
        GET /auth?token=<SERVER_TOKEN>

    On success a **Secure, HttpOnly, SameSite=Strict** cookie named ``auth_token`` is
    returned so that subsequent requests through the browser will be authenticated.
    """
    supplied = request.args.get("token") or _extract_token()
    if supplied != _SERVER_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    resp = make_response(jsonify({"status": "logged‑in"}))

    # In dev we may not use HTTPS; ``secure`` is therefore conditional.
    resp.set_cookie(
        "auth_token",
        _SERVER_TOKEN,
        httponly=True,
        samesite="Strict",
        secure=request.scheme == "https",  # only mark Secure on HTTPS
    )
    return resp


# ------------- helper to register blueprint from outside ---------------------

def register_auth_routes(app):
    """Register the authentication routes with the Flask app."""
    app.register_blueprint(auth_bp)
