import os
from fastapi import FastAPI, Header
from llama_cpp import Llama
import modal
import shelve
import logging
import subprocess

from pydantic import BaseModel

MODEL_DIR = "/root/models"

def download_model_to_folder():
    os.makedirs(MODEL_DIR, exist_ok=True)

    subprocess.run(['huggingface-cli',
                    'download',
                    'TheBloke/Vigogne-2-7B-Chat-GGUF',
                    'vigogne-2-7b-chat.Q5_K_M.gguf', 
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
    .run_function(download_model_to_folder,secret=modal.Secret.from_name("llama-cpp-hf"))
    .run_commands("pip install llama-cpp-python --force-reinstall --upgrade --no-cache-dir")
    .pip_install("langchain")
)


stub = modal.Stub("llama-cpp-python-nu", image=image)

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

    prompt = """
    <|system|>: Vos réponses sont concises
    <|user|>: {q}
    """
    #llm = LlamaCpp(model_path="/root/models/vigogne-2-7b-chat.Q5_K_M.gguf")
    llm = Llama(model_path="/root/models/vigogne-2-7b-chat.Q5_K_M.gguf")
    
    print("************************ Attention ça va commencer *******************")
    start = time.time()
    tstart = start
    
    m = "Qui était Henri IV de France ?"
    p = prompt.format(q=m)
    output = llm(p)
    print(output)
    end = time.time()
    print(end - start)
    start = end

    m = "Qui était le Dr Destouches ?"
    p = prompt.format(q=m)
    output = llm(p)
    print(output)
    end = time.time()
    print(end - start)
    start = end

    m = "Comment a débuté la première guerre mondiale ?"
    p = prompt.format(q=m)
    output = llm(p)
    print(output)
    end = time.time()
    print(end - start)
    start = end

    p = prompt.format(q="Comment se mangent les noix ?")
    output = llm(p)
    print(output)
    end = time.time()
    print(end - start)
    start = end

    p = prompt.format(q="Qu'est-ce que le sepuku ?")
    output = llm(p)
    print(output)
    end = time.time()
    print(end - start)
    start = end
    
    print(end - tstart)

@stub.local_entrypoint()
def main():
    install_llama_cpp.remote()
    

@stub.cls()
class Model:
    def __enter__(self):
        self.prompt = """
            <|system|>: Vos réponses sont concises
            <|user|>: {q}
            """

        self.llm =Llama(model_path="/root/models/vigogne-2-7b-chat.Q5_K_M.gguf")
        # Load the model. Tip: MPT models may require `trust_remote_code=true`.

    @modal.method()
    def generate(self, user_question):
        p = self.prompt.format(q=user_question)
        
        logging.info(user_question)
        print(user_question)
        result = self.llm(p)
        
        logging.info(result)
        print(result)
        return result

gmodel = Model()


web_app = FastAPI()

class Item(BaseModel):
    prompt: str

@web_app.get("/")
async def handle_root(user_agent: str = Header(None)):
    logging.info(f"GET /     - received user_agent={user_agent}")
    return "Hello World"


@web_app.post("/question")
async def handle_question(item: Item, user_agent: str = Header(None)):
    logging.info(
        f"POST /foo - received user_agent={user_agent}, item.prompt={item.prompt}"
    )
    print(item)
    logging.info(item)
    answer = gmodel.generate.remote(item.prompt)
    return answer


@stub.function(image=image)
@modal.asgi_app()
def fastapi_app():
    return web_app


if __name__ == "__main__":
    stub.deploy("webapp")
