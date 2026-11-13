# Flask + MongoDB Kubernetes Assignment

## Project Overview

This project demonstrates how to build and deploy a Flask REST API connected to MongoDB using Docker and Kubernetes.

The application allows users to insert and retrieve JSON documents through REST API endpoints. Docker is used to package the Flask application, while Kubernetes manages the application deployment, MongoDB database, persistent storage, service discovery, and horizontal pod autoscaling.

The project was developed and tested locally using Docker Desktop and Minikube on Windows.

## Technologies Used

- Python 3.11
- Flask 3.1.1
- PyMongo 4.13.2
- MongoDB 8.0
- Docker and Docker Hub
- Kubernetes
- Minikube
- kubectl
- Gunicorn
- PersistentVolume (PV)
- PersistentVolumeClaim (PVC)
- StatefulSet and Deployment
- Horizontal Pod Autoscaler (HPA)

## Project Structure

```text
flask-mongodb-kubernetes/
│
├── app.py
├── Dockerfile
├── requirements.txt
├── .dockerignore
├── .gitignore
├── README.md
│
├── screenshots/
│   ├── before-scaling.png
│   ├── after-scaling.png
│   └── after-scale-down.png
│
└── k8s/
    ├── mongodb-secret.yaml
    ├── mongodb-pv.yaml
    ├── mongodb-pvc.yaml
    ├── mongodb-service.yaml
    ├── mongodb-statefulset.yaml
    ├── flask-deployment.yaml
    ├── flask-service.yaml
    └── flask-hpa.yaml
```

## Prerequisites

Before running this project, make sure the following tools are installed:

- Python 3.11 or later
- Docker Desktop
- Docker Hub account
- kubectl
- Minikube
- PowerShell

Start Docker Desktop and make sure its Docker Engine is running before starting Minikube.

## Python Virtual Environment

A virtual environment keeps project dependencies separate from the system Python installation. This helps avoid dependency conflicts and makes local development easier.

Create a virtual environment:

```powershell
python -m venv venv
```

Activate the environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Install the required packages:

```powershell
pip install -r requirements.txt
```

## Application Endpoints

The Flask application provides the following endpoints:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Returns a welcome message with the current date and time |
| GET | `/healthz` | Checks the MongoDB connection |
| GET | `/data` | Retrieves all stored documents without the MongoDB `_id` field |
| POST | `/data` | Inserts a JSON document into MongoDB |

### 1. Welcome Endpoint

Request:

```http
GET /
```

Example response:

```text
Welcome to the Flask app! The current time is: <current date and time>
```

### 2. Health Check

Request:

```http
GET /healthz
```

Successful response:

```json
{
    "status": "ok"
}
```

The endpoint returns HTTP 200 when MongoDB is reachable and HTTP 503 when the database connection fails.

### 3. Insert Data

Request:

```http
POST /data
Content-Type: application/json
```

Example request body:

```json
{
    "name": "Vipul",
    "technology": "Flask",
    "database": "MongoDB"
}
```

Successful response:

```json
{
    "status": "Data inserted"
}
```

HTTP status: `201 Created`

### 4. Retrieve Data

Request:

```http
GET /data
```

The API returns the documents stored in MongoDB as a JSON array. The MongoDB `_id` field is excluded from the response.

## Docker Configuration

