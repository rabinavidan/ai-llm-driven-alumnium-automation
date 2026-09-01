FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencies first for better layer caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Test sources
COPY . .

# Results are written here and bind-mounted out via docker-compose
VOLUME ["/app/allure-results"]

# Default: run the whole suite. Override in compose / CLI, e.g. `-m smoke`.
CMD ["pytest"]
