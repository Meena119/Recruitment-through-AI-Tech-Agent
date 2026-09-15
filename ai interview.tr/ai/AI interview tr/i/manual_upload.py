# Manual dataset upload - run this in Python directly
# Copy and paste this code into a Python interpreter

import os
import json
import csv
from pymongo import MongoClient
from datetime import datetime

# Database connection
MONGO_URI = "mongodb://localhost:27017/ai_interview"
client = MongoClient(MONGO_URI)
db = client.ai_interview

def upload_csv_manually(file_path, domain, name):
    """Upload CSV dataset manually"""
    questions = []
    
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            question_data = {
                'question': row['question'].strip(),
                'answer': row['answer'].strip(),
                'type': row.get('type', 'conceptual').strip()
            }
            
            if 'options' in row and row['options'].strip():
                question_data['options'] = [opt.strip() for opt in row['options'].split(',')]
            
            questions.append(question_data)
    
    dataset = {
        'name': name,
        'domain': domain,
        'dataset': {'questions': questions},
        'is_active': True,
        'created_at': datetime.now(),
        'question_count': len(questions),
        'source': 'manual_upload'
    }
    
    result = db.datasets.insert_one(dataset)
    print(f"✅ Uploaded {len(questions)} questions for {domain}")
    return result.inserted_id

# Upload all datasets
datasets_to_upload = [
    ('sample_python_questions.csv', 'python', 'Python Programming Questions'),
    ('sample_java_questions.csv', 'java', 'Java Programming Questions'),
    ('sample_cpp_questions.csv', 'cpp', 'C++ Programming Questions'),
    ('sample_javascript_questions.csv', 'javascript', 'JavaScript Programming Questions'),
    ('sample_sql_questions.csv', 'sql', 'SQL Database Questions'),
    ('sample_web_questions.csv', 'web', 'Web Development Questions')
]

print("📤 Manual Dataset Upload")
print("=" * 40)

for file_path, domain, name in datasets_to_upload:
    if os.path.exists(file_path):
        try:
            upload_csv_manually(file_path, domain, name)
        except Exception as e:
            print(f"❌ Error uploading {file_path}: {e}")
    else:
        print(f"❌ File not found: {file_path}")

# Verify upload
print("\n📚 Verification:")
all_datasets = list(db.datasets.find({}))
print(f"Total datasets in database: {len(all_datasets)}")

for dataset in all_datasets:
    print(f"- {dataset['name']}: {dataset['question_count']} questions ({dataset['domain']})")

print("\n✅ Upload complete! Now you can:")
print("1. Start Flask app")
print("2. Create jobs with different domains")
print("3. Students will get domain-specific questions")
