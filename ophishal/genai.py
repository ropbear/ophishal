# ophishal/genai.py

"""
GenAI is currently only used to create the email body.
"""
import os
import json

from openai import OpenAI

from ophishal.log import create_logger
from ophishal.engagement import EmailEngagement


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def generate_email_body(eng:EmailEngagement, model="gpt-4o"):
    """
    Critical privacy note: whatever is sent as an argument to this function is sent to OpenAI.
    """
    logger = create_logger("openai:generate_email_body")
    
    if eng is None:
        logger.error("No EmailEngagement object specified")
        return None

    engagement_json = eng.to_dict()

    if OPENAI_API_KEY is None or OPENAI_API_KEY == "":
        logger.error("Invalid OPENAI_API_KEY")
        return None

    client = OpenAI(api_key=OPENAI_API_KEY)
    schema = {
        "body": {"type": "string", "description": "HTML body of the email, formatted to match the context"}
    }
    instructions = "You are a senior offensive security researcher on an F500 red team." + \
                    " When you receive user-provided JSON, use it as context." + \
                    " Generate an HTML (no CSS) email body based on, but not including verbatim, the sender's writing style, provided in the writing_sample attribute." + \
                    " You ONLY create an email body with DOCTYPE, html, head, and body tags. No code blocks, no extraneous text. Nothing except HTML. " + \
                    " Use the \"url\" parameter for any phishing links in the email, but ensure the link context makes sense in the context." + \
                    " Be sure to write an email that matches the configuration, do not deviate from the configuration for any reason."

    logger.info("Prompting %s", model)
    resp = client.responses.create(
        model=model,
        instructions=instructions,
        input= "Generate an potent phishing email for a red team engagement using the following configuration." + \
                f"\n\n{engagement_json}"
    )

    lines = resp.output_text.split("\n")
    if lines[0][0:3] == "```":
        lines = lines[1:]
    if lines[-1][0:3] == "```":
        lines = lines[:-1]
    return "\n".join(lines)
