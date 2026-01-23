# Telemetry API Client

A simple Python client that fetches **satellite telemetry data** from the onboard REST API and saves it as a JSON file.

The script automatically **polls the API until it becomes available**, ensuring that data retrieval only happens once the service is ready. When successful, it fetches multiple telemetry endpoints, stores the results locally, and then exits gracefully.

This example has been tested on AMD64 and on ARMv8 using Rosetta 2.

The Telemetry API reference can be found in the [Telemetry Section](/docs/2-specs/1-telemetry.md).

---

## Features

The client retrieves the following data from the onboard **Telemetry API**:

- **Health Status** – Confirms that the API is up and responding.
- **Latest Telemetry** – Most recent telemetry data entries.
- **Statistics** – Database record counts, timestamps, and related stats.
- **Data Types** – Available telemetry types.
- **Latest Positional Telemetry** – The latest positional data point.

All results are saved into a single JSON file (`telemetry.json`) in the current working directory or a mapped Docker volume.

---

## Telemetry API Endpoint

The API base URL is shown below, as detailed in the [Telemetry API Section](/docs/2-specs/1-telemetry.md), which also describes all available endpoints.

```
http://satellite-telemetry.dphi-tm
```

NOTE: This URL works only if you are running inside the docker compose file that will be shown here-after, or while running on the satellite cluster.
If you want to use the API from outside the docker compose, please simply use `http://localhost:8000` as a base URL. 

## Setup

Clone the public documentation repository to get the source code.

```bash
git clone git@github.com:DPhi-Space/public-documentation.git
cd public-documentation/examples/telemetry
```

---

## Running the Client

You can run the telemetry client in **two ways**:

- Inside a Docker environment (recommended)
- Natively on your local machine (for testing or debugging)

---

### Option 1: Run Within Docker

#### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

#### Docker Compose Setup

The provided `docker-compose.yml` defines three services:

```yaml
services:
  postgres:
    image: dphispace/telemetry-db
    restart: always
    environment:
      POSTGRES_DB: satellite_telemetry
      POSTGRES_USER: satellite_user
      POSTGRES_PASSWORD: satellite_pass
      PGDATA: /postgres

  satellite-telemetry.dphi-tm:
    image: dphispace/telemetry-api
    depends_on:
      - postgres
    restart: always
    ports:
      - 0.0.0.0:4949:4949
      - 0.0.0.0:8000:8000

  payload:
    build:
      context: .
      dockerfile: Dockerfile
    depends_on:
      - satellite-telemetry.dphi-tm
    environment:
      - ENVIRONMENT=DOCKER
    volumes:
      - type: bind
        source: ./
        target: /app/data
```

The `payload` container runs the Python telemetry client that polls the API and writes its output to the mounted volume.

#### Steps to Run

```bash
cd examples/telemetry/

# 1. Build the payload container
docker compose build

# 2. Pull API and database images
docker compose pull

# 3. Start all services in the background
docker compose up -d
```

To stop all services:

```bash
docker compose down
```

#### Expected Output

After a few seconds, you’ll see console logs confirming successful data retrieval.
A file named **`telemetry-docker.json`** will be created in your current directory:

```
examples/telemetry/telemetry-docker.json
```

This file contains the collected telemetry data in JSON format.

---

### Option 2: Run Natively with Python

#### Prerequisites

- Python 3.8+
- pip

#### Setup Environment

```bash
cd examples/telemetry/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Run the Services

Make sure the API and database are up before running the client:

```bash
docker compose up -d postgres satellite-telemetry.dphi-tm
```

Then run the Python client:

```bash
python3 telemetry-api-client.py
```

#### Expected Output

The client will fetch telemetry data and save it to:

```
telemetry-native.json
```

---

## Example Output Structure

A simplified example of what the generated JSON looks like:

```json
{
  "success": true,
  "data": [
    {
      "id": "cb760ade-fc4b-4bdc-9fd3-ff11cd9ff5d1",
      "timestamp": "2025-06-03T17:55:14Z",
      "original_timestamp": 1748973314,
      "data_type": "position",
      "data": {
        "x": 693.9917211431641,
        "y": 3862.9954080527136,
        "z": 5656.33788552188
      },
      "created_at": "2025-10-20T11:11:33.158280Z"
    }
  ],
  "error": null,
  "count": 1
}
```

---

## How It Works

The `telemetry-api-client.py` script:

1. Detects the runtime environment (`DOCKER` vs local).
2. Polls the `/health` endpoint until the API is ready.
3. Fetches all telemetry endpoints:
   - `/api/telemetry/latest`
   - `/api/telemetry/stats`
   - `/api/telemetry/types`
   - `/api/telemetry/latest?data_type=position`

4. Aggregates all results into a single dictionary.
5. Saves everything to a JSON file (either `telemetry-docker.json` or `telemetry-native.json`).

---

## Notes

- If running natively, ensure that both the **PostgreSQL** and **Telemetry API** containers are active before executing the script.
- The client retries until the API is reachable, avoiding race conditions during startup.

---
