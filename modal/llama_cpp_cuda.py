import os
import modal
import shelve
import logging
import subprocess

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


image = (
    modal.Image.debian_slim()
    .run_commands("apt-get update")
    .run_commands("apt-get install -y \
                  build-essential cmake \
                  python3 python3-pip gcc wget\
                  ocl-icd-opencl-dev opencl-headers clinfo \
                  libclblast-dev libopenblas-dev \
                  pkg-config")
    .run_commands("mkdir -p /etc/OpenCL/vendors && echo \"libnvidia-opencl.so.1\" > /etc/OpenCL/vendors/nvidia.icd")
    .run_commands("pip install --upgrade pip")
    .pip_install("torch")
    .pip_install("huggingface-hub>=0.17.1")
    .pip_install("huggingface")
    .pip_install("huggingface_hub")
    .run_function(download_model_to_folder,secret=modal.Secret.from_name("llama-cpp-hf"))
    .env({"LLAMA_CPP_LIB":"/usr/local/lib/python3.11/site-packages/llama_cpp/libllama.so"})
    .env({"CMAKE_ARGS":"-DLLAMA_CUBLAS=on","FORCE_CMAKE":"1"})
    .run_commands("pip install llama-cpp-python --force-reinstall --upgrade --no-cache-dir")
    .pip_install("langchain")
)


stub = modal.Stub("llama-cpp-python-inference", image=image)

@stub.function(gpu="any")
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
    #from langchain.llms import CTransformers
    import subprocess
    import time
    start = time.time()
    tstart = start

    print(os.getenv('LLAMA_CPP_LIB'))
    print("run find")
    subprocess.run(['find', '/', '-name', "*libllama*so", '-print'])
    subprocess.run(['find', '/', '-name', "*ocker*", '-print'])
    #subprocess.run(['nvidia-smi'])

    if torch.cuda.is_available():
        print("GPU is available")
    else:
        print("GPU is not available")
    
    prompt = """
    <|system|>: Vos réponses sont concises
    <|user|>: {q}
    """
    #llm = LlamaCpp(model_path="/root/models/vigogne-2-7b-chat.Q5_K_M.gguf",)
    llm = Llama(model_path="/root/models/vigogne-2-7b-chat.Q5_K_M.gguf",
                 n_ctx=2048, n_gpu_layers=60)
    #subprocess.run(['nvidia-smi'])
    
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
    
    #subprocess.run(['nvidia-smi'])
    end = time.time()
    print(end - tstart)

@stub.local_entrypoint()
def main():
    install_llama_cpp.remote()
    

#CUDA 70s BLAS 120s NU 50s Docker 1s