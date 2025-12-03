#!/usr/bin/env python3
import urllib.request
import json
import zipfile
import io
import os
import struct
from collections import Counter

# Configuration
API_BASE = "http://satellite-telemetry.dphi-tm/api/images"
OUTPUT_DIR = "/data"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_image_list():
    """Fetch list of available images"""
    print("Fetching image list...")
    req = urllib.request.Request(f"{API_BASE}/list")
    with urllib.request.urlopen(req) as response:
        data = response.read()
        return json.loads(data)


def fetch_specific_images(image_names):
    """Fetch specific images as ZIP"""
    print(f"Fetching {len(image_names)} images...")
    payload = json.dumps({"images": image_names}).encode("utf-8")
    req = urllib.request.Request(
        API_BASE, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as response:
        return response.read()


def fetch_recent_images(limit=10):
    """Fetch recent images with limit"""
    print(f"Fetching {limit} recent images...")
    payload = json.dumps({"limit": limit}).encode("utf-8")
    req = urllib.request.Request(
        API_BASE, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as response:
        return response.read()


def extract_images(zip_data):
    """Extract images from ZIP data"""
    images = []
    with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
        for filename in zf.namelist():
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                with zf.open(filename) as img_file:
                    img_data = img_file.read()
                    images.append((filename, img_data))
    return images


def read_png_metadata(png_data):
    """Extract basic PNG metadata without external libraries"""
    stats = {}

    # PNG signature check
    if png_data[:8] != b"\x89PNG\r\n\x1a\n":
        return {"error": "Not a valid PNG file"}

    pos = 8
    while pos < len(png_data):
        # Read chunk length and type
        if pos + 8 > len(png_data):
            break
        length = struct.unpack(">I", png_data[pos : pos + 4])[0]
        chunk_type = png_data[pos + 4 : pos + 8].decode("ascii", errors="ignore")

        if chunk_type == "IHDR":
            # Image header chunk
            width, height = struct.unpack(">II", png_data[pos + 8 : pos + 16])
            bit_depth = png_data[pos + 16]
            color_type = png_data[pos + 17]
            stats["width"] = width
            stats["height"] = height
            stats["bit_depth"] = bit_depth
            stats["color_type"] = (
                ["Grayscale", "RGB", "Palette", "Grayscale+Alpha", "RGBA"][color_type]
                if color_type < 5
                else "Unknown"
            )
            stats["total_pixels"] = width * height

        # Move to next chunk
        pos += 12 + length  # length + type + data + CRC

    return stats


def analyze_image(filename, img_data):
    """Perform basic image analysis using stdlib only"""
    stats = {"filename": filename, "size_bytes": len(img_data)}

    # Detect file type
    if img_data.startswith(b"\x89PNG"):
        stats["format"] = "PNG"
        stats.update(read_png_metadata(img_data))
    elif img_data.startswith(b"\xff\xd8\xff"):
        stats["format"] = "JPEG"
        # Basic JPEG size detection would be complex without PIL
        stats["note"] = "JPEG metadata extraction limited without libraries"
    else:
        stats["format"] = "Unknown"

    # Calculate basic file statistics
    byte_counter = Counter(img_data)
    stats["unique_bytes"] = len(byte_counter)
    stats["entropy_estimate"] = len(byte_counter) / 256.0  # Rough entropy indicator

    return stats


def main():
    insights = {"total_images_processed": 0, "images": {}}

    # Option 1: Fetch specific images
    # zip_data = fetch_specific_images(["20251031.png", "20251030.png"])

    # Option 2: Fetch recent images (using this as default)
    zip_data = fetch_recent_images(limit=10)

    # Extract and process images
    images = extract_images(zip_data)
    print(f"Extracted {len(images)} images")

    for filename, img_data in images:
        print(f"Processing {filename}...")
        stats = analyze_image(filename, img_data)
        insights["images"][filename] = stats

        # Save raw image file
        img_path = os.path.join(OUTPUT_DIR, filename)
        with open(img_path, "wb") as f:
            f.write(img_data)
        print(f"  Saved image to {img_path}")

    insights["total_images_processed"] = len(images)

    # Save insights to JSON
    insights_path = os.path.join(OUTPUT_DIR, "insights.json")
    with open(insights_path, "w") as f:
        json.dump(insights, f, indent=2)

    print(f"\nProcessing complete!")
    print(f"Insights saved to: {insights_path}")
    print(f"Total images processed: {insights['total_images_processed']}")


if __name__ == "__main__":
    main()
