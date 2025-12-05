## LLM-Debugger / Sandbox

This full-stack application allows you to visualize LLMs as a graph representation.  
The goal is to make a user interface to inspect different layers of an LLM.  
It allows you to inspect activations, biases, and weight distributions of neurons across layers.  
Single bias values of a neuron can be changed to see how stronger activations influence future outputs.

Every LLM can be visualized if it follows the typical industry naming conventions.  
This means you can also use it to debug your own custom models!

### Main Interface

<img width="1870" alt="LLM Debugger main interface showing graph visualization" src="https://github.com/user-attachments/assets/736bf08a-70e3-4c8c-9bc9-e9e46e16b719" />

*The charts show each single neuron on the x-axis, and the corresponding values on the y-axis.*


<img width="800" alt="Detailed neuron analysis chart" src="https://github.com/user-attachments/assets/f758bfbf-a598-46f5-b2f1-307627ec1302" />

*The avg and std charts show, for a single neuron, the average and standard deviation of all incoming parameters.*

For a single x-axis value (e.g., **0**), the calculation is:

<img width="313" alt="Mathematical formula for average and standard deviation calculation" src="https://github.com/user-attachments/assets/3f29eed6-3a3d-4565-9c7f-5895c23aff5f" />

$$\text{avg}(w_1, \ldots, w_n)$$  
$$\text{std}(w_1, \ldots, w_n)$$

## Installation

The backend can currently be instantiated in Google Colab.  
Since this application uses **ngrok** as an API gateway to connect Colab with your local environment, you need an ngrok key.

The frontend mainly uses **Vue.js** (dependencies can be found in the `package-lock.json`).

## Run backend in colab 
```bash
!git clone https://github.com/henrik253/LLM-Debugger
!cd LLM-Debugger && git pull
!pip install pyngrok
```
(Optional) Add a login key for specific huggingface models you may wanna use! 
```python 
import os
from google.colab import userdata, userdata
from huggingface_hub import login
from pyngrok import ngrok
import sys
sys.path.append("/content/LLM-Debugger")
from backend.app.main import start_backend

NGROK_AUTH_TOKEN = userdata.get('ngrok-key')
!ngrok config add-authtoken {NGROK_AUTH_TOKEN}
login(userdata.get('gemma-token'))

await start_backend()
