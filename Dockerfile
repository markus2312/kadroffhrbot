FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl

# Установка Xray (Linux amd64)
RUN curl -L -o /usr/local/bin/xray https://github.com/XTLS/Xray-core/releases/latest/download/xray-linux-64.zip && \
    apt-get install -y unzip && \
    unzip xray-linux-64.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/xray && \
    rm xray-linux-64.zip

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
