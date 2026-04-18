# --- Stage 1: Build Frontend ---
FROM node:20-slim AS frontend-build
WORKDIR /app/web
COPY web/package*.json ./
RUN npm install
COPY web/ ./
RUN npm run build

# --- Stage 2: Final Production Image ---
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# Copy backend source
COPY main.py .
COPY .env .
COPY src/ ./src/
COPY models/ ./models/
COPY data/processed/aggregated_data.csv ./data/processed/aggregated_data.csv

# Copy built frontend from Stage 1
COPY --from=frontend-build /app/web/dist ./web/dist

# Expose FastAPI port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Start the server (FastAPI)
CMD ["python", "main.py", "--mode", "serve"]
