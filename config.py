"""
Configuration file for Fake Job Posting Detection project
Contains paths, model parameters, and API settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent

# Data paths
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Model paths
MODEL_DIR = BASE_DIR / "models"
TRAINED_MODEL_PATH = MODEL_DIR / "trained_model.pkl"
VECTORIZER_PATH = MODEL_DIR / "vectorizer.pkl"

# Logs path
LOGS_DIR = BASE_DIR / "logs"

# Training parameters
TRAIN_TEST_SPLIT = 0.2
RANDOM_STATE = 42
MAX_FEATURES = 1000
VECTORIZER_PARAMS = {
    "max_features": MAX_FEATURES,
    "stop_words": "english",
    "ngram_range": (1, 2)
}

MODEL_PARAMS = {
    "random_state": RANDOM_STATE,
    "max_iter": 1000
}

# API Configuration
API_KEY = os.getenv("API_KEY", "your_secret_api_key_here")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GENAI_MODEL = os.getenv("GENAI_MODEL", "gpt-3.5-turbo")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Email Notification Configuration
EMAIL_NOTIFICATIONS_ENABLED = os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "False").lower() == "true"
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")  # Your Gmail email
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")  # Gmail app-specific password
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "")  # Admin email to receive alerts
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# Email notification triggers
NOTIFY_ON_FAKE_ONLY = os.getenv("NOTIFY_ON_FAKE_ONLY", "True").lower() == "true"
MIN_RISK_LEVEL_FOR_NOTIFICATION = os.getenv("MIN_RISK_LEVEL_FOR_NOTIFICATION", "High")  # High, Medium, Low

# Ensemble weights for hybrid scoring
ENSEMBLE_WEIGHTS = {
    "rule": 0.3,
    "ml": 0.5,
    "genai": 0.2
}

# Feature extraction parameters
MIN_WORD_LENGTH = 3
LANGUAGE = "english"

# Thresholds for detection
CONFIDENCE_THRESHOLD = 0.6
HYBRID_ENABLE = True  # Enable hybrid (ML + GenAI) detection
RISK_LEVEL_THRESHOLDS = {
    "low": 0.4,
    "medium": 0.65
}
RISK_LEVEL_THRESHOLDS = {
    "low": 0.4,
    "medium": 0.65
}
