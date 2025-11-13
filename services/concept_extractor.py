# services/concept_extractor.py

from typing import List
import json
from utils.llm_client import LLMClient

class ConceptExtractor:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def extract(self, transcript: str) -> List[str]:
        """Extracts key concepts from a lecture transcript using an LLM."""
        prompt = f"""Analyze the following lecture transcript and identify the main topics, key arguments, and critical conclusions. 

Please provide a concise list of these key concepts.

Respond with ONLY a JSON array of strings, where each string is a key concept. Do not include any other text or explanation.

Example response format:
[
  "The theory of relativity's impact on classical physics",
  "The role of gravitational lensing in verifying Einstein's predictions",
  "Key differences between special and general relativity"
]

Transcript:
"""{transcript}""""""

        try:
            response_text = await self.llm_client.generate_text(
                prompt=prompt,
                temperature=0.1, 
                max_tokens=500
            )
            # Clean the response to ensure it's valid JSON
            # LLMs sometimes add markdown backticks
            cleaned_response = response_text.strip().replace('`json', '').replace('`', '')
            key_concepts = json.loads(cleaned_response)
            if isinstance(key_concepts, list) and all(isinstance(c, str) for c in key_concepts):
                return key_concepts
            else:
                raise ValueError("LLM did not return a valid list of strings.")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error decoding key concepts from LLM: {e}")
            # Fallback or re-try logic could be implemented here
            return []
