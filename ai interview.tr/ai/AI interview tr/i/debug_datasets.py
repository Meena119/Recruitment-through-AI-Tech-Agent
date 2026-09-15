#!/usr/bin/env python3

import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def debug_datasets():
    """Debug dataset loading issues"""
    
    # Connect to MongoDB
    client = MongoClient(os.getenv('MONGO_URI'))
    db = client.ai_interview
    
    print("🔍 Dataset Debug Information")
    print("=" * 50)
    
    # Check all datasets
    print("\n📚 All Datasets in Database:")
    datasets = list(db.datasets.find({}))
    
    if not datasets:
        print("❌ No datasets found!")
        print("\n📤 Please upload datasets first:")
        print("   python upload_all_datasets.py")
        return
    
    for dataset in datasets:
        print(f"\n📁 Dataset: {dataset.get('name', 'unnamed')}")
        print(f"   ID: {dataset['_id']}")
        print(f"   Domain: {dataset.get('domain', 'unknown')}")
        print(f"   Active: {dataset.get('is_active', False)}")
        print(f"   Questions: {dataset.get('question_count', 0)}")
        
        # Check question structure
        questions = dataset.get('dataset', {}).get('questions', [])
        if questions:
            print(f"   Sample Question: {questions[0].get('question', 'No question')[:50]}...")
    
    # Check jobs
    print(f"\n💼 Available Jobs:")
    jobs = list(db.jobs.find({}))
    
    if not jobs:
        print("❌ No jobs found!")
        return
    
    for job in jobs:
        print(f"\n📋 Job: {job.get('title', 'unnamed')}")
        print(f"   ID: {job['_id']}")
        print(f"   Company: {job.get('company_name', 'unknown')}")
        print(f"   Domains: {job.get('domains', [])}")
        print(f"   Company ID: {job.get('company_id', 'unknown')}")
    
    # Test dataset loading logic
    print(f"\n🧪 Testing Dataset Loading Logic:")
    
    if jobs:
        job = jobs[0]  # Test with first job
        domain_for_exam = job['domains'][0] if job['domains'] else 'python'
        company_id = job.get('company_id')
        
        print(f"   Testing with job: {job.get('title')}")
        print(f"   Domain: {domain_for_exam}")
        print(f"   Company ID: {company_id}")
        
        # Test 1: Company-specific dataset
        company_dataset = db.datasets.find_one({
            'company_id': company_id,
            'domain': domain_for_exam,
            'is_active': True
        })
        
        if company_dataset:
            print(f"   ✅ Company dataset found: {len(company_dataset.get('dataset', {}).get('questions', []))} questions")
        else:
            print(f"   ❌ No company dataset found")
        
        # Test 2: Public dataset for domain
        public_dataset = db.datasets.find_one({
            'domain': domain_for_exam,
            'is_active': True
        })
        
        if public_dataset:
            print(f"   ✅ Public dataset found: {len(public_dataset.get('dataset', {}).get('questions', []))} questions")
        else:
            print(f"   ❌ No public dataset found")
        
        # Test 3: Any dataset for domain
        any_dataset = db.datasets.find_one({
            'domain': domain_for_exam
        })
        
        if any_dataset:
            print(f"   ✅ Any dataset found: {len(any_dataset.get('dataset', {}).get('questions', []))} questions")
        else:
            print(f"   ❌ No dataset found for domain {domain_for_exam}")

if __name__ == "__main__":
    debug_datasets()
