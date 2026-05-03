# Use a lightweight Python 3.11 image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the dependency list first to leverage Docker's caching
COPY requirements.txt .

# Install necessary libraries
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# DigitalOcean requires the app to listen on port 8080
EXPOSE 8080

# Execute the main career_hub_app.py
# --server.port 8080 is mandatory for the health checks to pass
# --server.address 0.0.0.0 ensures the app is accessible outside the container
CMD ["streamlit", "run", "career_hub_app.py", "--server.port", "8080", "--server.address", "0.0.0.0"]