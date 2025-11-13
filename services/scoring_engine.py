# services/scoring_engine.py

from typing import Dict, Tuple
from config import settings

class ScoringEngine:
    def __init__(self):
        self.weights = settings.SCORING_WEIGHTS
        # Ensure weights are somewhat sane
        if abs(sum(self.weights.values()) - 1.0) > 1e-6:
            print("Warning: Scoring weights do not sum to 1.0. Normalization will be affected.")

    def _normalize_score(self, score: float, scale_min: float, scale_max: float) -> float:
        """Normalizes a score from its original scale (e.g., 1-5) to a 0-10 scale."""
        if scale_min == scale_max:
            return 5.0 # Avoid division by zero, return neutral value
        # Convert to 0-1 range first
        normalized_0_1 = (score - scale_min) / (scale_max - scale_min)
        # Then scale to 0-10
        return normalized_0_1 * 10

    def calculate_final_score(self, raw_scores: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
        """
        Aggregates raw scores into a final weighted score.
        
        Args:
            raw_scores: A dictionary of scores, e.g., {'coverage': 0.8, 'clarity': 4.5}.
                        'coverage' and 'relevance' are expected to be 0-1.
                        Qualitative scores are expected to be 1-5.

        Returns:
            A tuple containing:
            - The final aggregated score (0-10).
            - A dictionary of individual scores, all normalized to a 0-10 scale.
        """
        final_score = 0.0
        normalized_scores = {}

        for param, score in raw_scores.items():
            if param not in self.weights:
                continue # Ignore scores without a defined weight

            # Normalize scores to a common 0-10 scale
            if param in ['coverage', 'relevance']:
                # These are already 0-1, so just scale by 10
                normalized_scores[param] = score * 10.0
            else:
                # Assume qualitative scores are 1-5
                normalized_scores[param] = self._normalize_score(score, 1.0, 5.0)
            
            # Add to weighted final score
            final_score += normalized_scores[param] * self.weights[param]

        return round(final_score, 2), {k: round(v, 2) for k, v in normalized_scores.items()}
