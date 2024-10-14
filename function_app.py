# function_app.py
import azure.functions as func
import logging

from azure.storage.queue import QueueClient

import os
from datetime import datetime
import json
import blob_trigger, queue_triggers, http_redis_trigger

# Define the queue name
QUEUE_NAME = "url-job-q"
app = func.FunctionApp()


# Register the blob triggers from blob_trigger.py
app.register_functions(blob_trigger.bp)
app.register_functions(queue_triggers.bp)
app.register_functions(http_redis_trigger.bp)

# Test if app is recognized by logging a message
@app.route(route="hello_world", methods=["GET", "POST", "PUT", "DELETE"])
def hello_world(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = None
        if req_body:
            name = req_body.get('name')

    if name:
        message = f"Hello {name}! Hello from FunctionApp!"
    else:
        message = "Hello from FunctionApp, stranger!"

    if req.method == "POST":
        return func.HttpResponse(f"{message} (POST)", status_code=200)
    elif req.method == "GET":
        return func.HttpResponse(f"{message} (GET)", status_code=200)
    elif req.method == "PUT":
        return func.HttpResponse(f"{message} (PUT)", status_code=200)
    elif req.method == "DELETE":
        return func.HttpResponse(f"{message} (DELETE)", status_code=200)
    else:
        return func.HttpResponse(message, status_code=200)

