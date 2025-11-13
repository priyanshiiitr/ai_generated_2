# services/semantic_analyzer.py

from typing import List, Dict
from sentence_transformers import SentenceTransformer, util
from config import settings
import torch

class SemanticAnalyzer:
    def __init__(self):
        # Load the model only once
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(self.device)

    def _get_embeddings(self, texts: List[str]):
        return self.model.encode(texts, convert_to_tensor=True, device=self.device)

    def analyze(self, summary: str, transcript: str, key_concepts: List[str]) -> Dict[str, float]:
        """Calculates semantic coverage and relevance scores."""
        if not key_concepts:
            return {"coverage": 0.0, "relevance": 0.0}

        # Embeddings
        summary_embedding = self._get_embeddings([summary])
        transcript_embedding = self._get_embeddings([transcript])
        concept_embeddings = self._get_embeddings(key_concepts)

        # 1. Calculate Relevance
        # Cosine similarity between the entire summary and the entire transcript
        relevance_similarity = util.cos_sim(summary_embedding, transcript_embedding).item()
        relevance_score = max(0.0, relevance_similarity) # Ensure non-negative

        # 2. Calculate Coverage
        # Check how many key concepts are semantically present in the summary
        # Find the cosine similarity between each concept and the summary
        coverage_similarities = util.cos_sim(summary_embedding, concept_embeddings)
        
        # A concept is considered 'covered' if its similarity to the summary is above a threshold
        coverage_threshold = 0.5
        covered_concepts_count = (coverage_similarities > coverage_threshold).sum().item()
        
        coverage_score = (covered_concepts_count / len(key_concepts))

        return {
            "coverage": round(coverage_score, 3),
            "relevance": round(relevance_score, 3)
        }
