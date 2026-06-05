# LiquidAI Inference server

[LiquidAI](https://www.liquid.ai/) builds native device foundation models for advanced intelligence outside data centers, with a focus on low latency, privacy, and hardware-constrained environments.

Their [LFM](https://github.com/Liquid4All/dphi-space-vl) is onboard on Clustergate 2 and available for API requests in the same general way as the Ollama server.
The main difference is the endpoint URL, which points to LiquidAI instead of Ollama.

The example in [`examples/liquidai/vlm_infer.py`](../../examples/liquidai/vlm_infer.py) shows how to submit an image plus a natural-language prompt to the server using an OpenAI-compatible chat completions request.

:::warning
API requests are tracked and chargeable. LiquidAI usage is considered a paid metric.
:::

This is the same basic interaction pattern you would use with other chat-completions APIs:

- send a `POST` request
- include the model name
- pass a `messages` array
- encode the image as a `data:` URL
- read the assistant response from the first completion choice

## Usage

To use it onboard Clustergate 2, make a `POST` request to `http://liquid-3b.dphi-public/v1/chat/completions`.

The endpoint accepts a JSON body and returns a standard chat-completions response.
For the example in this repository, the server is used for image understanding rather than plain text-only chat.

The request payload should follow the OpenAI chat format, with the image included in the user message content before the text prompt.
The image-first ordering matters in the example because the multimodal message content is structured as an array of typed parts.

## Example

The example script `examples/liquidai/vlm_infer.py` does the following:

- reads an image from disk
- detects the file type with `mimetypes.guess_type`
- base64-encodes the raw image bytes
- wraps the encoded image in a `data:<mime>;base64,...` URL
- sends the image and prompt together in a `messages` array
- prints the final answer from `choices[0].message.content`

Example request body:

```json
{
  "model": "local",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/png;base64,..."
          }
        },
        {
          "type": "text",
          "text": "describe this"
        }
      ]
    }
  ],
  "max_tokens": 256,
  "temperature": 0.2,
  "cache_prompt": false
}
```

The important parts of the payload are:

- `model`: set to `local` in the example
- `messages[0].role`: `user`
- `messages[0].content[0]`: the image part
- `messages[0].content[1]`: the text prompt
- `max_tokens`: controls the length of the generated answer
- `temperature`: controls sampling randomness
- `cache_prompt`: disabled in the example

## Request notes

- `image_url.url` must be a base64-encoded `data:` URL.
- The image should come before the text in the `content` array.
- `max_tokens` and `temperature` are optional parameters used by the example, but they are useful knobs if you want to tune answer length or variability.
- The response text is available at `choices[0].message.content`.
- The example uses a `python3` client with `urllib.request`, so no external SDK is required.

## Example script

Inside a container, you can run the sample like this:

```bash
python3 vlm_infer.py --server http://liquid-3b.dphi-public --image ./image.png --prompt "describe this"
```

If you want to test a different image, pass any local file path supported by your image tooling.
The script will infer the MIME type from the filename and fall back to `image/jpeg` if it cannot determine one.

For a full [Operation YAML example](https://cg2.dphispace.com/docs/operations), use [`examples/liquidai/liquidai.yaml`](../../examples/liquidai/liquidai.yaml). It is the YAML you would fill in through the dashboard. This operation does the following:

- `uplink` uploads `vlm_infer.py` and the image into a working volume
- `pod_run_job` runs the script inside a `python:3.10-slim` container and pipes the response to a file
- `downlink_results` retrieves the generated output file
