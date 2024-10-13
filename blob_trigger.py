import azure.functions as func
import logging
from datetime import datetime
import json
from uuid import uuid4
import fitz
import os
import helpers.llm

bp = func.Blueprint()  # Create a blueprint

# Define the queue name
QUEUE_NAME = "url-job-q"

@bp.function_name(name="states_blob_log_trigger")
@bp.blob_trigger(arg_name="myblob", path="states/{state}/{name}", connection="STORAGE_CONNECTION")
def states_blob_trigger(myblob: func.InputStream):
    state = myblob.name.split('/')[1]
    
    logging.info(f"Python blob trigger function processed blob \n"
                 f"State: {state}\n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")


"""

# Reads a blob from the 'state's container, assuming each line is a URL, and adds each URL to the queue
@bp.function_name(name="Blob_To_Q_Trigger")
@bp.blob_trigger(arg_name="myblob", path="states/{state}/{name}", connection="STORAGE_CONNECTION")
@bp.queue_output(arg_name="outputQueueItem", queue_name=QUEUE_NAME, connection="STORAGE_CONNECTION")
def queue_blob_trigger(myblob: func.InputStream, outputQueueItem: func.Out[str]):
    # Extract state and name from the blob path inside the function
    state = myblob.name.split('/')[1]
    name = myblob.name.split('/')[2]  # Assuming the blob name comes after the state

    # Log the info
    logging.info(f"Blob trigger processed blob\nState: {state}\nName: {name}\nBlob Size: {myblob.length} bytes")

    content = myblob.read().decode('utf-8')
    lines = content.splitlines()

    # Prepare the messages to send to the queue
    for line in lines:
        queue_item = {
            "state": state,
            "url": line.strip(),
            "created_at": datetime.utcnow().isoformat(),
            "depth": 0  # Initial depth level
        }
        outputQueueItem.set(json.dumps(queue_item))
    
    logging.info(f"Processed {len(lines)} URLs and added them to the queue.")

"""


@bp.function_name(name="Blob_LLM_Trigger")
@bp.blob_trigger(arg_name="myblob", path="states/{state}/{name}", connection="STORAGE_CONNECTION")
@bp.queue_output(arg_name="outputQueueItem", queue_name=QUEUE_NAME, connection="STORAGE_CONNECTION")
@bp.cosmos_db_output(arg_name="documents", database_name="dfas", container_name="items", connection="COSMOS_DB_CONNECTION", create_if_not_exists=False)
def blob_llm_trigger(myblob: func.InputStream, outputQueueItem: func.Out[str], documents: func.Out[func.Document]):
    content = ""
    # Extract state and name from the blob path inside the function
    state = myblob.name.split('/')[1]
    name = myblob.name.split('/')[2]  # Assuming the blob name comes after the state
    extension = os.path.splitext(name)[1].lower()

    # Log the info
    logging.info(f"Blob trigger processed blob\nState: {state}\nName: {name}\nBlob Size: {myblob.length} bytes")

    if extension in ['.txt', '.md']:
        # Read blob content only for text or markdown files
        content = myblob.read().decode('utf-8')
    elif extension == '.pdf':
        # Handle PDF files using PyMuPDF (Fitz)
        with fitz.open(stream=myblob.read(), filetype="pdf") as pdf_document:
            for page_number in range(pdf_document.page_count):
                page = pdf_document.load_page(page_number)
                content += page.get_text()

    response, json_response, pydantic_response = helpers.llm.call_llm_api(content, state)

    cosmos_dict = {
        "id": str(uuid4()),
        "state": state,
        "url": f"blob: {myblob.name}",
        "created_at": datetime.utcnow().isoformat(),
        "depth": "",
        "llm_response": json_response,
        "scraped_urls": ""
    }
            
    # Prepare the document for Cosmos DB
    logging.info(f"Document being sent to Cosmos DB: {json.dumps(cosmos_dict, indent=2)}")
    documents.set(func.Document.from_dict(cosmos_dict))

    
    logging.info(f"Completed processing blob '{name}' for state '{state}' and added to Cosmos DB.")


"""
@app.blob_trigger(arg_name="myblob", path="states/{state}/{name}", connection="STORAGE_CONNECTION")
def queue_blob_trigger(myblob: func.InputStream):
    state = myblob.name.split('/')[1]

    content = myblob.read().decode('utf-8') # Read the entire blob content
    lines = content.splitlines() # Split content into lines
    
    # Connect to the Azure Queue
    queue_client = QueueClient.from_connection_string(
        conn_str=os.getenv("STORAGE_CONNECTION"),
        queue_name=QUEUE_NAME
    )
    
    # Process each line and add to queue
    for line in lines:
        # Create JSON payload
        queue_item = {
            "state": state,
            "url": line.strip(),  # Ensure no extra spaces
            "created_at": datetime.utcnow().isoformat()
        }
    
        queue_message = json.dumps(queue_item) # Convert payload to JSON string
        queue_client.send_message(queue_message) # Add message to the queue
        logging.info(f"Added message to queue: {queue_message}") # Log the creation of the queue item
    
    logging.info(f"Processed blob and added {len(lines)} messages to queue '{QUEUE_NAME}'")
"""