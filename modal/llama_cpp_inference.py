import os
import modal
from fastapi import FastAPI, Request, Header

from modal import Image, Secret, Stub, asgi_app, method, web_endpoint
from pydantic import BaseModel
from pyparsing import Optional
from collections import deque
import logging

logging.basicConfig(level=logging.INFO)


MODEL_DIR = "/root/model"

def download_model_to_folder():
    from huggingface_hub import snapshot_download

    os.makedirs(MODEL_DIR, exist_ok=True)

    snapshot_download(
        #"meta-llama/Llama-2-13b-chat-hf",
        #"bofenghuang/vigogne-7b-chat",
        "TheBloke/Vigogne-2-7B-Chat-GGUF",
        local_dir=MODEL_DIR,
        token=os.environ["HUGGINGFACE_TOKEN"],
    )
    logging.info(os.listdir("/root/models/"))


image = (
    Image.debian_slim()
    .run_commands("pip install --upgrade pip")
    .pip_install("langchain==0.0.283")
    .pip_install("llama-cpp-python==0.1.83")
)

stub = Stub("llama-cpp-python-inference", image=image)

#@stub.function(mounts=[modal.Mount.from_local_dir("./models", remote_path=MODEL_DIR)])
def f():
    logging.info(os.listdir("/root/models/"))


@stub.function()
def llama_cpp() :
    image.run_commands("")

@stub.cls()
class ChatHistory:
    def __init__(self, msg_limit):
        self.stack = deque(maxlen=msg_limit)

    def append(self, msg):
        return self.stack.append(msg)

    def get_as_list(self):
        return list(self.stack)

    def get_as_string(self):
        res = ""
        for e in self.get_as_list():
            res +=  e + "\n"
        return res

@stub.cls(gpu="A100")
class Model:
    def __enter__(self):
        from langchain.llms import LlamaCpp
        from langchain.prompts import ChatPromptTemplate
        from langchain import PromptTemplate, LLMChain
        from langchain.callbacks.manager import CallbackManager
        from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
        from collections import deque


        self.callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        self.model = "ggml-model-q4_0.bin"
        self.history = ChatHistory(5)
        self.max_tokens = 2024
        self.llm = LlamaCpp(
            model_path="/root/models/ggml-model-q4_0.bin",
            temperature=1,
            #    model_pat
            max_tokens=1000,
            n_ctx=4096,
            top_p=1,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]), 
            verbose=True, # Verbose is required to pass to the callback manager
        )
        logging.basicConfig(level = logging.INFO)
        self.template = """
        <|system|>: Vous êtes l'assistant IA nommé Vigogne, créé par Zaion Lab (https://zaion.ai). Vous suivez extrêmement bien les instructions. Aidez autant que vous le pouvez.
        <|user|>: {user}
        """

        @method()
        def generate(self, user_question):
            p = self.prompt.format(q=user_question)
            r = self.llm(p)
            r = r.strip()
            
 
 
gmodel = Model()

@stub.function()
@web_endpoint(method="POST")
async def api_entrypoint(request: Request):
    body = await request.json()
    prompt = body["prompt"]
    logging.info(prompt)
    max_length = body.get("max_length", 50)
    #generated_text = await llama2_inference(prompt, max_length)
    
    answer = gmodel.generate([prompt])
    return {"answer": answer}


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
    m = Model()
    user_question = item.prompt
    answer = m.generate(user_question)
    return answer


@stub.function(image=image)
@asgi_app()
def fastapi_app():
    return web_app


if __name__ == "__main__":
    f.remote()
    stub.deploy("webapp")


