FROM python:3.13-bookworm

COPY requirements.txt .
COPY asgi_server.py .

RUN pip install -r requirements.txt


EXPOSE  8000
ENTRYPOINT ["python", "./asgi_server.py"]