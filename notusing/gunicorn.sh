#!/bin/bash

# Activate your virtual environment, if applicable
source ssenv/bin/activate


# Start Gunicorn with Uvicorn workers
gunicorn main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000