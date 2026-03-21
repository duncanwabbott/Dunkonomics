#!/bin/bash
echo "--- INITIALIZING DUNKONOMICS SERVER ---"
export PORT=${PORT:-8080}
echo "Binding to DigitalOcean Port: $PORT"

# Run Streamlit with unbuffered output so logs instantly stream to DO dashboard
python3 -u -m streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false

echo "Streamlit process terminated with exit code $?"

# Keep the container artificially alive so DigitalOcean cannot exit with a zero code
echo "Entering deep sleep to preserve container logs for debugging..."
tail -f /dev/null
