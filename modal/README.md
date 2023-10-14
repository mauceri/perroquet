# Comment lancer une fonction sur modal

Par exemple la configuration ayant un meilleur rapport est celle n'emplaoyant aucune accélération, pour la tester :

    modal serve llama_cpp_nu.py

Pour la déployer :

    modal deploy llama_cpp_nu.py

Pour tester une GPU :

    modal serve llama_cpp_docker_cuda.py

qui utilise le fichier Docker : Dockerfile.cuda

Pour un déploiement : 

    modal deploy llama_cpp_docker_cuda.py

