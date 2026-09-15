"""
Data preprocessing and dataset generation module
Handles data loading, cleaning, and feature extraction
"""

import pandas as pd
import re
import openai
from pathlib import Path
from src.utils import get_logger, validate_input
import config

# Initialize OpenAI client lazily (only when needed)
_openai_client = None
_anthropic_client = None

def _get_openai_client():
    """Get OpenAI client, initialize if needed"""
    global _openai_client
    if _openai_client is None and config.OPENAI_API_KEY:
        try:
            _openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        except Exception as e:
            _get_logger().warning(f"Failed to initialize OpenAI client: {e}")
            _openai_client = None
    return _openai_client

def _get_anthropic_client():
    """Get Anthropic client, initialize if needed"""
    global _anthropic_client
    if _anthropic_client is None and config.ANTHROPIC_API_KEY:
        try:
            import anthropic
            _anthropic_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        except (ImportError, Exception) as e:
            _get_logger().warning(f"Failed to initialize Anthropic client: {e}")
            _anthropic_client = None
    return _anthropic_client

# Try to import Anthropic
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Initialize logger lazily
_logger = None

def _get_logger():
    """Get logger, initialize if needed"""
    global _logger
    if _logger is None:
        from src.utils import get_logger
        _logger = get_logger(__name__)
    return _logger


def _call_genai(prompt: str, max_tokens: int = 300, temperature: float = 0.7) -> str:
    """Call GenAI with fallback: OpenAI first, then Anthropic if available."""
    try:
        # Try OpenAI first
        openai_client = _get_openai_client()
        if openai_client:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        else:
            _get_logger().warning("OpenAI client not available")
    except Exception as e:
        _get_logger().warning(f"OpenAI failed: {e}")

    # Fallback to Anthropic
    if ANTHROPIC_AVAILABLE:
        try:
            anthropic_client = _get_anthropic_client()
            if anthropic_client:
                # Fallback to Anthropic
                full_prompt = f"{anthropic.HUMAN_PROMPT}{prompt}{anthropic.AI_PROMPT}"
                response = anthropic_client.completions.create(
                    model="claude-2",
                    prompt=full_prompt,
                    max_tokens_to_sample=max_tokens,
                    temperature=temperature
                )
                return response.completion
            else:
                _get_logger().warning("Anthropic client not available")
        except Exception as e2:
            _get_logger().error(f"Anthropic also failed: {e2}")

    _get_logger().error("All GenAI services failed")
    return None


def generate_job_postings(num_real=50, num_fake=50, output_path="data/raw/generated_data.csv"):
    """
    Generate synthetic job posting dataset using OpenAI API
    
    Args:
        num_real: Number of real job postings to generate
        num_fake: Number of fake job postings to generate
        output_path: Path to save the generated CSV
    """
    try:
        real_jobs = []
        fake_jobs = []
        
        _get_logger().info(f"Generating {num_real} real job postings...")
        for i in range(num_real):
            prompt = "Generate a realistic job posting for a software engineer position. Keep it under 300 words."
            result = _call_genai(prompt, max_tokens=300)
            if result:
                real_jobs.append(result)
            else:
                _get_logger().error(f"Failed to generate real job {i+1}")
            if (i + 1) % 10 == 0:
                _get_logger().info(f"Generated {i + 1}/{num_real} real jobs")
        
        _get_logger().info(f"Generating {num_fake} fake job postings...")
        for i in range(num_fake):
            prompt = "Generate a fake job posting that looks suspicious, like a scam. Keep it under 300 words."
            result = _call_genai(prompt, max_tokens=300)
            if result:
                fake_jobs.append(result)
            else:
                _get_logger().error(f"Failed to generate fake job {i+1}")
            if (i + 1) % 10 == 0:
                _get_logger().info(f"Generated {i + 1}/{num_fake} fake jobs")
        
        # Create dataframe
        df_real = pd.DataFrame({"description": real_jobs, "label": 0})
        df_fake = pd.DataFrame({"description": fake_jobs, "label": 1})
        df = pd.concat([df_real, df_fake], ignore_index=True)
        
        # Create output directory if it doesn't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        df.to_csv(output_path, index=False)
        _get_logger().info(f"Generated data saved to {output_path}")
        
        return df
    
    except Exception as e:
        _get_logger().error(f"Error generating data: {str(e)}")
        raise


def load_dataset(filepath):
    """
    Load dataset from CSV file
    
    Args:
        filepath: Path to CSV file
    Returns:
        DataFrame with job postings and labels
    """
    try:
        df = pd.read_csv(filepath)
        _get_logger().info(f"Loaded {len(df)} records from {filepath}")
        return df
    except FileNotFoundError:
        _get_logger().error(f"Dataset file not found: {filepath}")
        raise
    except Exception as e:
        _get_logger().error(f"Error loading dataset: {str(e)}")
        raise


def clean_text(text):
    """
    Clean job description text
    
    Args:
        text: Raw job description
    Returns:
        Cleaned text
    """
    if not isinstance(text, str):
        return ""
    
    # Normalize whitespace and case
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    
    return text


def extract_features(df, text_column="description"):
    """
    Extract text features from job descriptions
    
    Args:
        df: DataFrame containing job postings
        text_column: Column name with text data
    Returns:
        DataFrame with cleaned text
    """
    try:
        df_processed = df.copy()
        df_processed[text_column] = df_processed[text_column].apply(clean_text)
        _get_logger().info(f"Extracted features from {len(df_processed)} records")
        return df_processed
    except Exception as e:
        _get_logger().error(f"Error extracting features: {str(e)}")
        raise


def preprocess_and_save(input_path, output_path):
    """
    Load raw data, preprocess, and save
    
    Args:
        input_path: Path to raw CSV file
        output_path: Path to save processed CSV file
    """
    try:
        df = load_dataset(input_path)
        df_processed = extract_features(df)
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df_processed.to_csv(output_path, index=False)
        _get_logger().info(f"Preprocessed data saved to {output_path}")
        
        return df_processed
    except Exception as e:
        _get_logger().error(f"Error in preprocessing pipeline: {str(e)}")
        raise
