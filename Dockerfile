# Use the official Python image from the Docker Hub, specifying Python 3.11.4
FROM python:3.11.4-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install Java SDK (OpenJDK 11)
RUN apt-get update && apt-get install -y openjdk-11-jdk && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME environment variable
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Copy the requirements.txt file (if you have one) and install dependencies
COPY requirements.txt .

# Install any Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code to the container
COPY . .

# Use ENTRYPOINT to allow passing arguments to the Python script
ENTRYPOINT ["python", "logD_predictor.py"]