The Flask application is packaged using Docker and runs with Gunicorn.

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
```

### Build Docker Image

Run the following command from the project root:

```powershell
docker build --no-cache -t flask-mongodb-app:v3 .
```

### Tag the Image

```powershell
docker tag flask-mongodb-app:v3 vipul089/flask-mongodb-app:v3
```

### Login to Docker Hub

```powershell
docker login
```

### Push Image to Docker Hub

```powershell
docker push vipul089/flask-mongodb-app:v3
```

### Pull Image from Docker Hub

```powershell
docker pull vipul089/flask-mongodb-app:v3
```

The image was successfully pushed to Docker Hub and verified by pulling the published `v3` tag.

**Docker Hub Repository:**

https://hub.docker.com/r/vipul089/flask-mongodb-app

## Kubernetes Deployment

The application is deployed on a local Kubernetes cluster using Minikube.

### 1. Start Docker Desktop

Open Docker Desktop and wait until the Docker Engine is running.

### 2. Start Minikube

Run:

```powershell
minikube start --driver=docker
```

### 3. Enable Metrics Server

The metrics-server is required for CPU-based horizontal pod autoscaling.

```powershell
minikube addons enable metrics-server
```

### 4. Configure kubectl

```powershell
kubectl config use-context minikube
```

### 5. Verify the Cluster

```powershell
minikube status
kubectl cluster-info
kubectl get nodes
```

Check whether CPU metrics are available:

```powershell
kubectl top nodes
```

### 6. Make the Docker Image Available to Minikube

The local Kubernetes Deployment uses the image `flask-mongodb-app:v3` with `imagePullPolicy: IfNotPresent`.

Build the image if required:

```powershell
docker build -t flask-mongodb-app:v3 .
```

Load it into Minikube:

```powershell
minikube image load flask-mongodb-app:v3
```

**Note:** The image is also available on Docker Hub as `vipul089/flask-mongodb-app:v3`. When deploying on another machine using Docker Hub, update the image field in `k8s/flask-deployment.yaml` to the published image name.

### 7. Apply Kubernetes Manifests

Run the following commands from the project root directory.

**Step 1: Create MongoDB Secret**

```powershell
kubectl apply -f k8s/mongodb-secret.yaml
```

**Step 2: Create PersistentVolume**

```powershell
kubectl apply -f k8s/mongodb-pv.yaml
```

**Step 3: Create PersistentVolumeClaim**

```powershell
kubectl apply -f k8s/mongodb-pvc.yaml
```

**Step 4: Create MongoDB Service**

```powershell
kubectl apply -f k8s/mongodb-service.yaml
```

**Step 5: Deploy MongoDB StatefulSet**

```powershell
kubectl apply -f k8s/mongodb-statefulset.yaml
```

**Step 6: Deploy Flask Application**

```powershell
kubectl apply -f k8s/flask-deployment.yaml
```

**Step 7: Create Flask Service**

```powershell
kubectl apply -f k8s/flask-service.yaml
```

**Step 8: Configure Horizontal Pod Autoscaler**

```powershell
kubectl apply -f k8s/flask-hpa.yaml
```

### 8. Wait for Deployments

Wait for MongoDB to become ready:

```powershell
kubectl rollout status statefulset/mongodb
```

Wait for Flask:

```powershell
kubectl rollout status deployment/flask-app
```

## Kubernetes Architecture and Design Choices

| Component | Implementation | Reason |
|---|---|---|
| Flask application | Deployment | Flask is stateless and can scale horizontally |
| MongoDB | StatefulSet | Provides stable pod identity and persistent storage |
| Flask Service | NodePort | Exposes the application for local access |
| MongoDB Service | Headless Service | Provides stable DNS discovery for MongoDB |
| Database storage | PersistentVolume and PersistentVolumeClaim | Preserves data across pod recreation |
| Credentials | Kubernetes Secret | Supplies database credentials outside the application image |
| Autoscaling | Horizontal Pod Autoscaler | Automatically adjusts Flask replicas based on CPU utilization |

### MongoDB StatefulSet

MongoDB runs as a StatefulSet with one replica.

The StatefulSet creates a stable pod identity:

```text
mongodb-0
```

MongoDB stores its database files inside:

```text
/data/db
```

### Persistent Storage

The project uses:

- PersistentVolume: `mongodb-pv`
- PersistentVolumeClaim: `mongodb-pvc`
- Storage capacity: `1Gi`
- Access mode: `ReadWriteOnce`
- Reclaim policy: `Retain`
- Storage type: `hostPath`
- Host path: `/data/mongodb`

The PVC is mounted into the MongoDB container. This allows database data to survive MongoDB pod deletion and recreation.

The `hostPath` configuration is suitable for this local Minikube assignment. Production environments should use a cloud storage provisioner or CSI driver.

## Kubernetes Service Discovery and DNS

Kubernetes uses CoreDNS for internal service discovery.

A Kubernetes Service can be accessed using the following DNS format:

```text
<service-name>.<namespace>.svc.cluster.local
```

The MongoDB Service in this project is named:

```text
mongodb
```

The Flask Deployment uses:

```text
MONGO_HOST=mongodb
```

Because both applications run in the default namespace, Flask can access MongoDB using the short hostname `mongodb`.

The fully qualified DNS name is:

```text
mongodb.default.svc.cluster.local
```

The MongoDB Service is headless (`clusterIP: None`). It provides DNS records that resolve to the MongoDB pod rather than a virtual ClusterIP.

This allows Flask to discover MongoDB through a stable Service name even when the MongoDB pod IP changes.

The Flask application is exposed internally through:

```text
flask-service
```

MongoDB is accessible inside the Kubernetes cluster and is not exposed through a public NodePort.

## Environment Variables and Secrets

The Flask Deployment receives MongoDB connection settings through environment variables.

| Variable | Purpose |
|---|---|
| `MONGO_HOST` | MongoDB Service hostname |
| `MONGO_PORT` | MongoDB port |
| `MONGO_USERNAME` | MongoDB username from Secret |
| `MONGO_PASSWORD` | MongoDB password from Secret |
| `MONGO_AUTH_SOURCE` | MongoDB authentication database |

MongoDB credentials are stored in a Kubernetes Secret and injected into the relevant containers.

**Security note:** Kubernetes Secrets are base64-encoded by default, not automatically encrypted. Appropriate RBAC and encryption-at-rest controls should be used in production. Never publish real database credentials in a public repository.

## Resource Requests and Limits

Resource requests and limits are configured for both Flask and MongoDB containers.

### Flask Container

```yaml
resources:
  requests:
    cpu: "200m"
    memory: "250Mi"
  limits:
    cpu: "500m"
    memory: "500Mi"
