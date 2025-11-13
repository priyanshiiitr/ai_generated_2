# main.api.py

from fastapi import FastAPI, HTTPException, status
from contextlib import asynccontextmanager

from schemas import EvaluationRequest, EvaluationResponse
from services.evaluation_orchestrator import EvaluationOrchestrator
from config import settings
from utils.llm_client import LLMClient

# Global objects to be initialized at startup
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize shared resources
    print("Starting up...")
    llm_client = LLMClient(api_key=settings.OPENAI_API_KEY)
    app_state["orchestrator"] = EvaluationOrchestrator(llm_client=llm_client)
    print("Orchestrator initialized.")
    yield
    # Shutdown
    print("Shutting down...")
    app_state.clear()

app = FastAPI(
    title="AI Summary Evaluation API",
    description="An API to evaluate student summaries against lecture transcripts.",
    version="1.0.0",
    lifespan=lifespan
)

@app.post("/evaluate", response_model=EvaluationResponse, status_code=status.HTTP_200_OK)
async def evaluate_summary(request: EvaluationRequest):
    """
    Evaluates a student's summary based on a lecture transcript.

    - **lecture_transcript**: The full text of the original lecture.
    - **student_summary**: The summary provided by the student.
    - **evaluation_parameters**: A list of qualitative aspects to evaluate (e.g., 'clarity', 'coherence').
    """
    try:
        orchestrator = app_state.get("orchestrator")
        if not orchestrator:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Orchestration service is not available."
            )
        
        result = await orchestrator.evaluate(request)
        return result
    except Exception as e:
        # Basic error logging
        print(f"An error occurred during evaluation: {e}")
        # In a real app, you'd have more sophisticated logging and error handling
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {str(e)}"
        )

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "ok"}
