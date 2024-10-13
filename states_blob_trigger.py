# states_blob_trigger.py
import logging
import azure.functions as func

bp = func.Blueprint()

@bp.blob_trigger(arg_name="myblob", path="states/{state}/{name}", connection="STORAGE_CONNECTION")
def StatesBlobTrigger(myblob: func.InputStream):
    state = myblob.name.split('/')[1]
    
    logging.info(f"Python blob trigger function processed blob \n"
                 f"State: {state}\n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")
