"""
Enhanced data generation script using scam patterns from Internshala article
Generates realistic job postings and sophisticated scams for better model training
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

# Real job templates based on legitimate postings - with some variation
REAL_JOB_TEMPLATES = [
    {
        "title": "Software Engineer",
        "template": "We are seeking a talented {title} to join our growing team at {company}. The ideal candidate will have {experience} years of experience in {skills}. Responsibilities include {responsibilities}. We offer competitive salary, health benefits, and opportunities for professional growth. Bachelor's degree in Computer Science or related field preferred."
    },
    {
        "title": "Data Analyst",
        "template": "Join our analytics team as a {title}. You will work with large datasets using {skills} to generate insights that drive business decisions. Requirements: {experience} years experience, proficiency in SQL, Python, and data visualization tools. Full-time position with remote work options available."
    },
    {
        "title": "Marketing Manager",
        "template": "{company} is looking for an experienced {title} to lead our marketing initiatives. The role involves developing marketing strategies, managing campaigns, and analyzing performance metrics. Required: {experience} years in digital marketing, experience with {skills}. Competitive salary and benefits package."
    },
    {
        "title": "Customer Service Representative",
        "template": "Entry-level {title} position available. We provide comprehensive training and support. Responsibilities include handling customer inquiries, processing orders, and maintaining customer satisfaction. High school diploma required. Full-time with benefits. Starting salary ${salary_range}."
    },
    {
        "title": "DevOps Engineer",
        "template": "Senior {title} needed for our infrastructure team. Experience with {skills} required. You will be responsible for {responsibilities}, ensuring system reliability and implementing CI/CD pipelines. {experience} years minimum experience. Competitive compensation and remote work options."
    },
    {
        "title": "Borderline Real Job",  # Less perfect real jobs
        "template": "Looking for {title} with some experience in {skills}. Great opportunity to grow with our company. We offer good salary and benefits. If you have {experience} years experience and are motivated, please apply. Training provided for the right candidate."
    },
    {
        "title": "Real Job with Minor Issues",  # Jobs with some red flags but legitimate
        "template": "{company} needs a {title} immediately. Must have {skills} experience. Competitive pay but requires quick start. We may ask for references. Full-time position with standard benefits. Apply today - interviews this week."
    }
]

# Scam templates based on real scam patterns from Internshala - made more subtle
SCAM_TEMPLATES = [
    {
        "type": "advance_fee_scam",
        "template": "Exciting opportunity: {title} position with competitive salary. To finalize your application, please complete the registration process with a ${fee} administrative fee. This covers background verification and is fully refundable. Contact {contact} for immediate processing."
    },
    {
        "type": "fake_recruitment_agency",
        "template": "Dear Candidate, Congratulations on being shortlisted for {title} at {fake_company}. Our client requires all candidates to undergo a standard verification process. Please submit ${fee} for document authentication. This amount will be reimbursed upon joining. Best regards, {contact}"
    },
    {
        "type": "work_from_home_scam",
        "template": "Work from home {title} opportunity! Flexible hours, excellent compensation. We provide all necessary tools and training. There is a one-time setup fee of ${fee} for software licensing and materials. Start earning within days of enrollment. Limited positions available."
    },
    {
        "type": "overseas_job_scam",
        "template": "International career opportunity: {title} in {country}. Excellent salary package plus relocation assistance. We handle all visa formalities. Candidates need to submit ${fee} for immigration processing and work permits. Successful applicants will be contacted within 48 hours."
    },
    {
        "type": "fake_offer_letter",
        "template": "Employment Offer: We are pleased to offer you the position of {title} at {fake_company}. Salary: ${salary}/month. To accept this offer, please complete the formalities including a ${fee} processing charge for HR documentation. This is standard procedure for all new hires."
    },
    {
        "type": "phishing_scam",
        "template": "Application Update Required: Your application for {title} requires additional verification. Please update your profile with current contact information and complete the security verification process. Click the link to proceed. Failure to complete may result in application cancellation."
    },
    {
        "type": "unrealistic_salary_scam",
        "template": "Premium {title} position available. We offer exceptional compensation of ${salary} monthly for qualified candidates. No extensive experience required - we provide comprehensive training. Submit your application along with a ${fee} application processing fee to be considered."
    },
    {
        "type": "borderline_scam",  # More subtle scams
        "template": "Great {title} opportunity with fast-growing company. Competitive salary and benefits. We require candidates to complete a skills assessment test. The testing fee is ${fee} and covers certification upon completion. Successful candidates will be fast-tracked for interviews."
    }
]

COMPANIES_REAL = ["Google", "Microsoft", "Amazon", "Meta", "Apple", "Netflix", "Tesla", "Adobe", "Salesforce", "Uber"]
COMPANIES_FAKE = ["TechSolutions Inc", "Global Ventures Ltd", "Premier Staffing", "Elite Recruitment", "ProStaff Agency", "CareerBoost Services"]

SKILLS = ["Python, JavaScript", "SQL, Tableau", "Digital Marketing, SEO", "AWS, Docker", "React, Node.js", "Java, Spring Boot"]
RESPONSIBILITIES = ["developing web applications", "analyzing business data", "managing marketing campaigns", "maintaining cloud infrastructure"]
COUNTRIES = ["UAE", "Singapore", "Canada", "Australia", "UK", "Germany"]
PAYMENT_METHODS = ["PayPal", "Western Union", "bank transfer", "crypto wallet"]
CONTACTS = ["hr@company.com", "recruitment@agency.net", "jobs@staffing.co.in"]

def add_noise_to_job(job_text, is_scam=False):
    """Add realistic noise and variation to job postings"""
    noises = [
        "Please apply ASAP.",
        "Great benefits included.",
        "We are an equal opportunity employer.",
        "Diverse team environment.",
        "Flexible working hours.",
        "Professional development opportunities.",
        "Apply with your resume and cover letter.",
        "No phone calls please.",
        "Background check required.",
        "Drug test may be required.",
    ]

    # Add 1-3 random noise elements
    num_noises = random.randint(1, 3)
    selected_noises = random.sample(noises, num_noises)

    # For scams, sometimes add urgency or pressure
    if is_scam and random.random() < 0.3:
        scam_pressures = [
            "Limited time offer!",
            "Only a few positions left.",
            "Act fast - applications close soon.",
            "Don't miss this opportunity!",
        ]
        selected_noises.append(random.choice(scam_pressures))

    # For real jobs, sometimes add legitimate urgency
    elif not is_scam and random.random() < 0.2:
        real_urgencies = [
            "Immediate start preferred.",
            "Interviewing candidates now.",
            "Position available immediately.",
        ]
        selected_noises.append(random.choice(real_urgencies))

    return job_text + " " + " ".join(selected_noises)

def generate_real_job():
    """Generate a realistic job posting with variation"""
    template = random.choice(REAL_JOB_TEMPLATES)

    job = template["template"].format(
        title=template["title"],
        company=random.choice(COMPANIES_REAL),
        experience=random.randint(1, 8),
        skills=random.choice(SKILLS),
        responsibilities=random.choice(RESPONSIBILITIES),
        salary_range=f"{random.randint(30, 60)}k-{random.randint(70, 120)}k"
    )

    # Add realistic noise
    job = add_noise_to_job(job, is_scam=False)

    return job

def generate_scam_job():
    """Generate a fake job posting based on real scam patterns - made more subtle"""
    template = random.choice(SCAM_TEMPLATES)

    job = template["template"].format(
        title=random.choice(["Software Engineer", "Data Analyst", "Marketing Manager", "Customer Service Rep", "DevOps Engineer"]),
        salary=random.randint(3000, 15000),  # More realistic salary ranges
        fee=random.randint(50, 500),  # Smaller, more believable fees
        fake_company=random.choice(COMPANIES_FAKE),
        country=random.choice(COUNTRIES),
        payment_method=random.choice(PAYMENT_METHODS),
        contact=random.choice(CONTACTS)
    )

    # Add noise to make it less obvious
    job = add_noise_to_job(job, is_scam=True)

    return job

def generate_training_data(num_real=100, num_fake=100, output_path="data/raw/enhanced_training_data.csv"):
    """
    Generate enhanced training dataset with realistic jobs and sophisticated scams

    Args:
        num_real: Number of real job postings to generate
        num_fake: Number of fake job postings to generate
        output_path: Path to save the generated CSV
    """
    logger.info(f"Generating {num_real} real job postings...")

    real_jobs = []
    for i in range(num_real):
        job = generate_real_job()
        real_jobs.append(job)
        if (i + 1) % 20 == 0:
            logger.info(f"Generated {i + 1}/{num_real} real jobs")

    logger.info(f"Generating {num_fake} fake job postings...")

    fake_jobs = []
    for i in range(num_fake):
        job = generate_scam_job()
        fake_jobs.append(job)
        if (i + 1) % 20 == 0:
            logger.info(f"Generated {i + 1}/{num_fake} fake jobs")

    # Create dataframe
    df_real = pd.DataFrame({"description": real_jobs, "label": 0})
    df_fake = pd.DataFrame({"description": fake_jobs, "label": 1})
    df = pd.concat([df_real, df_fake], ignore_index=True)

    # Shuffle the data
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    # Create output directory if it doesn't exist
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)
    logger.info(f"Enhanced training data saved to {output_path}")
    logger.info(f"Total samples: {len(df)} (Real: {len(df_real)}, Fake: {len(df_fake)})")

    return df

if __name__ == "__main__":
    import sys

    # Parse arguments
    num_real = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    num_fake = int(sys.argv[2]) if len(sys.argv) > 2 else 100

    print(f"Generating {num_real} real and {num_fake} fake job postings...")
    generate_training_data(num_real=num_real, num_fake=num_fake)