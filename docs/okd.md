# Deploy and Run on OKD / OpenShift

### 1. Pre-Requisites

- A **OKD** / **OpenShift**-Cluster must be installed, and the ```kubectl``` tool available.  

- The OpenShift CLI ```oc```must be installed

    Installation instructions: https://docs.okd.io/latest/cli_reference/openshift_cli/getting-started-cli.html

    Verify availability using
    ```shell
    $ oc version
    Client Version: 4.17.0
    Kustomize Version: v5.0.4-0.20230601165947-6ce0bf390ce3
    Kubernetes Version: v1.29.2
    ```

### 2. Login

* Login to the Web-Console of OKD/OpenShift

* Generate the token
You may generate your login command including creation of the requested API token via Web Console easily via the the web-console:
    - Click on the down-arrow right beside your Username
    - Select command "Copy login command"
    - Copy the receiving token and CURL snippet

* Login the CLI tool
    ```shell
    oc login --token=<your-token> --server=<your-server>
    ```

* Verify that you are working on the correct cluster:
    ```shell
    $ oc config current-context
    ```

### 3. Create or select project "AI CodeMentor"

- To create a new project:
    ```shell
    $ oc new-project inno-ai-codementor
    Now using project "inno-ai-codementor" on server "https:<your-server>:6443".
    ```

- If the project is already existing use:
    ```shell
    oc project inno-ai-codementor
    ```

- To delete the project and remove everything from OKD use:
    ```shell
    oc delete project inno-ai-codementor
    ```

### 3. Create the secrets

Use the following command and replace the <> sections with your secrets defined in your [.env](.env) file:

```shell
oc create secret generic openapi-secret \
    --from-literal=OPENAI_API_KEY=<your-openai-key> \
    --from-literal=OPENAI_ORGANIZATION_ID=<your-openai-org> 
```

### 4. Optional: Update/Create Kubernetes Resource Files for OKD

If you change anything in the docker-compose.yml or in the .env file, then you MUST rebuild the Kubernete Resources files as follows:

The directory ./okd/ must exist before running the following command:

```shell
docker compose -f docker-compose-production.yml config > docker-compose-k8s.yml
kompose convert -f docker-compose-k8s.yml --out okd/
```
This will generate seperate files for all resource objects in the subdirectory okd/.  

**Attention: Double-Check the generated output files in okd/ with git diff, because in the git repo there are
special settings required for the OKD cluster which have to be merged (manually)!**

For additional information about the kustomization.yaml see: https://www.densify.com/kubernetes-tools/kustomize/

Remarks: For OKD of FHTW 
1. the Resource Quotas of all Deployments must be set to >0 (cores, memory,...), e.g.
    - CPU request 100 millicores
    - CPU limit 1 cores
    - Memory request 512 Mi
    - Memory limit 512 Mi

2. the StorageClass of all presistentvolumeclaims must be set to nfs-research
    - storageClassName: nfs-research

3. create a [okd/kustomization.yaml](../okd/kustomization.yaml) file:
    ```yaml
    kind: Kustomization
    apiVersion: kustomize.config.k8s.io/v1beta1
    resources:
    - codementor-service.yaml
    - #... add all files in the /okd directory
    ```

4. create a [okd/codementor-route.yaml](../okd/codementor-route.yaml) 

### 5. Import docker.io images into OKD repository

* Optional: Create & Link Secret for docker.io
    ```shell
    oc create secret docker-registry dockerhub-secret \
    --docker-server=docker.io \
    --docker-username=<Your Username> \
    --docker-password=<Your Password> \
    --docker-email=<Your EMail>

    oc secrets link default dockerhub-secret --for=pull
    ```

* Optional: to delete the secret
    ```shell
    oc delete secret dockerhub-secret
    ```

* To verify the serviceaccount:

    ```shell
    $ oc describe serviceaccount default
    ```

* Import Docker Images
    ```shell
    oc import-image codementor:latest --from=docker.io/codepunx/codementor:latest --confirm
    oc import-image shellbox-java:latest --from=docker.io/codepunx/shellbox:latest --confirm
    ```

    Remark: To change the image source later, you need to use the ```oc tag``` command, e.g.
    ```shell
    oc tag docker.io/codepunx/codementor:latest codementor:latest --reference-policy=source
    oc tag docker.io/codepunx/shellbox-java:latest shellbox-java:latest --reference-policy=source
    ```


### 6. Deploy Kubernetes Resources

* Deploy Application Resources
    ```shell
    oc apply -k okd
    ```

* Verify the Pods are running
    ```shell
    oc get pods
    ```
    with more details
    ```shell
    oc get po,svc,ep --show-labels
    ```

* Retrieve the exposed services which may be accessed from external:
    ```shell
    $ oc get route
    NAME      HOST/PORT                                                              PATH   SERVICES   PORT   TERMINATION   WILDCARD
    ...
    ```
    - Open the Web-Site using the link provided.

* Remove Application Resources
    ```shell
    oc delete -k okd
    ```

### 7. Troubleshooting

* PersistentVolumeClaims not found after re-deploy:
    Sometimes it happens, that when re-deploying a new version that the persistent-volume-claims are not generated. In that case to it manually:

    ```sh
    oc apply -f okd/codementor-data-persistentvolumeclaim.yaml 
    oc apply -f okd/codementor-log-persistentvolumeclaim.yaml 
    ```
    ... and then redeploy the codementor pod.
