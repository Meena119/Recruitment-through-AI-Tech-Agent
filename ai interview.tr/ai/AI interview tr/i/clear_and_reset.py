# Script to clear old exam sessions and ensure fresh questions are used
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def clear_old_data():
    """Clear old exam sessions and test question loading"""
    
    # Connect to MongoDB
    client = MongoClient(os.getenv('MONGO_URI'))
    db = client.ai_interview
    
    print("🧹 Clearing old data...")
    
    # Clear old exam sessions
    result = db.exam_sessions.delete_many({})
    print(f"✅ Cleared {result.deleted_count} old exam sessions")
    
    # Check what's in mixed_questions (this should show our new questions)
    print("\n📋 Checking current questions in code:")
    
    # Import the mixed_questions from app.py to verify
    try:
        import sys
        sys.path.append('.')
        import app
        
        python_questions = app.mixed_questions.get('python', [])
        print(f"Python questions in code: {len(python_questions)}")
        
        for i, q in enumerate(python_questions[:3]):
            print(f"  {i+1}. {q.get('question', 'No question')}")
            print(f"     Type: {q.get('type', 'No type')}")
            print(f"     Answer: {q.get('answer', 'No answer')}")
            
    except Exception as e:
        print(f"❌ Error importing app: {e}")
    
    # Check if there are any datasets in database that might be interfering
    datasets = list(db.datasets.find({}))
    print(f"\n📊 Datasets in database: {len(datasets)}")
    
    for dataset in datasets[:3]:
        domain = dataset.get('domain', 'unknown')
        questions = dataset.get('dataset', {}).get('questions', [])
        print(f"  {domain}: {len(questions)} questions")
        if questions:
            print(f"    First question: {questions[0].get('question', 'No question')}")
    
    print("\n✅ Reset complete!")
    print("🚀 Now start your app and create a fresh exam to test questions")

if __name__ == "__main__":
    clear_old_data()
