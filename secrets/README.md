# Secrets

* Put your credential and secret files here.

## Setup shellbox containers

Execute this **once on your host machine** to generate a key pair and prepare the 'authorized_keys' file, which has to be provided for the [shellbox](../docker/shellbox/Dockerfile):

Run the following commands from the `/secrets` directory:
```bash
mkdir ssh_keys
cd ssh_keys

# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -C "mentor@aicodementor" -f ssh_mentor_key

# Create authorized_keys file
cp ssh_mentor_key.pub authorized_keys

cd ..
```

