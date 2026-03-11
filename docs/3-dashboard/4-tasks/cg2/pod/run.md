# Pod run task

**Task type:** `dphi.space.cg2.pod.run`

## Purpose
Launch a pod run on Clustergate-2 using a container image and runtime settings.

## Definition
```yaml
  - id: pod_run_job
    type: dphi.space.cg2.pod.run
    description: Run a pod with parameters
    pod_name: test
    image:
      name: my-app
      tag: latest
    command: ["/bin/sh"]
    args: ["-c", "echo 'Debi tirar mas fotos' > /data/hello-from-space.txt"]
    env:
      - name: LOG_LEVEL
        value: info
      - name: CONFIG_PATH
        value: /data/config/config.yaml
    ports:
      - container: 8080
        host: 8080
        protocol: tcp
    node: default
    volume: payload
    max_duration: 600
    scheduled_time: null
```

## Inputs
- `id`: Name of the task.
- `description`: Description of the task.
- `pod_name`: Name attributed to the running pod.
- `image.name` and `image.tag`: Container image reference.
- `command` and `args`: Optional command override of the Docker image.
- `env`: Optional environment variables list.
- `ports`: Optional container port mappings.
- `node`: Target node to run on (FPGA, MPU, or GPU).
- `max_duration`: Optional run timeout, in minutes. The pod will be gracefully killed after the timeout expires.
- `volume`: Optional volume name to attach to the pod. Defaults to the main user's volume, *i.e.* `[username]-pvc`.

## Outputs
- `status`: Boolean success flag.
- `message`: Optional error message.

## Common failure reasons
- Image name or tag is missing.
- Node selection is invalid.
- Remote manifest upload fails.
- Sequence execution fails.
