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
We will soon publish the associated sha256sum for each image so that this is more precise.
To be sure your workload will run on the FM, please assure you had a testing in our Engineering Model first.

| Image Name                                                  | Tag                                                         |
| ----------------------------------------------------------- | ----------------------------------------------------------- |
| almalinux                                                   | 8                                                           |
| almalinux                                                   | 9                                                           |
| alpine                                                      | 3.18                                                        |
| alpine                                                      | 3.19                                                        |
| alpine                                                      | edge                                                        |
| alpine                                                      | latest                                                      |
| bellsoft/liberica-runtime-container                         | jre-21-slim-musl                                            |
| busybox                                                     | latest                                                      |
| busybox                                                     | musl                                                        |
| busybox                                                     | stable                                                      |
| caddy                                                       | 2                                                           |
| caddy                                                       | alpine                                                      |
| cassandra                                                   | 3.11                                                        |
| cassandra                                                   | 4                                                           |
| debian                                                      | bookworm                                                    |
| debian                                                      | bookworm-slim                                               |
| debian                                                      | bullseye                                                    |
| debian                                                      | bullseye-slim                                               |
| dinov3-sat493m_orin16-r36.4.0                               | latest                                                      |
| distroless-base                                             | latest                                                      |
| distroless-java17-debian12                                  | latest                                                      |
| distroless-nodejs20-debian12                                | latest                                                      |
| distroless-python3-debian12                                 | latest                                                      |
| distroless-static                                           | latest                                                      |
| docker                                                      | cli                                                         |
| docker                                                      | dind                                                        |
| docker                                                      | latest                                                      |
| dotnet-aspnet                                               | 8.0                                                         |
| dotnet-runtime                                              | 8.0                                                         |
| dotnet-sdk                                                  | 7.0                                                         |
| dotnet-sdk                                                  | 8.0                                                         |
| dphi-embedded-ml-armv8-py311                                | latest                                                      |
| eclipse-temurin                                             | 11-jdk                                                      |
| eclipse-temurin                                             | 17-jdk                                                      |
| eclipse-temurin                                             | 17-jre                                                      |
| eclipse-temurin                                             | 21-jdk                                                      |
| eclipse-temurin                                             | 21-jre                                                      |
| elasticsearch                                               | 7.17.0                                                      |
| elasticsearch                                               | 8.11.0                                                      |
| fedora                                                      | 38                                                          |
| fedora                                                      | 39                                                          |
| fedora                                                      | latest                                                      |
| fluent/fluentd                                              | latest                                                      |
| gcc                                                         | 12                                                          |
| gcc                                                         | 13                                                          |
| gcc                                                         | latest                                                      |
| gcr.io/distroless/base                                      | latest                                                      |
| gcr.io/distroless/java17-debian12                           | latest                                                      |
| gcr.io/distroless/nodejs20-debian12                         | latest                                                      |
| gcr.io/distroless/python3-debian12                          | latest                                                      |
| gcr.io/distroless/static                                    | latest                                                      |
| ghcr.io/graalvm/native-image-community                      | 21                                                          |
| golang                                                      | 1.20                                                        |
| golang                                                      | 1.20-alpine                                                 |
| golang                                                      | 1.21                                                        |
| golang                                                      | 1.21-alpine                                                 |
| golang                                                      | latest                                                      |
| graalvm-native-image-community                              | 21                                                          |
| gradle                                                      | 8.5-jdk17                                                   |
| gradle                                                      | 8.5-jdk21                                                   |
| grafana/grafana                                             | 9.3.6                                                       |
| grafana/grafana                                             | latest                                                      |
| haproxy                                                     | 2.8                                                         |
| haproxy                                                     | alpine                                                      |
| httpd                                                       | alpine                                                      |
| httpd                                                       | latest                                                      |
| influxdb                                                    | 1.8                                                         |
| influxdb                                                    | 2.7                                                         |
| l4t-ml                                                      | latest                                                      |
| l4t-pytorch-r36-2-0                                         | latest                                                      |
| l4t-pytorch-r36-4-0                                         | latest                                                      |
| mariadb                                                     | 10.11                                                       |
| mariadb                                                     | 10.6                                                        |
| mariadb                                                     | 11                                                          |
| mariadb                                                     | 11.8.2                                                      |
| mariadb                                                     | latest                                                      |
| mcr.microsoft.com/dotnet/aspnet                             | 8.0                                                         |
| mcr.microsoft.com/dotnet/runtime                            | 8.0                                                         |
| mcr.microsoft.com/dotnet/sdk                                | 7.0                                                         |
| mcr.microsoft.com/dotnet/sdk                                | 8.0                                                         |
| mongo                                                       | 24.04                                                       |
| mongo                                                       | 6                                                           |
| mongo                                                       | 7                                                           |
| mongo                                                       | latest                                                      |
| mysql                                                       | 8.0                                                         |
| mysql                                                       | latest                                                      |
| nginx                                                       | alpine                                                      |
| nginx                                                       | latest                                                      |
| node                                                        | 18                                                          |
| node                                                        | 18-alpine                                                   |
| node                                                        | 18-slim                                                     |
| node                                                        | 20                                                          |
| node                                                        | 20-alpine                                                   |
| node                                                        | 20-slim                                                     |
| node                                                        | lts                                                         |
| node                                                        | lts-alpine                                                  |
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
| postgres                                                    | latest                                                      |
| power-aware-extender                                        | latest                                                      |
| prom/node-exporter                                          | latest                                                      |
| prom/prometheus                                             | latest                                                      |
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
| redis                                                       | latest                                                      |
| registry                                                    | 2                                                           |
| rocker/rstudio                                              | 4.3.2                                                       |
| rockylinux                                                  | 8                                                           |
| rockylinux                                                  | 9                                                           |
| ruby                                                        | 3.2                                                         |
| ruby                                                        | 3.2-alpine                                                  |
| ruby                                                        | 3.3                                                         |
| ruby                                                        | 3.3-alpine                                                  |
| ruby                                                        | latest                                                      |
| rust                                                        | 1.75                                                        |
| rust                                                        | 1.75-slim                                                   |
| rust                                                        | alpine                                                      |
| rust                                                        | latest                                                      |
| traefik                                                     | latest                                                      |
| traefik                                                     | v3.0                                                        |
| traefik                                                     | v3.5.2                                                      |
| ubuntu                                                      | 20.04                                                       |
| ubuntu                                                      | 22.04                                                       |
| ubuntu                                                      | 24.04                                                       |
| ubuntu                                                      | latest                                                      |
| ultralytics-latest-jetson-jetpack6                          | latest                                                      |
