# Dockerfile
# Build: docker build -t email-triage-openenv .
# Run:   docker run -p 7860:7860 email-triage-openenv

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose the port Hugging Face Spaces uses
EXPOSE 7860

# Create a non-root user (security best practice)
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Start the FastAPI server
CMD ["python", "app.py"]
