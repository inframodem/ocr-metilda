from dataclasses import dataclass
@dataclass
class DeviceInfo:
    kind: str                      # "cuda", "rocm", "mps" or "cpu"
    description: str
    paddle_device: str             # what PaddleOCR is told: "gpu:0" or "cpu"
"""
"""
def detect_device() -> DeviceInfo:
    #Best available accelerator: NVIDIA CUDA, AMD ROCm, Apple silicon, else CPU. Each one is test-run first,
    #because a GPU that PyTorch can see is not always one it can compute on (for example a new card with an old build).
    try:
        import torch
    except Exception:
        return DeviceInfo("cpu", "CPU (PyTorch is not installed)", "cpu")
    note = ""
    if torch.cuda.is_available():
        try:
            name = torch.cuda.get_device_name(0)
        except Exception:
            name = "GPU"
        try:
            (torch.zeros(8, device="cuda") + 1).sum().item()
            hip = getattr(torch.version, "hip", None)
            if hip:
                return DeviceInfo("rocm", f"AMD ROCm: {name}", "gpu:0")      # ROCm builds of PyTorch use the "cuda" name
            return DeviceInfo("cuda", f"NVIDIA CUDA: {name}", "gpu:0")
        except Exception:
            note = f" ({name} found but this PyTorch build cannot run on it)"
    mps = getattr(torch.backends, "mps", None)
    try:
        if mps is not None and mps.is_available():
            (torch.zeros(8, device="mps") + 1).sum().item()
            return DeviceInfo("mps", "Apple silicon (MPS)", "cpu")
    except Exception:
        note = " (Apple GPU found but not usable)"
    return DeviceInfo("cpu", "CPU" + note, "cpu")