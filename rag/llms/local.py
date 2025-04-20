from openai import OpenAI
from sentence_transformers import SentenceTransformer

def call_llm(query, temperature=0.3, seed=42, model="gemma-3-4b-it@Q8_0"):
    client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": query}
        ],
        temperature=temperature,
        seed=seed,
    )
    return completion.choices[0].message.content


class Encoder():
    def __init__(self, encoder_type: str):
        self.encoder_type = encoder_type
        self.encoder = SentenceTransformer(encoder_type, device='mps',trust_remote_code=True)

    def encode(self, text):
        return self.encoder.encode(text)