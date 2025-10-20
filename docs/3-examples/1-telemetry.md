# Example: Telemetry API

A simple Python client that fetches satellite telemetry data from the REST API onboard and saves it to a JSON file.

## What It Does

The script continuously polls the telemetry API every 10 seconds and fetches:

- **Health status** - API health check
- **Latest telemetry** - Most recent data point
- **Statistics** - Database stats (record counts, time ranges)
- **Data types** - Available telemetry types
- **All telemetry** - Last 1000 records

All data is saved to `/data/telemetry_data.json` (mounted volume).

The script fetches the data from the satellite telemetry url, as explained in the ![](Telemetry Section):

```
http://satellite-telemetry.dphi-tm:8000
```

## How to Run

### Prerequisites

- Docker and Docker Compose installed

### Build and Run

```bash
cd examples/telemetry/

# Build the Docker image
docker-compose build

# Start the fetcher
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f telemetry-fetcher

# Stop
docker-compose down
```

## Output

Data is saved to `./data/telemetry_data.json` on your host machine.

Example output structure:

```json
{
  "health": {...},
  "latest": {...},
  "stats": {...},
  "types": [...],
  "telemetry": [...]
}
```

## Files

- `telemetry-api-client.py` - Python fetcher script
- `Dockerfile` - Container definition
- `docker-compose.yml` - Service orchestration
- `data/` - Output directory (created automatically)
