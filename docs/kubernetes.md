# Deploy and Run on Kubernetes

### 1. Pre-Requisites:

- A **Kubernetes cluster** must be installed, and the ```kubectl``` tool available.  

- The **Kompose** tool to translate docker-compose.yml must be installed:  
    For linux:
    ```shell
    curl -L https://github.com/kubernetes/kompose/releases/download/v1.36.0/kompose-linux-amd64 -o kompose

    chmod +x kompose
    sudo mv ./kompose /usr/local/bin/kompose
    ```

* Optional: Update Images on Docker Hub
If codementor,.. source is changed you need to update the docker image on hub.docker.com, see [docker/CONTRIBUTION.md](../docker/CONTRIBUTION.md)  
For the demo [codepunx/codementor](https://hub.docker.com/repository/docker/codepunx/codementor/general) is used,
replace it with your own registry and update [docker-compose-production.yml](./docker-compose-production.yml).

    ```shell
    docker build -t codementor -f docker/codementor/Dockerfile .
    docker tag codementor codementor:latest
    docker tag codementor:latest codepunx/codementor:latest
    docker push codepunx/codementor:latest
    ```

    Remarks: do that for all necessary images (codementor, shellbox, codementor-cuda, shellbox-java,...) and with the version tags respecively.

### 2. Convert the docker-compose-production.yml to Kubernetes
```shell
docker compose config -f docker-compose-production.yml > docker-compose-k8s.yml 
kompose convert -f docker-compose-k8s.yml --out k8s/
```

### 3. Run in Kubernetes
```shell
kubectl apply -k k8s
```

### 4. Verify if pods are running
```shell
kubectl get pods
```
with more details
```shell
kubectl get po,svc,ep --show-labels
```

Check that all pods are in "Running" state

### 5. Access the Frontend
There are three possibilities:

1. Port-Forward on your local Kubernetes
    ```shell
    kubectl get pod | grep codementor
    # grab the full pod-name
    kubectl port-forward codementor-6bff6f6d8d-t9ttk 5000:5000
    ```
    Attention: as long as the kubectl port-forward command runs, 
    the website is accessible via http://localhost:5000.  
    As soon as you stop the command, it is no longer accessible.

2. NodePort Service
    Attention: this may not work in "Docker Desktop Kubernetes" (for whatever reason), in this case use port-forward

2. LoadBalancer Service
    Attention: this may not work in "Docker Desktop Kubernetes" (for whatever reason), in this case use port-forward

### 6. Stop pods in Kubernetes
```shell
kubectl delete -k k8s
```

Remarks: currently there are the following issues with k8s integration
- the network healthchecks do not work within kubernetes (and are therefore commented out)

see [Translate a Docker Compose File to Kubernetes Resources](https://kubernetes.io/docs/tasks/configure-pod-container/translate-compose-kubernetes/) 
