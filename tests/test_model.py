"""
Unit tests for machine learning model
Tests model training, prediction, and evaluation
"""

import unittest
import pandas as pd
from src.model import FakeJobDetectionModel


class TestFakeJobDetectionModel(unittest.TestCase):
    """Test cases for ML model"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.job_postings = [
            # Real jobs
            "Senior Software Engineer needed with 5+ years Python experience",
            "Marketing Coordinator - Full time position with benefits",
            "Data Analyst role - Bachelor's in STEM required",
            "Customer Service Representative - Training provided",
            "UX Designer wanted - Portfolio required",
            
            # Fake jobs
            "Earn $5000 per week from home! No experience needed",
            "Make millions overnight! Send bank details",
            "Work from home and get rich quick! No interview needed",
            "CEO position - No qualifications needed, instant approval",
            "Win lottery by applying for this job! Send SSN",
        ]
        
        cls.labels = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
    
    def setUp(self):
        """Create a fresh model instance for each test"""
        self.model = FakeJobDetectionModel()
    
    def test_model_initialization(self):
        """Test model initializes correctly"""
        self.assertIsNone(self.model.model)
        self.assertIsNone(self.model.vectorizer)
        self.assertEqual(self.model.metrics, {})
    
    def test_model_training(self):
        """Test model training functionality"""
        metrics = self.model.train(self.job_postings, self.labels)
        
        self.assertIsNotNone(self.model.model)
        self.assertIsNotNone(self.model.vectorizer)
        self.assertGreater(metrics["accuracy"], 0)
        self.assertGreater(metrics["f1"], 0)
        self.assertIn("confusion_matrix", metrics)
    
    def test_single_prediction(self):
        """Test single job prediction"""
        self.model.train(self.job_postings, self.labels)
        
        test_text = "Earn $10000 per week from home!"
        prediction, confidence = self.model.predict(test_text)
        
        self.assertIn(prediction, [0, 1])
        self.assertGreaterEqual(confidence, 0)
        self.assertLessEqual(confidence, 1)
    
    def test_batch_prediction(self):
        """Test batch prediction"""
        self.model.train(self.job_postings, self.labels)
        
        test_texts = [
            "Senior DevOps Engineer needed",
            "Make $5000 weekly from your home!"
        ]
        
        results = self.model.predict_batch(test_texts)
        
        self.assertEqual(len(results), 2)
        for prediction, confidence in results:
            self.assertIn(prediction, [0, 1])
            self.assertGreaterEqual(confidence, 0)
            self.assertLessEqual(confidence, 1)
    
    def test_model_without_training(self):
        """Test that prediction fails without training"""
        test_text = "Some job posting"
        
        with self.assertRaises(ValueError):
            self.model.predict(test_text)
    
    def test_vectorizer_dimensions(self):
        """Test vectorizer creates correct feature dimensions"""
        self.model.train(self.job_postings, self.labels)
        
        features = self.model.vectorizer.transform(["test job description"])
        self.assertGreater(features.shape[1], 0)  # Should have features


class TestModelIntegration(unittest.TestCase):
    """Integration tests for model with data pipeline"""
    
    def test_end_to_end_pipeline(self):
        """Test complete pipeline from data to prediction"""
        from src.preprocessing import extract_features
        
        # Create sample data
        data = {
            "description": [
                "Senior Engineer wanted",
                "Make money fast!",
                "Software Developer - Full-time",
                "Earn $1000 per day!"
            ],
            "label": [0, 1, 0, 1]
        }
        
        df = pd.DataFrame(data)
        df_processed = extract_features(df)
        
        # Train model
        model = FakeJobDetectionModel()
        model.train(df_processed["description"].tolist(), df["label"].tolist())
        
        # Make predictions
        prediction, confidence = model.predict("Data Scientist position")
        
        self.assertIn(prediction, [0, 1])
        self.assertGreater(confidence, 0)


if __name__ == "__main__":
    unittest.main()
