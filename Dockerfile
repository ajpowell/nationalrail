FROM python:3.9-slim

# Create a non-root user to own the files and run our server
# Funky arguments to suppress prompting
RUN adduser --gecos "" --disabled-password  nationalrailboards
USER nationalrailboards
WORKDIR /home/nationalrailboard

# Copy the static website
# Use the .dockerignore file to control what ends up inside the image!
COPY ./national_rail_pipeline/ ./national_rail_pipeline/
COPY requirements.txt .
COPY railtimes.py .
COPY run_poll.sh .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5000

ENV LDB_TOKEN=''
ENV AZURE_STORAGE_CONNECTION_STRING=''
ENV CRS=''
ENV POLL_INTERVAL=120

# Run BusyBox httpd
CMD ["/bin/bash", "-c", "./run_poll.sh"]

# Build with:
# podman build -t nationarailboards:latest . 
#
# Run interactively with:
# podman run -it --rm -p 5000:5000 -e LDB_TOKEN='00000000-0000-0000-0000-000000000000' --name nationarailboards nationarailboards:latest

# Run as a daemon with:
# podman run -d --rm -p 5000:5000 -e LDB_TOKEN='00000000-0000-0000-0000-000000000000' --name nationarailboards nationarailboards:latest