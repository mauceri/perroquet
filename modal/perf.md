## Quelques perfs à la louche.

llama_cpp_nu.py (aucune accélération)
70ms/token 40s (pour les 5 requêtes)

llama_cpp_docker_oblas.py (OpenBLAS)
170ms/token 146s

llama_cpp_docker_cuda.py (CUDA)
10ms/token 8s

Il n'y a pas photo sur l'accélération CUDA, OpenBlas est complètement dans les 
choux mais je n'ai plus le temps pour essayer d'analyser pourquoi, la version
pure CPU est bien sûr mais 3 fois plus rapide qu'OpenBLAS, il faut maintenant 
voir les coûts (CUDA n'est pas donné)

Le modèle est : vigogne-2-7b-chat.Q5_K_M.gguf
https://huggingface.co/TheBloke/Vigogne-2-7B-Chat-GGUF