# Use the official lightweight Python image.
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app's code
COPY . .

# Streamlit uses 8501 by default, but DigitalOcean prefers 8080
EXPOSE 8080

# Command to run the app
CMD ["streamlit", "run", "app.py", "--server.port