**Attention ceci est un prototype en construction, il est aussi solide qu’un château de cartes, par ailleurs les esthètes du développement python sont priés de passer leur chemin, le contenu de ce dépôt pourrait gravement heurter leur sensibilité**
# Amicus un ami qui sait garder un secret
Le 20/01/2024 l’organisation du dépôt est la suivante
```
.
├── Dockerfile
├── README.md
├── amicus.py
├── amicus.sqlite
├── amicusdb
│   └── amicus.sqlite
├── check_signald.py
├── docker-compose.yml
├── interrogationMixtralAnyscale.py
├── question_immigration.txt
├── questions.txt
├── signald
│   ├── avatars
│   │   └── contact-+33659745825
│   ├── data
│   ├── signald.db
│   └── signald.sock
├── sqlite_handler.py
├── test_contexte.sqlite
├── test_contexte_mixtral.py
├── test_replicate.py
├── test_sqlite_handler.py
└── tree.txt
```

À l’heure actuelle Amicus utilise la librairie `signald` pour recevoir du texte d’un client Signal Messenger, l’envoyer vers un LLM sur une fonction `Anyscale`, et renvoyer la réponse retournée. C’est le prototype d’un projet plus vaste qui permettra de discuter en toute confidentialité (Signal est crypté de bout en bout) avec un agent intelligent utilisant un moteur logique avancé et un RAG (Retrieval Augmented Generation), toutes ces composantes seront bien sûr, à terme, hébergées par un serveur local, l’utilisation d’Anyscale est aujourd’hui nécessaire du fait de la faiblesse du serveur local utilisé.
Les deux fichiers de base permettant de comprendre comment fonctionne Amicus sont :
- `Dockerfile`, et
- `docker-compose.yml`
## Dockerfile
`‌FROM python:3.9.12-slim-bullseye` indique la version de python utilisée.
```
 RUN pip install --no-cache-dir semaphore-bot==v0.16.0 requests transformers sentencepiece protobuf jinja2
```
 indique quels sont les packages python utilisés bien que transformers et sentencepiece ne sont pas utilisés en ce moment.
```
‌COPY amicus.py amicus.py
COPY sqlite_handler.py sqlite_handler.py
COPY interrogationMixtralAnyscale.py interrogationMixtralAnyscale.py
COPY .localenv .localenv
```

Permet de savoir quels sont les fichiers nécessaires au fonctionnement d’Amicus

- `amicus.py` est le pont entre Signal Messenger et Amicus, slite_handler.py fournit une interface vers une base de donnée sqlite permettant essentiellement de stocker l’historique des transaction entre les clients Signal Messenger identifiés par leur numéro de téléphone et un LLM Mixtral-8x7b servi pas une fonction Anyscale.
- `sqlite_handler.py` permet d’accéder à la base de données stockant les transactions entre le Signal Messenger et Mixtral, cette interface est utilisée par `amicus.py`et `interrogationMixtralAnyscale.py`
- `interrogationMixtralAnyscale.py` permet d’interroger Mixtral en construisant une requête json contenant l’historique des transactions précédentes utilisé comme contexte, les instructions données au robot, et le texte de la requête lui-même. Ce programme est utilisé par `amicus.py’
- `.localenv`contient la clef d’API d’Anyscale.
`CMD ["python", "amicus.py"]` lance amicus.py au démarrage de l’application docker par docker-compose.yml
## docker-compose.yml
L’application est lancée en utilisant la commande `docker compose up -d --build` dans le répertoire contenant `docker-compose.yml` et `Dockerfile`. Lors de la première exécution il faut enregistrer l’application sur le téléphone portable contenant le numéro qui sera utilisé pour contacter Amicus (il ne sera donc pas possible d’utiliser ce téléphone pour interroger Amicus). Pour ce faire il faut se connecter sur le conteneur signald en utilisant la commande `docker exec -it signald bash` et en suivant les instruction données [dans cette page de la documentation de signald](https://signald.org/articles/getting-started/).
Deux services sont décrits dans `docker-compose.yml` : `signald` et `amicus`.
### signald 
`image: signald/signald:0.23.2` indique que ce service utilise une image préenregistrée dans [https://hub.docker.com/u/signald](https://hub.docker.com/u/signald) 
```
volumes
 - ./signald:/signal 
```
indique que le fichier local `./signald` est monté sur `/signald` du conteneur.
### amicus
- `dockerfile: Dockerfile` indique que ce service est construit à partir du fichier `Dockerfile` précédemment décrit.
```
environment:
      - SIGNAL_PHONE_NUMBER
```
- Indique que le numéro utilisé pour contacter Amicus est enregistré dans la variable d’environnement `SIGNAL_PHONE_NUMBER` 
```
volumes:
      - ./signald:/signald
      - ./amicusdb:/amicusdb
```
- Indique, d’une part, que le répertoire local `./signald` déjà utilisé par le service `signald` est monté sur le répertoire `/signald` du conteneur, ainsi la `socket` définie par `signald` peut être utilisée par les deux services ce qui permet à `amicus`de communiquer avec les clients Signal Messenger, et d’autre part que le répertoire local `./amicusdb`est monté sur le répertoire `/amicusdb` du conteneur. Ainsi les historiques sont conservés et consultables d’une session à l’autre.

## Divers
- `test_sqlite_handler.py` est un fichier de tests unitaires des fonctions d’accès à `sqlite`  décrits dans `sqlite_handler.py`
- Les différents fichiers préfixés par `test_` sont des fichiers de tests de certaines fonctionnalités en développement.
- Les fichiers suffixés `.txt` contiennent des entrées pour tester  via `test_contexte_mixtral.py` le LLM Mixtral de Anyscale ainsi que l’historique.
- Le fichier `check_signald.py` doit être lancé via la commande   `'nohup python3 script.py &'`, il contient une fonction qui vérifie toutes les minutes que le service `signald` est bien vivant. Si une coupure du réseau l’a tué le service est redémarré (L’utilisation de `systemd` serait plus orthodoxe) .

**Voilà c’est tout pour l’instant**
  