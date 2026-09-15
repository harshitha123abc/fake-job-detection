#!/usr/bin/env python3
"""
Test script for the Multi-Agent Fake Job Detection System
"""

import os
# Force fallback mode for testing
os.environ['OPENAI_API_KEY'] = ''
os.environ['GOOGLE_SEARCH_API_KEY'] = 'AIzaSyDJS6vSNSRpHUtbqYNpgIXnRLuzjrJJbpI'
os.environ['GOOGLE_SEARCH_ENGINE_ID'] = '9739254e10a3442a5'

from src.agent import MultiAgentFakeJobDetector

def test_multi_agent_system():
    """Test the multi-agent fake job detection system"""

    # Initialize the detector
    detector = MultiAgentFakeJobDetector()

    # Test cases
    test_cases = [
        {
            "name": "Legitimate Job Posting",
            "text": """
            Software Engineer at Google

            Company: Google LLC
            Location: Mountain View, CA
            Salary: $120,000 - $150,000 per year

            We are looking for a talented Software Engineer to join our team.
            The ideal candidate will have experience with Python, Java, and distributed systems.

            Responsibilities:
            - Design and develop scalable software solutions
            - Collaborate with cross-functional teams
            - Write clean, maintainable code

            Requirements:
            - Bachelor's degree in Computer Science
            - 3+ years of software development experience
            - Strong problem-solving skills

            Benefits:
            - Competitive salary
            - Health insurance
            - 401(k) matching
            - Flexible work hours

            Apply at: careers.google.com
            """,
            "expected_risk": "Low"
        },
        {
            "name": "Fake Job Scam",
            "text": """
            Earn ₹50,000 per week from home!

            Work from home typing job. No experience needed.
            Make money fast with our easy online work.

            Company: Global Tech Solutions
            Location: Remote

            Requirements:
            - Computer with internet
            - No skills required
            - Start immediately

            Send your bank details to get started.
            Training fee: ₹2,000 (refundable after first paycheck)

            Contact: +91-9876543210
            Email: jobs@globaltechsolutions.com
            """,
            "expected_risk": "High"
        },
        {
            "name": "Suspicious Job Posting",
            "text": """
            Data Entry Specialist - Work from Home

            Company: ABC Services
            Location: Remote
            Salary: ₹30,000 per month

            Easy data entry job. No experience needed.
            Flexible hours. Be your own boss.

            Requirements:
            - Basic computer skills
            - Internet connection

            Investment required: ₹5,000 for software and training.
            Guaranteed income after training.

            Apply now! Limited positions available.
            """,
            "expected_risk": "Medium"
        }
    ]

    print("🧪 Testing Multi-Agent Fake Job Detection System")
    print("=" * 60)
    print("⚠️  Note: API keys not configured - testing fallback behavior")
    print("=" * 60)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print("-" * 40)

        # Run detection
        result = detector.detect(test_case['text'])

        # Display results
        risk_level = result['risk_level']
        risk_score = result['final_risk_score']
        recommendation = result['recommendation']

        print(f"Risk Level: {risk_level} ({risk_score}%)")
        print(f"Recommendation: {recommendation}")

        # Agent breakdown
        breakdown = result['confidence_breakdown']
        print("\nAgent Confidence Scores:")
        print(f"  Cross-Platform Search: {breakdown['cross_platform_search']:.1f}%")
        print(f"  Company Verification: {breakdown['company_verification']:.1f}%")
        print(f"  Scam Detection: {breakdown['scam_detection']:.1f}%")
        print(f"  Data Quality: {breakdown['data_quality']:.1f}%")

        # Extracted info
        extracted = result['agent_results']['extractor']
        print("\nExtracted Information:")
        print(f"  Company: {extracted['company']}")
        print(f"  Role: {extracted['role']}")
        print(f"  Salary: {extracted['salary']}")
        print(f"  Location: {extracted['location']}")

        # Platform search
        search = result['agent_results']['search']
        platforms = search.get('found_on_platforms', [])
        print(f"\nPlatforms Found: {', '.join(platforms) if platforms else 'None'}")

        # Company verification
        verification = result['agent_results']['verification']
        print(f"Company Website: {'✅ Found' if verification.get('website_exists') else '❌ Not found'}")
        print(f"LinkedIn Page: {'✅ Found' if verification.get('linkedin_exists') else '❌ Not found'}")

        # Scam detection
        scam = result['agent_results']['scam_detection']
        scam_score = scam.get('scam_score', 0)
        print(f"Scam Detection Score: {scam_score}%")

        detected_scams = scam.get('detected_scams', [])
        if detected_scams:
            print(f"Detected Scam Patterns: {', '.join(detected_scams)}")

        # Expected vs Actual
        expected = test_case['expected_risk']
        actual = risk_level

        if expected == actual:
            print(f"✅ PASS: Expected {expected}, Got {actual}")
        else:
            print(f"⚠️  MISMATCH: Expected {expected}, Got {actual}")

        print("\n" + "=" * 60)

if __name__ == "__main__":
    test_multi_agent_system()