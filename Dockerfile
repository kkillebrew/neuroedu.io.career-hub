# Use a lightweight Python 3.11 image
FROM python:3.11-slim

# Install system dependencies required for compiling heavy data libraries
# MATLAB Analogy: This is like installing the C/C++ MinGW or Fortran Compiler Add-on 
# into MATLAB so you can compile custom MEX files from source code.
RUN apt-get update && apt-get install -y \
    build-essential \
    gfortran \
    pkg-config \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

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