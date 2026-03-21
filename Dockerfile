FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make the wrapper executable
RUN chmod +x run.sh

# Bypass all shell routing errors with a strict JSON entrypoint
ENTRYPOINT ["./run.sh"]
