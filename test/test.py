import os
from dotenv import load_dotenv
load_dotenv()  # Ini memuat .env agar os.getenv("OPENAI_API_KEY") bisa membaca

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Say hello!"}]
)

print(response.choices[0].message.content)