```

### MongoDB Container

```yaml
resources:
  requests:
    cpu: "200m"
    memory: "250Mi"
  limits:
    cpu: "500m"
    memory: "500Mi"
```

**Resource requests:** Kubernetes uses requests when scheduling pods and checking whether a node has sufficient available resources.

**Resource limits:** Limits restrict the resources a container can consume. CPU is throttled when it reaches its limit, while exceeding the memory limit can result in an OOMKilled container.

HPA CPU utilization is calculated relative to the CPU request, not the CPU limit. Therefore, accurate CPU requests are important for autoscaling.

## Horizontal Pod Autoscaling

The Flask Deployment uses a Horizontal Pod Autoscaler.

### Configuration

| Setting | Value |
|---|---|
| Target Deployment | `flask-app` |
| Minimum replicas | 2 |
| Maximum replicas | 5 |
| Target CPU utilization | 70% |

The HPA monitors CPU utilization and adjusts the number of Flask pods based on the configured target.

Check HPA status:

```powershell
kubectl get hpa
```

Watch autoscaling:

```powershell
kubectl get hpa flask-app-hpa --watch
```

### Autoscaling Test

Load was generated using two BusyBox pods sending continuous requests to the Flask Service.

Start the first load generator:

```powershell
kubectl run flask-load --image=busybox:1.36 --restart=Never --command -- sh -c 'for i in 1 2 3 4 5; do (while true; do wget -q -O- http://flask-service:5000/ >/dev/null; done) & done; wait'
```

Start the second load generator:

```powershell
kubectl run flask-load-2 --image=busybox:1.36 --restart=Never --command -- sh -c 'for i in 1 2 3 4 5; do (while true; do wget -q -O- http://flask-service:5000/ >/dev/null; done) & done; wait'
```

Monitor HPA:

```powershell
kubectl get hpa flask-app-hpa --watch
```

During the test, the Flask Deployment scaled from 2 to 3 replicas under increased CPU load.

After the load generators were stopped, CPU utilization decreased and the HPA scaled the Deployment back down to 2 replicas.

Stop the load generators:

```powershell
kubectl delete pod flask-load flask-load-2
```

Verify the final state:

```powershell
kubectl get hpa
kubectl get pods
kubectl top pods
```

**Observed scaling result: `2 → 3 → 2`**

The HPA is configured with a maximum of 5 replicas. The test demonstrated scaling up to 3 replicas; reaching 5 replicas was not verified.

## Accessing the Flask Application

For local access on Windows, port-forwarding is used:

```powershell
kubectl port-forward service/flask-service 5000:5000
```

Keep this terminal open while testing.

Open the application:

```text
http://127.0.0.1:5000
```

API endpoint:

```text
http://127.0.0.1:5000/data
```

Health endpoint:

```text
http://127.0.0.1:5000/healthz
```

The Flask Service is also configured as a NodePort Service on port `30050`.

## API Testing Using PowerShell

Make sure port-forwarding is running in another terminal.

### 1. Health Check

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/healthz"
```

Expected response:

```text
status
------
ok
```

### 2. POST Request – Insert Data

```powershell
$body = @{
    name = "Vipul"
    technology = "Flask"
    database = "MongoDB"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:5000/data" -Method POST -ContentType "application/json" -Body $body
```

Expected response:

```json
{
    "status": "Data inserted"
}
```

