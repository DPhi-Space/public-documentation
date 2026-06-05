import base64
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, request


OLLAMA_URL = "http://ollama-dphi.dphi-public/api/generate"
IMAGE_PATH = Path("/data/fisheye.jpg")
OUTPUT_DIR = Path("/data")
LOG_PATH = OUTPUT_DIR / "vlms.log"
PROMPT = (
    "You are the first vision language model onboard a satellite to caption a picture from orbit."
    "Here is a fisheye image taken on the satellite where you're running. Write a brief message to humans to tell us what you're seeing!"
)
MODELS = ["gemma3:4b", "ministral-3:8b", "llava:7b"]
TIMEOUT_SECONDS = 240


class TeeStream:
    def __init__(self, stream, logger, level):
        self.stream = stream
        self.logger = logger
        self.level = level
        self.buffer = ""

    def write(self, message):
        self.stream.write(message)
        self.stream.flush()

        self.buffer += message
        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            if line:
                self.logger.log(self.level, line)

        return len(message)

    def flush(self):
        self.stream.flush()
        if self.buffer:
            self.logger.log(self.level, self.buffer)
            self.buffer = ""


def setup_logging():
    logger = logging.getLogger("vlms")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    try:
        file_handler = logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.info("Logging initialized at %s", LOG_PATH)
    except Exception as exc:
        stream_handler = logging.StreamHandler(sys.__stderr__)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        logger.warning(
            "Unable to open log file %s: %s: %s",
            LOG_PATH,
            type(exc).__name__,
            exc,
        )

    sys.stdout = TeeStream(sys.__stdout__, logger, logging.INFO)
    sys.stderr = TeeStream(sys.__stderr__, logger, logging.ERROR)
    return logger


def safe_filename(model_name):
    return model_name.replace(":", "_") + ".txt"


def timestamp_utc():
    return datetime.now(timezone.utc).isoformat()


def build_report(model_name, status, body):
    return "\n".join(
        [
            f"model: {model_name}",
            f"image: {IMAGE_PATH}",
            f"prompt: {PROMPT}",
            f"timestamp_utc: {timestamp_utc()}",
            f"status: {status}",
            "",
            body.strip() if body.strip() else "No content returned.",
            "",
        ]
    )


def save_report(model_name, status, body):
    output_path = OUTPUT_DIR / safe_filename(model_name)
    try:
        output_path.write_text(build_report(model_name, status, body), encoding="utf-8")
        return output_path, None
    except Exception as exc:
        return None, f"Unable to write {output_path}: {type(exc).__name__}: {exc}"


def load_image_base64():
    return base64.b64encode(IMAGE_PATH.read_bytes()).decode("ascii")


def analyze_model(model_name, image_b64):
    payload = {
        "model": model_name,
        "prompt": PROMPT,
        "images": [image_b64],
        "stream": False,
    }
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            raw_body = resp.read().decode("utf-8", errors="replace")
        try:
            response_json = json.loads(raw_body)
        except json.JSONDecodeError:
            return "error", (
                f"Ollama returned a non-JSON response.\nRaw response:\n{raw_body}"
            )

        if response_json.get("error"):
            return "error", f"Ollama error: {response_json['error']}"

        response_text = response_json.get("response", "").strip()
        if not response_text:
            return "error", (
                "Ollama returned JSON without a response field containing text.\n"
                f"JSON:\n{json.dumps(response_json, indent=2)}"
            )

        return "success", response_text
    except error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        return "error", (
            f"HTTP error {exc.code}: {exc.reason}\nResponse body:\n{error_body}"
        )
    except error.URLError as exc:
        return "error", f"Connection error while contacting Ollama: {exc.reason}"
    except TimeoutError:
        return "timeout", (
            f"Request exceeded {TIMEOUT_SECONDS} seconds and was stopped cleanly."
        )
    except Exception as exc:
        return "error", f"Unexpected error: {type(exc).__name__}: {exc}"


def main():
    logger = setup_logging()
    logger.info("Starting VLM image analysis run")

    try:
        image_b64 = load_image_base64()
    except Exception as exc:
        message = f"Unable to read image {IMAGE_PATH}: {type(exc).__name__}: {exc}"
        logger.error(message)
        for model_name in MODELS:
            output_path, write_error = save_report(model_name, "error", message)
            if output_path:
                print(f"[error] {model_name} -> {output_path}")
            else:
                logger.error(write_error)
                print(f"[error] {model_name} -> {write_error}")
        print(message)
        return

    for model_name in MODELS:
        logger.info("Requesting analysis from %s", model_name)
        status, body = analyze_model(model_name, image_b64)
        output_path, write_error = save_report(model_name, status, body)
        if output_path:
            logger.info("Saved %s result to %s", model_name, output_path)
            print(f"[{status}] {model_name} -> {output_path}")
        else:
            logger.error(write_error)
            print(f"[{status}] {model_name} -> {write_error}")

    logger.info("Completed VLM image analysis run")


if __name__ == "__main__":
    main()
