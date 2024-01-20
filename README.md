**Warning: This is a prototype under construction, as stable as a house of cards. Python development aesthetes are advised to steer clear, as the content of this repository might severely offend their sensibilities.**

# Amicus, a Friend Who Knows How to Keep a Secret

As of January 20, 2024, the repository's organization is as follows:

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

Currently, Amicus uses the `signald` library to receive text from a Signal Messenger client, send it to a LLM on an `Anyscale` function, and return the response received. This is a prototype of a larger project that will allow for confidential discussions (Signal is end-to-end encrypted) with an intelligent agent using an advanced logic engine and RAG (Retrieval Augmented Generation). Ultimately, all these components will be hosted on a local server. The use of Anyscale is necessary for now due to the limitations of the local server in use.

The two primary files for understanding how Amicus operates are:
- `Dockerfile`, and
- `docker-compose.yml`

## Dockerfile
- `FROM python:3.9.12-slim-bullseye` indicates the version of Python being used.
- `RUN pip install --no-cache-dir semaphore-bot==v0.16.0 requests transformers sentencepiece protobuf jinja2` specifies the Python packages being used, although transformers and sentencepiece are not in use at the moment.
```
COPY amicus.py amicus.py
COPY sqlite_handler.py sqlite_handler.py
COPY interrogationMixtralAnyscale.py interrogationMixtralAnyscale.py
COPY .localenv .localenv
```
- indicates the files necessary for Amicus to operate.

- `amicus.py` is the bridge between Signal Messenger and Amicus. `sqlite_handler.py` provides an interface to a SQLite database, mainly for storing the history of transactions between identified Signal Messenger clients by their phone number and a Mixtral-8x7b LLM served by an Anyscale function.
- `sqlite_handler.py` enables access to the database storing transactions between Signal Messenger and Mixtral. This interface is used by `amicus.py` and `interrogationMixtralAnyscale.py`.
- `interrogationMixtralAnyscale.py` allows querying Mixtral by constructing a JSON request containing the history of previous transactions as context, the instructions given to the robot, and the query text itself. This program is used by `amicus.py`.
- `.localenv` contains the Anyscale API key.

`CMD ["python", "amicus.py"]` launches amicus.py when the Docker application is started by docker-compose.yml.

## docker-compose.yml
The application is launched using the command `docker compose up -d --build` in the directory containing `docker-compose.yml` and `Dockerfile`. The first time it is run, it is necessary to register the application on the mobile phone containing the number that will be used to contact Amicus (thus, it will not be possible to use this phone to query Amicus). To do this, connect to the signald container using the command `docker exec -it signald bash` and follow the instructions given [on this signald documentation page](https://signald.org/articles/getting-started/).

Two services are described in `docker-compose.yml`: `signald` and `amicus`.

### signald
`image: signald/signald:0.23.2` indicates that this service uses a pre-recorded image from [https://hub.docker.com/u/signald](https://hub.docker.com/u/signald).
```
-volumes
	./signald:/signal
```
indicates that the local file `./signald` is mounted on `/signald` in the container.

### amicus
- `dockerfile: Dockerfile` indicates that this service is built from the previously described `Dockerfile`.
```
environment:
	- SIGNAL_PHONE_NUMBER
```
- Indicates that the number used to contact Amicus is stored in the `SIGNAL_PHONE_NUMBER` environment variable.
```
volumes:
	- ./signald:/signald
	- ./amicusdb:/amicusdb
```
- Indicates that the local directory `./signald`, already used by the `signald` service, is mounted on the `/signald` directory of the container, allowing `amicus` to communicate with Signal Messenger clients. It also indicates that the local directory `./amicusdb` is mounted on the `/amicusdb` directory of the container, allowing histories to be preserved and consulted from one session to another.

## Miscellaneous
- `test_sqlite_handler.py` is a file for unit testing the SQLite access functions described in `sqlite_handler.py`.
- The various files prefixed with `test_` are test files for certain features under development.
- The `.txt` suffixed files contain entries for testing the Anyscale Mixtral LLM as well as the history via `test_contexte_mixtral.py`.
- The `check_signald.py` file must be launched using the command `'nohup python3 script.py &'`. It contains a function that checks every minute that the `signald` service is alive. If a network cut has killed the service, it is restarted (Using `systemd` would be more orthodox).

**That's all for now.**
