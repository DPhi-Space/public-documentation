# Telemetry Onboard

## API Overview

The API provides telemetry access for satellite data, exposing endpoints to query historic and latest telemetry records, power stats, supported data types, and TLE information.
All the data comes from the spacecraft telemetry, as well as teh fisheye images.

### Base URL

The base url for every request is the following:

```bash
http://satellite-telemetry.dphi-tm
```

It will be referred to as `BASE_URL` in the rest of the documentation.

### Swagger UI

For development purposes and to help on the overall understanding of the API, there's a version with an included swagger-ui route.
This is only for test and dev purpose as this is not present in the Flight Model version of the API.

To access it simply go to `$BASE_URL/swagger-ui`, examples and specifications are already done to easify adoption.
There is also the OpenAPI json spec available [here](./tlm-api.json) with [Swagger documentation](https://editor.swagger.io/).

### Base Endpoints
Those are all the available endpoints that one may query and a brief purpose presented for each of them.

| Endpoint                | HTTP Verb | Purpose                       |
| ----------------------- | --------- | ------------------------      |
| `/health`               | GET       | API health/status             |
| `/api/telemetry`        | GET       | Query telemetry records       |
| `/api/telemetry/latest` | GET       | Latest telemetry per type     |
| `/api/telemetry/types`  | GET       | List available telemetry types|
| `/api/telemetry/stats`  | GET       | Returns telemetry stats types |
| `/api/telemetry/tle`    | GET       | Latest TLE record             |
| `/api/images/list`      | GET       | Returns images list           |
| `/api/images`           | POST      | Ask for images                |

## Request Parameters

Most query endpoints accept parameters inside the HTTP query string, captured as `TelemetryQueryParams`:

- `starttime` (`Option<String>`): RFC3339 start timestamp
- `endtime` (`Option<String>`): RFC3339 end timestamp
- `datatype` (`Option<String>`): type of telemetry (e.g., "temperature", "power")
- `limit` (`Option<i64>`): number of records to return

---
Note: this is not true for Fisheye API camera under `/api/images`.
---

Example curl for telemetry data, getting at most 10 measurements of temperature from 2025-01-01T00:00:00 to 2025-01-02T00:00:00Z:

```bash
curl "$BASE_URL/api/telemetry?starttime=2025-01-01T00:00:00Z&endtime=2025-01-02T00:00:00Z&datatype=temperature&limit=10"
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

---
NOTE: This is not true for answers of the /api/images calls as seen afterwards.
---

## Core Data Models

Responses contain telemetry data structured per the following models:

- `TelemetryData`: main composite model (timestamp, position, velocity, attitude, power, temperature, tle)
- `Position`, `Velocity`, `Attitude` (quaternion + angular velocity)
- `Temperature`: up to 8 sensor readings
- `Tle`: satellite Two-Line Element set as a String
- `TelemetryRecord`: database row including UUID, timestamp, datatype, and serialized data
- `FileList`: In case of using the api images list, only a list of strings to describe the allowed images to download

Full JSON example of a TelemetryData (can be retrieved with `/api/telemetry/latest` for example).
```json
{
  "success": true,
  "data": [
    {
      "id": "4be0349e-94fa-453b-9e16-ecea05719bc8",
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
      "created_at": "2026-01-13T11:16:18.849071Z"
    }
  ],
  "count": 1
}
```

Example JSON for a Temperature Telemetry Record

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

## Images data retrieval

To get back image, a filename or multiples are expected, for this the `/api/images/list` exists.

```bash
curl "$BASE_URL/api/images/list"
```

An example of the returned JSON might look as follows :
```json
{
  "success":true,
  "data":["20230606.png","20230607.png","20230608.png", "20251031.png"],
  "error":null,
  "count":4
}
```

For now the images have only dates as names, but the goal is that the Fisheye images will have their names as full timestamp afterwards.
Note that API might evolve slighlty to add features between EM and FM.

The `/api/images` POST request can accept this JSON structured data : 
```json
{"images": ["20230606.png","20230607.png"], "limit": 10}
```

`images` is used to get 1 or more images selected by filenames : 
- In case 1 image is selected it will be sent raw in PNG directly via HTTP and `Content-Type: image/png`.
- In case there is a selection of images, all those images will be zipped together (without compression) and sent back via HTTP and `Content-Type: application/zip`.
- In case no images are specified, create a Zip with all images and sent it back as previously explained via Zip.

`limit` is used to :
- truncate the answers if needed when asked multiple images
- limit the images that are zipped together in the case all images are being zipped (no `images` in request).

If there was an error during zipping or selecting files the error will be returned as simple text, so please keep this in mind.