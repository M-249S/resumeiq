from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

response = client.responses.create(
    model="gpt-4.1-mini",
    input="Say only: OpenAI connection successful!"
)

print(response.output_text)