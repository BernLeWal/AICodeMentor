# AI CodeMentor

This image contains the tools required for Java for AI CodeMentor supporting Java and Maven.

It additionally prepares the Maven local repo cache with: Sprint Boot 3, OpenAPI 3 and further often used libraries.
ATTENTION: if the java-project uses dynamic versions (aka "LATEST") or SNAPSHOT versions, then Maven will still reload all dependencies from remote repos.

## Setup

Execute this **once on your host machine** to generate a key pair and prepare the 'authorized_keys' file:

Run the following commands from the current directory (./docker/shellbox-java):
```bash
cd ssh_keys

# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -C "mentor@aicodementor" -f ssh_mentor_key

# Create authorized_keys file
cp ssh_mentor_key.pub authorized_keys

cd ..
```

Ensure the ssh_keys/authorized_keys file is in the same directory as the Dockerfile before building the container.

## Build Docker Image

From the project root directory run the following command:
```shell
docker build -t shellbox-java -f docker/shellbox-java/Dockerfile .
```

## Run & Test the Docker Container
Run the container with a fixed port mapping:
```shell
docker run -d -p 2223:22 --name shellbox-java shellbox-java
```

Test the container login using from the project root directory:
```bash
ssh -i secrets/ssh_keys/ssh_mentor_key -p 2223 mentor@localhost
```
If it logs in without a password, the configuration is correct.

