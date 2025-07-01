FROM python:3.10-slim-bullseye

ENV PYTHONBUFFERED 1
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /app
COPY . .
