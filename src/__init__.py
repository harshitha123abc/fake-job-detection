"""
Fake Job Posting Detection - Main Package
"""

__version__ = "2.0.0"
__description__ = "Multi-agent system for detecting fraudulent job postings"

from src.model import FakeJobDetectionModel
from src.agent import MultiAgentFakeJobDetector
from src.preprocessing import generate_job_postings, load_dataset, preprocess_and_save

__all__ = [
    "FakeJobDetectionModel",
    "MultiAgentFakeJobDetector",
    "generate_job_postings",
    "load_dataset",
    "preprocess_and_save"
]
