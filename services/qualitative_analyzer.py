# services/qualitative_analyzer.py

from typing import List, Dict
import json
import asyncio
from schemas import EvaluationParameter
from utils.llm_client import LLMClient

class QualitativeAnalyzer:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def _get_llm_rating(self, parameter: str, summary: str, transcript: str) -> float:
        """Gets a single qualitative rating from the LLM."""
        prompt_map = {
            'clarity': "How clear and easy to understand is the student's summary?",
            'coherence': "Does the summary flow logically and connect ideas smoothly?",
            'conciseness': "Does the summary capture the main points without unnecessary words or repetition?"
        }

        prompt = f"""You are an expert evaluator. Analyze the student's summary in the context of the original lecture transcript.

Original Transcript:
"""{transcript}"""

Student Summary:
"""{summary}"""

Evaluation Question: {prompt_map[parameter]}

Rate the summary on a scale from 1 (very poor) to 5 (excellent) for the specific quality of '{parameter}'.

Respond with ONLY a JSON object containing a single key 'score' with your numeric rating.
Example: {{"score": 4.5}}
"""

        try:
            response_text = await self.llm_client.generate_text(
                prompt=prompt, 
                temperature=0.1, 
                max_tokens=50
            )
            # Clean and parse JSON
            cleaned_response = response_text.strip().replace('`json', '').replace('`', '')
            data = json.loads(cleaned_response)
            score = float(data.get('score', 0.0))
            # Clamp score between 1 and 5
            return max(1.0, min(5.0, score))
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            print(f"Error getting LLM rating for {parameter}: {e}")
            return 2.5 # Return a neutral score on failure

    def _get_grammar_score(self, summary: str) -> float:
        """
        Simulates a grammar check. In a real application, this would integrate
        a library like language_tool_python or an external API.
        """
        # Simple heuristic: penalize for very short summaries and assume a base quality
        # This is a placeholder for a real implementation.
        word_count = len(summary.split())
        if word_count < 25:
            return 3.0
        # Mock score based on length for demonstration
        mock_errors = max(0, 10 - word_count // 10)
        score = 5.0 - (mock_errors / 2) # More errors = lower score
        return max(1.0, min(5.0, score))

    async def analyze(self, summary: str, transcript: str, parameters: List[EvaluationParameter]) -> Dict[str, float]:
        """Analyzes the summary for qualitative aspects like clarity, coherence, etc."""
        tasks = {}
        for param in parameters:
            param_str = param.value
            if param_str == 'grammar':
                # Grammar check is synchronous
                tasks[param_str] = self._get_grammar_score(summary)
            else:
                # LLM calls are asynchronous
                tasks[param_str] = self._get_llm_rating(param_str, summary, transcript)
        
        # Separate async and sync results
        async_param_names = [k for k, v in tasks.items() if asyncio.iscoroutine(v)]
        async_coroutines = [v for k, v in tasks.items() if asyncio.iscoroutine(v)]
        
        # Await async tasks concurrently
        async_results = await asyncio.gather(*async_coroutines)
        
        # Combine results
        final_scores = {k: v for k, v in tasks.items() if not asyncio.iscoroutine(v)}
        final_scores.update(zip(async_param_names, async_results))

        # The scores are currently on a 1-5 scale. They will be normalized by the scoring engine.
        return final_scores
