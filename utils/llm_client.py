# utils/llm_client.py

import openai
from config import settings

class LLMClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI API key is required.")
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = settings.LLM_MODEL_NAME

    async def generate_text(
        self, 
        prompt: str, 
        temperature: float = 0.5,
        max_tokens: int = 1500
    ) -> str:
        """Generates text using the configured LLM."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides concise and accurate information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"An error occurred with the OpenAI API: {e}")
            # In a real app, you might want to raise a custom exception
            raise
