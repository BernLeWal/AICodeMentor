#!/bin/python
"""
RESTful API - File Management
"""

import logging
import os
from dotenv import load_dotenv
from flask import request, jsonify, send_from_directory

WORKFLOWS_DIR = os.getenv('WORKFLOWS_DIR', '../../workflows')


# Setup logging framework
if not logging.getLogger().hasHandlers():
    load_dotenv()
    logging.basicConfig(level=os.getenv('LOGLEVEL', 'INFO').upper(),
                        format=os.getenv('LOGFORMAT', '%(message)s'))
logger = logging.getLogger(__name__)


def register_file_routes(app):
    """
    Register file management routes with the Flask app.
    """
    @app.route("/api/files/", methods=["GET"])
    def list_files():
        entries = []
        # list all files and directories in the WORKFLOWS_DIR only
        # and not in the subdirectories
        for name in os.listdir(WORKFLOWS_DIR):
            path = os.path.join(WORKFLOWS_DIR, name)
            if os.path.isfile(path):
                entries.append({"name": name, "path": name, "type": "file"})
            elif os.path.isdir(path):
                entries.append({"name": name, "path": name, "type": "directory"})
        return jsonify(entries)

    @app.route("/api/files/<path:filepath>/", methods=["GET"])
    def retrieve_file(filepath):
        dirpath = os.path.join(WORKFLOWS_DIR, os.path.dirname(filepath))
        filename = os.path.basename(filepath)
        full_path = os.path.join(dirpath, filename)
        logger.info("Retrieve: %s from %s", filepath, full_path)

        # check if it is a file or a directory
        if not os.path.isdir(full_path):
            return send_from_directory(directory=os.path.abspath(dirpath),
                                       path=filename, as_attachment=True)
        else:
            subdir = filepath
            path = os.path.join(WORKFLOWS_DIR, subdir)
            if not os.path.exists(path):
                return jsonify({"error": "Directory not found"}), 404
            entries = [
                {"name": f, "path": os.path.join(subdir, f),
                "type": "file" if os.path.isfile(os.path.join(path, f)) else "directory"}
                for f in os.listdir(path)
            ]
            return jsonify(entries)


    @app.route("/api/files/<path:filepath>", methods=["POST", "PUT"])
    def create_file(filepath):
        dirpath = os.path.join(WORKFLOWS_DIR, os.path.dirname(filepath))
        filename = os.path.basename(filepath)
        full_path = os.path.join(dirpath, filename)
        logger.info("Upload: %s to %s", filepath, full_path)

        # check if it is a file or a directory
        if os.path.exists(dirpath) and not os.path.isdir(full_path):
            with open(full_path, "wb") as f:
                f.write(request.data)
            logger.info("Uploaded file: %s", filepath)
            return '', 201
        else:
            os.makedirs(dirpath, exist_ok=True)
            os.makedirs(full_path, exist_ok=True)
            logger.info("Created subdir: %s", filepath)
            return '', 201


    @app.route("/api/files/<path:filepath>", methods=["DELETE"])
    def delete_file(filepath):
        dirpath = os.path.join(WORKFLOWS_DIR, os.path.dirname(filepath))
        filename = os.path.basename(filepath)
        full_path = os.path.join(dirpath, filename)
        logger.info("Delete: %s from %s", filepath, full_path)

        # check if it is a file or a directory
        if os.path.exists(dirpath) and not os.path.isdir(full_path):
            try:
                os.remove(os.path.join(WORKFLOWS_DIR, filepath))
                logger.info("Deleted file: %s", filepath)
                return '', 200
            except FileNotFoundError:
                return jsonify({"error": "File not found"}), 404
        else:
            subdir = filepath
            try:
                os.rmdir(os.path.join(WORKFLOWS_DIR, subdir))
                logger.info("Deleted subdir: %s",subdir)
                return '', 200
            except FileNotFoundError:
                return jsonify({"error": "Directory not found"}), 404
            except OSError:
                return jsonify({"error": "Directory not empty"}), 400
