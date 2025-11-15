from fastapi import FastAPI
from pyngrok import ngrok, conf
import uvicorn
import threading
from fastapi.middleware.cors import CORSMiddleware
import time
from pyngrok import ngrok 
from google.colab import userdata 
from routers.model_router import model_router
from routers.main_router import main_router
from managers.model_manager import ModelManager

ngrok.kill()


# Instatiate

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def run():
    uvicorn.run(app, host="0.0.0.0", port=8000)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()


    # Start ngrok tunnel
    public_url = ngrok.connect(8000)
    print("Public URL:", public_url)

def start_backend():
  print('BACKEND STARTED') 
  
  model_manager_singleton = ModelManager() 

  ngrok_auth = None
  try:
    ngrok_auth = userdata.get('ngrok-key')
  except Exception: 
    print('google.colab userdata.get("ngrok-key") failed') 
    conf.get_default().auth_token = ngrok_auth 
    
  app.include_router(model_router)
  app.include_router(main_router) 

  thread = threading.Thread(target=run, daemon=True) 
  thread.start() 

  public_url = ngrok.connect(8000)
  print("Public URL:", public_url)

    
