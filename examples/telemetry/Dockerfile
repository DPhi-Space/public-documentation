FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir requests

COPY telemetry-api-client.py .

RUN mkdir -p /data

CMD ["python", "-u", "telemetry-api-client.py"]
