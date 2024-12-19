## Setup
1. Install Poetry https://python-poetry.org/docs/#installation
2. Run `poetry install`
    - Might have to run `poetry cache clear pypi --all` and `poetry cache clear virtualenvs --all` first
3. Go into `infra` directory and run `npm i --force`
    - Might have to run `npm cache clean --force`
4. Install Docker and Docker Desktop
5. Make sure you have a Docker Hub account
6. Add whatever packages you need using `poetry add <package name>`

## Training Model
1. Set `MLFLOW_TRACKING_URI` and `AZURE_STORAGE_CONNECTION_STRING` environment variables with the corresponding values through terminal
    - Do not set these values with double quotes surrounding!
2. Run `poetry run train`

## Serving Model
1. Set `MLFLOW_RUN_ID`, `AZURE_STORAGE_CONNECTION_STRING`, and `MLFLOW_TRACKING_URI` through terminal then run `poetry run serve`
2. To run serving container locally 
    - Build the Docker image first using `docker build . -t <image name>`
        - Note that building the image may not work if you are currently running an experiment.
    - run `docker run -e MLFLOW_RUN_ID=<run id> -e AZURE_STORAGE_CONNECTION_STRING=<connection string> -e MLFLOW_TRACKING_URI=<mlflow uri> -p <local port>:<app port in container> <image name>` 

### Deploying with Pulumi
1. Make sure Docker Desktop is running
2. Select `<create a new stack>` and follow instructions
3. Set the `azureStorageConnectionString` using `pulumi config set --secret azureStorageConnectionString <connection string>`
4. Run `pulumi config set <config property> <config value>` for each required config property in `index.ts`
    - `pulumi config set baseStackName <name of Pulumi stack that setup the Kubernetes cluster>`
        - A stack reference's name should be of the form `<organization>/<project>/<stack>`
    - `pulumi config set dockerUsername <username>`
    - `pulumi config set port <port number>`
    - `pulumi config set mlflowURI <MLflow URI>`
    - `pulumi config set runID <ID of the MLflow run>`
5. Run `pulumi up --yes --skip-preview`
    - Note that it may take more than one try to get this working. Run `pulumi cancel` if stuck.
    - Note that creating the pod may result in Pulumi saying failed because it timed out, but it still ends up being created on your AKS.

## Deleting Deployed Model
Comment out everything in `index.ts` and run `pulumi up --yes --skip-preview`. Pulumi will detect everything is gone and remove the appropriate resources from Azure.
