# Example: Telemetry API

A simple Python client that fetches satellite telemetry data from the REST API onboard and saves it to a JSON file. The script exits by itself after it successfully fetches the data, otherwise it keeps polling the API until the service is up and running.

## What It Does

The script fetches different data from the telemetry API onboard, such as:

- **Health Status** - API health check to make sure it is up and ready to provide data.
- **Latest Telemetry** - Most recent telemetry data points.
- **Statistics** - Database stats (record counts, time ranges)
- **Data Types** - Available telemetry types
- **Latest Positional Telemetry** - Latest Positional telemetry data point.

All data is saved to `telemetry.json` on the root folder from where the docker compose or the python script is run.

The script fetches the data from the satellite telemetry url, as explained in the [Telemetry Section](2-specs/1-telemetry.md):

```
http://satellite-telemetry.dphi-tm:8000
```

## How to Run

### Within Docker

#### Prerequisites

- Docker
- Docker Compose

#### Build and Run

The docker compose will pull the API and dummy database with virtual data when ran. The `payload` service builds from the `Dockerfile` in the folder.

```bash
cd examples/telemetry/

# Build the Docker image for the payload service
docker compose build

# Pull the Docker images for the API and the database
docker compose pull

# Start the system
docker compose up

# Alternatively: Run in background
docker compose up -d

# Stop
docker-compose down
```

#### Output

This will run the `payload` service, which fetches data from the API and saves it to a file after a few seconds. Data is saved to `telemetry-docker.json` on your host machine in the same folder where the docker compose file is, i.e. `examples/telemetry/`

### Native Python

#### Prerequisites

- Python
- pip

Install the necessary pip packages by running the following:

```bash
cd examples/telemetry
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Run

```bash
docker compose up postgres satellite-telemetry.dphi-tm
python3 telemetry-api-client.py
```

#### Output

Data is saved to `telemetry-native.json` on your host machine in the folder were the script was executed.

### Example Output

The json file generated has the structure shown below.

```json
{
  "health": {
    "service": "satellite-telemetry-api",
    "status": "healthy",
    "timestamp": "2025-10-21T07:01:42.960895563Z"
  },
  "latest": {
    "success": true,
    "data": [
      {
        "id": "13ef8cf3-1f6a-4629-bf1e-674ad5d8ffd1",
        "timestamp": "2025-06-03T17:55:14Z",
        "original_timestamp": 1748973314,
        "data_type": "attitude",
        "data": {
          "angular_velocity": {
            "x": 0.00025407286011613905,
            "y": 0.0001094558829208836,
            "z": 0.0002309548872290179
          },
          "quaternion": {
            "w": 0.5180827379226685,
            "x": 0.5806567668914795,
            "y": -0.33653801679611206,
            "z": -0.5302548408508301
          }
        },
        "created_at": "2025-10-20T11:03:24.978570Z"
      },
      {
        "id": "a92f1244-7c1b-4453-9b69-a8c178a5585c",
        "timestamp": "2025-06-03T17:55:14Z",
        "original_timestamp": 1748973314,
        "data_type": "complete",
        "data": {
          "attitude": {
            "angular_velocity": {
              "x": 0.00025407286011613905,
              "y": 0.0001094558829208836,
              "z": 0.0002309548872290179
            },
            "quaternion": {
              "w": 0.5180827379226685,
              "x": 0.5806567668914795,
              "y": -0.33653801679611206,
              "z": -0.5302548408508301
            }
          },
          "position": {
            "x": 693.9917211431641,
            "y": 3862.9954080527136,
            "z": 5656.33788552188
          },
          "power": null,
          "temperature": null,
          "timestamp": 1748973314,
          "tle": null,
          "velocity": {
            "x": 3.0590987427791116,
            "y": 5.645034499476198,
            "z": -4.212076409076806
          }
        },
        "created_at": "2025-10-20T11:03:24.980581Z"
      },
      {
        "id": "53e4370a-2ec2-471b-8768-1ee105abaa9c",
        "timestamp": "2025-06-03T17:55:14Z",
        "original_timestamp": 1748973314,
        "data_type": "position",
        "data": {
          "x": 693.9917211431641,
          "y": 3862.9954080527136,
          "z": 5656.33788552188
        },
        "created_at": "2025-10-20T11:03:24.962370Z"
      },
      {
        "id": "c5ed3446-47e1-4a63-8b11-bd3bf4917e85",
        "timestamp": "2025-06-03T17:55:14Z",
        "original_timestamp": 1748973314,
        "data_type": "velocity",
        "data": {
          "x": 3.0590987427791116,
          "y": 5.645034499476198,
          "z": -4.212076409076806
        },
        "created_at": "2025-10-20T11:03:24.975126Z"
      }
    ],
    "error": null,
    "count": 4
  },
  "stats": {
    "success": true,
    "data": {
      "total_records": 1728,
      "data_types_count": 4,
      "earliest_timestamp": "2025-06-03T02:06:13Z",
      "latest_timestamp": "2025-06-03T17:55:14Z",
      "data_type_breakdown": {
        "velocity": 432,
        "attitude": 432,
        "complete": 432,
        "position": 432
      }
    },
    "error": null,
    "count": null
  },
  "types": {
    "success": true,
    "data": [
      "attitude",
      "complete",
      "position",
      "velocity"
    ],
    "error": null,
    "count": 4
  },
  "telemetry": {
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
}
```
