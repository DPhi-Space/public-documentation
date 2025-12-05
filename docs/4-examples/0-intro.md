# Examples

This section contains **application examples** demonstrating how to deploy and interact with software running on **Clustergate-2**.

> :construction: These examples are still under active development. More use cases and integrations will be added over time.

> :warning: Remember that by default, everything that the DPhi Pods print to the console, be it standard output or errors, will not be saved by our system. It is the responsibility of the user to log to the mounted volume `/data` everything they wish to keep persistent accross runs and downlinkable.

All example source code is available under the `examples/` directory of the repository.

---

## Getting Started

Clone the public documentation repository:

```bash
git clone git@github.com:DPhi-Space/public-documentation.git
cd public-documentation
```

---

## Index of Examples

1. [**Telemetry Client API**](/docs/3-examples/1-telemetry.md)
   A Python client that connects to the onboard telemetry API, fetches health, telemetry, and statistics data, and stores it locally in JSON format. It can run both **natively** or **inside Docker** and integrates directly with the onboard database and telemetry REST service.
1. [**EM API Python Client Implementation**](/docs/4-examples/2-python-em-api.md)
   A simple EM API Client implementation in Python for interfacing with CG2's EM. It provides a simple interface for interacting with the EM, handling authentification, file operations, Docker image management and DPhi Pod execution.
1. [**Fisheye Telemetry Analysis**](/docs/4-examples/3-fisheye-gpu.md)
   This example is designed to fetch fisheye images from the onboard telemetry API, perform GPU-accelerated analysis using CUDA, and generate detailed insights including deep features, color statistics, edge detection, texture, and histogram analysis.

---
