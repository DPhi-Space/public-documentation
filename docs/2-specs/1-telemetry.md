# Telemetry Onboard

## API Overview

The API provides telemetry access for satellite data, exposing endpoints to query historic and latest telemetry records, power stats, supported data types, and TLE information. It uses [axum](https://docs.rs/axum/latest/axum/) for routing and [serde](https://serde.rs/) models for JSON serialization.

### Base URL

The base url for evey request is the following:

```bash
http://satellite-telemetry.dphi-tm
```

It will be referred to as `BASE_URL` in the rest of the documentation.

### Base Endpoints

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

Most query endpoints accept parameters in the query string, captured as `TelemetryQueryParams`:

- `starttime` (`Option<String>`): RFC3339 start timestamp
- `endtime` (`Option<String>`): RFC3339 end timestamp
- `datatype` (`Option<String>`): type of telemetry (e.g., "temperature", "power")
- `limit` (`Option<i64>`): number of records to return

Note: this is not true for Fisheye API camera under `/api/images`.

Example curl for telemetry data:

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

## Core Data Models

Responses contain telemetry data structured per the following models:

- `TelemetryData`: main composite model (timestamp, position, velocity, attitude, power, temperature, tle)
- `Position`, `Velocity`, `Attitude` (quaternion + angular velocity)
- `Temperature`: up to 8 sensor readings
- `Tle`: satellite Two-Line Element set as a String
- `TelemetryRecord`: database row including UUID, timestamp, datatype, and serialized data
- `FileList`: In case of using the api images list, only a list of strings to describe the allowed images to download

Full JSON example of a TelemetryData (can be retrieved with `/api/telemetry/latest` for example).
Here some data is repeated, this is still partially work-in-progress, but in the datatype `complete` the wole set of available data is here.
```json
{
  "success":true,
  "data":[
    {
      "id":"d7553869-b8b7-4c6f-ad61-9ce0c3f79811",
      "timestamp":"2025-06-03T17:55:14Z",
      "original_timestamp":1748973314,
      "data_type":"attitude",
      "data":{
        "angular_velocity":{"x":0.00025407286011613905,"y":0.0001094558829208836,"z":0.0002309548872290179},
        "quaternion":{"w":0.5180827379226685,"x":0.5806567668914795,"y":-0.33653801679611206,"z":-0.5302548408508301}},
      "created_at":"2025-12-02T11:37:03.783355Z"
    },
    {
      "id":"a5c5aadf-79c5-4cc3-80ea-56e76d2988c0",
      "timestamp":"2025-06-03T17:55:14Z",
      "original_timestamp":1748973314,
      "data_type":"complete",
      "data":
        {
          "attitude":{
            "angular_velocity":{"x":0.00025407286011613905,"y":0.0001094558829208836,"z":0.0002309548872290179},
            "quaternion":{"w":0.5180827379226685,"x":0.5806567668914795,"y":-0.33653801679611206,"z":-0.5302548408508301}
          },
          "position":{"x":693.9917211431641,"y":3862.9954080527136,"z":5656.33788552188},
          "power":null,
          "temperature":null,
          "timestamp":1748973314,
          "tle":null,
          "velocity":{"x":3.0590987427791116,"y":5.645034499476198,"z":-4.212076409076806}
        },
      "created_at":"2025-12-02T11:37:03.787218Z"},
    {
      "id":"b90279f1-b0f2-4f08-8dcf-7b2ef881b040",
      "timestamp":"2025-06-03T17:55:14Z",
      "original_timestamp":1748973314,
      "data_type":"position",
      "data":{"x":693.9917211431641,"y":3862.9954080527136,"z":5656.33788552188},
      "created_at":"2025-12-02T11:37:03.683689Z"
    },
    {
      "id":"5e3a258f-7675-4cdc-ac80-1c3718a59659",
      "timestamp":"2025-06-03T17:55:14Z",
      "original_timestamp":1748973314,
      "data_type":"velocity",
      "data":{"x":3.0590987427791116,"y":5.645034499476198,"z":-4.212076409076806},
      "created_at":"2025-12-02T11:37:03.770613Z"
    }
  ],
  "error":null,
  "count":4
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
- In case there is a selection of images, all thos images will be zipped together (without compression) and sent back via HTTP and `Content-Type: application/zip`.
- In case no images are specified, create a Zip with all images and sent it back as previously explained via Zip.

`limit` is used to :
- truncate the answers if needed when asked multiple images
- limit the images that are zipped together in the case all images are being zipped (no `images` in request).

If there was an error during zipping or selecting files the error will be returned as simple text, so please keep this in mind when testing for now.