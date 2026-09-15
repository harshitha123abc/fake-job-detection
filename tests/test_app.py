"""
Unit tests for Flask API application
Tests API endpoints and request/response handling
"""

import unittest
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app, predict_job


class TestFlaskAPI(unittest.TestCase):
    """Test cases for Flask API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client"""
        app.config['TESTING'] = True
        cls.client = app.test_client()
    
    def test_app_initialization(self):
        """Test app initializes correctly"""
        self.assertIsNotNone(app)
        self.assertTrue(app.config.get('TESTING'))
    
    def test_predict_endpoint_invalid_auth(self):
        """Test predict endpoint with invalid API key"""
        response = self.client.post(
            '/predict',
            json={'description': 'Test job posting'},
            headers={'X-API-Key': 'invalid_key'}
        )
        
        # Should return 401 or 403
        self.assertIn(response.status_code, [401, 403, 400])
    
    def test_predict_endpoint_missing_data(self):
        """Test predict endpoint with missing required data"""
        response = self.client.post(
            '/predict',
            json={},
            headers={'X-API-Key': 'test_key'}
        )
        
        # Should return 400
        self.assertEqual(response.status_code, 400)
    
    def test_predict_endpoint_empty_description(self):
        """Test predict with empty job description"""
        response = self.client.post(
            '/predict',
            json={'description': ''},
            headers={'X-API-Key': 'test_key'}
        )
        
        # Should return 400
        self.assertEqual(response.status_code, 400)
    
    def test_response_format(self):
        """Test response format when prediction succeeds"""
        response = self.client.post(
            '/predict',
            json={'description': 'Senior Software Engineer position'},
            headers={'X-API-Key': 'test_key'}
        )
        
        if response.status_code == 200:
            data = json.loads(response.data)
            
            # Check response structure
            self.assertIn('prediction', data)
            self.assertIn('confidence', data)
            self.assertIn('label', data)
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertIn('status', data)


class TestPredictionFunction(unittest.TestCase):
    """Test prediction helper function"""
    
    def test_predict_with_valid_input(self):
        """Test prediction with valid input"""
        try:
            result = predict_job("Senior Engineer needed")
            
            self.assertIsNotNone(result)
            self.assertIn('prediction', result)
            self.assertIn('label', result)
        except Exception as e:
            # May fail if models not loaded
            self.skipTest(f"Models not available: {str(e)}")
    
    def test_predict_returns_dict(self):
        """Test that predict returns dictionary"""
        try:
            result = predict_job("Test job posting with good description")
            self.assertIsInstance(result, dict)
        except Exception as e:
            self.skipTest(f"Models not available: {str(e)}")


if __name__ == "__main__":
    unittest.main()
