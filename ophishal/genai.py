# ophishal/genai.py

"""
GenAI will cannot provide the following:
- server
- url
- attach_params

Also note that template and attach_template will be the
actual template file content which will be written to disk.
"""
import os
import openai


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SCHEMA_EMAIL = {
    "subject":"string",
    "template":"string",
    "attach_template":"string"
}

prompt = ""

response = openai.Completion.create(
    model="",
    prompt=prompt,
    temperature=0.7,
    max_tokens=150
)

print(response.choices[0].text.strip())