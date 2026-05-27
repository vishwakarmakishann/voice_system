FROM python:3.12-slim

# Install system dependencies (needed for compiling some python packages and for audio processing if required)
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements file
COPY requirements.txt ./requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY apps/api /app/apps/api

# Copy the entrypoint script
COPY apps/api/entrypoint.sh /app/apps/api/entrypoint.sh
RUN chmod +x /app/apps/api/entrypoint.sh

# Set PYTHONPATH so the imports work properly
ENV PYTHONPATH=/app/apps/api

# Use the entrypoint script
ENTRYPOINT ["/app/apps/api/entrypoint.sh"]

# Default command (can be overridden by docker-compose)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
