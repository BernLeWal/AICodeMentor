# Dockerfile
FROM ubuntu:24.10

ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update && \
    apt-get install -y openssh-server sudo && \
    apt-get install -y curl git wget procps lsb-release jq lynx iputils-ping iproute2

# Install OpenJDK 21 - see https://www.tecmint.com/install-java-on-debian-12/
RUN wget https://download.oracle.com/java/21/latest/jdk-21_linux-x64_bin.deb && \
    dpkg -i jdk-21_linux-x64_bin.deb && \
    rm jdk-21_linux-x64_bin.deb && \
    java -version

RUN apt-get -y install maven


#RUN mkdir /var/run/sshd
RUN useradd -m -s /bin/bash mentor && \
    echo "mentor ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    mkdir -p /home/mentor/.ssh && \
    chmod 700 /home/mentor/.ssh && \
    chown mentor:mentor /home/mentor/.ssh

WORKDIR /home/mentor

## Prepare the Maven local repository caches (may speed up the build later on)
COPY docker/shellbox-java/pom.xml /home/mentor/pom.xml
RUN mvn dependency:go-offline
RUN rm /home/mentor/pom.xml


# Add public key (will be mounted via volume or during build)
COPY docker/shellbox-java/ssh_keys/authorized_keys /home/mentor/.ssh/authorized_keys
RUN chmod 600 /home/mentor/.ssh/authorized_keys && \
    chown mentor:mentor /home/mentor/.ssh/authorized_keys


# Configure SSH to allow key auth and avoid pam issues
RUN sed -i 's/#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config && \
    sed -i 's/#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config && \
    sed -i 's/#\?PubkeyAuthentication.*/PubkeyAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' /etc/pam.d/sshd

RUN echo "-s" > .curlrc

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D", "-e", "-o", "LogLevel=VERBOSE"]

# Set the entry point to keep the container alive
#CMD ["tail", "-f", "/dev/null"]