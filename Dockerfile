# Use official Python slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install ffmpeg for yt-dlp
RUN apt-get update && apt-get install -y ffmpeg

# Copy bot code
COPY bot.py .

# Command to run the bot
CMD ["python", "bot.py"]
