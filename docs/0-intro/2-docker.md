---
sidebar_position: 1
---

# Docker Onboard

**Docker** is a platform that allows developers to package their applications and all necessary dependencies into a single, lightweight unit called a **container**. These containers can run consistently across different environments—whether on a laptop, in a data center, or onboard a satellite like Clustergate-2.

By using Docker, we ensure that client software behaves the same way in space as it does during development and testing on Earth. This eliminates issues caused by differences in operating systems, libraries, or system configurations.

In the Clustergate-2 mission, Docker plays a critical role in how we execute and manage user-provided software:

* **Simplified Deployment**: Developers can submit their applications as self-contained Docker containers, avoiding complex setup or integration steps.
* **Reliability**: Containers run in isolated environments, reducing the risk of interference between different applications.
* **Portability**: Applications can easily be moved between our different onboard processors—whether it's the Arm core, Jetson module, or FPGA—without modification.
* **Efficiency**: Docker containers launch quickly and use system resources efficiently, which is crucial in a space environment with limited compute capacity.

Leveraging Docker allows Clustergate-2 to offer a smooth, consistent, and scalable experience for running software in orbit—just as you would on Earth.

