import os
import csv
import json
import socket
import time
import requests
from datetime import datetime

environment = os.getenv("ENVIRONMENT")

if environment == "DOCKER":
    API_HOST = "satellite-telemetry.dphi-tm"
    print("Running inside a Docker Container")
    OUTPUT_FILE = "/app/data/telemetry.json"
else:
    API_HOST = "localhost"
    print("Running natively")
    OUTPUT_FILE = "telemetry.json"
API_PORT = 8000


def fetch_from_api(api_host=API_HOST, api_port=API_PORT, output_file=OUTPUT_FILE):
    """Fetch telemetry data from REST API and save to file."""
    base_url = f"http://{api_host}:{api_port}"

    try:
        all_data = {}

        print("Fetching health status...")
        while True:
            response = requests.get(f"{base_url}/health")
            if response.ok:
                all_data["health"] = response.json()
                print(f"Health: {response.json()}")
                break

        print("\n\n\nFetching latest telemetry...")
        response = requests.get(f"{base_url}/api/telemetry/latest")
        all_data["latest"] = response.json()
        print(f"Latest data: {json.dumps(response.json(), indent=2)}")

        print("\n\n\nFetching statistics...")
        response = requests.get(f"{base_url}/api/telemetry/stats")
        all_data["stats"] = response.json()
        print(f"Stats: {json.dumps(response.json(), indent=2)}")

        print("\n\n\nFetching data types...")
        response = requests.get(f"{base_url}/api/telemetry/types")
        all_data["types"] = response.json()
        print(f"Types: {response.json()}")

        print("\n\n\nFetching latest positional telemetry data point...")
        response = requests.get(f"{base_url}/api/telemetry/latest?data_type=position")
        all_data["telemetry"] = response.json()
        print(f"Position: {json.dumps(response.json(), indent=2)}")

        with open(output_file, "w") as f:
            json.dump(all_data, f, indent=2)
        print(f"\n\n\nData saved to {output_file}")

    except Exception as e:
        print(f"Error fetching from API: {e}")


if __name__ == "__main__":
    fetch_from_api()
