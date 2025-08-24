FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install runtime dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copy project code into the container
COPY . /app

# When building the image we need a secret key to run collectstatic.
# Accept a build‑time argument and default to a dummy value.  At runtime,
# Django will read DJANGO_SECRET_KEY from the environment.
ARG BUILD_DJANGO_SECRET_KEY=dummy-secret-key
RUN DJANGO_SECRET_KEY=$BUILD_DJANGO_SECRET_KEY DJANGO_DEBUG=False python manage.py collectstatic --noinput

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]