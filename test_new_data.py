"""
Test the trained model on new, unseen job postings to evaluate real-world performance
"""

import sys
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.model import FakeJobDetectionModel
from src.utils import get_logger
import config

logger = get_logger(__name__)

# New test cases that the model hasn't seen before
NEW_TEST_CASES = [
    # Real jobs
    "Senior Python Developer at TechCorp. 3-5 years experience required. Competitive salary $80k-$120k. Full benefits including health, dental, 401k. Remote work options available.",
    "Digital Marketing Specialist needed. Experience with Google Ads and Facebook marketing required. Bachelor's degree preferred. Salary $50k-$70k plus bonuses.",
    "Data Scientist position at Analytics Inc. PhD preferred. Strong Python and R skills required. Competitive compensation and equity package.",
    "UX Designer role. Portfolio required. Experience with Figma and Adobe XD. Full-time position with creative team. Salary $60k-$90k.",
    "DevOps Engineer - AWS certified. 4+ years experience. Manage cloud infrastructure and CI/CD pipelines. Competitive salary and benefits.",

    # Fake jobs (subtle scams)
    "Work from home opportunity! Earn $3000/month as virtual assistant. No experience needed. Pay $99 for training materials. Start immediately.",
    "International business opportunity. Earn $5000 weekly from home. Simple data entry work. Send $149 for starter kit. Guaranteed income.",
    "Make money online! $2000/day potential. Part-time work from home. Pay $79 for software access. No selling required.",
    "Online tutoring position. Flexible hours, good pay. Pay $49 for background check processing. Start teaching online today.",
    "Customer service representative - work from home. $25/hour starting pay. Pay $89 for headset and training. Immediate start.",

    # Borderline cases
    "Freelance graphic designer needed. Must have portfolio. $50/hour rate. Pay $25 for portfolio review fee. Serious inquiries only.",
    "Software testing position. Experience preferred but not required. Competitive pay. Background check fee $75 (reimbursed). Apply now.",
    "Content writer - remote work. $30/hour. Pay $39 for writing assessment. Flexible schedule, ongoing projects.",
]

def test_model_on_new_data():
    """Test the trained model on completely new, unseen data"""

    logger.info("Testing model on new, unseen job postings...")

    try:
        # Load the trained model
        model = FakeJobDetectionModel()
        model.load()
        logger.info("Model loaded successfully")

        # Test predictions
        predictions = []
        probabilities = []

        for i, job_text in enumerate(NEW_TEST_CASES):
            pred = model.predict(job_text)
            prob = model.predict_proba([job_text])  # Fix: pass as list
            predictions.append(pred[0])
            probabilities.append(prob[0])

            logger.info(f"Job {i+1}: {'FAKE' if pred[0] == 1 else 'REAL'} "
                       f"(confidence: {prob[0][pred[0]]:.3f})")
            logger.info(f"  Text: {job_text[:100]}...")

        # Calculate accuracy on test set
        # First 5 are real (0), next 5 are fake (1), last 3 are mixed
        true_labels = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1]  # Manual labeling

        correct = sum(p == t for p, t in zip(predictions, true_labels))
        accuracy = correct / len(true_labels)

        logger.info(f"\nTest Results on {len(NEW_TEST_CASES)} new samples:")
        logger.info(f"Accuracy: {accuracy:.3f} ({correct}/{len(true_labels)})")

        # Show confusion matrix style results
        real_correct = sum(1 for p, t in zip(predictions[:5], true_labels[:5]) if p == t)
        fake_correct = sum(1 for p, t in zip(predictions[5:10], true_labels[5:10]) if p == t)
        mixed_correct = sum(1 for p, t in zip(predictions[10:], true_labels[10:]) if p == t)

        logger.info(f"Real jobs accuracy: {real_correct}/5")
        logger.info(f"Fake jobs accuracy: {fake_correct}/5")
        logger.info(f"Mixed cases accuracy: {mixed_correct}/3")

        return accuracy

    except Exception as e:
        logger.error(f"Testing failed: {str(e)}")
        raise

if __name__ == "__main__":
    test_model_on_new_data()