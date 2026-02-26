#!/usr/bin/env python3
import json
import requests
import sys
from pathlib import Path

def ai_mistral_embeddings(args, context):
    """
    Generate embeddings using Mistral's API (v1) via REST requests.

    Accepts a single string. Stores the embedding.
    in context[set_context] (default: "prev"). Errors are stored in context[<set_name>_error].

    Optional context parameter:
        - MISTRAL_MODEL: override the embedding model (default: "mistral-embed")

    Args:
        args (list): args[0] must be a string.
        context (dict): may contain 'set_context' and 'MISTRAL_API_KEY'.

    Returns:
        int: 0 for success, -1 for failure
    """
    set_name = context.get("set_context", "prev")
    error_key = f"{set_name}_error"

    # Validate input
    if not args or args[0] is None:
        context[error_key] = "Usage: ai_mistral_embeddings <text>"
        return -1

    api_key = context.get("MISTRAL_API_KEY")
    if not api_key:
        context[error_key] = "Error: MISTRAL_API_KEY not found in context."
        return -1

    input_text = args[0]

    # Model selection
    model = context.get("MISTRAL_MODEL", "mistral-embed")
    endpoint = "https://api.mistral.ai/v1/embeddings"

    # Build payload (required fields only)
    payload = {
        "model": model,
        "input": input_text
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Send request
    try:
        response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
    except requests.RequestException as e:
        context[error_key] = f"Request error: {e}"
        return -1

    # Check HTTP response
    if response.status_code != 200:
        context[error_key] = f"API returned HTTP {response.status_code}: {response.text}"
        return -1

    # Parse response
    try:
        decoded = response.json()
        embeddings = [item.get("embedding") for item in decoded.get("data", [])]

        # Return single embedding if original input was a string
        if len(embeddings) == 1 and isinstance(args[0], str):
            context[set_name] = embeddings[0]
        else:
            context[set_name] = embeddings

        return 0
    except Exception as e:
        context[error_key] = f"Error parsing response: {e}"
        return -1


if __name__ == "__main__":
    # Expect first argument to be the path to a JSON file containing args/context
    if len(sys.argv) < 2:
        print("Usage: python ai_mistral_embeddings.py <data.json>")
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

    # Run embeddings
    result = ai_mistral_embeddings(args, context)
    set_name = context.get("set_context", "prev")

    # Print result or error
    if result == 0:
        print(context.get(set_name, ""))
    else:
        print(context.get(f"{set_name}_error", "Unknown error"))
