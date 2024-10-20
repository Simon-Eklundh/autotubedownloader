# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /
RUN apt-get update && apt-get install -y ffmpeg git
# Copy the current directory contents into the container at /app
RUN git clone https://github.com/Simon-Eklundh/autotubedownloader.git
WORKDIR /autotubedownloader

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Define environment variable
ENV NAME=autotubedownloader

# Run app.py when the container launches
CMD ["python", "src/main.py"]
