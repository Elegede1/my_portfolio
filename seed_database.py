#!/usr/bin/env python3
"""
Seed MongoDB with portfolio data from Jekuthiel Okafor's resume.
Run this script to populate the database with experience, education, skills, and projects.
"""

import os
import sys
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

load_dotenv()

# Get MongoDB URI from environment
mongo_uri = os.getenv('MONGO_URI') or os.getenv('mongo_uri')
if not mongo_uri:
    print("ERROR: MONGO_URI not set in environment variables")
    sys.exit(1)

# Clean up URI
mongo_uri = mongo_uri.strip().replace('/?', '?')
if mongo_uri.endswith('/'):
    mongo_uri = mongo_uri[:-1]

def get_db():
    """Connect to MongoDB and return database handle."""
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client.get_default_database()
        return db
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)

def seed_experience(db):
    """Seed experience collection."""
    experience_data = [
        {
            "company": "OmniDigitals",
            "title": "Senior Software Engineer (SaaS)",
            "date_range": "2023 – Present",
            "location": "Remote",
            "description": [
                "Designed and deployed an AI-powered customer-care bot that automated 60% of routine support queries and reduced average response times by 50%, freeing the support team for complex, high-value cases.",
                "Refactored core backend services for scalability, and developed APIs powering multiple SaaS applications.",
                "Built automation workflows for coaches and consultants with n8n and GoHighLevel, integrating CRM systems and marketing funnels; implemented retrieval-augmented generation (RAG) with Python and LangChain so clients could query internal knowledge bases in natural language.",
                "Deployed applications with Docker and AWS Lambda; instrumented production monitoring with Sentry and Grafana.",
                "Partnered with QA teams on test coverage and release quality, keeping production systems maintainable as the platform grew."
            ]
        },
        {
            "company": "Drug Drive",
            "title": "Software Engineer — Contract (Health-Tech)",
            "date_range": "2022 – Present",
            "location": "Remote",
            "description": [
                "Built backend services for pharmacist registration and identity verification in a compliance-sensitive domain.",
                "Developed integrations powering customer support and regulatory compliance workflows.",
                "Collaborated with cross-functional teams to deliver secure, reliable systems handling sensitive professional data."
            ]
        },
        {
            "company": "Home Hive",
            "title": "Software Engineer — Contract (Prop-Tech)",
            "date_range": "2022 – Present",
            "location": "Remote",
            "description": [
                "Developed the communication layer for landlord–tenant interactions: property inquiries, notifications, and messaging.",
                "Engineered email handling and prioritization logic that surfaced urgent tenant support requests first, improving response quality."
            ]
        },
        {
            "company": "Career Challenge Africa",
            "title": "Software Engineer — Contract (Ed-Tech)",
            "date_range": "2024 – Present",
            "location": "Remote",
            "description": [
                "Designed backend services supporting learners and program administrators on a career-development training platform.",
                "Built scraping workflows aggregating job postings, internships, and fellowships into a single opportunities pipeline for African job seekers.",
                "Developed integrations connecting the training platform with external career portals, and worked with the product team to streamline the learner experience."
            ]
        }
    ]
    
    # Clear existing and insert new
    db.experience.delete_many({})
    result = db.experience.insert_many(experience_data)
    print(f"Inserted {len(result.inserted_ids)} experience records")
    return result.inserted_ids

def seed_education(db):
    """Seed education collection."""
    education_data = [
        {
            "institution": "Federal School of Dental Technology and Therapy, Enugu",
            "degree": "Higher National Diploma (HND)",
            "field": "Dental Technology and Therapy",
            "date_range": "2013 – 2017",
            "location": "Enugu, Nigeria"
        },
        {
            "institution": "Udemy (Dr. Angela Yu)",
            "degree": "100 Days of Python Code",
            "field": "Python, Flask, APIs, GUI Applications, Data Analysis, Automation",
            "date_range": "2023",
            "location": "Online"
        },
        {
            "institution": "Udemy (Kurt Anderson)",
            "degree": "Software Engineering 101 + SCRUM Framework",
            "field": "Software Design, Agile/SCRUM Methodology",
            "date_range": "2023",
            "location": "Online"
        },
        {
            "institution": "Bincom Academy",
            "degree": "Python Development, Intermediate",
            "field": "Python Development",
            "date_range": "2023",
            "location": "Online"
        }
    ]
    
    db.education.delete_many({})
    result = db.education.insert_many(education_data)
    print(f"Inserted {len(result.inserted_ids)} education records")
    return result.inserted_ids

