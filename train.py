"""
Training script for model training and evaluation
Trains ML model and saves artifacts
"""

import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.model import FakeJobDetectionModel
from src.preprocessing import load_dataset, preprocess_and_save
from src.utils import get_logger, save_metrics
import config

logger = get_logger(__name__)


def main():
    """Main training loop"""
    
    logger.info("Starting model training...")
    
    try:
        # Load both training datasets
        data_paths = [
            "data/raw/challenging_training_data.csv",
            "data/raw/enhanced_training_data.csv"
        ]
        
        all_job_postings = []
        all_labels = []
        
        for data_path in data_paths:
            logger.info(f"Loading training data from {data_path}...")
            df = pd.read_csv(data_path)
            all_job_postings.extend(df['description'].tolist())
            all_labels.extend(df['label'].tolist())
        
        job_postings = all_job_postings
        labels = all_labels
        
        logger.info(f"Loaded {len(job_postings)} job postings ({sum(labels)} fake, {len(labels) - sum(labels)} real)")
        
        # Create model instance
        model = FakeJobDetectionModel()
        
        # Train model with cross-validation
        logger.info("Training model with cross-validation...")
        from sklearn.model_selection import cross_val_score
        import numpy as np
        
        # First, train on full dataset for deployment
        metrics = model.train(job_postings, labels, test_size=0.2)
        
        # Then perform cross-validation for more robust evaluation
        logger.info("Performing 5-fold cross-validation...")
        cv_scores = cross_val_score(
            model.model, 
            model.vectorizer.fit_transform(job_postings), 
            labels, 
            cv=5, 
            scoring='f1'
        )
        
        logger.info(f"Cross-validation F1 scores: {cv_scores}")
        logger.info(f"Mean CV F1: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        # Update metrics with CV results
        metrics['cv_f1_mean'] = cv_scores.mean()
        metrics['cv_f1_std'] = cv_scores.std()
        
        # Display metrics
        logger.info(f"Model Training Complete!")
        logger.info(f"  Accuracy: {metrics['accuracy']:.3f}")
        logger.info(f"  Precision: {metrics['precision']:.3f}")
        logger.info(f"  Recall: {metrics['recall']:.3f}")
        logger.info(f"  F1 Score: {metrics['f1']:.3f}")
        logger.info(f"  Train set size: {metrics['train_size']}")
        logger.info(f"  Test set size: {metrics['test_size']}")
        
        # Save model
        logger.info("Saving model and vectorizer...")
        model.save()
        
        # Save metrics
        save_metrics(metrics, "model_metrics.json")
        
        logger.info("Training completed successfully!")
        logger.info(f"Model saved to: {config.TRAINED_MODEL_PATH}")
        logger.info(f"Vectorizer saved to: {config.VECTORIZER_PATH}")
        logger.info(f"Metrics saved to: {config.LOGS_DIR / 'model_metrics.json'}")
        
        return True
    
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()

print("Model and vectorizer saved to models/ directory.")