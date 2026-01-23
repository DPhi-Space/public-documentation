# Telemetry

## Intro

This page can serve as base examples on how your flight application will be able to retrieve and make use of on-board telemetry from within the satellite. 
More detailed specifications of the API can be found [here](/docs/2-specs/1-telemetry.md).

### Base URL

The base url for every request is the following:

```bash
http://satellite-telemetry.dphi-tm
```

It will be referred to as `BASE_URL` in the rest of the documentation.

## Example Workflow for simple telemetry tasks

1. Check API status

```bash
curl "$BASE_URL/health"
```

Returns service status and timestamp.

2. List available types

```bash
curl "$BASE_URL/api/telemetry/types"
```

Returns all supported telemetry types.

3. Get telemetry records

```bash
curl "$BASE_URL/api/telemetry?datatype=attitude&limit=5"
```

Returns latest 5 attitude records.

WARNING: querying the endpoint without any parameter will cause the whole database to be returned, and therefore may timeout or fail if too many datapoints are present. We **discourage** relying on retrieving telemetry without constraining the query through time range parameters. 

4. Fetch stats or latest TLE

```bash
curl "$BASE_URL/api/telemetry/stats"
curl "$BASE_URL/api/telemetry/tle"
```

Returns telemetry stats or latest TLE string.

5. Full example curl for telemetry data:

```bash
curl "$BASE_URL/api/telemetry?starttime=2025-01-01T00:00:00Z&endtime=2025-01-02T00:00:00Z&datatype=attitude&limit=10"
```

## Fisheye images workflow
 
To get the Images the Fisheye camera took, one can gather a list of files first :
```bash
curl "$BASE_URL/api/images/list"
```
 
An example of the returned JSON might look as follows :
```json
{"success":true,"data":["example3.png","example2.png","example1.png"],"error":null,"count":3}
```
 
With this, one can either:
 
-  Get 1 single image, the result will be the image directly. One example to gather an image with curl would be :
```bash
curl -X POST -d '{"images": ["example3.png"]}' -H "Content-Type: application/json" http://satellite-telemetry.dphi-tm/api/images --output example3.png
```
 
- Get multiple images zipped together :
```bash
curl -X POST -d '{"images": ["example3.png","example2.png"]}' -H "Content-Type: application/json" http://satellite-telemetry.dphi-tm/api/images --output example.zip
```
 
- Finally get the whole set of images with a limit (Highly discouraged to go over 100 images as processing might take too long and timeout) :
```bash
curl -X POST -d '{"limit": 100}' -H "Content-Type: application/json" http://satellite-telemetry.dphi-tm/api/images --output example.zip
```
 
The zipped files are in fact not compressed, it uses the `STORED` algorithm, so it's more a convenient way to get multiple images at once.
