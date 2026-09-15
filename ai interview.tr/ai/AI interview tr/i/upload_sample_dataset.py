import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGO_URI'))
db = client.ai_interview

# Sample dataset for Python
sample_python_dataset = {
    "questions": [
        {
            "question": "What is the output of: print(2 ** 3)?",
            "answer": "8",
            "type": "mcq",
            "options": ["8", "6", "9", "12"]
        },
        {
            "question": "Write a function to calculate factorial.",
            "answer": "def factorial(n): if n <= 1: return 1; return n * factorial(n-1)",
            "type": "coding"
        },
        {
            "question": "What is a Python list?",
            "answer": "A list is an ordered collection of items in Python, defined with square brackets [].",
            "type": "conceptual"
        },
        {
            "question": "How do you create a dictionary in Python?",
            "answer": "{}",
            "type": "mcq",
            "options": ["{}", "[]", "()", "<>"]
        },
        {
            "question": "Write a Python function to reverse a string.",
            "answer": "def reverse_string(s): return s[::-1]",
            "type": "coding"
        },
        {
            "question": "What is the difference between list and tuple?",
            "answer": "Lists are mutable, tuples are immutable. Lists use [], tuples use ().",
            "type": "conceptual"
        }
    ]
}

# Upload sample dataset
def upload_sample_dataset():
    try:
        # Insert sample dataset
        result = db.datasets.insert_one({
            'company_id': 'your_company_id_here',  # Replace with actual company ID
            'domain': 'python',
            'dataset': sample_python_dataset,
            'is_active': True,
            'created_at': datetime.now()
        })
        
        print(f"Sample dataset uploaded with ID: {result.inserted_id}")
        print("You can now use this dataset for Python exams!")
        
    except Exception as e:
        print(f"Error uploading dataset: {e}")

if __name__ == "__main__":
    upload_sample_dataset()
