#!/usr/bin/env python3

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def trigger_backend_generation():
    """Trigger backend LLM question generation"""
    
    # Flask app URL
    flask_url = "http://localhost:5000/backend/auto_populate_datasets"
    
    # API key (you can set this in .env file)
    api_key = os.getenv('BACKEND_API_KEY', 'your-secret-key')
    
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        print("🚀 Triggering backend LLM question generation...")
        
        response = requests.post(flask_url, headers=headers, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ Backend LLM generation completed successfully!")
                print(f"Message: {result['message']}")
            else:
                print(f"❌ Backend generation failed: {result['message']}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure Flask app is running on localhost:5000")
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Generation took too long")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🤖 Backend LLM Question Generation Trigger")
    print("=" * 50)
    print("This script will trigger LLM question generation in the backend.")
    print("Make sure your Flask app is running on localhost:5000")
    print()
    
    # Check if Flask app is running
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        print("✅ Flask app is running")
        print()
        
        # Trigger generation
        trigger_backend_generation()
        
    except requests.exceptions.ConnectionError:
        print("❌ Flask app is not running!")
        print("Please start the Flask app first:")
        print("  python app.py")
        print()
        print("Then run this script again:")
        print("  python trigger_backend_generation.py")
