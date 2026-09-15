#!/usr/bin/env python3

import os
import json
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class DatasetUploader:
    """Upload datasets from your laptop to the system"""
    
    def __init__(self):
        # Connect to MongoDB
        self.client = MongoClient(os.getenv('MONGO_URI'))
        self.db = self.client.ai_interview
        
    def upload_csv_dataset(self, csv_file_path, domain, dataset_name=None):
        """Upload dataset from CSV file"""
        try:
            # Read CSV file
            df = pd.read_csv(csv_file_path)
            
            # Validate required columns
            required_columns = ['question', 'answer']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                print(f"❌ Missing required columns: {missing_columns}")
                return False
            
            # Convert DataFrame to questions format
            questions = []
            for index, row in df.iterrows():
                question_data = {
                    'question': str(row['question']).strip(),
                    'answer': str(row['answer']).strip(),
                    'type': str(row.get('type', 'conceptual')).strip()
                }
                
                # Add options if available (for MCQ questions)
                if 'options' in df.columns and pd.notna(row['options']):
                    options_str = str(row['options'])
                    question_data['options'] = [opt.strip() for opt in options_str.split(',')]
                
                questions.append(question_data)
            
            # Create dataset
            dataset = {
                'name': dataset_name or f"{domain}_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'domain': domain,
                'dataset': {
                    'questions': questions
                },
                'is_active': True,
                'created_at': datetime.now(),
                'question_count': len(questions),
                'source': 'csv_upload',
                'file_name': os.path.basename(csv_file_path)
            }
            
            # Insert into database
            result = self.db.datasets.insert_one(dataset)
            
            print(f"✅ Successfully uploaded {len(questions)} questions for {domain}")
            print(f"   Dataset ID: {result.inserted_id}")
            print(f"   File: {os.path.basename(csv_file_path)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error uploading CSV: {e}")
            return False
    
    def upload_json_dataset(self, json_file_path, domain, dataset_name=None):
        """Upload dataset from JSON file"""
        try:
            # Read JSON file
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate JSON structure
            if 'questions' not in data:
                print("❌ JSON must contain 'questions' array")
                return False
            
            questions = data['questions']
            
            # Validate each question
            for i, question in enumerate(questions):
                if 'question' not in question or 'answer' not in question:
                    print(f"❌ Question {i+1} missing required 'question' or 'answer' field")
                    return False
            
            # Create dataset
            dataset = {
                'name': dataset_name or f"{domain}_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'domain': domain,
                'dataset': data,
                'is_active': True,
                'created_at': datetime.now(),
                'question_count': len(questions),
                'source': 'json_upload',
                'file_name': os.path.basename(json_file_path)
            }
            
            # Insert into database
            result = self.db.datasets.insert_one(dataset)
            
            print(f"✅ Successfully uploaded {len(questions)} questions for {domain}")
            print(f"   Dataset ID: {result.inserted_id}")
            print(f"   File: {os.path.basename(json_file_path)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error uploading JSON: {e}")
            return False
    
    def list_available_datasets(self):
        """List all available datasets in the system"""
        try:
            datasets = list(self.db.datasets.find({}))
            
            if not datasets:
                print("📭 No datasets found in the system")
                return
            
            print(f"📚 Found {len(datasets)} datasets:")
            print("=" * 60)
            
            for dataset in datasets:
                domain = dataset.get('domain', 'unknown')
                count = dataset.get('question_count', 0)
                name = dataset.get('name', 'unnamed')
                created = dataset.get('created_at', 'unknown')
                source = dataset.get('source', 'unknown')
                
                print(f"📁 {name}")
                print(f"   Domain: {domain}")
                print(f"   Questions: {count}")
                print(f"   Source: {source}")
                print(f"   Created: {created}")
                print()
                
        except Exception as e:
            print(f"❌ Error listing datasets: {e}")
    
    def create_sample_csv(self, domain, output_file):
        """Create a sample CSV file for reference"""
        sample_data = [
            {
                'question': f'What is the output of: print(2 ** 3) in {domain}?',
                'answer': '8',
                'type': 'mcq',
                'options': '8,6,9,12'
            },
            {
                'question': f'Write a {domain} function to reverse a string.',
                'answer': f'def reverse_string(s): return s[::-1]',
                'type': 'coding'
            },
            {
                'question': f'What is a list in {domain}?',
                'answer': f'A list is an ordered collection of items in {domain}.',
                'type': 'conceptual'
            }
        ]
        
        df = pd.DataFrame(sample_data)
        df.to_csv(output_file, index=False)
        print(f"✅ Sample CSV created: {output_file}")

def main():
    """Main function for dataset upload"""
    uploader = DatasetUploader()
    
    print("📤 Dataset Upload Tool")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Upload CSV dataset")
        print("2. Upload JSON dataset")
        print("3. List available datasets")
        print("4. Create sample CSV")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            file_path = input("Enter CSV file path: ").strip()
            domain = input("Enter domain (python/java/cpp/javascript/sql/web): ").strip()
            name = input("Enter dataset name (optional): ").strip() or None
            
            if os.path.exists(file_path):
                uploader.upload_csv_dataset(file_path, domain, name)
            else:
                print("❌ File not found")
                
        elif choice == '2':
            file_path = input("Enter JSON file path: ").strip()
            domain = input("Enter domain (python/java/cpp/javascript/sql/web): ").strip()
            name = input("Enter dataset name (optional): ").strip() or None
            
            if os.path.exists(file_path):
                uploader.upload_json_dataset(file_path, domain, name)
            else:
                print("❌ File not found")
                
        elif choice == '3':
            uploader.list_available_datasets()
            
        elif choice == '4':
            domain = input("Enter domain (python/java/cpp/javascript/sql/web): ").strip()
            output_file = f"sample_{domain}_questions.csv"
            uploader.create_sample_csv(domain, output_file)
            
        elif choice == '5':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
