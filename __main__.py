import pulumi
from pulumi_gcp import cloudrun, config as gcp_config
from pulumi_gcp import artifactregistry

class CloudRunService(pulumi.ComponentResource):
    def __init__(self, name: str, args: dict, opts: pulumi.ResourceOptions = None):
        super().__init__("custom:index:CloudRunService", name, {}, opts)

        image_url = args["image_url"]
        container_port = int(args.get("container_port", 8080))
        cpu = int(args.get("cpu", 1))
        memory = args.get("memory", "1Gi")
        concurrency = int(args.get("concurrency", 50))
        message = args.get("message", "Hello from Cloud Run!")
        location = args["location"]
        project = args["project"]

        # Create a Cloud Run service definition.
        service = cloudrun.Service(
            f"{name}-service",
            location=location,
            template={
                "spec": {
                    "containers": [
                        {
                            "image": image_url,
                            "resources": {
                                "limits": {
                                    "memory": memory,
                                    "cpu": str(cpu),
                                },
                            },
                            "ports": [
                                {
                                    "container_port": container_port,
                                },
                            ],
                            "envs": [
                                {
                                    "name": "DUMMY_VAR",
                                    "value": "1",
                                },
                            ],
                        },
                    ],
                    "container_concurrency": concurrency,
                },
            },
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Create an IAM member to make the service publicly accessible.
        invoker = cloudrun.IamMember(
            f"{name}-invoker",
            location=location,
            service=service.name,
            role="roles/run.invoker",
            member="allUsers",
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.url = service.statuses.apply(lambda statuses: statuses[0].url)
        self.register_outputs({})

# Import the program's configuration settings.
config = pulumi.Config()
container_port = config.get_int("containerPort", 8080)
cpu = config.get_int("cpu", 1)
memory = config.get("memory", "1Gi")
concurrency = config.get_int("concurrency", 50)
custom_message = config.get("customMessage", "Hello from Pulumi Cloud Run!")

# Import the provider's configuration settings.
gcp_config = pulumi.Config("gcp")
location = gcp_config.require("region")
project = gcp_config.require("project")

# Hardcode the image URL since it's built manually
image_url = f"europe-west1-docker.pkg.dev/{project}/my-cloudrun-repo/my-app:latest"

# Instantiate the custom CloudRunService component
cloud_run_app = CloudRunService(
    "my-cloudrun-app",
    args={
        "image_url": image_url,
        "container_port": container_port,
        "cpu": cpu,
        "memory": memory,
        "concurrency": concurrency,
        "message": custom_message,
        "location": location,
        "project": project,
    },
)

# Export the URL of the service.
pulumi.export("url", cloud_run_app.url)

