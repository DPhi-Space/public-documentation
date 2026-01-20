# EM Testing API

This API provides a ground-based simulation of satellite operations, allowing developers and engineers to safely test software payloads, manage files, and run containerized applications as if interacting with CG2 in orbit.

> :warning: This Documentation described the inner workings of the EM API. To receive the documentation on how to access and interface with the API, please contact us.

> :warning: This EM API does not take into account communication windows. Meaning it will execute the request as soon as possible. However, always keep in mind that during space operations, requests will be batched and run together when communication windows are opened with CG2.

1. [Overview](/docs/3-em-api/01-overview.md)
2. [API Specifications](/docs/3-em-api/02-api-specs.md)
3. [Example](/docs/4-examples/2-python-em-api.md)
4. [FAQ](/docs/3-em-api/03-faq.md)
