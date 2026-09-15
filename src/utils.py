"""
Utility functions for data processing and model predictions
"""

import logging
from pathlib import Path
import json
import os

# Get logs directory with fallback
try:
    from config import LOGS_DIR
except ImportError:
    # Fallback if config import fails
    LOGS_DIR = Path(__file__).parent.parent / "logs"

# Configure logging
try:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / "app.log"
    # Test if we can write to the log file
    with open(log_file, 'a') as f:
        f.write('')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
except Exception as e:
    # Fallback to console-only logging if file logging fails
    print(f"Warning: Could not set up file logging: {e}")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )


def get_logger(name):
    """Get a logger instance"""
    return logging.getLogger(name)


def save_metrics(metrics, filename="metrics.json"):
    """Save model metrics to a JSON file"""
    filepath = LOGS_DIR / filename
    with open(filepath, 'w') as f:
        json.dump(metrics, f, indent=4)
    get_logger(__name__).info(f"Metrics saved to {filepath}")


def load_metrics(filename="metrics.json"):
    """Load model metrics from JSON file"""
    filepath = LOGS_DIR / filename
    if filepath.exists():
        with open(filepath, 'r') as f:
            return json.load(f)
    return {}


def preprocess_text(text):
    """
    Basic text preprocessing
    Args:
        text: Input job description text
    Returns:
        Cleaned text
    """
    if not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower().strip()
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    return text


def format_prediction(prediction, confidence=None, model_name="ML Model"):
    """
    Format prediction results
    Args:
        prediction: 0 for real, 1 for fake
        confidence: Confidence score (0-1)
        model_name: Name of the model used
    Returns:
        Formatted prediction dict
    """
    result = {
        "label": "Fake" if prediction == 1 else "Real",
        "prediction": int(prediction),
        "model": model_name
    }
    
    if confidence is not None:
        result["confidence"] = round(float(confidence), 3)
    
    return result


def validate_input(job_description):
    """
    Validate job description input
    Args:
        job_description: Input text
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not job_description:
        return False, "Job description cannot be empty"
    
    if not isinstance(job_description, str):
        return False, "Job description must be a string"
    
    if len(job_description.strip()) < 10:
        return False, "Job description too short (minimum 10 characters)"
    
    if len(job_description) > 10000:
        return False, "Job description too long (maximum 10000 characters)"
    
    return True, None
