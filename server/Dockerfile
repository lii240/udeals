# Use a base Python image
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy the application code into the container
COPY . /app

# Install dependencies into the virtual environment
RUN pip install --no-cache-dir -r requirements.txt

# Expose any necessary ports
EXPOSE 5001

# Define environment variable
ENV FLASK_APP=server.py
ENV FLASK_RUN_HOST=0.0.0.0

# Set the command to run your application
CMD ["python", "server.py"]