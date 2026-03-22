FROM python:3.12

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the default app port
EXPOSE 8080

# Run the Flask app using the configured PORT env var when deployed
CMD ["python", "app.py"]
