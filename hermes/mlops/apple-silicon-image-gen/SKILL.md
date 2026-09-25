---
name: apple-silicon-image-gen
description: Use for ComfyUI/GGUF image-gen setup on Apple Silicon Mac.
---

# Local image generation on Apple Silicon (ComfyUI)

## Environment setup

- Use `uv` (installed) with a Homebrew python (3.11/3.12/3.14 available); the system python 3.9 is too old for current torch. `uv venv --python 3.12 .venv`.
- `uv venv` does NOT create a `pip` binary — install with `uv pip install --python .venv/bin/python <pkgs>` instead of `.venv/bin/pip`, or the install fails with 'no such file'.
- Install order: `torch torchvision torchaudio` first, then ComfyUI `requirements.txt` plus each custom node's requirements. Verify with `python -c "import torch; print(torch.backends.mps.is_available())"`.
- Standard layout: clone ComfyUI to `~/github/ComfyUI`, custom nodes under `custom_nodes/`. The GGUF loader node is `leejet/ComfyUI-GGUF`.

## Model formats on Mac — pick before downloading

- NEVER download the `fp8` safetensors variant for a Mac: fp8 is an NVIDIA/CUDA format that PyTorch MPS does not properly support. Use bf16 / int8_convrot safetensors or GGUF.
- GGUF quant choice by RAM: with 48 GB unified memory take Q8_0 (~8 GB denoiser); K-quants are slower on MPS — no benefit at this RAM headroom.
- File placement: denoiser → `models/unet/`, text encoder → `models/text_encoders/`, VAE → `models/vae/`. A Qwen-Image-style release ships three separate files, not one checkpoint.

## Downloading

- HuggingFace file URLs need `-L` on curl (resolve/main redirects to CDN): `curl -sL "https://huggingface.co/<repo>/resolve/main/<path>" -o <target>`. Multi-GB files: run downloads as a background terminal job with notify, parallel per file, then verify sizes with `ls -l` against the repo's listed sizes before first use.

## Running

- Start: `.venv/bin/python main.py` from the ComfyUI dir (UI at http://127.0.0.1:8188).
- On MPS the GGUF node dequantizes on the fly; Q8_0 is stable, expect slower K-quant math. If a text encoder is heavy, keep it on CPU and let only the denoiser ride Metal.
- First-run validation: queue a small (512px) test generation before declaring the stack working — a successful server start does not prove model loading.
