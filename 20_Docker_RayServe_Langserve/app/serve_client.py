import requests
import json
import os

# The endpoint address and port are based on the default Ray Serve setup.
API_URL = "http://127.0.0.1:8000/ask"

# Define the question you want to ask the LLM
payload = {
    "query": "What is the world of genai like?"
}

print(f"Sending POST request to: {API_URL}")
print(f"Query: {payload['query']}")

try:
    # Send the POST request with the JSON payload
    response = requests.post(
        API_URL, 
        data=json.dumps(payload), 
        headers={'Content-Type': 'application/json'},
        timeout=30 # Add a timeout in case the LLM call takes time
    )

    # Check for a successful response (status code 200-299)
    response.raise_for_status() 

    # Parse the JSON response
    result = response.json()
    
    # Print the LLM's response
    print("\n--- LLM Response ---")
    print(result.get("response"))
    print("--------------------")

except requests.exceptions.ConnectionError:
    print("\nError: Could not connect to the server.")
    print("Please ensure 'rayservie_app.py' is running in a separate terminal.")
    print("The server must be active before running the client script.")

except requests.exceptions.RequestException as e:
    print(f"\nError processing request: {e}")

except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")