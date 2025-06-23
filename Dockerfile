FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-root
COPY . .
ENV TZ="Europe/Moscow"
ENV PYTHONPATH=/app
CMD poetry run python src