"""
Create challenging test data with edge cases and borderline scenarios
"""

import pandas as pd
import random
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils import get_logger
import config

logger = get_logger(__name__)

# Mixed templates that can be real or fake depending on context
MIXED_TEMPLATES = [
    # Legitimate jobs that mention fees (background checks, etc.)
    {
        "type": "real_with_fee",
        "label": 0,
        "template": "{company} is hiring a {title}. Competitive salary and full benefits. All candidates must undergo a background check costing ${fee} (reimbursed upon hire). Experience with {skills} required. Apply today!"
    },
    {
        "type": "real_with_fee",
        "label": 0,
        "template": "Join {company} as a {title}. We cover all relocation costs and provide training. However, candidates are responsible for a ${fee} drug screening fee. {experience} years experience preferred. Excellent benefits package."
    },
    # Scam jobs that sound legitimate
    {
        "type": "subtle_scam",
        "label": 1,
        "template": "{fake_company} offers excellent {title} positions. We provide comprehensive training and support. To ensure candidate quality, we require a ${fee} assessment fee. Successful candidates receive full reimbursement. Contact us today."
    },
    {
        "type": "subtle_scam",
        "label": 1,
        "template": "Professional {title} opportunity at {fake_company}. Competitive compensation and growth potential. We conduct thorough background verification for all applicants. The verification process requires a ${fee} processing fee. Apply now for immediate consideration."
    },
    # Borderline cases - hard to classify
    {
        "type": "borderline",
        "label": 0,  # Let's make these real but suspicious
        "template": "Urgent: {company} needs {title} immediately. Great pay and benefits. Due to high demand, we prioritize candidates who can start right away. May require quick payment for background check (${fee}). Apply ASAP."
    },
    {
        "type": "borderline",
        "label": 1,  # Suspicious but could be real
        "template": "{fake_company} is expanding rapidly. We need experienced {title}s. To fast-track your application, complete our premium screening process for ${fee}. This guarantees interview priority. Limited spots available."
    }
]

COMPANIES_REAL = ["Google", "Microsoft", "Amazon", "Meta", "Apple", "Netflix", "Tesla", "Adobe", "Salesforce", "Uber"]
COMPANIES_FAKE = ["TechSolutions Inc", "Global Ventures Ltd", "Premier Staffing", "Elite Recruitment", "CareerBoost Services", "ProStaff Agency"]

SKILLS = ["Python, JavaScript", "SQL, Tableau", "Digital Marketing, SEO", "AWS, Docker", "React, Node.js", "Java, Spring Boot"]

def generate_mixed_job():
    """Generate jobs from mixed templates that create classification challenges"""
    template = random.choice(MIXED_TEMPLATES)

    job = template["template"].format(
        title=random.choice(["Software Engineer", "Data Analyst", "Marketing Manager", "Customer Service Rep", "DevOps Engineer"]),
        company=random.choice(COMPANIES_REAL) if template["label"] == 0 else random.choice(COMPANIES_FAKE),
        fake_company=random.choice(COMPANIES_FAKE),
        skills=random.choice(SKILLS),
        experience=random.randint(1, 5),
        fee=random.randint(20, 200)  # Smaller, more believable fees
    )

    return job, template["label"]

def generate_challenging_dataset(num_samples=500, output_path="data/raw/challenging_training_data.csv"):
    """
    Generate challenging training dataset with edge cases and mixed scenarios

    Args:
        num_samples: Total number of job postings to generate
        output_path: Path to save the generated CSV
    """
    logger.info(f"Generating {num_samples} challenging job postings...")

    jobs = []
    labels = []

    for i in range(num_samples):
        job, label = generate_mixed_job()
        jobs.append(job)
        labels.append(label)

        if (i + 1) % 50 == 0:
            logger.info(f"Generated {i + 1}/{num_samples} jobs")

    # Create dataframe
    df = pd.DataFrame({"description": jobs, "label": labels})

    # Shuffle the data
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Create output directory if it doesn't exist
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)
    logger.info(f"Challenging training data saved to {output_path}")

    real_count = sum(labels)
    fake_count = len(labels) - real_count
    logger.info(f"Total samples: {len(df)} (Real: {len(df) - real_count}, Fake: {real_count})")

    return df

if __name__ == "__main__":
    import sys

    # Parse arguments
    num_samples = int(sys.argv[1]) if len(sys.argv) > 1 else 500

    print(f"Generating {num_samples} challenging job postings...")
    generate_challenging_dataset(num_samples=num_samples)