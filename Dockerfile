# Grab Python image.
FROM python:3.9.12-slim-bullseye

WORKDIR /

# Upgrade pip.
RUN pip install --upgrade pip

# Update packages and install SQLite.
RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

# Upgrade pip.
RUN pip install --upgrade pip

# Install Semaphore request anf llama_cpp.
RUN pip install --no-cache-dir semaphore-bot==v0.16.0 requests transformers sentencepiece protobuf jinja2

# Copy bot script and SQLite handler script.
COPY perroquet.py perroquet.py
COPY sqlite_handler.py sqlite_handler.py
COPY interrogation_Vigogne.py interrogation_Vigogne.py

# Start the bot.
CMD ["python", "perroquet.py"]