### 3. GET Request – Retrieve Data

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/data" -Method GET | ConvertTo-Json -Depth 5
```

The response contains the documents stored in MongoDB without exposing the `_id` field.

## Testing Scenarios

### 1. Application Deployment Test

Verified that:

- Flask Deployment was running with 2 ready replicas in its baseline state.
- MongoDB StatefulSet was running with 1 ready pod.
- Flask application pods passed their readiness checks.

### 2. Database Interaction Test

Inserted JSON data through the POST `/data` endpoint and retrieved the stored documents through GET `/data`.

The API successfully returned the stored records from MongoDB without exposing the `_id` field.

### 3. MongoDB Health Check

The `/healthz` endpoint checks the MongoDB connection using a ping command.

It returns HTTP 200 when the database is reachable and HTTP 503 when the connection fails.

### 4. Database Persistence Test

The MongoDB pod was deleted:

```powershell
kubectl delete pod mongodb-0
```

The StatefulSet recreated the MongoDB pod. Previously inserted test data remained retrievable after pod recreation, demonstrating persistent storage through the PVC.

**Important:** The pod was deleted for this test, not the PersistentVolumeClaim or PersistentVolume.

### 5. Autoscaling Test

Multiple load-generator pods were used to generate continuous traffic.

The HPA scaled the Flask Deployment from 2 to 3 replicas and subsequently scaled it back down to 2 after the load was stopped.

## Verification Commands

Check pods:

```powershell
kubectl get pods -o wide
```

Check deployments:

```powershell
kubectl get deployments
```

Check services:

```powershell
kubectl get services
```

Check PersistentVolume and PersistentVolumeClaim:

```powershell
kubectl get pv,pvc
```

Check HPA:

```powershell
kubectl get hpa
```

Check CPU and memory utilization:

```powershell
kubectl top nodes
kubectl top pods
```

View Flask logs:

```powershell
kubectl logs deployment/flask-app
```

View MongoDB logs:

```powershell
kubectl logs mongodb-0
```

## Issues Encountered and Solutions

### 1. Readiness Probe Configuration

The initial readiness probe used a different health endpoint from the Flask application.

The application's health endpoint was `/healthz`, so the readiness probe was corrected to use `/healthz`.

After rebuilding the Docker image and updating the Deployment, the Flask pods became ready.

### 2. Minikube Service Access on Windows

The `minikube service` command encountered an SSH executable issue in the Windows environment.

The application was accessed successfully using:

```powershell
kubectl port-forward service/flask-service 5000:5000
```

### 3. Minikube Command Not Found

If PowerShell cannot recognize the `minikube` command, add the Minikube installation directory to the Windows Path environment variable and open a new terminal.

### 4. HPA Metrics

The metrics-server required some time to provide CPU metrics after startup.

After metrics became available, the HPA successfully monitored CPU utilization and scaled the Flask Deployment.

### 5. Autoscaling Behavior

A single load generator did not produce enough CPU utilization to trigger scaling consistently.

Multiple load-generator pods were used to generate additional traffic and demonstrate HPA scale-up.

## Screenshots and Evidence

The following screenshots document the actual autoscaling test performed on Minikube.

### 1. Before Scaling

The Flask Deployment was running with 2 replicas before additional traffic was generated.

![Before Scaling](screenshots/before-scaling.png)

### 2. During Autoscaling

Under increased CPU load, the HPA increased the Flask Deployment to 3 replicas.

![After Scaling](screenshots/after-scaling.png)

### 3. After Scale Down

After stopping the load generators, CPU utilization decreased and the HPA returned the Flask Deployment to 2 replicas.

![After Scale Down](screenshots/after-scale-down.png)

## Security Notes

- Do not publish real database passwords or `.env` files in a public repository.
- Do not upload a Kubernetes Secret manifest containing real credentials to a public repository.
- Use placeholder values in example Secret manifests and create actual credentials locally.
- Kubernetes Secret data is base64-encoded by default; base64 encoding is not encryption.
- Use suitable RBAC permissions and encryption-at-rest controls in production.

## Conclusion

This project demonstrates how to containerize a Flask REST API, integrate it with an authenticated MongoDB database, and deploy both components using Kubernetes.

It includes persistent database storage, Kubernetes DNS-based service discovery, resource requests and limits, health checks, and CPU-based horizontal autoscaling.

The application was tested on Minikube. Database insertion and retrieval, MongoDB pod recreation with persistent data, and HPA scaling from 2 to 3 and back to 2 replicas were demonstrated.

**Docker image:**

```text
vipul089/flask-mongodb-app:v3
```

**Docker Hub:**

https://hub.docker.com/r/vipul089/flask-mongodb-app
