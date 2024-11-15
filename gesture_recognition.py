# gesture_recognition.py
from transformers import AutoImageProcessor, AutoModelForImageClassification
import torch
from PIL import Image

model_name = "dima806/hand_gestures_image_detection"  # Replace with your actual model name
model = AutoModelForImageClassification.from_pretrained(model_name)
processor = AutoImageProcessor.from_pretrained(model_name)

label_to_gesture = {
    0: 'call',
    1: 'dislike',
    2: 'fist',
    3: 'four',
    4: 'like',
    5: 'mute',
    6: 'ok',
    7: 'one',
    8: 'palm',
    9: 'peace',
    10: 'peace_inverted',
    11: 'rock',
    12: 'stop',
    13: 'stop_inverted',
    14: 'three',
    15: 'three2',
    16: 'two_up',
    17: 'two_up_inverted'
}

CONFIDENCE_THRESHOLDS = {
    "call": 0.8,
    "like": 0.0,
    "fist": 0.6,
    "default": 0.3
    
}

def preprocess_image(image):
    inputs = processor(images=image, return_tensors="pt")
    return inputs

def predict_gesture(image):
    inputs = preprocess_image(image)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        confidences = torch.nn.functional.softmax(logits, dim=-1)
        max_confidence, predicted_label = confidences.max(dim=-1)
        max_confidence = max_confidence.item()
        predicted_label = predicted_label.item()
    
    gesture_name = label_to_gesture.get(predicted_label, "Unknown Gesture")
    confidence_threshold = CONFIDENCE_THRESHOLDS.get(gesture_name, CONFIDENCE_THRESHOLDS["default"])

    if max_confidence < confidence_threshold:
        gesture_name = "No Gesture"
    
    return gesture_name
