import torch
import sys

print(f"Python Version: {sys.version}")
print(f"Torch Version: {torch.version.cuda}")
cuda_available = torch.cuda.is_available()
print(f"CUDA Available: {cuda_available}")

if cuda_available:
    print(f"GPU Device: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
else:
    print("CUDA is NOT available. We need to fix the Torch installation for GPU support.")
