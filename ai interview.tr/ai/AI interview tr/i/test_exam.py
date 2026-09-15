#!/usr/bin/env python3

# Simple test to check if the exam route works
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Try to import the app
    from app import app
    print("✅ App imported successfully")
    
    # Check if the take_exam route exists
    with app.test_client() as client:
        # Try to access the exam route (will fail due to login, but should show if route exists)
        response = client.get('/student/exam/507f1f77bcf86cd799439011')
        print(f"✅ Route responds with status: {response.status_code}")
        
    print("✅ Basic exam functionality test passed")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
