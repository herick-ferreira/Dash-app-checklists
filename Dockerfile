FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

# Install system dependencies (if needed) and Python deps
COPY requirements.txt ./
COPY Exemplo.xlsx ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . /app

EXPOSE 8080

# Run with Gunicorn using the Flask server exposed by Dash (`app.server`)
CMD ["gunicorn", "app:server", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8"]
