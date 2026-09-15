#!/usr/bin/env python3

import os
from upload_my_datasets import DatasetUploader

def upload_all_sample_datasets():
    """Upload all sample datasets at once"""
    
    uploader = DatasetUploader()
    
    # List of all sample datasets to upload
    datasets = [
        {
            'file': 'sample_python_questions.csv',
            'domain': 'python',
            'name': 'Python Programming Questions'
        },
        {
            'file': 'sample_java_questions.csv', 
            'domain': 'java',
            'name': 'Java Programming Questions'
        },
        {
            'file': 'sample_cpp_questions.csv',
            'domain': 'cpp', 
            'name': 'C++ Programming Questions'
        },
        {
            'file': 'sample_javascript_questions.csv',
            'domain': 'javascript',
            'name': 'JavaScript Programming Questions'
        },
        {
            'file': 'sample_sql_questions.csv',
            'domain': 'sql',
            'name': 'SQL Database Questions'
        },
        {
            'file': 'sample_web_questions.csv',
            'domain': 'web',
            'name': 'Web Development Questions'
        }
    ]
    
    print("📤 Uploading All Sample Datasets")
    print("=" * 50)
    
    success_count = 0
    total_count = len(datasets)
    
    for dataset in datasets:
        file_path = dataset['file']
        domain = dataset['domain']
        name = dataset['name']
        
        print(f"\n📁 Uploading: {file_path}")
        print(f"   Domain: {domain}")
        print(f"   Name: {name}")
        
        if os.path.exists(file_path):
            if uploader.upload_csv_dataset(file_path, domain, name):
                success_count += 1
                print("✅ Success!")
            else:
                print("❌ Failed!")
        else:
            print(f"❌ File not found: {file_path}")
    
    print(f"\n📊 Upload Summary:")
    print(f"   Successfully uploaded: {success_count}/{total_count}")
    print(f"   Failed: {total_count - success_count}")
    
    if success_count > 0:
        print("\n🎉 Datasets are ready! Now you can:")
        print("   1. Start Flask app: python app.py")
        print("   2. Login as company user")
        print("   3. Create jobs with these domains")
        print("   4. Students will get these questions in exams")
    
    # Show all datasets after upload
    print(f"\n📚 All Available Datasets:")
    print("=" * 50)
    uploader.list_available_datasets()

if __name__ == "__main__":
    upload_all_sample_datasets()
