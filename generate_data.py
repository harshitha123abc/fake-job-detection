"""
Alternative data generation module
Generates synthetic job postings using OpenAI API
Can be used to create training datasets
"""

import pandas as pd
import openai
from pathlib import Path
from src.utils import get_logger
import config

openai.api_key = config.OPENAI_API_KEY
logger = get_logger(__name__)


def generate_job_postings(num_real=50, num_fake=50, output_path="data/raw/generated_data.csv"):
    """
    Generate synthetic job posting dataset using OpenAI API
    
    Usage:
        python generate_data.py
    
    Args:
        num_real: Number of real job postings to generate
        num_fake: Number of fake job postings to generate
        output_path: Path to save the generated CSV
    """
    try:
        from src.preprocessing import generate_job_postings as gen_postings
        df = gen_postings(num_real=num_real, num_fake=num_fake, output_path=output_path)
        print(f"Generated {len(df)} job postings")
        print(f"Saved to {output_path}")
        return df
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise


if __name__ == "__main__":
    import sys
    
    # Parse arguments
    num_real = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    num_fake = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    print(f"Generating {num_real} real and {num_fake} fake job postings...")
    generate_job_postings(num_real=num_real, num_fake=num_fake)