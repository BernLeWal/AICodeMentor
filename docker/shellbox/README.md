# SSH-Server with Ubuntu 24 LTS
for using as remote command executor

## Setup

Execute this **once on your host machine** to generate a key pair and prepare the 'authorized_keys' file:

Run the following commands from the `/secrets/ssh_keys` directory (./secrets/ssh_keys):
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
docker build -t shellbox -f docker/shellbox/Dockerfile .
```

## Run & Test the Docker Container
Run the container with a fixed port mapping:
```shell
docker run -d -p 2222:22 --name shellbox shellbox
```

Test the container login using from the project root directory:
```bash
ssh -i secrets/ssh_keys/ssh_mentor_key -p 2222 mentor@localhost
```
If it logs in without a password, the configuration is correct.

