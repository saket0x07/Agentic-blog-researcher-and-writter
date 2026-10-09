# FX_LangGraph: Docker, AWS EC2 (Free Tier) & Vercel Deployment Guide

This guide provides end-to-end, production-ready instructions tailored specifically for this project: the **Agentic AI Content Planner & Writer** built with **LangGraph**, **LangChain**, **Streamlit**, and **FastAPI**.

---

## Architecture Overview

```
                      ┌──────────────────────────────────────────────┐
                      │              AWS EC2 (Free Tier)             │
                      │  Instance: t2.micro / t3.micro (Ubuntu 24)   │
                      │  Memory: 1 GB RAM + 2 GB Swap               │
                      │                                              │
                      │  ┌────────────────────────────────────────┐  │
                      │  │          Docker Container              │  │
┌──────────────────┐  │  │  Image: <dockerhub-user>/fx-agent      │  │
│ External Client  │──┼──┼─► Port 8501: Streamlit Dashboard       │  │
│ or Vercel WebApp │──┼──┼─► Port 8000: FastAPI REST Endpoints    │  │
└──────────────────┘  │  │  Volume: /app/output (Persisted blogs) │  │
                      │  └────────────────────────────────────────┘  │
                      └──────────────────────────────────────────────┘
```

The project includes two interfaces:
1. **Streamlit UI** (`app.py`): Interactive web dashboard on port `8501`.
2. **FastAPI Backend** (`api.py`): REST API with CORS enabled on port `8000` (provides `/blog/write`, `/generate`, and `/health`).

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on your local computer.
- An account on [Docker Hub](https://hub.docker.com/) (free).
- An active [AWS Account](https://aws.amazon.com/) (Free Tier eligible).
- Your API keys configured in `.env` (`OPENROUTER_API_KEY` or `OPENAI_API_KEY`, optional `TAVILY_API_KEY`, `GEMINI_API_KEY`).

---

## Step 1: Dockerize the Application Locally

The project includes a ready-to-use `Dockerfile` and `.dockerignore`.

### 1.1 Verify Dockerfile Structure
The `Dockerfile` is optimized with `python:3.11-slim`, system dependencies, and clean layers:
- Base: `python:3.11-slim`
- Working Directory: `/app`
- Exposed Ports: `8501` (Streamlit) & `8000` (FastAPI)
- Default Entrypoint: Streamlit Web UI

### 1.2 Build the Docker Image Locally
Open PowerShell or Command Prompt in the project root (`d:\Fxis.ai\FX_LangGraph`) and run:

```bash
docker build -t fx-langgraph-agent:latest .
```

### 1.3 Test the Container Locally

#### Option A: Run the Streamlit Interface
```bash
docker run -d \
  --name fx-agent-ui \
  -p 8501:8501 \
  --env-file .env \
  -v ${PWD}/output:/app/output \
  fx-langgraph-agent:latest
```
Visit `http://localhost:8501` in your browser.

#### Option B: Run the FastAPI REST Backend
```bash
docker run -d \
  --name fx-agent-api \
  -p 8000:8000 \
  --env-file .env \
  fx-langgraph-agent:latest \
  uvicorn api:app --host 0.0.0.0 --port 8000
```
Visit `http://localhost:8000/docs` to test interactive Swagger API docs.

#### Stop the local test containers:
```bash
docker stop fx-agent-ui fx-agent-api
docker rm fx-agent-ui fx-agent-api
```

---

## Step 2: Push the Docker Image to Docker Hub

### 2.1 Log in to Docker Hub
In your terminal:
```bash
docker login
```
Enter your Docker Hub username and password (or Personal Access Token).

### 2.2 Tag and Push Your Image
Replace `<your-dockerhub-username>` with your actual Docker Hub username:

```bash
# 1. Tag the image with your Docker Hub repository name
docker tag fx-langgraph-agent:latest <your-dockerhub-username>/fx-langgraph-agent:latest

# 2. Push the image to Docker Hub
docker push <your-dockerhub-username>/fx-langgraph-agent:latest
```

Once uploaded, your image will be publicly accessible (or privately if you configured a private repo) for your EC2 instance to pull.

---

## Step 3: Launch an AWS EC2 Free Tier Instance

### 3.1 Open the AWS EC2 Console
1. Log in to [AWS Management Console](https://console.aws.amazon.com/).
2. Select your preferred region (e.g., `us-east-1` (N. Virginia), `eu-west-1` (Ireland), or `ap-south-1` (Mumbai)).
3. Navigate to **EC2** > Click **Launch Instance**.

### 3.2 Configure the Instance
- **Name**: `fx-langgraph-server`
- **Application and OS Images (AMI)**: Select **Ubuntu** (Choose `Ubuntu Server 24.04 LTS (HVM), SSD Volume Type` - marked **Free tier eligible**).
- **Architecture**: `64-bit (x86)`.
- **Instance type**: Select **`t2.micro`** (or **`t3.micro`** if available in your region) — **Free tier eligible** (1 vCPU, 1 GiB Memory).

### 3.3 Create or Select a Key Pair
1. Under **Key pair (login)**, click **Create new key pair**.
2. **Key pair name**: `fx-agent-key`.
3. **Key pair type**: `RSA`.
4. **Private key file format**: `.pem` (for OpenSSH / PowerShell / macOS / Linux).
5. Click **Create key pair**. A file named `fx-agent-key.pem` will be downloaded to your computer. **Keep this file secure!**

### 3.4 Configure Network & Security Group
Under **Network settings**, choose **Create security group** and check:
- [x] **Allow SSH traffic from Anywhere (0.0.0.0/0)** or **My IP**.
- [x] **Allow HTTP traffic from the internet**.
- [x] **Allow HTTPS traffic from the internet**.

Click **Edit network settings** and add the custom ports:

| Type | Protocol | Port Range | Source | Description |
| :--- | :--- | :--- | :--- | :--- |
| SSH | TCP | 22 | Anywhere (0.0.0.0/0) | Remote terminal access |
| Custom TCP | TCP | 8501 | Anywhere (0.0.0.0/0) | Streamlit Web Dashboard |
| Custom TCP | TCP | 8000 | Anywhere (0.0.0.0/0) | FastAPI REST API |
| HTTP | TCP | 80 | Anywhere (0.0.0.0/0) | Nginx Web Server |
| HTTPS | TCP | 443 | Anywhere (0.0.0.0/0) | Secure Web Server |

### 3.5 Configure Storage
- Free Tier allows up to **30 GB** of General Purpose (gp3 or gp2) SSD storage.
- Change the root volume size from `8 GiB` to **`20 GiB`** or **`30 GiB`** to comfortably store Docker images and caches.

Click **Launch Instance**.

---

## Step 4: Connect to EC2 and Configure the Environment

### 4.1 Obtain the EC2 Public IPv4 Address
1. Go to **EC2** > **Instances**.
2. Click on `fx-langgraph-server`.
3. Copy the **Public IPv4 address** (e.g., `3.85.120.45`).

### 4.2 Connect via SSH
Open PowerShell in the folder where your `fx-agent-key.pem` is stored:

```powershell
# Set proper permissions on Windows (if needed) or directly SSH:
ssh -i "fx-agent-key.pem" ubuntu@<YOUR-EC2-PUBLIC-IP>
```

> **Note on Windows SSH permissions**: If you get `Permissions are too open`, run:
> ```powershell
> icacls.exe fx-agent-key.pem /reset
> icacls.exe fx-agent-key.pem /grant:r "$($env:username):(R)"
> icacls.exe fx-agent-key.pem /inheritance:r
> ```

### 4.3 Configure 2GB Swap Memory (CRITICAL for Free Tier t2.micro)
Because `t2.micro` instances only have 1 GB of physical RAM, Python AI libraries can trigger the Linux Out-Of-Memory (OOM) killer during execution. Adding 2 GB of swap memory completely prevents this:

Run on the EC2 terminal:
```bash
# 1. Create a 2GB swap file
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 2. Make swap permanent across reboots
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 3. Verify memory and swap
free -h
```

### 4.4 Install Docker on EC2
Install the official Docker engine using the convenience script:

```bash
# Update package indices
sudo apt-get update && sudo apt-get install -y curl

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Enable non-root docker commands for ubuntu user
sudo usermod -aG docker ubuntu
newgrp docker

# Verify Docker installation
docker --version
```

---

## Step 5: Deploy and Run the Container on AWS EC2

### 5.1 Create the Environment File on EC2
Create a `.env` file on the EC2 instance with your API keys:

```bash
nano .env
```

Paste your production keys:
```env
OPENROUTER_API_KEY=your_openrouter_api_key
# or OPENAI_API_KEY=your_openai_api_key

TAVILY_API_KEY=your_tavily_api_key
GEMINI_API_KEY=your_gemini_api_key
HF_TOKEN=your_huggingface_token
```
Press `Ctrl + O`, then `Enter` to save, and `Ctrl + X` to exit.

### 5.2 Pull Your Docker Image
```bash
docker pull <your-dockerhub-username>/fx-langgraph-agent:latest
```

*(If you used a private repository, run `docker login` first).*

### 5.3 Launch the Application

#### Option 1: Run the Streamlit Application (Port 8501)
```bash
mkdir -p output
docker run -d \
  --name fx-agent-streamlit \
  --restart unless-stopped \
  -p 8501:8501 \
  --env-file .env \
  -v $(pwd)/output:/app/output \
  <your-dockerhub-username>/fx-langgraph-agent:latest
```

Verify it's running:
```bash
docker ps
docker logs -f fx-agent-streamlit
```
You can now open your browser and navigate to:
```text
http://<YOUR-EC2-PUBLIC-IP>:8501
```

#### Option 2: Run the FastAPI REST Backend (Port 8000)
```bash
docker run -d \
  --name fx-agent-api \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/output:/app/output \
  <your-dockerhub-username>/fx-langgraph-agent:latest \
  uvicorn api:app --host 0.0.0.0 --port 8000
```
Access the REST API:
- Health check: `http://<YOUR-EC2-PUBLIC-IP>:8000/health`
- Swagger UI docs: `http://<YOUR-EC2-PUBLIC-IP>:8000/docs`

---

## Step 6: Connecting to Vercel

### Understanding the Architecture
Vercel is a serverless platform designed for hosting static and frontend applications (e.g. Next.js, React). Long-running AI agents (such as LangGraph workflows with iterative research and image generation) exceed Vercel's standard serverless function timeout limits (10–60s).

The ideal and standard production setup is:
- **AWS EC2**: Hosts the long-running LangGraph backend (`api.py` or `app.py`).
- **Vercel**: Hosts the modern frontend (Next.js / React / Web UI) that calls the EC2 backend.

### 6.1 Avoiding Mixed Content Issues (HTTP vs HTTPS)
Vercel apps are served exclusively over **HTTPS** (e.g., `https://my-app.vercel.app`).
Browsers block HTTPS websites from calling insecure HTTP endpoints (`http://<EC2-IP>:8000`).

To make EC2 accessible to a Vercel frontend, you have two simple options:

#### Solution A: Setup Nginx Reverse Proxy with Free SSL (Recommended)
On your EC2 instance, install Nginx and Certbot:

```bash
sudo apt-get install -y nginx certbot python3-certbot-nginx
```

Configure Nginx to proxy requests to your FastAPI or Streamlit app:
```bash
sudo nano /etc/nginx/sites-available/default
```

Replace contents with:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Point your domain/subdomain A-record to your EC2 IP

    location / {
        proxy_pass http://localhost:8000; # or 8501 for Streamlit
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

Enable SSL certificate with Certbot (free):
```bash
sudo systemctl restart nginx
sudo certbot --nginx -d your-domain.com
```

Now your backend is securely available at `https://your-domain.com`.

#### Solution B: Vercel Rewrites (Proxy through Vercel)
If you don't have a custom domain yet, configure Vercel to route backend requests through its own domain using `vercel.json` in your Vercel project repository:

```json
{
  "rewrites": [
    {
      "source": "/api/backend/:path*",
      "destination": "http://<YOUR-EC2-PUBLIC-IP>:8000/:path*"
    }
  ]
}
```
Now your Vercel frontend can make requests to `/api/backend/generate` or `/api/backend/blog/write` without any HTTPS/CORS issues!

### 6.2 Setting Vercel Environment Variables
In your Vercel Project Dashboard:
1. Go to **Settings** > **Environment Variables**.
2. Add:
   ```text
   NEXT_PUBLIC_API_URL = https://your-domain.com
   ```
   (or `http://<YOUR-EC2-PUBLIC-IP>:8000` if using server-side fetches or rewrites).
3. Trigger a redeployment on Vercel.

---

## Step 7: Management & Monitoring Cheatsheet

### Useful Docker Commands on EC2
| Task | Command |
| :--- | :--- |
| View running containers | `docker ps` |
| View logs in real time | `docker logs -f fx-agent-streamlit` |
| Check resource usage (CPU/RAM) | `docker stats` |
| Restart container | `docker restart fx-agent-streamlit` |
| Stop container | `docker stop fx-agent-streamlit` |
| Update to new image | `docker pull <user>/fx-langgraph-agent:latest && docker restart fx-agent-streamlit` |

### AWS Free Tier Safety Rules
- EC2 Free Tier provides **750 hours/month** of `t2.micro` or `t3.micro`. Running **one** instance 24/7 uses 744 hours max — fully within the free limit.
- Ensure only **one** `t2.micro`/`t3.micro` instance is running in your account.
- Keep EBS storage at or under **30 GB**.
- If not using the instance for extended periods, you can **Stop** the instance from the AWS EC2 console (note: stopping keeps EBS storage, terminating deletes the instance entirely).
