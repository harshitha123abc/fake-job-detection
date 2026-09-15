"""
Machine Learning model training and evaluation module
Handles model training, evaluation, and prediction
"""

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import pandas as pd
from pathlib import Path
import config
from src.utils import get_logger, save_metrics

logger = get_logger(__name__)


class FakeJobDetectionModel:
    """Machine learning model for fake job detection"""
    
    def __init__(self):
        self.vectorizer = None
        self.model = None
        self.metrics = {}
    
    def train(self, job_postings, labels, test_size=config.TRAIN_TEST_SPLIT):
        """
        Train the ML model on job postings
        
        Args:
            job_postings: List of job description texts
            labels: List of labels (0=real, 1=fake)
            test_size: Test set size ratio
        """
        try:
            logger.info(f"Training model with {len(job_postings)} samples")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                job_postings, 
                labels, 
                test_size=test_size,
                random_state=config.RANDOM_STATE,
                stratify=labels
            )
            
            # Vectorize text
            logger.info("Vectorizing text with TF-IDF...")
            self.vectorizer = TfidfVectorizer(**config.VECTORIZER_PARAMS)
            X_train_vec = self.vectorizer.fit_transform(X_train)
            X_test_vec = self.vectorizer.transform(X_test)
            
            # Train model
            logger.info("Training Logistic Regression model...")
            self.model = LogisticRegression(**config.MODEL_PARAMS)
            self.model.fit(X_train_vec, y_train)
            
            # Evaluate
            logger.info("Evaluating model...")
            y_pred = self.model.predict(X_test_vec)
            y_pred_proba = self.model.predict_proba(X_test_vec)
            
            self.metrics = {
                "accuracy": float(accuracy_score(y_test, y_pred)),
                "precision": float(precision_score(y_test, y_pred)),
                "recall": float(recall_score(y_test, y_pred)),
                "f1": float(f1_score(y_test, y_pred)),
                "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
                "train_size": len(X_train),
                "test_size": len(X_test)
            }
            
            logger.info(f"Model trained - Accuracy: {self.metrics['accuracy']:.3f}, F1: {self.metrics['f1']:.3f}")
            return self.metrics
            
        except Exception as e:
            logger.error(f"Error during model training: {str(e)}")
            raise
    
    def predict(self, text):
        """
        Make prediction on a single job posting
        
        Args:
            text: Job description text
        Returns:
            Tuple of (prediction, confidence)
        """
        if not self.model or not self.vectorizer:
            raise ValueError("Model not trained. Train the model first.")
        
        try:
            features = self.vectorizer.transform([text])
            prediction = self.model.predict(features)[0]
            confidence = self.model.predict_proba(features)[0][int(prediction)]
            return int(prediction), confidence
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise

    def predict_proba(self, texts):
        """
        Get class probability predictions for one or more job postings.

        Args:
            texts: List of job description texts
        Returns:
            Numpy array of probability vectors for each input text
        """
        if not self.model or not self.vectorizer:
            raise ValueError("Model not trained. Train the model first.")

        try:
            features = self.vectorizer.transform(texts)
            return self.model.predict_proba(features)
        except Exception as e:
            logger.error(f"Error during predict_proba: {str(e)}")
            raise
    
    def predict_batch(self, texts):
        """
        Make predictions on multiple job postings
        
        Args:
            texts: List of job description texts
        Returns:
            List of tuples (prediction, confidence)
        """
        if not self.model or not self.vectorizer:
            raise ValueError("Model not trained. Train the model first.")
        
        try:
            features = self.vectorizer.transform(texts)
            predictions = self.model.predict(features)
            confidences = self.model.predict_proba(features)
            
            results = []
            for pred, conf in zip(predictions, confidences):
                results.append((int(pred), float(conf[int(pred)])))
            return results
        except Exception as e:
            logger.error(f"Error during batch prediction: {str(e)}")
            raise
    
    def save(self, model_path=None, vectorizer_path=None):
        """
        Save model and vectorizer to disk
        
        Args:
            model_path: Path to save model
            vectorizer_path: Path to save vectorizer
        """
        if not self.model or not self.vectorizer:
            raise ValueError("Model not trained. Train the model first.")
        
        try:
            model_path = model_path or config.TRAINED_MODEL_PATH
            vectorizer_path = vectorizer_path or config.VECTORIZER_PATH
            
            Path(model_path).parent.mkdir(parents=True, exist_ok=True)
            Path(vectorizer_path).parent.mkdir(parents=True, exist_ok=True)
            
            joblib.dump(self.model, model_path)
            joblib.dump(self.vectorizer, vectorizer_path)
            
            logger.info(f"Model saved to {model_path}")
            logger.info(f"Vectorizer saved to {vectorizer_path}")
            
            if self.metrics:
                save_metrics(self.metrics, "model_metrics.json")
        
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise
    
    def load(self, model_path=None, vectorizer_path=None):
        """
        Load model and vectorizer from disk
        
        Args:
            model_path: Path to model file
            vectorizer_path: Path to vectorizer file
        """
        try:
            model_path = model_path or config.TRAINED_MODEL_PATH
            vectorizer_path = vectorizer_path or config.VECTORIZER_PATH
            
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(vectorizer_path)
            
            logger.info(f"Model loaded from {model_path}")
            logger.info(f"Vectorizer loaded from {vectorizer_path}")
        
        except FileNotFoundError:
            logger.error(f"Model files not found. Please train the model first.")
            raise
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
