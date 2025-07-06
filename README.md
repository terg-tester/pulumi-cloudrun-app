# GCP Cloud Run Web Application Deployment with Pulumi

This project demonstrates how to deploy a simple web application to Google Cloud Run using Pulumi, a modern infrastructure as code platform. The application displays a configurable message on a web page.

## Task Description

The goal was to implement a web application running in a managed container service (GCP Cloud Run) using Pulumi. Key requirements included:
*   A `Dockerfile` to build a custom Docker image.
*   Deployment to GCP Cloud Run.
*   Utilization of relevant cloud provider resources.
*   A configurable value (via Pulumi config) that changes the message displayed on the web page.
*   A `ComponentResource` to illustrate reusability.

## Project Structure

```
pulumi-cloudrun-app/
├── __main__.py           # Pulumi program defining the infrastructure
├── app.py                # Python Flask web application
├── Dockerfile            # Defines the Docker image for the web application
├── requirements.txt      # Python dependencies for the web application
├── Pulumi.yaml           # Pulumi project definition
├── Pulumi.dev.yaml       # Pulumi stack configuration for 'dev' environment
└── implementation_steps.txt # Detailed log of implementation steps and troubleshooting
```

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
*   [Pulumi CLI](https://www.pulumi.com/docs/get-started/install/)
*   [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
*   [Docker](https://docs.docker.com/get-docker/) (if building images locally, though Cloud Build is used here)
*   [Minikube](https://minikube.sigs.k8s.io/docs/start/) (if using local Kubernetes/Docker daemon)
*   [Python 3.9+](https://www.python.org/downloads/)
*   [GitHub CLI](https://cli.github.com/) (for pushing code to GitHub)

### Configuration

1.  **Authenticate Google Cloud SDK:**
    ```bash
    gcloud auth login
    gcloud config set project YOUR_GCP_PROJECT_ID
    gcloud config set compute/region europe-west1 # Or your preferred region
    ```

2.  **Authenticate Docker for Artifact Registry:**
    ```bash
    gcloud auth configure-docker europe-west1-docker.pkg.dev
    ```

3.  **Pulumi Configuration:**
    Navigate to the `pulumi-cloudrun-app` directory:
    ```bash
    cd pulumi-cloudrun-app
    ```
    Set your GCP project and region for Pulumi:
    ```bash
    pulumi config set gcp:project YOUR_GCP_PROJECT_ID --stack dev
    pulumi config set gcp:region europe-west1 --stack dev
    ```
    Set the custom message for your web application:
    ```bash
    pulumi config set customMessage "Hello from Pulumi Cloud Run!" --stack dev
    ```

### Deployment

1.  **Build and Push Docker Image (using Google Cloud Build):**
    Due to potential local Docker environment issues, we use Google Cloud Build to build and push the Docker image directly to Google Artifact Registry.
    ```bash
    gcloud builds submit --tag europe-west1-docker.pkg.dev/YOUR_GCP_PROJECT_ID/my-cloudrun-repo/my-app:latest .
    ```
    Replace `YOUR_GCP_PROJECT_ID` with your actual GCP project ID.

2.  **Deploy with Pulumi:**
    ```bash
    pulumi up --yes
    ```
    This command will deploy the Cloud Run service and associated resources. Upon successful deployment, Pulumi will output the URL of your deployed application.

### Testing the Configurable Message

To change the message displayed on the web page:

1.  **Update the Pulumi configuration:**
    ```bash
    pulumi config set customMessage "Your New Custom Message Here!" --stack dev
    ```

2.  **Run Pulumi Up:**
    ```bash
    pulumi up --yes
    ```
    Pulumi will detect the change in the `customMessage` and force a new revision of the Cloud Run service, updating the message.

3.  **Verify:**
    Access the URL outputted by `pulumi up` in your browser or using `curl`. The new message should be displayed.

## Lessons Learned (from a Gemini CLI Agent's Perspective)

This project was primarily implemented with the assistance of a Gemini CLI agent, operating within a Linux environment. While the core task was straightforward, several challenges arose, highlighting the complexities of interacting with diverse local development environments and cloud services.

### Key Challenges & Human Intervention Points:

1.  **Docker Permissions & Minikube Integration:**
    *   **Problem:** Persistent `permission denied` errors when attempting to interact with the Docker daemon, both directly and via Pulumi's `docker_build` provider. This was exacerbated by Docker running within Minikube's VM, leading to issues with `docker.sock` permissions and environment variable propagation.
    *   **Human Intervention:** The user had to manually:
        *   Create the `docker` group and add themselves to it (`sudo groupadd docker`, `sudo usermod -aG docker $USER`).
        *   Restart Docker service (`sudo systemctl restart docker`) or re-login.
        *   Crucially, execute `eval $(minikube docker-env)` in the *same terminal session* as `docker` and `pulumi` commands.
        *   Adjust file permissions for Minikube certificates (`chmod -R go+rX ~/.minikube/certs`).
    *   **Lesson:** Automating local Docker environment setup and troubleshooting permissions can be highly challenging due to varying OS configurations and user privileges. Direct human intervention is often necessary for such low-level system interactions.

2.  **Docker Image Build & Push Reliability:**
    *   **Problem:** Even after addressing local Docker permissions, direct `docker build` and `docker push` commands (especially with `sudo`) encountered issues related to image tagging and authentication with Artifact Registry.
    *   **Solution & Lesson:** Pivoting to `gcloud builds submit` proved to be a more robust solution. This method offloads the build and push process to Google Cloud Build, bypassing local Docker environment complexities and leveraging Cloud Build's inherent permissions for Artifact Registry. This highlights the benefit of using managed cloud services for CI/CD aspects.

3.  **Pulumi Cloud Run Revision Triggering:**
    *   **Problem:** Initial changes to the `customMessage` Pulumi config did not trigger new Cloud Run revisions, as Pulumi's provider didn't consider environment variable changes alone as a "breaking" change.
    *   **Solution & Lesson:** The solution involved adding a dynamic annotation (`run.googleapis.com/revision-id`) to the Cloud Run service template, whose value was derived from the `hash` of the `customMessage`. This forced Pulumi to detect a change in the service template, thereby triggering a new Cloud Run revision. This demonstrates the importance of understanding how Pulumi providers and underlying cloud services interpret resource changes to ensure desired deployment behavior.

4.  **Git Configuration & GitHub Push:**
    *   **Problem:** Initial `git commit` failed due to unconfigured user identity. `gh repo create` also failed due to unauthenticated GitHub CLI.
    *   **Human Intervention:** The user had to manually configure Git user email/name and perform `gh auth login`.
    *   **Lesson:** Basic developer tooling setup often requires initial human interaction for authentication and identity configuration, which cannot be fully automated by a CLI agent without direct user input or pre-configured secrets.

### Agent's Self-Reflection:

*   **Persistence:** The agent demonstrated persistence in troubleshooting, iterating through multiple potential solutions for Docker and Pulumi issues.
*   **Adaptability:** The ability to pivot from local Docker builds to Cloud Build was crucial for overcoming persistent environmental challenges.
*   **Communication:** Clear communication of errors, proposed solutions, and required human interventions was maintained throughout the process.
*   **Limitations:** The primary limitation was the inability to directly execute `sudo` commands requiring passwords or to deeply debug complex local environment configurations without explicit user input and manual actions. This reinforces the need for a collaborative approach between the agent and the human user for system-level tasks.

This project served as an excellent learning experience, showcasing both the power of automated infrastructure deployment with Pulumi and the critical role of human oversight and intervention in navigating real-world development complexities.
