import azure.functions as func
import logging
import json
import helpers.web_scraper
import helpers.llm
import requests
from datetime import datetime, timezone
from typing import List, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator
from uuid import uuid4
bp = func.Blueprint()  # Create a new blueprint for the queue triggers

# Just a placeholder for simple web scraping/testing. Use Selenium for more complex scenarios with dynamic content.
def get_url_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful (status code 200)
        return response.text  # Return the content of the page
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


@bp.function_name(name="ReadFromQueue")
@bp.queue_trigger(arg_name="msg", queue_name="url-job-q", connection="STORAGE_CONNECTION")
@bp.queue_output(arg_name="outputQueueItem", queue_name="url-job-q", connection="STORAGE_CONNECTION")
@bp.cosmos_db_output(arg_name="documents", database_name="dfas", container_name="items", connection="COSMOS_DB_CONNECTION", create_if_not_exists=False)
def read_from_queue(msg: func.QueueMessage, outputQueueItem: func.Out[str], documents: func.Out[func.Document]):
    """
    This function is triggered when a message is added to the 'url-job-q' queue.
    It logs the payload of the message.
    
    Parameters:
        - msg: The queue message received from the 'url-job-q' queue.
    """
    logging.info(f"Queue trigger function processed a message: {msg.get_body().decode('utf-8')}")
    response, json_response, pydantic_response = None, None, None

    # Parse the message if it's a JSON string and log the fields
    try:
        payload = json.loads(msg.get_body().decode('utf-8'))
        logging.info(f"Parsed message: State = {payload['state']}, URL = {payload['url']}, Created at = {payload['created_at']}, Depth = {payload['depth']}")
        
        """
        No longer needed. Superceded by getting Body content and URLs in one go, below.
        logging.info(f"Scrapping URL: {payload['url']}")
        page_content = helpers.web_scraper.WebScraper().scrape_url(payload['url'])
        logging.info(f"Scraped content length: {len(page_content)}")    
        """
        logging.info(f"Scraped Content AND URLs...")    

        body, urls = None, []
        if payload['depth'] == 0:
            body, urls = helpers.web_scraper.WebScraper().scrape_url_and_extract_links(payload['url'])
            
            # Call LLM API with the scraped content
            response, json_response, pydantic_response = helpers.llm.call_llm_api(body, payload['state'])
            logging.info(f"LLM Response: {response}")

            cosmos_dict = {
                "id": str(uuid4()),
                "state": payload["state"],
                "url": payload["url"],
                "created_at": payload["created_at"],
                "depth": payload["depth"],
                "llm_response": json_response,
                "scraped_urls": payload['url']
            }
            # Prepare the document for Cosmos DB
            logging.info(f"Document being sent to Cosmos DB: {json.dumps(cosmos_dict, indent=2)}")
            documents.set(func.Document.from_dict(cosmos_dict))
            logging.info("Document stored in Cosmos DB successfully.")
            
            # Iterate through each URL and add it to the queue as well, but at Depth=1
            n = 0
            if len(urls) > 1:
                for url in urls:
                    n += 1
                    queue_item = {
                        "state": payload['state'],
                        "url": "",
                        "created_at": datetime.utcnow().isoformat(),
                        "depth": 1  # Max depth level
                    }
                    # outputQueueItem.set(json.dumps(queue_item)) # Uncomment this line to add URLs to the queue!
                logging.info(f"Processed {n} URLs and added them to the queue.")
        else:
            body = get_url_content(payload['url'])
            response, json_response, pydantic_response = llm.call_llm_api(body)
            logging.info(f"LLM Response: {response}")

        if hasattr(response, 'usage'):
            log_usage_tokens(response.usage.total_tokens, response.usage.completion_tokens, response.usage.total_tokens)

        
        logging.info(f"# of Scraped Links: {len(urls)}")

    except json.JSONDecodeError as e:
        logging.error(f"Error decoding message: {str(e)}")



def log_usage_tokens(prompt_tokens: int, completion_tokens: int, total_tokens: int):
    """
    Log the usage tokens for a given LLM API call.
    
    Parameters:
        - prompt_tokens: The number of tokens used for the prompt.
        - completion_tokens: The number of tokens used for the completion.
        - total_tokens: The total number of tokens used.
    """
    logging.info(f"Tokens used: {total_tokens}, Input tokens: {prompt_tokens}, Output tokens: {completion_tokens}")



"""
Use this function if you want to peek at messages in the queue without deleting them.

@bp.function_name(name="PeekQueueMessages")
def peek_queue_messages(req: func.HttpRequest) -> func.HttpResponse:

    #Azure Function that peeks at messages from the Azure Storage Queue 'url-job-q' without deleting them.
    
    #Parameters:
    #    - req: The HTTP request that triggers this function.

    #Returns:
    #    - HttpResponse with a status message.

    try:
        # Connect to the Azure Queue
        queue_client = QueueClient.from_connection_string(STORAGE_CONNECTION_STRING, queue_name=QUEUE_NAME)

        # Peek at the top 10 messages in the queue (you can customize max_messages)
        peeked_messages = queue_client.peek_messages(max_messages=10)

        if not peeked_messages:
            logging.info("No messages to peek at in the queue.")
            return func.HttpResponse("No messages found in the queue.", status_code=200)

        # Log each peeked message
        for message in peeked_messages:
            logging.info(f"Peeked message: {message.content}")

            # Try to parse the message as JSON and log the fields if applicable
            try:
                payload = json.loads(message.content)
                logging.info(f"Parsed message: State = {payload['state']}, URL = {payload['url']}, Created at = {payload['created_at']}")
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding message: {str(e)}")

        return func.HttpResponse(f"Peeked {len(peeked_messages)} message(s) from the queue.", status_code=200)

    except Exception as e:
        logging.error(f"Error while peeking messages from the queue: {str(e)}")
        return func.HttpResponse(f"Failed to peek messages: {str(e)}", status_code=500)
"""