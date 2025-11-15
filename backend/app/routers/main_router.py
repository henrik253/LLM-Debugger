from fastapi import APIRouter

router = APIRouter(
    prefix="/main",
    tags=["Main"]
)

@router.get("/")
def health_check():
    """
    Basic health-check endpoint.
    Returns a simple JSON message to confirm the backend is running.
    """
    return {"status": "OK", "message": "Backend is running"}


@router.get("/info")
def info():
    """
    Returns generic backend information.
    You can add version, environment flags, or debug info here.
    """
    return {
        "app": "LLM-Debugger Backend",
        "version": "1.0.0",
        "description": "FastAPI backend running in Colab with ngrok."
    }
