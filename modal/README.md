# Comment lancer une fonction sur modal

Par exemple la configuration ayant un meilleur rapport est celle n'employant aucune accélération, pour la tester :

    modal serve llama_cpp_nu.py

Pour la déployer :

    modal deploy llama_cpp_nu.py

Pour tester une GPU beaucoup plus chère :

    modal serve llama_cpp_docker_cuda.py

Ce fichier utilise le fichier Docker : Dockerfile.cuda

Pour un déploiement : 

    modal deploy llama_cpp_docker_cuda.py

