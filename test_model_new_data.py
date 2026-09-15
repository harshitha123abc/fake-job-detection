"""
Test script to evaluate ML model performance on new job postings
"""

from src.model import FakeJobDetectionModel
import numpy as np

def test_model_on_new_data():
    """Test the trained model on new job postings not seen during training"""

    # Load the trained model
    model = FakeJobDetectionModel()
    try:
        model.load()
        print("✅ Model loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return

    # Test with new job postings (not in training data)
    test_jobs = [
        # Real job examples
        {
            'text': 'Software Engineer position at Google. Requirements: 3+ years experience with Python, Java, and distributed systems. Competitive salary and benefits.',
            'expected': 'REAL'
        },
        {
            'text': 'Data Scientist role. Must have experience with machine learning, statistics, and Python. PhD preferred. Salary range: $120k-$150k.',
            'expected': 'REAL'
        },
        {
            'text': 'Marketing Manager needed. 5+ years experience in digital marketing, SEO, and social media. Full-time position with remote work option.',
            'expected': 'REAL'
        },

        # Fake job examples
        {
            'text': 'Earn $10,000 per week working from home! No experience needed. Just send us your bank details and start immediately!',
            'expected': 'FAKE'
        },
        {
            'text': 'URGENT: Make $5000/day stuffing envelopes! Send $99 processing fee and your home address for starter kit.',
            'expected': 'FAKE'
        },
        {
            'text': 'CEO Position Available - No Experience Required! Guaranteed $200,000 salary. Apply now with your SSN.',
            'expected': 'FAKE'
        },
        {
            'text': 'Get Rich Quick! Work 1 hour per day and earn $3000. No skills needed, just provide your credit card information.',
            'expected': 'FAKE'
        }
    ]

    print('\n🧪 Testing ML model on new job postings:')
    print('=' * 60)

    correct_predictions = 0
    total_predictions = len(test_jobs)

    for i, job_data in enumerate(test_jobs, 1):
        job_text = job_data['text']
        expected = job_data['expected']

        try:
            prediction, confidence = model.predict(job_text)
            proba = model.predict_proba([job_text])[0]
            fake_prob = proba[1] if len(proba) > 1 else 0.0

            predicted_label = 'FAKE' if prediction == 1 else 'REAL'
            is_correct = predicted_label == expected

            if is_correct:
                correct_predictions += 1
                status = '✅ CORRECT'
            else:
                status = '❌ WRONG'

            print(f'{i}. {status} - Expected: {expected}, Predicted: {predicted_label}')
            print(f'   Confidence: {confidence:.3f}, Fake Probability: {fake_prob:.3f}')
            print(f'   "{job_text[:80]}..."')
            print()

        except Exception as e:
            print(f'{i}. ERROR: {str(e)}')
            print(f'   "{job_text[:80]}..."')
            print()

    # Summary
    accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
    print('=' * 60)
    print(f'📊 Test Results Summary:')
    print(f'   Total tests: {total_predictions}')
    print(f'   Correct predictions: {correct_predictions}')
    print(f'   Accuracy on new data: {accuracy:.1%}')

    if accuracy >= 0.8:
        print('🎉 Model performs well on new data!')
    elif accuracy >= 0.6:
        print('⚠️ Model has moderate performance on new data.')
    else:
        print('❌ Model needs improvement - poor performance on new data.')

if __name__ == "__main__":
    test_model_on_new_data()