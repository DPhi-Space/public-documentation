---
sidebar_position: 1
---

# Docker Images Onboard

The following table contains the list of available Docker images onboard.
To locally pull and test these images, run the following:

```bash
docker pull <Image Tag>
```

For example, for `alpine`, run the following (select arm64 version also):

```bash
docker --platform=arm64 pull alpine:3
```

Just be aware that those images were pulled a while ago, the latest tags for example are not from now, but from the time pulled.
To be sure your workload will run on the FM, please assure you had a testing in our Engineering Model first.
The latest, alpine, slim tags were push as-is, you will find in `()` the version running.
In the registry, the tag does not contain the `()` part.
For example, if you want to use the image alpine on the latest(3.20) you will use `FROM fpga.dphi.space:5000/alpine:latest`.
For your reference and internal testing, you can fix it to version 3.20 in case the latest tag has been otherwise moved.

| Image Name                                                  | Tag                                                         |
| ----------------------------------------------------------- | ----------------------------------------------------------- |
| almalinux                                                   | 8                                                           |
| almalinux                                                   | 9                                                           |
| alpine                                                      | 3.18                                                        |
| alpine                                                      | 3.19                                                        |
| alpine                                                      | edge(20250108)                                              |
| alpine                                                      | latest(3.22.1)                                              |
| bellsoft/liberica-runtime-container                         | jre-21-slim-musl                                            |
| busybox                                                     | latest(1.37.0)                                              |
| busybox                                                     | musl(1.37.0-musl)                                           |
| busybox                                                     | stable(1.36.1)                                              |
| caddy                                                       | 2                                                           |
| caddy                                                       | alpine(2.10.2-alpine)                                       |
| cassandra                                                   | 3.11                                                        |
| cassandra                                                   | 4                                                           |
| debian                                                      | bookworm                                                    |
| debian                                                      | bookworm-slim                                               |
| debian                                                      | bullseye                                                    |
| debian                                                      | bullseye-slim                                               |
| dinov3-sat493m_orin16-r36.4.0(*)                            | latest                                                      |
| distroless-base                                             | latest(base)                                                |
| distroless-java17-debian12                                  | latest(java17-debian12)                                     |
| distroless-nodejs20-debian12                                | latest(nodejs20-debian12)                                   |
| distroless-python3-debian12                                 | latest(python3-debian12)                                    |
| distroless-static                                           | latest(static)                                              |
| docker                                                      | cli                                                         |
| docker                                                      | dind                                                        |
| docker                                                      | latest(28.4.0)                                              |
| dotnet-aspnet                                               | 8.0                                                         |
| dotnet-runtime                                              | 8.0                                                         |
| dotnet-sdk                                                  | 7.0                                                         |
| dotnet-sdk                                                  | 8.0                                                         |
| dphi-embedded-ml-armv8-py311(**)                  | latest                                                      |
| eclipse-temurin                                             | 11-jdk                                                      |
| eclipse-temurin                                             | 17-jdk                                                      |
| eclipse-temurin                                             | 17-jre                                                      |
| eclipse-temurin                                             | 21-jdk                                                      |
| eclipse-temurin                                             | 21-jre                                                      |
| elasticsearch                                               | 7.17.0                                                      |
| elasticsearch                                               | 8.11.0                                                      |
| fedora                                                      | 38                                                          |
| fedora                                                      | 39                                                          |
| fedora                                                      | latest(42)                                                  |
| fluent/fluentd                                              | latest(v1.19.0-1.0)                                         |
| gcc                                                         | 12                                                          |
| gcc                                                         | 13                                                          |
| gcc                                                         | latest(15.2.0)                                              |
| golang                                                      | 1.20                                                        |
| golang                                                      | 1.20-alpine                                                 |
| golang                                                      | 1.21                                                        |
| golang                                                      | 1.21-alpine                                                 |
| golang                                                      | latest(1.25.1)                                              |
| graalvm-native-image-community                              | 21                                                          |
| gradle                                                      | 8.5-jdk17                                                   |
| gradle                                                      | 8.5-jdk21                                                   |
| grafana/grafana                                             | 9.3.6                                                       |
| grafana/grafana                                             | latest(12.2.0-16791878397)                                  |
| haproxy                                                     | 2.8                                                         |
| haproxy                                                     | alpine                                                      |
| httpd                                                       | alpine                                                      |
| httpd                                                       | latest(2.4.65)                                              |
| influxdb                                                    | 1.8                                                         |
| influxdb                                                    | 2.7                                                         |
| l4t-ml                                                      | latest(r36.4.4)                                             |
| l4t-pytorch-r36-2-0                                         | latest(r36.2.0)                                             |
| l4t-pytorch-r36-4-0                                         | latest(r36.4.0)                                             |
| mariadb                                                     | 10.11                                                       |
| mariadb                                                     | 10.6                                                        |
| mariadb                                                     | 11                                                          |
| mariadb                                                     | 11.8.2                                                      |
| mariadb                                                     | latest(11.8.2)                                              |
| mcr.microsoft.com/dotnet/aspnet                             | 8.0                                                         |
| mcr.microsoft.com/dotnet/runtime                            | 8.0                                                         |
| mcr.microsoft.com/dotnet/sdk                                | 7.0                                                         |
| mcr.microsoft.com/dotnet/sdk                                | 8.0                                                         |
| mysql                                                       | 8.0                                                         |
| mysql                                                       | latest(9.4.0)                                               |
| nginx                                                       | alpine(1.29.0-alpine)                                       |
| nginx                                                       | latest(1.29.0)                                              |
| node                                                        | 18                                                          |
| node                                                        | 18-alpine                                                   |
| node                                                        | 18-slim                                                     |
| node                                                        | 20                                                          |
| node                                                        | 20-alpine                                                   |
| node                                                        | 20-slim                                                     |
| node                                                        | lts(22.19.0)                                                |
| node                                                        | lts-alpine(22.19.0-alpine3.22)                              |
| php                                                         | 8.1-fpm                                                     |
| php                                                         | 8.2-apache                                                  |
| php                                                         | 8.2-fpm                                                     |
| php                                                         | 8.3-apache                                                  |
| php                                                         | 8.3-cli                                                     |
| php                                                         | 8.3-fpm                                                     |
| postgres                                                    | 13                                                          |
| postgres                                                    | 14                                                          |
| postgres                                                    | 15                                                          |
| postgres                                                    | 15-alpine                                                   |
| postgres                                                    | 16                                                          |
| postgres                                                    | 16-alpine                                                   |
| postgres                                                    | 17                                                          |
| postgres                                                    | latest(17.6-trixie)                                         |
| prom/node-exporter                                          | latest(v1.9.1)                                              |
| prom/prometheus                                             | latest(v3.5.0)                                              |
| prom/prometheus                                             | v2.42.0                                                     |
| python                                                      | 3.10                                                        |
| python                                                      | 3.10-slim                                                   |
| python                                                      | 3.11                                                        |
| python                                                      | 3.11-alpine                                                 |
| python                                                      | 3.11-slim                                                   |
| python                                                      | 3.12                                                        |
| python                                                      | 3.12-alpine                                                 |
| python                                                      | 3.12-slim                                                   |
| redis                                                       | 6-alpine                                                    |
| redis                                                       | 7-alpine                                                    |
| redis                                                       | latest(8.2.1-bookworm)                                      |
| registry                                                    | 2                                                           |
| rocker/rstudio                                              | 4.3.2                                                       |
| rockylinux                                                  | 8                                                           |
| rockylinux                                                  | 9                                                           |
| ruby                                                        | 3.2                                                         |
| ruby                                                        | 3.2-alpine                                                  |
| ruby                                                        | 3.3                                                         |
| ruby                                                        | 3.3-alpine                                                  |
| ruby                                                        | latest(3.4.5-trixie)                                        |
| rust                                                        | 1.75                                                        |
| rust                                                        | 1.75-slim                                                   |
| rust                                                        | alpine(1.89.0-alpine)                                       |
| rust                                                        | latest(1.89.0)                                              |
| traefik                                                     | latest(v3.5.2)                                              |
| traefik                                                     | v3.0                                                        |
| traefik                                                     | v3.5.2                                                      |
| ubuntu                                                      | 20.04                                                       |
| ubuntu                                                      | 22.04                                                       |
| ubuntu                                                      | 24.04                                                       |
| ubuntu                                                      | latest(24.04)                                               |
| ultralytics-latest-jetson-jetpack6                          | latest(8.3.241-jetson-jetpack6)                             |

(*) dinov3 is a model developed by Meta (https://ai.meta.com/dinov3/). It encodes the image into embedding s just like LLMs do so for test, which can later be used for many tasks: segmentation, depth estimation, classification, change detection etc..
We loaded the model dinov3-vitl16-pretrain-sat493m which a backbone thats pretrained on satellite imagery. It is therefore ideal for usage on CG2 and later missions with high resolution images. The dockerfile requires a hugging face token to pull the dinov3-vitl16-pretrain-sat493m which is removed from this [Dockerfile](./Dockerfile.dinov3)

(**) dphi-embedded-ml is an image that has useful machine learning libraries that can run on a cpu (torch, tflite, onnx runtime). It is a lightweight alternative for images like dustynv-ml that can only run on the jetson. The image also includes useful libraries for orbital calculations (sgp4, pyorbital, pyproj). This is an ideal compromse to test AI in a CPU rather than on the GPU. You can pull it from dockerhub or you can find the Dockerfile used at: [Dockerfile](./Dockerfile.dphi-embedded).
