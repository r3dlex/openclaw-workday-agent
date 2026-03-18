FROM python:3.12-slim

# System deps for Playwright browsers
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.2

# Set up working directory
WORKDIR /app

# Copy dependency spec first for layer caching
COPY pyproject.toml ./

# Install Python dependencies (no virtualenv inside container)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Install Playwright Chromium and its system dependencies
RUN playwright install --with-deps chromium

# Copy application source
COPY pipeline_runner/ ./pipeline_runner/

# Install the project itself
RUN poetry install --no-interaction --no-ansi

# Create non-root user
RUN useradd --create-home runner
USER runner

ENTRYPOINT ["python", "-m", "pipeline_runner"]
