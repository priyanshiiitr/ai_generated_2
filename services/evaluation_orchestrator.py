# services/evaluation_orchestrator.py

from schemas import EvaluationRequest, EvaluationResponse, IndividualScore
from .concept_extractor import ConceptExtractor
from .semantic_analyzer import SemanticAnalyzer
from .qualitative_analyzer import QualitativeAnalyzer
from .scoring_engine import ScoringEngine
from .feedback_generator import FeedbackGenerator
from utils.llm_client import LLMClient

class EvaluationOrchestrator:
    def __init__(self, llm_client: LLMClient):
        self.concept_extractor = ConceptExtractor(llm_client)
        self.semantic_analyzer = SemanticAnalyzer()
        self.qualitative_analyzer = QualitativeAnalyzer(llm_client)
        self.scoring_engine = ScoringEngine()
        self.feedback_generator = FeedbackGenerator(llm_client)

    async def evaluate(self, request: EvaluationRequest) -> EvaluationResponse:
        # 1. Extract key concepts from the transcript
        key_concepts = await self.concept_extractor.extract(request.lecture_transcript)
        
        # 2. Perform semantic analysis (Coverage & Relevance)
        semantic_scores = self.semantic_analyzer.analyze(
            summary=request.student_summary, 
            transcript=request.lecture_transcript, 
            key_concepts=key_concepts
        )
        
        # 3. Perform qualitative analysis
        qualitative_scores = await self.qualitative_analyzer.analyze(
            summary=request.student_summary, 
            transcript=request.lecture_transcript,
            parameters=request.evaluation_parameters
        )
        
        # Combine all raw scores
        all_raw_scores = {**semantic_scores, **qualitative_scores}
        
        # 4. Aggregate scores using the scoring engine
        final_score, individual_scores_out_of_10 = self.scoring_engine.calculate_final_score(all_raw_scores)
        
        # 5. Generate human-readable feedback
        feedback = await self.feedback_generator.generate(
            individual_scores=individual_scores_out_of_10, 
            summary=request.student_summary,
            transcript=request.lecture_transcript
        )
        
        # 6. Format the final response
        response = EvaluationResponse(
            final_score=final_score,
            feedback=feedback,
            individual_scores={k: IndividualScore(score=v) for k, v in individual_scores_out_of_10.items()}
        )
        
        return response
