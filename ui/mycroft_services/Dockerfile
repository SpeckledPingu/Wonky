# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY pyproject.toml .

# Install any needed packages specified in pyproject.toml
# We use pip to install the project dependencies.
# The --no-cache-dir option reduces the image size.
RUN pip install --no-cache-dir -e .[standard]

# Copy the rest of the application's source code from your host to your image filesystem.
COPY ./src /app/src

# Make port 8000 available to the world outside this container (for FastAPI)
# Make port 7241 available for the Burr UI
EXPOSE 8000
EXPOSE 7241

# The command to run when the container starts will be specified in docker-compose.yml
