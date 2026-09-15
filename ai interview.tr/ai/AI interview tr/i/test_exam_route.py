#!/usr/bin/env python3

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId

load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv('MONGO_URI'))
db = client.ai_interview

print("=== Testing Exam Route Logic ===")

# Get a student and job
student = db.students.find_one()
job = db.jobs.find_one()

if student and job:
    print(f"Testing with student: {student.get('name')} (ID: {student['_id']})")
    print(f"Testing with job: {job.get('title')} (ID: {job['_id']})")
    
    # Check if student already took this exam
    existing_result = db.exam_results.find_one({
        'student_id': str(student['_id']),
        'job_id': str(job['_id'])
    })
    
    if existing_result:
        print(f"❌ Student already took this exam on {existing_result.get('submitted_at')}")
    else:
        print("✅ Student has not taken this exam yet")
        
        # Test dataset loading
        domain_for_exam = job['domains'][0] if job['domains'] else 'python'
        print(f"Using domain: {domain_for_exam}")
        
        # Check if dataset exists for this domain
        dataset = db.datasets.find_one({
            'domain': domain_for_exam,
            'is_active': True
        })
        
        if dataset:
            print(f"✅ Found dataset for {domain_for_exam}")
            raw_questions = dataset.get('dataset', {}).get('questions', [])
            print(f"Dataset has {len(raw_questions)} questions")
            
            if len(raw_questions) > 0:
                print("✅ Questions available for exam")
                print(f"Sample question: {raw_questions[0].get('question', 'No question')[:100]}...")
            else:
                print("❌ No questions in dataset")
        else:
            print(f"❌ No dataset found for domain: {domain_for_exam}")
            
else:
    print("❌ No student or job found in database")

print("=== End Test ===")
