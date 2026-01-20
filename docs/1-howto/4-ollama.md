# Ollama Inference server

There will be running an Ollama server running on the GPU of CG2 at all time.
You can have access to the preloaded models via the API calls ollama defines on his documentation.

## Usage

To use it you will need to simply make API calls to the `http://ollama-dphi.dphi-public` URL.

The Ollama endpoints available are : 

- `POST` `/api/generate` [ollama doc](https://docs.ollama.com/api/generate)
- `POST` `/api/chat` [ollama doc](https://docs.ollama.com/api/chat)
- `POST` `/api/embed` [ollama doc](https://docs.ollama.com/api/embed)
- `GET` `/api/tags` [ollama doc](https://docs.ollama.com/api/tags)
- `GET` `/api/ps` [ollama doc](https://docs.ollama.com/api/ps)
- `GET` `/api/show` [ollama doc](https://docs.ollama.com/api/show)
- `GET` `/api/version` [ollama doc](https://docs.ollama.com/api/version)

## Models

We have the following preloaded images (answer of the `/api/tags` endpoint) :

```json
{
  "models": [
    {
      "name": "llava:13b",
      "model": "llava:13b",
      "modified_at": "2025-12-27T12:24:24Z",
      "size": 8011256494,
      "digest": "0d0eb4d7f485d7d0a21fd9b0c1d5b04da481d2150a097e81b64acb59758fdef6",
      "details": {
        "parent_model": "",
        "format": "gguf",
        "family": "llama",
        "families": [
          "llama",
          "clip"
        ],
        "parameter_size": "13B",
        "quantization_level": "Q4_0"
      }
    },
    {
      "name": "ministral-3:8b",
      "model": "ministral-3:8b",
      "modified_at": "2025-12-27T12:20:58Z",
      "size": 6022236616,
      "digest": "1922accd5827ebe6829e536369195db25eaf664528dc66206d646ea3bb386b71",
      "details": {
        "parent_model": "",
        "format": "gguf",
        "family": "mistral3",
        "families": [
          "mistral3"
        ],
        "parameter_size": "8.9B",
        "quantization_level": "Q4_K_M"
      }
    },
    {
      "name": "deepseek-r1:8b",
      "model": "deepseek-r1:8b",
      "modified_at": "2025-12-27T12:16:44Z",
      "size": 5225376047,
      "digest": "6995872bfe4c521a67b32da386cd21d5c6e819b6e0d62f79f64ec83be99f5763",
      "details": {
        "parent_model": "",
        "format": "gguf",
        "family": "qwen3",
        "families": [
          "qwen3"
        ],
        "parameter_size": "8.2B",
        "quantization_level": "Q4_K_M"
      }
    },
    {
      "name": "llava:7b",
      "model": "llava:7b",
      "modified_at": "2025-12-27T12:07:47Z",
      "size": 4733363377,
      "digest": "8dd30f6b0cb19f555f2c7a7ebda861449ea2cc76bf1f44e262931f45fc81d081",
      "details": {
        "parent_model": "",
        "format": "gguf",
        "family": "llama",
        "families": [
          "llama",
          "clip"
        ],
        "parameter_size": "7B",
        "quantization_level": "Q4_0"
      }
    },
    {
      "name": "gemma3:4b",
      "model": "gemma3:4b",
      "modified_at": "2025-12-27T11:37:27Z",
      "size": 3338801804,
      "digest": "a2af6cc3eb7fa8be8504abaf9b04e88f17a119ec3f04a3addf55f92841195f5a",
      "details": {
        "parent_model": "",
        "format": "gguf",
        "family": "gemma3",
        "families": [
          "gemma3"
        ],
        "parameter_size": "4.3B",
        "quantization_level": "Q4_K_M"
      }
    }
  ]
}
```
