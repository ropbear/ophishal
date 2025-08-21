# ophishal/genai.py

"""
GenAI is currently only used to create the email body.
"""
import os
import json
from pathlib import Path

from openai import OpenAI

from ophishal.log import create_logger

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_cfg_json_from_file(filepath:Path):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_email_body_and_subject(config:Path, model="gpt-4o"):
    """
    Critical privacy note: whatever is sent as an argument to this function is sent to OpenAI.
    """
    logger = create_logger("openai:generate_email_body_and_subject")
    
    if config is not None and isinstance(config, Path):
        if config.exists():
            cfg_dict = get_cfg_json_from_file(config)
        else:
            logger.error("Configuration file does not exist")
            return None

    if OPENAI_API_KEY is None or OPENAI_API_KEY == "":
        logger.error("Invalid OPENAI_API_KEY")
        return None

    client = OpenAI(api_key=OPENAI_API_KEY)
    schema = {
        "body": {"type": "string", "description": "HTML body of the email, formatted to match the context"}
    }

    logger.info("Prompting %s", model)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You generate phishing content in structured format given a context." + \
                            "The emails you create are sent from the \"sender\" to each email in the \"targets\" list." + \
                            "You only generate HTML than can be rendered by almost any email client." + \
                            "Use the \"url\" parameter for any phishing links in the email, but ensure the link context makes sense in the context." + \
                            "Your HTML should include the DOCTYPE, html, head, and body tags, with the focus on the body."
            },
            {"role": "user", "content": f"Generate an potent phishing email using the following configuration:\n{cfg_dict}"}
        ],
        functions=[
            {
                "name": "generate_email_phish",
                "description": "Generate phishing email structure",
                "parameters": {
                    "type": "object",
                    "properties":schema,
                    "required": ["body"]
                }
            }
        ],
        function_call={"name": "generate_email_phish"}
    )
    resp = json.loads(response.choices[0].message.function_call.arguments)

    if list(resp.keys()) != ["body"]:
        logger.error("Invalid keys returned: %s", list(resp.keys()))
        return None
    return resp
