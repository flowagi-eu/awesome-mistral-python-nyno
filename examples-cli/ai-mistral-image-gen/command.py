#!/usr/bin/env python3
import os
import uuid
import time
import json
import sys
from mistralai import Mistral
from mistralai.models import ToolFileChunk

def ai_mistral_image_gen(args, context):
    """
    Generate images using Mistral with context and arguments.

    :param args: list [prompt]
    :param context: dict containing:
        - MISTRAL_API_KEY: required
        - SYSTEM_PROMPT: optional
        - MISTRAL_MODEL: optional
        - output_dir: optional, default 'output'
        - set_context: optional, default 'prev'
    :return: int (0 on success, 1 on error)
    """
    set_name = context.get("set_context", "prev")
    error_key = f"{set_name}_error"

    if not args or not args[0]:
        context[error_key] = "Usage: ai_mistral_image_gen <prompt>\nMissing prompt in args[0]"
        return 1

    prompt = args[0]

    API_KEY = context.get("MISTRAL_API_KEY")
    if not API_KEY:
        context[error_key] = "MISTRAL_API_KEY not set in context."
        return 1

    output_dir = context.get("output_dir", "output")
    os.makedirs(output_dir, exist_ok=True)

    model = context.get("MISTRAL_MODEL", "mistral-medium-2505")
    system_prompt = context.get("SYSTEM_PROMPT", "")

    # Initialize client
    client = Mistral(api_key=API_KEY)

    # Create image generation agent
    try:
        image_agent = client.beta.agents.create(
            model=model,
            name="Image Generation Agent",
            description="Agent used to generate images.",
            instructions="Use the image generation tool when you have to create images.",
            tools=[{"type": "image_generation"}],
            completion_args={
                "temperature": 0.3,
                "top_p": 0.3
            }
        )
    except Exception as e:
        context[error_key] = f"Failed to create agent: {e}"
        return 1

    # Optional wait for agent readiness
    time.sleep(2)

    # Start conversation and generate image
    try:
        response = client.beta.conversations.start(
            agent_id=image_agent.id,
            inputs=prompt
        )
    except Exception as e:
        context[error_key] = f"Conversation error: {e}"
        return 1

    saved_files = []
    uid = uuid.uuid4()

    try:
        for i, chunk in enumerate(response.outputs[-1].content):
            if isinstance(chunk, ToolFileChunk):
                file_bytes = client.files.download(file_id=chunk.file_id).read()
                if file_bytes:
                    file_name = os.path.join(output_dir, f"{uid}_{i}.png")
                    with open(file_name, "wb") as f:
                        f.write(file_bytes)
                    saved_files.append(file_name)
        if not saved_files:
            context[error_key] = "No images were generated."
            return 1
        # Store first image path in context[set_name] (like ai_mistral_text)
        context[set_name] = saved_files[0]
        context[f"{set_name}_all"] = saved_files
        return 0
    except Exception as e:
        context[error_key] = f"Error saving images: {e}"
        return 1


# ——————————————————————————
# CLI / Demo
# ——————————————————————————
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ai_mistral_image_gen.py <data.json>")
        sys.exit(1)

    data_file = sys.argv[1]
    if not os.path.exists(data_file):
        print(f"Error: JSON file '{data_file}' not found.")
        sys.exit(1)

    with open(data_file, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing {data_file}: {e}")
            sys.exit(1)

    args = data.get("args", [])
    context = data.get("context", {})

    result = ai_mistral_image_gen(args, context)
    set_name = context.get("set_context", "prev")

    if result == 0:
        print(f"Saved image: {context[set_name]}")
        print(f"All images: {context.get(f'{set_name}_all', [])}")
    else:
        print(context.get(f"{set_name}_error", "Unknown error"))
