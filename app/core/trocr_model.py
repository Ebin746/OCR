from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from .config import MODEL_NAME, DEVICE
import torch

processor = TrOCRProcessor.from_pretrained(MODEL_NAME)
model = VisionEncoderDecoderModel.from_pretrained(MODEL_NAME)
model.to(DEVICE)
