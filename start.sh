#!/bin/bash
export PORT=${PORT:-8080}
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
