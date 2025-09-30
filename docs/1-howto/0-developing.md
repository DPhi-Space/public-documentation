---
sidebar_position: 1
---

# Developing Locally with Docker for Clustergate-2

Clustergate-2 runs Docker containers in space, so the best way to develop and test your application is to build it as a Docker container **locally on your laptop**, and optionally test it on an **ARM64-based device** like a Raspberry Pi before deployment.

---

### Step 1: Install Docker on Your Laptop

First, install Docker Desktop (Windows/macOS) or Docker Engine (Linux):

[Install Docker](https://docs.docker.com/get-docker/)

Once installed, verify Docker is working:

```bash
docker --version
```

---

### Step 2: Create a Simple Dockerfile

Clustergate-2 has a list of loaded Docker images developers can use as a base for their own images. Check it out in the Docker images section. Below is an example of Dockerfile for a simple python application:

```Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy your code into the container
COPY . .

# Set the command to run your app
CMD ["python", "main.py"]
```

Save this as `Dockerfile` in your project folder.

Your folder structure might look like:

```
earth-observation-app/
│
├── main.py
└── Dockerfile
```

Remember that, given that the system is air-gapped, no updates requiring internet access can be executed. Otherwise the build will fail.

---

### Step 3: Build and Run Locally 

You can build the image for your laptop's architecture by running the following:

```bash
docker build  -t my-arm-app .
```

Run it locally:

```bash
docker run --rm my-arm-app
```


---

### Step 4: Test on a Real ARM64 Device (Raspberry Pi)

If you have a **Raspberry Pi 4 or 5 running a 64-bit OS**, you can test your container natively. Even though Docker is great, sometimes there are cross-compilation caveats that happen, and it is better to catch them on the ground before executing them in space. 

Make sure your Pi uses a 64-bit OS (such as Raspberry Pi OS 64-bit). Simply transfer the files to it, rebuild it as done locally on a laptop and run it. 


---
