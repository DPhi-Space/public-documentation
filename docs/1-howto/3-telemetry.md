---
sidebar_position: 1
---

# Telemetry Onboard

## API Overview

The API provides telemetry access for satellite data, exposing endpoints to query historic and latest telemetry records, power stats, supported data types, and TLE information. It uses axum for routing and serde models for JSON serialization.

### Base endpoints

| Endpoint | HTTP Verb | Purpose |
| -------- | -------- | -------- |
| `/health` |   GET |   API health/ |status
| `/api/telemetry` |    GET |   Query telemetry records |
| `/api/telemetry/power` |  GET |   Query power telemetry | only
| `/api/telemetry/latest` | GET |   Latest telemetry per | type
| `/api/telemetry/types` |  GET |   List available telemetry | types
| `/api/telemetry/stats` |  GET |   Returns telemetry stats |
| `/api/telemetry/tle` |    GET |   Latest TLE record |



## Request Parameters

Most query endpoints accept parameters in the query string, captured as TelemetryQueryParams:
- `starttime` (`Option<String>`): RFC3339 start timestamp
- `endtime` (`Option<String>`): RFC3339 end timestamp
- `datatype` (`Option<String>`): type of telemetry (e.g., "temperature", "power")
- `limit` (`Option<i64>`): number of records to return

Example curl for telemetry data:

```bash
curl "http://satellite-telemetry.dphi-tm:8080/api/telemetry?starttime=2025-01-01T00:00:00Z&endtime=2025-01-02T00:00:00Z&datatype=temperature&limit=10"
```

## Response Format

All responses use the generic API response wrapper:

```json
{
  "success": true,
  "data": [ ... ],
  "count": 10,
  "error": null
}
```

- `success`: indicates operation status
- `data`: the result payload (models described below)
- `count`: returned item count (if applicable)
- `error`: error message on failure

## Core Data Models

Responses contain telemetry data structured per the following models:

- `TelemetryData`: main composite model (timestamp, position, velocity, attitude, power, temperature, tle)
- `Position`, `Velocity`, `Attitude` (quaternion + angular velocity)
- `Power`: details payload/internal power, with per-channel status, consumption, current
- `Temperature`: up to 8 sensor readings
- `Tle`: satellite Two-Line Element set
- `TelemetryRecord`: database row including UUID, timestamp, datatype, and serialized data

Example JSON for a Telemetry Record
```json
{
  "id": "uuid-string",
  "timestamp": "2025-09-30T09:42:00Z",
  "originaltimestamp": 1706757600,
  "datatype": "temperature",
  "data": {
    "sensor0": 34,
    "sensor1": 35,
    ...
  },
  "createdat": "2025-09-30T09:42:00Z"
}
```

Example Workflow

1. Check API status

```bash
curl "http://satellite-telemetry.dphi-tm:8080/health"
```
Returns service status and timestamp.

2. List available types

```bash
curl "http://satellite-telemetry.dphi-tm:8080/api/telemetry/types"
```
Returns all supported telemetry types.

3. Get telemetry records

```bash
curl "http://satellite-telemetry.dphi-tm:8080/api/telemetry?datatype=temperature&limit=5"
```
Returns latest 5 temperature records.

4. Get only power telemetry

```bash
curl "http://satellite-telemetry.dphi-tm:8080/api/telemetry/power?limit=3"
```
Returns power telemetry records.

5. Fetch stats or latest TLE

```bash
curl "http://satellite-telemetry.dphi-tm:8080/api/telemetry/stats"
curl "http://satellite-telemetry.dphi-tm:8080/api/telemetry/tle"
```
Returns telemetry stats or latest TLE string.

### Error Handling

Errors are returned with `success: false`, and informative messages in the `error` field:

```json
{ "success": false, "error": "Database error: ..." }
```
