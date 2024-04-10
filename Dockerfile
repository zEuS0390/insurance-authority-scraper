FROM debian:latest

WORKDIR /insurance_authority_scraper

# Copy the entire directory into the container
COPY . .

# Install system dependencies
RUN apt-get update -y && \
    apt-get install -y \
    python3-pip \
    python3-virtualenv \
    curl \
    jq \
    tesseract-ocr firefox-esr

# Install geckodriver
RUN /bin/bash install_geckodriver.sh

# Create and activate Python virtual environment, and install Python dependencies
RUN python3 -m virtualenv .venv/ && .venv/bin/pip install -r requirements.txt

# Set the default command to run when the container starts
CMD [".venv/bin/python3", "main.py"]
