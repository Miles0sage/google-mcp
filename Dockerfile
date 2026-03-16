FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml .
COPY server.py .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir .[dev]

EXPOSE 8080

CMD ["python", "server.py"]