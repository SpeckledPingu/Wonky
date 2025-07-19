from google import genai
from google.genai import types
from datetime import datetime
import os

# model = "gemini-2.0-flash"
# model = "gemini-2.5-flash-lite-preview-06-17"
model = "gemini-2.5-flash"

total_tokens = list()

def call_llm_flash(query, temperature=0.1, seed=42, max_tokens=12000 ):
    client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
    response = client.models.generate_content(
        model=model,
        contents=[query],
        config=types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
            seed=seed,
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        )
    )
    total_tokens.append({'prompt_tokens':response.usage_metadata.prompt_token_count,
                         'completion_tokens':response.usage_metadata.candidates_token_count,
                         'total_tokens':response.usage_metadata.total_token_count,
                         'timestamp':datetime.now().strftime("%Y_%m_%d_%H_%M_%S")})

    return response.text