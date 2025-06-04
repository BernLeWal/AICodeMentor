# Dockerfile
FROM ubuntu:24.10

ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update && \
    apt-get install -y openssh-server sudo && \
    apt-get install -y curl git wget procps lsb-release jq lynx

#RUN mkdir /var/run/sshd
RUN useradd -m -s /bin/bash mentor && \
    echo "mentor ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    mkdir -p /home/mentor/.ssh && \
    chmod 700 /home/mentor/.ssh && \
    chown mentor:mentor /home/mentor/.ssh

# Add public key (will be mounted via volume or during build)
COPY docker/shellbox/ssh_keys/authorized_keys /home/mentor/.ssh/authorized_keys
RUN chmod 600 /home/mentor/.ssh/authorized_keys && \
    chown mentor:mentor /home/mentor/.ssh/authorized_keys

# Configure SSH to allow key auth and avoid pam issues
RUN sed -i 's/#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config && \
    sed -i 's/#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config && \
    sed -i 's/#\?PubkeyAuthentication.*/PubkeyAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' /etc/pam.d/sshd

RUN echo "-s" > .curlrc

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
