FROM python:3.9

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


#gunicorn is listening on port 8000 and will pass anything that comes to the fastapi code

#running python app and binding web server to port 80 on the container port
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80", "--timeout", "300", "main:app"] 