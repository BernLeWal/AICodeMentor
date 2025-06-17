FROM python:3.12-slim

RUN apt-get update && \
    apt-get -y install curl git wget procps lsb-release jq lynx

RUN pip install --upgrade pip

# AIMentor will run as a non-root user
RUN useradd -ms /bin/bash mentor

WORKDIR /home/mentor

COPY requirements.txt /home/mentor
RUN pip install --no-cache-dir -r requirements.txt

COPY app /home/mentor/app
COPY workflows /home/mentor/workflows

# Copy the .env file (optional, but you can override it with docker run or volumes)
#COPY .env /home/mentor/.env

# Change ownership of the app directory to the "mentor" user
RUN chown -R mentor:mentor /home/mentor/app
RUN chown -R mentor:mentor /home/mentor/workflows

RUN mkdir -p /home/mentor/log && chown mentor:mentor /home/mentor/log


# Switch to the "mentor" user
USER mentor

RUN touch /home/mentor/log/codementor.log

ENV PYTHONPATH=/home/mentor
ENV WORKFLOWS_DIR=/home/mentor/workflows


RUN echo "-s" > .curlrc

EXPOSE 5000

# Set the default entry point
ENTRYPOINT ["python", "app/main.py"]

# Set the entry point to keep the container alive
#CMD ["tail", "-f", "/dev/null"]