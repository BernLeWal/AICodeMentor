FROM python:3.12-slim

RUN apt-get update && \
    apt-get -y install curl git wget procps

# Install OpenJDK 21 - see https://www.tecmint.com/install-java-on-debian-12/
RUN wget https://download.oracle.com/java/21/latest/jdk-21_linux-x64_bin.deb && \
    dpkg -i jdk-21_linux-x64_bin.deb && \
    rm jdk-21_linux-x64_bin.deb && \
    java -version

RUN apt-get -y install maven

RUN pip install --upgrade pip

# AIMentor will run as a non-root user
RUN useradd -ms /bin/bash mentor

WORKDIR /home/mentor

COPY requirements.txt /home/mentor
RUN pip install --no-cache-dir -r requirements.txt

COPY app /home/mentor/app

# Copy the .env file (optional, but you can override it with docker run or volumes)
COPY .env /home/mentor/.env

## Prepare the Maven local repository caches (may speed up the build later on)
#COPY docker/codementor-java/pom.xml /home/mentor/pom.xml
#RUN mvn dependency:go-offline
#RUN rm /home/mentor/pom.xml


# Change ownership of the app directory to the "mentor" user
RUN chown -R mentor:mentor /home/mentor/app

RUN mkdir -p /home/mentor/output && chown mentor:mentor /home/mentor/output
RUN mkdir -p /home/mentor/log && chown mentor:mentor /home/mentor/log
RUN touch /home/mentor/log/codementor.log


# Switch to the "mentor" user
USER mentor

ENV PYTHONPATH=/home/mentor

RUN echo "-s" > .curlrc

# Set the default entry point
ENTRYPOINT ["python", "app/main.py"]

# Set the entry point to keep the container alive
#CMD ["tail", "-f", "/dev/null"]