#!/usr/bin/env python3
import json
import requests
import sys
from pathlib import Path

def mistral_moderations(args, context):
    """
    Moderate text using Mistral Moderation API.

    Accepts a single string in args[0]. Stores the result in context[set_context]
    (default: "prev"). Errors are stored in context[<set_name>_error].

    Optional context parameter:
        - MISTRAL_MODERATION_MODEL: override the default model (default: "mistral-moderation-latest")

    Args:
        args (list): [input_text]
        context (dict): may contain 'set_context' and 'MISTRAL_API_KEY'

    Returns:
        int: 0 for success, -1 for failure
    """
    set_name = context.get("set_context", "prev")
    error_key = f"{set_name}_error"

    # Validate input
    if not args or args[0] is None:
        context[f"{set_name}_usage"] = {
            "description": "Moderate text using Mistral Moderation API",
            "args": ["input_text (required) - Text to moderate"],
            "context": [
                "MISTRAL_API_KEY: The API key for accessing the Mistral API",
                "MISTRAL_MODERATION_MODEL: (optional) Model to use (default: mistral-moderation-latest)"
            ],
            "example": 'mistral_moderations(["This is some text to moderate"], context)'
        }
        return -1

    api_key = context.get("MISTRAL_API_KEY")
    if not api_key:
        context[error_key] = "Error: MISTRAL_API_KEY is not set in context"
        return -1

    input_text = args[0]
    model = context.get("MISTRAL_MODERATION_MODEL", "mistral-moderation-latest")
    endpoint = "https://api.mistral.ai/v1/moderations"

    payload = {
        "input": input_text,
        "model": model
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Send request
    try:
        response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
    except requests.RequestException as e:
        context[error_key] = f"Request failed: {e}"
        return -1

    # Check HTTP response
    if response.status_code != 200:
        context[error_key] = f"API returned HTTP {response.status_code}: {response.text}"
        return -1

    # Parse response
    try:
        result = response.json()
        context[set_name] = result
        return 0
    except Exception as e:
        context[error_key] = f"Error parsing response: {e}"
        return -1


if __name__ == "__main__":
    # Expect first argument to be the path to a JSON file containing args/context
    if len(sys.argv) < 2:
        print("Usage: python mistral_moderations.py <data.json>")
        sys.exit(1)

    data_file = Path(sys.argv[1])
    if not data_file.exists():
        print(f"Error: JSON file '{data_file}' not found.")
        sys.exit(1)

    # Load JSON file
    with data_file.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing {data_file}: {e}")
            sys.exit(1)

    args = data.get("args", [])
    context = data.get("context", {})

    # Run moderation
    result = mistral_moderations(args, context)
    set_name = context.get("set_context", "prev")

    # Print result or error
    if result == 0:
        print(json.dumps(context.get(set_name, {}), indent=2))
    else:
        print(context.get(f"{set_name}_error", "Unknown error"))
