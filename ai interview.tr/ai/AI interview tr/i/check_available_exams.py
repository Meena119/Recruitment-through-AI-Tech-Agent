#!/usr/bin/env python3

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId

load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv('MONGO_URI'))
db = client.ai_interview

print("=== Checking Available Exams ===")

# Get all students and jobs
students = list(db.students.find())
jobs = list(db.jobs.find())

print(f"Total students: {len(students)}")
print(f"Total jobs: {len(jobs)}")

if len(students) > 0 and len(jobs) > 0:
    student = students[0]
    print(f"\nChecking for student: {student.get('name')} (ID: {student['_id']})")
    
    for i, job in enumerate(jobs):
        print(f"\n--- Job {i+1}: {job.get('title')} ---")
        print(f"Job ID: {job['_id']}")
        print(f"Domains: {job.get('domains', [])}")
        print(f"Company: {job.get('company_name', 'Unknown')}")
        
        # Check if student already took this exam
        existing_result = db.exam_results.find_one({
            'student_id': str(student['_id']),
            'job_id': str(job['_id'])
        })
        
        if existing_result:
            print(f"❌ Already taken on {existing_result.get('submitted_at')}")
            print(f"   Score: {existing_result.get('score', 'N/A')}")
        else:
            print(f"✅ AVAILABLE - Not taken yet")
            
            # Check if dataset exists
            domain_for_exam = job['domains'][0] if job['domains'] else 'python'
            dataset = db.datasets.find_one({
                'domain': domain_for_exam,
                'is_active': True
            })
            
            if dataset:
                raw_questions = dataset.get('dataset', {}).get('questions', [])
                print(f"   Dataset: {len(raw_questions)} questions available")
            else:
                print(f"   ⚠️  No dataset for domain: {domain_for_exam}")

print("\n=== Summary ===")
available_jobs = []
for job in jobs:
    existing_result = db.exam_results.find_one({
        'student_id': str(students[0]['_id']),
        'job_id': str(job['_id'])
    })
    if not existing_result:
        available_jobs.append(job)

print(f"Jobs available for this student: {len(available_jobs)}")
for job in available_jobs:
    print(f"  - {job.get('title')} (ID: {job['_id']})")

print("=== End Check ===")
