FROM python:3.11-slim

WORKDIR /src

# Install system dependencies
RUN sed -i 's|deb.debian.org|mirror.yandex.ru|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || true && \
    apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt /src/

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /src/

# Collect static files
RUN python manage.py collectstatic --noinput

# Run ASGI server
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "arabica.asgi:application"]
