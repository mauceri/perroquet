import json
import os
import time
from fastapi import FastAPI, Request, Header
from llama_cpp import Llama
import modal
import logging
import subprocess
from pydantic import BaseModel

MODEL_DIR = "/root/models"

def download_model_to_folder():
    from huggingface_hub import snapshot_download
    
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
    print(os.listdir("/root/models/"))


path = os.path.join(os.path.dirname(__file__), "Dockerfile.cuda")
dockerImage = (
    modal.Image.from_dockerfile(path)
    .run_commands("apt-get update")
    .pip_install("huggingface")
    .pip_install("huggingface_hub")
    .run_function(download_model_to_folder,secret=modal.Secret.from_name("llama-cpp-hf"))
)

stub = modal.Stub("docker-image",image=dockerImage)
    

@stub.function(gpu="any")
def install_llama_cpp() :
    from llama_cpp import Llama
    #from langchain.llms import LlamaCpp
    import subprocess
    import time
    start = time.time()
    tstart = start

    prompt = """
    <|system|>: Vos réponses sont concises
    <|user|>: {q}
    """
    #llm = LlamaCpp(model_path="/root/models/vigogne-2-7b-chat.Q5_K_M.gguf")
    print("******* 5")
    llm = Llama(model_path="/root/models/vigogne-2-7b-chat.Q5_K_M.gguf",
                 n_ctx=2048, n_gpu_layers=60)
    
    
   
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
    
"""
@stub.function(image=dockerImage)
@modal.asgi_app()
def llama_cpp_app():
    print("Ici")
    subprocess.run(['python3',
                    '-m',
                    'llama-cpp.server',
                    '--model',
                    '/root/models/vigogne-2-7b-chat.Q5_K_M.gguf'
                    ])
"""


@stub.local_entrypoint()
def main():
    install_llama_cpp.remote()


@stub.cls(gpu="any")
class Model:
    def __enter__(self):
        self.prompt = """
            <|system|>: Vos réponses sont concises
            <|user|>: {q}
            """

        self.llm =Llama(model_path="/root/models/vigogne-2-7b-chat.Q5_K_M.gguf",
                 n_ctx=2048, n_gpu_layers=60)
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


@stub.function(image=dockerImage)
@modal.asgi_app()
def fastapi_app():
    return web_app


if __name__ == "__main__":
    stub.deploy("webapp")
