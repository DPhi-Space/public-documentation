#!/usr/bin/env python3
import sys
import urllib.request
import json
import zipfile
import io
import os
import struct
from collections import Counter
import numpy as np
import torch
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import time

# Configuration
API_BASE = "http://satellite-telemetry.dphi-tm/api/images"
OUTPUT_DIR = "/data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Redirect stdout and stderr to log file
log_file = open("/data/log.txt", "w")
sys.stdout = log_file
sys.stderr = log_file

# CUDA Configuration
print("=" * 60)
print("JETSON NANO CUDA IMAGE ANALYSIS")
print("=" * 60)
print(f"PyTorch Version: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA Device: {torch.cuda.get_device_name(0)}")
    print(f"CUDA Version: {torch.version.cuda}")
    print(f"cuDNN Version: {torch.backends.cudnn.version()}")
    print(
        f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB"
    )
print("=" * 60)

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\nUsing device: {device}\n")


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


class ImageAnalyzer:
    """CUDA-accelerated image analyzer with deep learning features"""

    def __init__(self, device):
        self.device = device

        # Load pre-trained ResNet18 for feature extraction (lightweight for Jetson)
        print("Loading ResNet18 model from local checkpoint...")
        ckpt = "/data/resnet18-f37072fd.pth"

        self.feature_model = models.resnet18()
        state = torch.load(ckpt, map_location=device)
        self.feature_model.load_state_dict(state)

        self.feature_model = self.feature_model.to(device)
        self.feature_model.eval()

        # Remove final classification layer to get features
        self.feature_extractor = torch.nn.Sequential(
            *list(self.feature_model.children())[:-1]
        )

        # Image preprocessing
        self.preprocess = transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

        # For classification (optional)
        with open("/tmp/imagenet_classes.txt", "w") as f:
            # Simplified - in practice you'd load actual ImageNet classes
            f.write("satellite\nearth\ncloud\nocean\nland\n")

    def analyze_cuda(self, img_data):
        """Perform GPU-accelerated image analysis"""
        start_time = time.time()

        # Load image
        img = Image.open(io.BytesIO(img_data)).convert("RGB")
        img_np = np.array(img)

        stats = {
            "basic_info": {
                "width": img.width,
                "height": img.height,
                "total_pixels": img.width * img.height,
                "mode": img.mode,
                "size_bytes": len(img_data),
            }
        }

        # Convert to tensor and move to GPU
        img_tensor = self.preprocess(img).unsqueeze(0).to(self.device)

        # Extract deep features using CUDA
        with torch.no_grad():
            features = self.feature_extractor(img_tensor)
            feature_vector = features.squeeze().cpu().numpy()

            stats["deep_features"] = {
                "feature_dimension": len(feature_vector),
                "feature_mean": float(np.mean(feature_vector)),
                "feature_std": float(np.std(feature_vector)),
                "feature_l2_norm": float(np.linalg.norm(feature_vector)),
                "feature_sparsity": float(
                    np.sum(feature_vector == 0) / len(feature_vector)
                ),
            }

        # Color analysis on GPU
        img_tensor_rgb = torch.from_numpy(img_np).float().to(self.device)

        # Channel statistics
        r_channel = img_tensor_rgb[:, :, 0]
        g_channel = img_tensor_rgb[:, :, 1]
        b_channel = img_tensor_rgb[:, :, 2]

        stats["color_analysis"] = {
            "red_channel": {
                "mean": float(r_channel.mean()),
                "std": float(r_channel.std()),
                "min": float(r_channel.min()),
                "max": float(r_channel.max()),
            },
            "green_channel": {
                "mean": float(g_channel.mean()),
                "std": float(g_channel.std()),
                "min": float(g_channel.min()),
                "max": float(g_channel.max()),
            },
            "blue_channel": {
                "mean": float(b_channel.mean()),
                "std": float(b_channel.std()),
                "min": float(b_channel.min()),
                "max": float(b_channel.max()),
            },
            "overall_brightness": float(img_tensor_rgb.mean()),
            "overall_contrast": float(img_tensor_rgb.std()),
        }

        # Edge detection (Sobel operator on GPU)
        gray = img_tensor_rgb.mean(dim=2)

        # Sobel kernels
        sobel_x = (
            torch.tensor(
                [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]],
                dtype=torch.float32,
                device=self.device,
            )
            .unsqueeze(0)
            .unsqueeze(0)
        )
        sobel_y = (
            torch.tensor(
                [[-1, -2, -1], [0, 0, 0], [1, 2, 1]],
                dtype=torch.float32,
                device=self.device,
            )
            .unsqueeze(0)
            .unsqueeze(0)
        )

        gray_4d = gray.unsqueeze(0).unsqueeze(0)

        # Apply convolution for edge detection
        edges_x = torch.nn.functional.conv2d(gray_4d, sobel_x, padding=1)
        edges_y = torch.nn.functional.conv2d(gray_4d, sobel_y, padding=1)
        edges_magnitude = torch.sqrt(edges_x**2 + edges_y**2)

        stats["edge_analysis"] = {
            "edge_density": float(edges_magnitude.mean()),
            "edge_strength_std": float(edges_magnitude.std()),
            "max_edge_strength": float(edges_magnitude.max()),
            "complexity_score": float(
                edges_magnitude.std() / (edges_magnitude.mean() + 1e-6)
            ),
        }

        # Texture analysis (local variance)
        kernel_size = 5
        unfold = torch.nn.Unfold(kernel_size=kernel_size, padding=kernel_size // 2)
        patches = unfold(gray_4d)
        local_variance = patches.var(dim=1)

        stats["texture_analysis"] = {
            "mean_local_variance": float(local_variance.mean()),
            "texture_uniformity": float(1.0 / (local_variance.std() + 1e-6)),
            "roughness_score": float(local_variance.std()),
        }

        # Histogram analysis on GPU
        hist_bins = 32
        r_hist = torch.histc(r_channel, bins=hist_bins, min=0, max=255)
        g_hist = torch.histc(g_channel, bins=hist_bins, min=0, max=255)
        b_hist = torch.histc(b_channel, bins=hist_bins, min=0, max=255)

        stats["histogram_analysis"] = {
            "red_entropy": float(-torch.sum(r_hist * torch.log2(r_hist + 1e-10))),
            "green_entropy": float(-torch.sum(g_hist * torch.log2(g_hist + 1e-10))),
            "blue_entropy": float(-torch.sum(b_hist * torch.log2(b_hist + 1e-10))),
        }

        # Processing time
        processing_time = time.time() - start_time
        stats["performance"] = {
            "processing_time_seconds": processing_time,
            "pixels_per_second": stats["basic_info"]["total_pixels"] / processing_time,
            "cuda_used": True,
        }

        return stats


def main():
    insights = {
        "cuda_info": {
            "available": torch.cuda.is_available(),
            "device_name": torch.cuda.get_device_name(0)
            if torch.cuda.is_available()
            else "CPU",
            "pytorch_version": torch.__version__,
        },
        "total_images_processed": 0,
        "images": {},
    }

    # Initialize CUDA analyzer
    analyzer = ImageAnalyzer(device)

    # Fetch images
    zip_data = fetch_recent_images(limit=10)

    # Extract and process images
    images = extract_images(zip_data)
    print(f"\n{'=' * 60}")
    print(f"Extracted {len(images)} images - Starting GPU Analysis")
    print(f"{'=' * 60}\n")

    total_processing_time = 0

    for idx, (filename, img_data) in enumerate(images, 1):
        print(f"[{idx}/{len(images)}] Processing {filename}...")

        # GPU-accelerated analysis
        stats = analyzer.analyze_cuda(img_data)
        insights["images"][filename] = stats

        total_processing_time += stats["performance"]["processing_time_seconds"]

        # Print key insights
        print(
            f"  ✓ Size: {stats['basic_info']['width']}x{stats['basic_info']['height']}"
        )
        print(f"  ✓ Brightness: {stats['color_analysis']['overall_brightness']:.1f}")
        print(f"  ✓ Edge Density: {stats['edge_analysis']['edge_density']:.2f}")
        print(f"  ✓ Complexity: {stats['edge_analysis']['complexity_score']:.2f}")
        print(
            f"  ✓ Processing Time: {stats['performance']['processing_time_seconds']:.3f}s"
        )
        print(
            f"  ✓ Throughput: {stats['performance']['pixels_per_second'] / 1e6:.2f} Mpx/s\n"
        )

        # Save raw image file
        img_path = os.path.join(OUTPUT_DIR, filename)
        with open(img_path, "wb") as f:
            f.write(img_data)

    insights["total_images_processed"] = len(images)
    insights["summary"] = {
        "total_processing_time": total_processing_time,
        "average_time_per_image": total_processing_time / len(images) if images else 0,
        "total_throughput_mpx_per_sec": sum(
            i["performance"]["pixels_per_second"] for i in insights["images"].values()
        )
        / 1e6
        / len(images)
        if images
        else 0,
    }

    # Save insights to JSON
    insights_path = os.path.join(OUTPUT_DIR, "cuda_insights.json")
    with open(insights_path, "w") as f:
        json.dump(insights, f, indent=2)

    print(f"{'=' * 60}")
    print(f"PROCESSING COMPLETE!")
    print(f"{'=' * 60}")
    print(f"Insights saved to: {insights_path}")
    print(f"Total images processed: {insights['total_images_processed']}")
    print(f"Total processing time: {total_processing_time:.2f}s")
    print(
        f"Average throughput: {insights['summary']['total_throughput_mpx_per_sec']:.2f} Mpx/s"
    )
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
