# Grab Python image.
FROM python:3.9.12-slim-bullseye

WORKDIR /semaphore

# Upgrade pip.
RUN pip install --upgrade pip

# Install Semaphore.
RUN pip install --no-cache-dir semaphore-bot==v0.16.0 requests

# Copy bot script.
COPY perroquet.py perroquet.py

# Start the bot.
CMD ["python", "perroquet.py"]
