import torch

MODEL_NAME = "microsoft/trocr-small-handwritten"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
