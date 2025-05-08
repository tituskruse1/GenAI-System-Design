FROM python:3.13-bookworm

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY app/ .


RUN pip install -r requirements.txt

RUN chmod +x entrypoint.sh

EXPOSE  8000
ENTRYPOINT ["./entrypoint.sh"]