FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get -y install --no-install-recommends \
      curl git wget procps lsb-release jq lynx iputils-ping iproute2 && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Create "mentor" user (we won't rely on this UID at runtime on OpenShift) -
RUN useradd -ms /bin/bash mentor

# Keep app under /opt/mentor and the expected paths under /home/mentor
RUN mkdir -p /opt/mentor \
    && mkdir -p /home/mentor/workflows \
    && mkdir -p /var/log/mentor

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
RUN touch /var/log/mentor/codementor.log
RUN chown -R mentor:mentor /var/log/mentor
ENV LOGFILES_DIR=/var/log/mentor

# SSH keys (used by your app) required for shellbox
# TODO: On OpenShift restricted SCC, *baked-in* private keys are discouraged. Prefer mounting as a Secret
COPY secrets/ssh_keys /home/mentor/.ssh
# Ensure the .ssh directory has the correct permissions
RUN chown -R mentor:mentor /home/mentor/.ssh && \
    chmod 700 /home/mentor/.ssh && \
    chmod 600 /home/mentor/.ssh/*

# OpenShift arbitrary-UID friendliness
# 1) Place group ownership to 0 (root group).
# 2) Mirror user perms to group (g=u) so the random UID (with fsGroup 0) can access.
# 3) Add setgid (g+s) on directories so new files/dirs keep group 0.
# 4) Ensure /home/mentor itself is traversable (g+rx) so subpaths are reachable.
# 5) DO NOT relax ~/.ssh beyond 700/600; keep SSH strict. Keys should ideally be mounted.
RUN chgrp -R 0 /opt/mentor /home/mentor /var/log/mentor && \
    chmod -R g=u /opt/mentor /var/log/mentor && \
    find /opt/mentor /var/log/mentor -type d -exec chmod g+xs {} \; && \
    chmod g+rx /home/mentor && \
    chmod -R g=u /home/mentor/workflows && \
    find /home/mentor/workflows -type d -exec chmod g+xs {} \; && \
    # keep SSH strict (do not make group-writable)
    chmod 700 /home/mentor/.ssh && chmod 600 /home/mentor/.ssh/*

ENV SHELLBOX_SSH_KEYFILE=/home/mentor/.ssh/ssh_mentor_key
ENV SHELL=/bin/bash
# Set HOME so apps relying on $HOME behave consistently under arbitrary UID
ENV HOME=/home/mentor \
    SHELL=/bin/bash

RUN echo "-s" > /home/mentor/.curlrc || true

# Use a non-root default. OpenShift will override to an arbitrary, non-root UID.
USER mentor

EXPOSE 5000

# Set the default entry point
ENTRYPOINT ["python", "app/main.py"]

# Set the entry point to keep the container alive
#CMD ["tail", "-f", "/dev/null"]