# function_app.py
import azure.functions as func
#import logging
#from azure.storage.queue import QueueClient
#import os
#from datetime import datetime
#import json
#import blob_trigger, queue_triggers, http_redis_trigger

# Define the queue name
QUEUE_NAME = "url-job-q"
app = func.FunctionApp()


# Register the blob triggers from blob_trigger.py
# app.register_functions(blob_trigger.bp)
# app.register_functions(queue_triggers.bp)
# app.register_functions(http_redis_trigger.bp)


# Test if app is recognized by logging a message
@app.route(route="hello", methods=["GET","POST","PUT", "DELETE"])
def hello_function(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "POST":
        return func.HttpResponse("Hello from FunctionApp! (POST)", status_code=200)
    elif req.method == "GET":
        return func.HttpResponse("Hello from FunctionApp! (GET)", status_code=200)
    elif req.method == "PUT":
        return func.HttpResponse("Hello from FunctionApp! (PUT)", status_code=200)
    elif req.method == "DELETE":
        return func.HttpResponse("Hello from FunctionApp! (DELETE)", status_code=200)
    else:
        return func.HttpResponse("Hello from FunctionApp!", status_code=200)


