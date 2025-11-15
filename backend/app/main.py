from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pyngrok import ngrok, conf
from google.colab import userdata
import uvicorn
import threading

from backend.app.routers.model_router import router as model_router
from backend.app.routers.main_router import router as main_router


ngrok.kill()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def start_uvicorn():
    uvicorn.run(app, host="0.0.0.0", port=8000)


def start_backend():
    print("BACKEND STARTED")

    try:
        ngrok_auth = userdata.get("ngrok-key")
        conf.get_default().auth_token = ngrok_auth
    except Exception:
        print("google.colab userdata.get('ngrok-key') failed")

    app.include_router(model_router)
    app.include_router(main_router)

    thread = threading.Thread(target=start_uvicorn, daemon=True)
    thread.start()

    public_url = ngrok.connect(8000)
    print("Public URL:", public_url)
