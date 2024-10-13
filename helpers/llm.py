from openai import OpenAI, AzureOpenAI
from azure.identity import DefaultAzureCredential
import openai
import argparse
import os
import json
import logging
from typing import List, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Pydantic Classes
class TaxChange(BaseModel):
    """
    Represents a single tax law change.
    """
    state: str
    category: str
    subcategory: str
    rationale: str
    confidence: int
    is_match: bool
    created_at: Optional[str] = None

    @field_validator('created_at', mode='before')
    @classmethod
    def set_created_at(cls, v: Any) -> str:
        """
        Set the created_at field to the current UTC time if it's empty.
        """
        return datetime.now(timezone.utc).isoformat() if v == '' else v

class TaxChangeResponse(BaseModel):
    """
    Represents a collection of tax law changes.
    """
    changes: List[TaxChange]

def get_pydantic_function_signature():
    # Dynamically generate the schema from the Pydantic model
    schema = TaxChange.model_json_schema()

    # Return the function signature with the generated schema
    return {
        "name": "extract_tax_changes",
        "description": "Extracts tax law changes from a provided context.",
        "parameters": schema
    }



# Read the prompt file and return the content
def read_prompt_file(prompt_file: str = "llm_prompt.md") -> str:
    script_dir = os.path.dirname(__file__)  # Get the directory of the script
    file_path = os.path.join(script_dir, prompt_file)  # Construct the full path to the prompt file
    with open(file_path, "r") as file:
        return file.read()


def initialize_clients():
    use_azure = os.getenv("USE_AZURE_OPENAI", "false").lower() == "true"
    logger.info(f"Using Azure OpenAI: {use_azure}")

    if use_azure:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
    else:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    return client


def call_llm_api(prompt_text: str, state: str, model: str = None):
    """
    Calls the LLM API with a given prompt and model, and returns the response in three formats.
    
    Parameters:
        prompt_text (str): The prompt text to send to the API.
        state (str): The State for which the tax changes are being requested.
        model (str): The model to use. If None, will default to the environment model.
    
    Returns:
        tuple: A tuple containing:
            - raw_response (str): The raw response from the API.
            - json_response (dict): The response parsed as JSON.
            - pydantic_response (TaxChangeResponse): The response parsed into the Pydantic model.
    """
    client = initialize_clients()
    model = model if model is not None else os.getenv("LLM_MODEL")

    prompt_file_text = read_prompt_file()  # Get the prompt text from the file
    prompt = prompt_file_text.replace("{state}", state)
    prompt = prompt_file_text.replace("{context}", prompt_text)
    #prompt = f"{prompt_file_text}\n\n--------\nCONTEXT:\n\n{prompt_text}"  # Set up the prompt

    try:
        # AOAI call uses the model from the deployment specified in the .env file
        if isinstance(client, AzureOpenAI):
            response = client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.0
            )
        else:
            # OpenAI call uses the model param passed in
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.0
            )

        raw_response = response.choices[0].text if hasattr(response.choices[0], 'text') else response.choices[0].message.content
        # Clean the response content if required (assuming JSON is returned as a formatted string)
        json_response = json.loads(raw_response.strip('```json\n').strip('\n```'))
        
        # Parse the JSON response into a Pydantic model
        pydantic_response = TaxChangeResponse(changes=[TaxChange(**item) for item in json_response])

        # Return all three: raw response, JSON response, and Pydantic object
        return raw_response, json_response, pydantic_response

    except Exception as e:
        print(f"An error occurred: {e}")
        raise




    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        exit(1)