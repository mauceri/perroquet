import json
import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import re

from llama_cpp import Llama

import modal
import logging
import subprocess

from pydantic import BaseModel

MODEL_DIR = "/root/models"

def download_model_to_folder():
    os.makedirs(MODEL_DIR, exist_ok=True)
    logging.info(f"Loading model")
    subprocess.run(['huggingface-cli',
                    'download',
                    'TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF',
                    'mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf', 
                    '--local-dir',
                    MODEL_DIR,
                    '--local-dir-use-symlinks',
                    'False'])
  
  

    logging.info(os.listdir("/root/models/"))



image = (
    modal.Image.debian_slim()
    .run_commands("apt-get update")
    .run_commands("apt-get install -y build-essential cmake libopenblas-dev pkg-config")
    .run_commands("pip install --upgrade pip")
    .pip_install("torch")
    .pip_install("huggingface")
    .pip_install("huggingface_hub")
    .run_commands("pip uninstall llama-cpp-python")
    .run_commands("pip install llama-cpp-python --force-reinstall --upgrade --no-cache-dir")
    .run_function(download_model_to_folder,secret=modal.Secret.from_name("llama-cpp-hf"))
    .pip_install("langchain")
)


stub = modal.Stub("mixtral-llama-cpp-nu", image=image)

@stub.function()
def install_llama_cpp() :
    import torch
    from llama_cpp import Llama
    from langchain.llms import LlamaCpp
    """
    from langchain.prompts import ChatPromptTemplate
    from langchain import PromptTemplate, LLMChain
    from langchain.callbacks.manager import CallbackManager
    from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
    """

    import subprocess
    import time
    start = time.time()
    tstart = start

    if torch.cuda.is_available():
        print("GPU is available")
    else:
        print("GPU is not available")

@stub.local_entrypoint()
def main():
    install_llama_cpp.remote()
    

ex = """
<s>[INST] <<SYS>>
Vous êtes Vigogne, un assistant IA créé par Zaion Lab. Vous suivez extrêmement bien les instructions. 
Aidez autant que vous le pouvez.
<</SYS>>
Bonjour ! Comment ça va aujourd'hui ? [/INST] 
Bonjour ! Je suis une IA, donc je n'ai pas de sentiments, mais je suis prêt à vous aider. Comment puis-je vous assister aujourd'hui ? </s>
[INST] Quelle est la hauteur de la Tour Eiffel ? [/INST] 
La Tour Eiffel mesure environ 330 mètres de hauteur. </s>
[INST] Comment monter en haut ? [/INST]"""
@stub.cls()
class Model:
    def __enter__(self):

        self.instructions = [{"role":"system","content":"Vos réponses sont concises"}]
        self.llm = Llama(
                model_path="/root/models/mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf",chat_format="llama-2"
                )

        # Load the model. Tip: MPT models may require `trust_remote_code=true`.

    @modal.method()
    def generate(self, question):
        print(f"Dans generate {question}")   
        for i in range(10):
            print(f"Essai n° {i}")
            self.llm.reset()
            # prompt_tokens: List[int] = (
            #     self.llm.tokenize(question.encode("utf-8"))
            #         if question != "" else [self.token_bos()]
            # )
            print(f"Voici le prompt: \"{question}\" ")
            result = self.llm.create_chat_completion(
                messages=question,max_tokens=1024,temperature=0.6,
            )

            print(f"retour{result}")
            #'choices': [{'index': 0, 'message': 
            #{'role': 'assistant', 'content': " Non, généralement les tortues ne courent pas plus vite que les lièvres. Les lièvres peuvent atteindre des vitesses jusqu'à 80 km/h, tandis que les tortues ne dépassent pas quelques kilomètres par heure."}, 'finish_reason': 'stop'}], 'usage': {'prompt_tokens': 78, 'completion_tokens': 64, 'total_tokens': 142}}
            if result["choices"][0]["message"]["content"].strip() != "":
                print(f"Voici le résultat {result}")
                return result
           
        raise Exception("No reply")
 
gmodel = Model()


web_app = FastAPI()

class Item(BaseModel):
    question: str



@web_app.get("/")
async def handle_root(user_agent: str = Header(None)):
    logging.info(f"GET /     - received user_agent={user_agent}")
    return "Hello World"


@web_app.post("/question")
async def handle_question(item:Item):
    answer = None  
    print(f"Models: {os.listdir('/root/models/')}")
    try:
        print(f"****************************************** Question {json.loads(item.question)}")
        # Logique si context n'est pas fourni
        answer = gmodel.generate.remote(json.loads(item.question))
    except Exception as e:
        raise Exception(f"Quelque chose n'a pas fonctionné {e}") 
    print(f"****************************************** Réponse : {answer}")
    return answer



@stub.function(image=image)
@modal.asgi_app()
def fastapi_app():
    return web_app


if __name__ == "__main__":
    stub.deploy("webapp")
