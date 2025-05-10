#!/bin/bash

# Kill existing Streamlit processes
echo "Stopping existing Streamlit processes..."
pkill -f streamlit

# Wait a moment for processes to stop
sleep 2

# Install dependencies
echo "Installing dependencies..."
poetry install

# Start the application with a new port and PYTHONPATH
echo "Starting the application..."
PYTHONPATH=$PYTHONPATH:$(pwd) poetry run streamlit run app/main.py --server.port 8501 