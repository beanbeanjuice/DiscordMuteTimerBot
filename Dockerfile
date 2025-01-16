# Use a Python base image
FROM python:alpine

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your bot's code
COPY . .

# Run your bot
CMD ["python", "bot.py"]
