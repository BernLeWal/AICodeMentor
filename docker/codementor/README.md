# AI CodeMentor Docker Image

This image contains the base tools for AI CodeMentor supporting the Python Tools and the Bash Commandshell.

## Pre-Requisites

- Generate your own .env file into the parent (docker/) directory, based on [../.env.sample](../.env.sample)

## Build the Docker Image

From the project root directory run the following command:
```shell
docker build -t codementor -f docker/codementor/Dockerfile .
```

## Run the Docker Container

```shell
docker run --name codementor --env-file docker/.env -p 5000:5000 codementor --server
```

CodeMentor will then run as server, so workflows can be executed and managed through the REST-API

## Use the REST-API provided by the Container

Entry Points:
* OpenAI Specification of the REST interface: [http://localhost:5000/openapi.yaml](http://localhost:5000/openapi.yaml)
* SwaggerUI: [http://localhost:5000/docs](http://localhost:5000/docs)
* You may use the browser as REST-Client:
    - **Login** before using the API (once per browser session): http://localhost:5000/auth?token=<SERVER_TOKEN>  
        The SERVER_TOKEN is defined in your [.env](../../.env) file
        On success a **Secure, HttpOnly, SameSite=Strict** cookie named ``auth_token`` is returned so that subsequent requests through the browser will be authenticated.
    - **Workfile Explorer**: http://localhost:5000/files
    - **History Explorer**: http://localhost:5000/history

* There are REST-Requests prepared for testing, see:
    - [test/api/rest-tests-api.http](../../test/api/rest-tests-api.http)
    - [test/api/rest-tests-files.http](../../test/api/rest-tests-files.http)
    - [test/api/rest-tests-workflow.http](../../test/api/rest-tests-workflow.http)
    - [test/api/rest-tests-log.http](../../test/api/rest-tests-log.http)
