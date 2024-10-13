import redis
import json
import os
from dotenv import load_dotenv

# Get the Redis connection details from environment variables
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6380))  # Default to 6380 for SSL connections
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Connect to Redis using host, port, and password
redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    ssl=True  # Use SSL for Azure Redis connections
)


# List all keys
def list_all_keys():
    try:
        keys = redis_client.keys('*')
        if keys:
            return [key.decode('utf-8') for key in keys]  # Decode from bytes to string
        else:
            print("No keys found.")
    except redis.RedisError as error:
        print(f"Error listing keys: {error}")


# Store data in Redis
def store_data(key, value):
    try:
        # Convert the value to a string (JSON) and store in Redis
        redis_client.set(key, json.dumps(value))
        print(f"Data stored successfully with key: {key}")
    except redis.RedisError as error:
        print(f"Error storing data in Redis: {error}")

# Retrieve data from Redis
def get_data(key):
    try:
        # Retrieve the data from Redis
        value = redis_client.get(key)
        if value:
            # Deserialize the stored JSON string back to a Python object
            return value.decode("utf-8")
        else:
            print(f"No data found for key: {key}")
            return None
    except redis.RedisError as error:
        print(f"Error retrieving data from Redis: {error}")
        return None