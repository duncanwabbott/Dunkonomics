FROM python:3.9-slim

WORKDIR /app

# Install system dependencies if any are needed (Streamlit sometimes needs these)
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

# Expose the port DigitalOcean expects
EXPOSE 8080

# Run the application
CMD sh -c "streamlit run app.py --server.port=${PORT:-8080} --server.address=0.0.0.0"