def seed_skills(db):
    """Seed skills collection."""
    skills_data = [
        # Professional Skills
        {"name": "Python (Django, FastAPI, Flask)", "skill_type": "Professional"},
        {"name": "Node.js / Express", "skill_type": "Professional"},
        {"name": "REST & GraphQL API Design", "skill_type": "Professional"},
        {"name": "React.js / Next.js / TypeScript", "skill_type": "Professional"},
        {"name": "Responsive UI Development", "skill_type": "Professional"},
        {"name": "OpenAI API / LangChain / RAG Pipelines", "skill_type": "Professional"},
        {"name": "Chatbot Development", "skill_type": "Professional"},
        {"name": "n8n / GoHighLevel / Zapier", "skill_type": "Professional"},
        {"name": "AWS (Lambda, Fargate, EKS, S3, SES, SQS, SNS)", "skill_type": "Professional"},
        {"name": "GCP", "skill_type": "Professional"},
        {"name": "Docker / Kubernetes", "skill_type": "Professional"},
        {"name": "Terraform", "skill_type": "Professional"},
        {"name": "CI/CD (GitHub Actions, Jenkins)", "skill_type": "Professional"},
        {"name": "PostgreSQL / MongoDB / SQL", "skill_type": "Professional"},
        {"name": "pytest / unittest", "skill_type": "Professional"},
        {"name": "Sentry / Grafana", "skill_type": "Professional"},
        {"name": "Agile / Scrum", "skill_type": "Professional"},
        {"name": "Code Review / Architecture Decisions / Mentoring", "skill_type": "Professional"},
        
        # Programming Languages
        {"name": "Python", "skill_type": "Language"},
        {"name": "JavaScript / TypeScript", "skill_type": "Language"},
        {"name": "Node.js", "skill_type": "Language"},
        {"name": "SQL", "skill_type": "Language"},
        {"name": "HTML / CSS", "skill_type": "Language"},
    ]
    
    db.skills.delete_many({})
    result = db.skills.insert_many(skills_data)
    print(f"Inserted {len(result.inserted_ids)} skill records")
    return result.inserted_ids

def seed_projects(db):
    """Seed projects collection."""
    projects_data = [
        {
            "title": "AI-Powered Customer Care Bot",
            "body": "Designed and deployed a customer-care bot that automated 60% of routine support queries and cut response times in half. Built with Python, LangChain, and RAG pipelines for natural language querying of internal knowledge bases.",
            "img_url": "assets/project-ai-bot.jpg",
            "github_url": "",
            "live_url": "",
            "date": datetime.utcnow()
        },
        {
            "title": "n8n & GoHighLevel Automation Workflows",
            "body": "Built automation workflows for coaches and consultants integrating CRM systems and marketing funnels. Implemented RAG with Python and LangChain so clients could query internal knowledge bases in natural language.",
            "img_url": "assets/project-automation.jpg",
            "github_url": "",
            "live_url": "",
            "date": datetime.utcnow()
        },
        {
            "title": "Pharmacist Registration & Verification System",
            "body": "Built backend services for pharmacist registration and identity verification in a compliance-sensitive health-tech domain. Developed integrations for customer support and regulatory compliance workflows.",
            "img_url": "assets/project-pharmacist.jpg",
            "github_url": "",
            "live_url": "",
            "date": datetime.utcnow()
        },
        {
            "title": "Landlord-Tenant Communication Platform",
            "body": "Developed the communication layer for property inquiries, notifications, and messaging. Engineered email handling and prioritization logic that surfaced urgent tenant support requests first.",
            "img_url": "assets/project-landlord.jpg",
            "github_url": "",
            "live_url": "",
            "date": datetime.utcnow()
        },
        {
            "title": "Career Development Training Platform",
            "body": "Designed backend services supporting learners and program administrators. Built scraping workflows aggregating job postings, internships, and fellowships into a single opportunities pipeline for African job seekers.",
            "img_url": "assets/project-career.jpg",
            "github_url": "",
            "live_url": "",
            "date": datetime.utcnow()
        },
        {
            "title": "Portfolio Website with Admin Panel",
            "body": "Full-stack portfolio with Flask, MongoDB, and Flask-Admin. Features dark mode, responsive design, project showcase, resume management, and contact form with graceful degradation when MongoDB is unavailable.",
            "img_url": "assets/project-portfolio.jpg",
            "github_url": "https://github.com/Elegede1/my-portfolio",
            "live_url": "https://my-portfolio-sigma-lilac-14.vercel.app",
            "date": datetime.utcnow()
        }
    ]
    
    db.projects.delete_many({})
    result = db.projects.insert_many(projects_data)
    print(f"Inserted {len(result.inserted_ids)} project records")
    return result.inserted_ids

def seed_admin_user(db):
    """Create default admin user if none exists."""
    from werkzeug.security import generate_password_hash
    
    existing = db.users.find_one({"email": "jekuthielnnamdi@gmail.com"})
    if existing:
        print("Admin user already exists")
        return
    
    admin_user = {
        "name": "Jekuthiel Okafor",
        "email": "jekuthielnnamdi@gmail.com",
        "password": generate_password_hash("changeme123"),  # Change this!
        "role": "admin"
    }
    result = db.users.insert_one(admin_user)
    print(f"Created admin user: {admin_user['email']} (password: changeme123 - CHANGE THIS!)")

def main():
    print("Connecting to MongoDB...")
    db = get_db()
    print(f"Connected to database: {db.name}")
    
    print("\nSeeding experience...")
    seed_experience(db)
    
    print("\nSeeding education...")
    seed_education(db)
    
    print("\nSeeding skills...")
    seed_skills(db)
    
    print("\nSeeding projects...")
    seed_projects(db)
    
    print("\nCreating admin user...")
    seed_admin_user(db)
    
    print("\n✅ Database seeding complete!")
    print("\n⚠️  IMPORTANT: Change the admin password after first login!")
    print("   Login at: /12812673-738234login")
    print("   Email: jekuthielnnamdi@gmail.com")
    print("   Default password: changeme123")

if __name__ == "__main__":
    main()