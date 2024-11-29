## Setup
1. Install Poetry https://python-poetry.org/docs/#installation
2. Run `poetry install`
    - Might have to run `poetry cache clear pypi --all` and `poetry cache clear virtualenvs --all` first
3. Go into `infra` directory and run `npm i --force`
    - Might have to run `npm cache clean --force`
4. Install Docker and Docker Desktop
5. Make sure you have a Docker Hub account

## Training Model
1. Set `MLFLOW_TRACKING_URI` and `AZURE_STORAGE_CONNECTION_STRING` environment variables with the corresponding values through terminal
2. Run `poetry run train`

## Serving Model
1. To run serving container locally 
    - Build the Docker image first using `docker build . -t <image name>`
    - run `docker run -e MLFLOW_RUN_ID=<run id> -e AZURE_STORAGE_CONNECTION_STRING=<connection string> -e MLFLOW_TRACKING_URI=<mlflow uri> -p <local port>:<app port in container> <image name>` 

### Deploying with Pulumi
1. Make sure Docker Desktop is running
1. Set the `azureStorageConnectionString` using `pulumi config set --secret azureStorageConnectionString <connection string>`
2. Add other fields directly into the generated yaml file that has all the config properties, or run `pulumi config set <config property> <config value>` for each required config property in `index.ts`
3. Run `pulumi up --yes --skip-preview`

## Deleting Deployed Model
Comment out everything in `index.ts` and run `pulumi up --yes --skip-preview`. Pulumi will detect everything is gone and remove the appropriate resources from Azure.
