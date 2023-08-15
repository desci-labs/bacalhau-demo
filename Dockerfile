# Use an official Python runtime as the base image
FROM python:3.9.6

# Update the package list and install git
RUN apt-get update && apt-get install -y git

# Install LaTeX for matplotlib
RUN apt-get install -y texlive-latex-base texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra cm-super dvipng

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt in a separate layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of directory contents into the container
COPY . .

# Define the command to run your app using CMD
CMD ["python3", "main.py"]

