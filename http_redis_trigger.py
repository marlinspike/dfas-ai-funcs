import azure.functions as func
import logging
from datetime import datetime
import json
import redis
import os
import helpers.redis_handler as rh

bp = func.Blueprint()  # Create a blueprint


# Define the queue name
QUEUE_NAME = "url-job-q"

@bp.function_name(name="http_redis_trigger")
@bp.route(route="redis", methods=["GET","POST","PUT", "DELETE"])
def redis_trigger(req: func.HttpRequest) -> func.HttpResponse:

    # Extract the state and name from the request body
    
    # Log the info
    logging.info(f"Redis Request Received!")
    keys = rh.list_all_keys()
    logging.info(f"Keys: {keys}")

    try:
        retrieved_data = rh.get_data('web_resources')
        parsed_data = json.loads(retrieved_data)

        for resource in parsed_data['resources']:
            print(f"Name: {resource['name']}, URL: {resource['url']}")
    except Exception as e:
        logging.error(f"Error retrieving data from Redis: {str(e)}")
    
    return func.HttpResponse("Redis Request Received!", status_code=200)