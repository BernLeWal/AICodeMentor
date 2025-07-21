FROM python:3.13-slim

RUN apt-get update && \
    apt-get -y install curl git wget procps lsb-release jq lynx iputils-ping iproute2

RUN pip install --upgrade pip

# AIMentor will run as a non-root user
RUN useradd -ms /bin/bash mentor

# (Python) application installation into /opt/mentor
RUN mkdir -p /opt/mentor
WORKDIR /opt/mentor

COPY requirements.txt /opt/mentor
RUN pip install --no-cache-dir -r requirements.txt

COPY app /opt/mentor/app
RUN chown -R mentor:mentor /opt/mentor/app
ENV PYTHONPATH=/opt/mentor

# Working directory for the workflows
COPY workflows /home/mentor/workflows
RUN chown -R mentor:mentor /home/mentor/workflows
ENV WORKFLOWS_DIR=/home/mentor/workflows

# Logging 
RUN mkdir -p /var/log/mentor
RUN touch /var/log/mentor/codementor.log
RUN chown -R mentor:mentor /var/log/mentor
ENV LOGFILES_DIR=/var/log/mentor

# SSH keys required for shellbox
COPY secrets/ssh_keys /home/mentor/.ssh
# Ensure the .ssh directory has the correct permissions
RUN chown -R mentor:mentor /home/mentor/.ssh
RUN chmod 700 /home/mentor/.ssh && \
    chmod 600 /home/mentor/.ssh/*
ENV SHELLBOX_SSH_KEYFILE=/home/mentor/.ssh/ssh_mentor_key
ENV SHELL=/bin/bash


# Switch to the "mentor" user
USER mentor
RUN echo "-s" > /home/mentor/.curlrc

EXPOSE 5000

# Set the default entry point
ENTRYPOINT ["python", "app/main.py"]

# Set the entry point to keep the container alive
#CMD ["tail", "-f", "/dev/null"]