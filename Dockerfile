FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Force the PORT variable into a start script to ensure DO binds to it
RUN echo '#!/bin/bash\nstreamlit run app.py --server.port=${PORT:-8080} --server.address=0.0.0.0 --server.headless=true' > start_app.sh
RUN chmod +x start_app.sh

# Use the script as the entrypoint
CMD ["./start_app.sh"]
