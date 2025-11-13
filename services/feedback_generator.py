# services/feedback_generator.py

from typing import Dict
from utils.llm_client import LLMClient

class FeedbackGenerator:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def generate(self, individual_scores: Dict[str, float], summary: str, transcript: str) -> str:
        """Generates a human-readable feedback text based on the evaluation scores."""
        
        scores_str = "\n".join([f"- {param.capitalize()}: {score:.1f}/10" for param, score in individual_scores.items()])

        prompt = f"""You are an encouraging and constructive teaching assistant.

Based on the following evaluation scores for a student's summary of a lecture, provide a concise, helpful feedback paragraph.

The feedback should start by highlighting a key strength, then constructively point out one or two main areas for improvement. Keep the tone positive and action-oriented. Do not simply list the scores.

Evaluation Scores (out of 10):
{scores_str}

For context, here is the student's summary:
"""{summary}"""

And the original transcript:
"""{transcript}"""

Provide the feedback as a single paragraph of text.
"""

        try:
            feedback_text = await self.llm_client.generate_text(
                prompt=prompt, 
                temperature=0.7,
                max_tokens=250
            )
            return feedback_text.strip()
        except Exception as e:
            print(f"Error generating feedback: {e}")
            return "Feedback could not be generated due to an internal error. Please check the individual scores for details."
