import * as pulumi from '@pulumi/pulumi';
import * as docker from "@pulumi/docker";
import * as k8s from '@pulumi/kubernetes';
import * as kx from '@pulumi/kubernetesx';
import TraefikRoute from './TraefikRoute';

// Load configuration
const config = new pulumi.Config();
const baseStack = new pulumi.StackReference(config.require('baseStackName'));

// Create Kubernetes provider
const provider = new k8s.Provider('k8s-provider', {
    kubeconfig: baseStack.requireOutput('kubeconfig'),
});

const dockerImage = new docker.Image("{{cookiecutter.project_slug}}-image", {
    imageName: "{{cookiecutter.project_slug}}-image",
    build: {
        context: "../", // path to your Dockerfile
    },
    registry: {
        server: baseStack.requireOutput('registryUrl'),
        username: baseStack.requireOutput('adminUsername'),
        password: baseStack.requireOutput('adminPassword'),
    },
});

// Kubernetes Deployment
const podBuilder = new kx.PodBuilder({
    containers: [{
        image: dockerImage.imageName,
        ports: { http: 8000 },
        env: {
            'LISTEN_PORT': '8000',
            'MLFLOW_TRACKING_URI': 'http://minimlstack.duckdns.org/mlflow',
            'MLFLOW_RUN_ID': config.require('runID'),
            'AZURE_STORAGE_CONNECTION_STRING': config.require('azureStorageConnectionString')
        }
    }],
});

const deployment = new kx.Deployment('{{cookiecutter.project_slug}}-serving', {
    spec: podBuilder.asDeploymentSpec({ replicas: 2 }) 
}, { provider });


// Create a Horizontal Pod Autoscaler
const hpa = new k8s.autoscaling.v2.HorizontalPodAutoscaler("{{cookiecutter.project_slug}}-hpa", {
    spec: {
        scaleTargetRef: {
            apiVersion: "apps/v1",
            kind: "Deployment",
            name: deployment.metadata.name,
        },
        maxReplicas: 5,
        metrics: [{
            type: "Resource",
            resource: {
                name: "cpu",
                target: {
                    type: "Utilization",
                    averageUtilization: 50,
                },
            },
        }],
    },
}, { provider });

const service = deployment.createService();

new TraefikRoute(
    '{{cookiecutter.project_slug}}',
    {
      prefix: "/models/{{cookiecutter.project_slug}}",
      service,
      namespace: "default",
    },
    { provider: provider, dependsOn: [service] }
  );
  

// Outputs
export const deploymentName = deployment.metadata.name;
export const serviceName = service.metadata.name;