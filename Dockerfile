FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if any are needed (fpdf2 works purely in python, but good practice)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

COPY . .

# We use python bot.py as the entrypoint
CMD ["python", "-u", "bot.py"]
