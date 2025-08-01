import openai
from app.core.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def ask_chatgpt(prompt, model):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        # max_tokens=1500,
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()
    