#!/usr/bin/env python3
import json
import requests
import sys
from pathlib import Path

def ai_mistral_text(args, context):
    """
    Generate text using Mistral Chat Completion with context and arguments.

    :param args: list of arguments [prompt, reasoning_effort (optional)]
    :param context: dict containing API key, system prompt, and storage
    :return: int (0 on success, 1 on error)
    """
    set_name = context.get("set_context", "prev")
    error_key = f"{set_name}_error"

    if not args:
        context[error_key] = (
            "Usage: ai_mistral_text <prompt> [reasoning_effort]\n"
            "ai_mistral_text:\n"
            "    args:\n"
            "        - prompt\n"
            "        - reasoning_effort (optional) // High; defaults to None\n"
            "    context:\n"
            "        - MISTRAL_API_KEY: The API key for accessing the Mistral API.\n"
            "        - SYSTEM_PROMPT: The system prompt to be used in the API call.\n"
            "        - MISTRAL_MODEL: Optional custom model to use.\n"
            "        - MISTRAL_MESSAGES: Optional fully custom message list.\n"
            "        - MISTRAL_TEMPERATURE: Optional float (0.0–2.0) for sampling randomness.\n"
            "        - MISTRAL_K: Optional int for top-k sampling.\n"
        )
        return 1

    api_key = context.get('MISTRAL_API_KEY')
    if not api_key:
        context[error_key] = "Error: MISTRAL_API_KEY is not set in context."
        return 1

    prompt = args[0]
    reasoning_effort = args[1] if len(args) > 1 else None
    system_prompt = context.get('SYSTEM_PROMPT', '')
    model = context.get('MISTRAL_MODEL', "mistral-large-latest")

    endpoint = "https://api.mistral.ai/v1/chat/completions"

    # Build messages
    if 'MISTRAL_MESSAGES' in context:
        messages = context['MISTRAL_MESSAGES'] 
    else:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "reasoning_effort": reasoning_effort
    }

    # Add temperature and k only if present
    if 'MISTRAL_TEMPERATURE' in context:
        payload['temperature'] = context['MISTRAL_TEMPERATURE']
    if 'MISTRAL_K' in context:
        payload['k'] = context['MISTRAL_K']

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
    except requests.RequestException as e:
        context[error_key] = f"Request error: {e}"
        return 1

    if response.status_code != 200:
        context[error_key] = f"API returned HTTP {response.status_code}: {response.text}"
        return 1

    decoded = response.json()
    context[set_name] = decoded.get('choices', [{}])[0].get('message', {}).get('content', '')
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ai_mistral.py <data.json>")
        sys.exit(1)

    data_file = Path(sys.argv[1])
    if not data_file.exists():
        print(f"Error: JSON file '{data_file}' not found.")
        sys.exit(1)

    with data_file.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing {data_file}: {e}")
            sys.exit(1)

    args = data.get("args", [])
    context = data.get("context", {})

    result = ai_mistral_text(args, context)
    set_name = context.get("set_context", "prev")
    if result == 0:
        print(context.get(set_name, ""))
    else:
        print(context.get(f"{set_name}_error", "Unknown error"))
