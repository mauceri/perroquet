import os
import modal
import shelve
import logging
import subprocess

MODEL_DIR = "/root/models"

def download_model_to_folder():   
    os.makedirs(MODEL_DIR, exist_ok=True)
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
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
    .pip_install("git")
    .pip_install("huggingface")
    .pip_install("huggingface_hub")
    .run_function(download_model_to_folder,secret=modal.Secret.from_name("llama-cpp-hf"))
    .env({"LLAMA_CPP_LIB":"/usr/local/lib/python3.11/site-packages/llama_cpp/libllama.so"})
    .env(({"CMAKE_ARGS":"-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"}))
    .run_commands("pip install llama-cpp-python --force-reinstall --upgrade --no-cache-dir")
    .pip_install("langchain")
)


stub = modal.Stub("llama-cpp-python-inference", image=image)

@stub.function()
def install_llama_cpp() :
    import subprocess
    import torch
    from llama_cpp import Llama
    from langchain.llms import LlamaCpp
    """
    from langchain.prompts import ChatPromptTemplate
    from langchain import PromptTemplate, LLMChain
    from langchain.callbacks.manager import CallbackManager
    from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
    """

    subprocess.run(['find',
                    '/',
                    '-name',
                    "*libllama*.so", 
                    '-print'])

    if torch.cuda.is_available():
        print("GPU is available")
    else:
        print("GPU is not available")

    import subprocess
    import time
    start = time.time()
    tstart = start

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
    

