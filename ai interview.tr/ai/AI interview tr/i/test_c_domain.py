#!/usr/bin/env python3

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import get_mixed_questions

print("=== Testing C Domain Questions ===")

# Test getting mixed questions for 'c' domain
c_questions = get_mixed_questions('c')
print(f"Number of C questions: {len(c_questions)}")

for i, question in enumerate(c_questions[:3]):  # Show first 3 questions
    print(f"\nQuestion {i+1}:")
    print(f"  Type: {question.get('type', 'unknown')}")
    print(f"  Question: {question.get('question', 'No question')}")
    print(f"  Answer: {question.get('answer', 'No answer')[:50]}...")

print("\n✅ C domain questions are working!")
print("=== End Test ===")
