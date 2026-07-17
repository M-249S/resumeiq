import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

try:
    models = client.models.list()

    print("\n===== AVAILABLE MODELS =====\n")

    for model in models.data:
        print(model.id)

except Exception as e:
    print(e)