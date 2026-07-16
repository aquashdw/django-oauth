FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev && \
    rm -rf /var/lib/apt/lists/*

FROM base AS deps

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

FROM deps AS runtime

COPY . .

RUN addgroup --system app && adduser --system --ingroup app app
RUN mkdir -p /app/media && chown -R app:app /app

USER app

EXPOSE 8000

CMD ["gunicorn", "django_oauth.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
