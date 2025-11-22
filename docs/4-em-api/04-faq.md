# Frequent Asked Questions

## DPhi Pod Execution

### What is the difference between a container and a dphi pod?

A container is a self-contained environment that runs an application.

A DPhiPod is a wrapper around a container — technically, it’s a Kubernetes pod that runs your container inside it.

Why it matters?

For simple jobs, running a container directly or through a DPhiPod is essentially the same.

Using a dphi pod enables more complex setups if needed, like scheduling, telemetry, or resource isolation.

The dphi pod name was chosen to highlight user-friendliness and the fact that it’s optimized for running jobs in a space-like execution environment.

### Do I need to adapt my Docker image for the onboard system?

No — you do not need to make any changes for Kubernetes.

Our system automatically adapts your image to run inside a dphi pod.

The only requirement is that your Docker image is built for arm64, which matches the architecture of the execution environment.

This makes it easy to use your existing images without extra modifications.

### Where is the persistent volume mounted for my dphi pods?

The persistent volume for your dphi pods is mounted at:

```bash
/data
```

All dphi pods scheduled by the same user share this volume, so any files you write in /data will be accessible across all your dphi pods.

Because the volume is shared, running multiple dphi pods in parallel can lead to file conflicts or data races.

It’s up to you to manage how different dphi pods read and write to `/data` if you use multiple pods at the same time.

### What actually runs on the EM when I submit a command with the dphi pod run POST request?

Exactly the command you typed, executed inside a standard Linux shell (/bin/sh).
Your command is not changed — only wrapped so the shell can process it.

### Can I use redirection, pipes, and multiple commands?

Yes. All of these work:

```bash
echo hello > /data/msg.txt
cat /data/file | grep foo
echo start && do-something && echo done
```

Because everything runs inside a normal shell.

### Can I run multiple commands in one submission?

Yes. For example:

```
mkdir /data/logs && cp file.txt /data/logs/
```

### Can I run my own script?

Yes. If your image contains the script:

```
sh /path/to/script.sh
```

### My DPhiPod was scheduled successfully but I don’t see logs — why?

A DPhiPod being “scheduled successfully” only means your request was accepted.
It does not guarantee that the job actually started running on the execution machine.

Once the scheduler tries to launch the pod, several things can still go wrong, for example:

- the requested Docker image does not exist
- the command inside the image fails immediately
- the pod starts and exits before producing logs

In all these cases, the pod is still considered “scheduled”, but it may never run or may fail instantly. To ensure the dphi pod is correctly running, always fetch its state with the GET /pod/status endpoint and check if there are any errors.

### Why is my previous DPhiPod removed when I request a new one?

At the moment, each client can run only one dphi pod at a time.
This is a temporary limitation that ensures stable resource usage and avoids conflicts inside the execution environment.

Because of this, when you submit a new dphi pod, the system automatically removes your previous pod, and then schedules the new one.

This is expected behavior for now.

In the near future, you will be able to run multiple dphi pod in parallel for the same client.

However, it is important to know that all dphi pod belonging to a given user share the same dedicated volume on the EM. Therefore, data races, file conflicts, and overwrites will be the user’s responsibility to manage.

This gives you more flexibility but also more control over how your pods interact with shared data.

### Do I need to provide a command for each DPhi Pod request?

No — you don’t have to provide a command every time.

If you don’t specify a command, the dphi pod will automatically run the default command baked into the Docker image you requested.

If you do provide a command, it overrides the image’s default, allowing you to run the same container with different commands without needing to rebuild the Docker image.

This makes it easy to run different experiments using the same container image.
