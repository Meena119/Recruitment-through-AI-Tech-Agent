#!/usr/bin/env python3

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

def view_all_datasets():
    """View all available datasets in a nice format"""
    
    # Connect to MongoDB
    client = MongoClient(os.getenv('MONGO_URI'))
    db = client.ai_interview
    
    try:
        # Get all datasets
        datasets = list(db.datasets.find({}))
        
        if not datasets:
            print("📭 No datasets found in the system")
            print("\nTo upload datasets:")
            print("1. Run: python upload_my_datasets.py")
            print("2. Choose option 1 (CSV) or 2 (JSON)")
            print("3. Use the sample file: sample_python_questions.csv")
            return
        
        # Prepare data for table
        table_data = []
        for dataset in datasets:
            domain = dataset.get('domain', 'unknown')
            count = dataset.get('question_count', 0)
            name = dataset.get('name', 'unnamed')
            created = dataset.get('created_at', 'unknown')
            source = dataset.get('source', 'unknown')
            file_name = dataset.get('file_name', 'unknown')
            
            table_data.append([
                name[:30],  # Truncate long names
                domain,
                count,
                source,
                file_name[:20] if file_name != 'unknown' else 'N/A',
                str(created)[:19] if created != 'unknown' else 'N/A'
            ])
        
        # Display table
        headers = ['Dataset Name', 'Domain', 'Questions', 'Source', 'File', 'Created']
        print("📚 Available Datasets")
        print("=" * 100)
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        # Summary by domain
        domain_summary = {}
        for dataset in datasets:
            domain = dataset.get('domain', 'unknown')
            count = dataset.get('question_count', 0)
            if domain not in domain_summary:
                domain_summary[domain] = 0
            domain_summary[domain] += count
        
        print(f"\n📊 Summary by Domain:")
        print("-" * 30)
        for domain, count in domain_summary.items():
            print(f"{domain:15}: {count:3} questions")
        
        print(f"\n📈 Total: {sum(domain_summary.values())} questions across {len(domain_summary)} domains")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    view_all_datasets()
