#!/usr/bin/env python3

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId

load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv('MONGO_URI'))
db = client.ai_interview

print("=== Database Debug ===")
print(f"Connected to MongoDB: {os.getenv('MONGO_URI')}")

# List all collections
collections = db.list_collection_names()
print(f"Available collections: {collections}")

# Check if there are any jobs
jobs_count = db.jobs.count_documents({})
print(f"Total jobs in database: {jobs_count}")

if jobs_count > 0:
    # Get first job
    job = db.jobs.find_one()
    print(f"First job: {job.get('title', 'No title')} (ID: {job['_id']})")
    print(f"Job domains: {job.get('domains', [])}")

# Check if there are any students
students_count = db.students.count_documents({})
print(f"Total students in database: {students_count}")

if students_count > 0:
    student = db.students.find_one()
    print(f"First student: {student.get('name', 'No name')} (ID: {student['_id']})")

# Check if exam_sessions collection exists
if 'exam_sessions' in collections:
    exam_sessions_count = db.exam_sessions.count_documents({})
    print(f"Exam sessions count: {exam_sessions_count}")
else:
    print("exam_sessions collection does not exist - will be created automatically")

# Check if there are any datasets
datasets_count = db.datasets.count_documents({})
print(f"Total datasets in database: {datasets_count}")

if datasets_count > 0:
    dataset = db.datasets.find_one()
    print(f"First dataset domain: {dataset.get('domain', 'No domain')}")

print("=== End Debug ===")
