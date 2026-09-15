#!/usr/bin/env python3
"""
Test script to check scoring behavior with random answers
"""
import ollama
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()

def test_random_answer_scoring():
    """Test how the current scoring system handles random answers"""

    # Test cases with random/incorrect answers
    test_cases = [
        {
            "question": "Write a Python function to calculate factorial.",
            "correct_answer": "def factorial(n): if n <= 1: return 1; return n * factorial(n-1)",
            "random_answer": "I don't know, maybe use a loop or something?",
            "domain": "python"
        },
        {
            "question": "What is the output of: print(2 ** 3)?",
            "correct_answer": "8",
            "random_answer": "I think it's 6 or maybe 9, not sure.",
            "domain": "python"
        },
        {
            "question": "Write a Python function to reverse a string.",
            "correct_answer": "def reverse_string(s): return s[::-1]",
            "random_answer": "Something with loops and characters I guess.",
            "domain": "python"
        },
        {
            "question": "What is inheritance in Python?",
            "correct_answer": "Inheritance allows a class to inherit attributes and methods from another class.",
            "random_answer": "It's when classes share stuff, I think.",
            "domain": "python"
        }
    ]

    print("🧪 Testing Random Answer Scoring")
    print("=" * 50)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['question'][:50]}...")
        print(f"Correct Answer: {test_case['correct_answer']}")
        print(f"Random Answer: {test_case['random_answer']}")

        score = calculate_similarity_with_ollama(
            test_case['random_answer'],
            test_case['correct_answer'],
            test_case['domain']
        )

        print(f"Score Given: {score}")
        print("Expected: 0-20 (completely wrong/irrelevant)"
        print("❌ HIGH SCORE!" if score > 30 else "✅ Low score - good")

def calculate_similarity_with_ollama(student_answer, correct_answer, domain):
    """Current implementation from app.py"""
    if not correct_answer:
        return 70 if len(student_answer.strip()) > 10 else 40

    try:
        is_coding = any(lang in domain.lower() for lang in ['python', 'javascript', 'java', 'cpp', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'typescript', 'html', 'css', 'sql'])

        if is_coding:
            evaluation_prompt = f"""
            You are an expert technical interviewer evaluating a {domain} CODING answer.

            IMPORTANT: Focus on CORRECTNESS and FUNCTIONALITY, not exact code matching.
            Accept different variable names, alternative implementations, and equivalent solutions.

            CODING EVALUATION CRITERIA:
            1. Functional Correctness (40%) - Does the code solve the problem correctly?
            2. Logic Soundness (25%) - Is the algorithm/approach fundamentally correct?
            3. Syntax Validity (20%) - Is the code syntactically correct and runnable?
            4. Efficiency (15%) - Is the solution reasonably efficient for the problem?

            FLEXIBLE SCORING GUIDELINES:
            - 90-100: Perfect solution - correct, efficient, handles all cases
            - 80-89: Excellent - correct with minor efficiency or style differences
            - 70-79: Good - correct solution but different approach/implementation
            - 60-69: Adequate - works but has minor issues or inefficiencies
            - 40-59: Poor - works but has significant problems
            - 20-39: Very poor - major logic errors or doesn't fully work
            - 0-19: Completely wrong or doesn't compile

            SIMILAR CODING EXAMPLES (should score 70-90):
            - Question: "Write a function to reverse a string"
            - Perfect: "def reverse(s): return s[::-1]"
            - Similar: "def reverse(s): return ''.join(reversed(s))"  # Different approach
            - Similar: "def reverse(s): result = ''; for char in s: result = char + result; return result"  # Loop approach
            - Similar: "def reverse_string(text): return text[::-1]"  # Different function name

            QUESTION: {correct_answer}
            STUDENT CODE: {student_answer}

            Evaluate if student's code achieves the same result and follows correct logic,
            even if implemented differently. Focus on functionality, not exact syntax.

            Provide your evaluation in this exact JSON format:
            {{
                "score": <number 0-100>,
                "confidence": <high|medium|low>,
                "reasoning": "<brief technical explanation>",
                "breakdown": {{
                    "functional_correctness": <0-40>,
                    "logic_soundness": <0-25>,
                    "syntax_validity": <0-20>,
                    "efficiency": <0-15>
                }}
            }}

            IMPORTANT: Return ONLY the JSON object, no additional text.
            """
        else:
            evaluation_prompt = f"""
            You are an expert technical interviewer evaluating a {domain} programming answer.

            IMPORTANT: Focus on CONCEPTUAL UNDERSTANDING and TECHNICAL CORRECTNESS, not exact wording.
            Accept alternative approaches, different variable names, and equivalent solutions.

            EVALUATION CRITERIA (Weight in final score):
            1. Conceptual Understanding (40%) - Does the student understand the core concept?
            2. Technical Accuracy (30%) - Is the solution technically correct and valid?
            3. Completeness (20%) - Does it address the problem requirements?
            4. Clarity (10%) - Is the answer clear and understandable?

            FLEXIBLE SCORING GUIDELINES:
            - 90-100: Perfect understanding, technically correct, complete solution
            - 85-89: Excellent understanding with minor differences in approach
            - 75-84: Good understanding, technically sound but different implementation
            - 65-74: Adequate understanding with some minor technical issues
            - 50-64: Partial understanding with some conceptual gaps
            - 30-49: Poor understanding, major conceptual errors
            - 10-29: Very poor understanding, mostly incorrect
            - 0-9: Completely wrong or irrelevant

            SIMILAR ANSWER EXAMPLES (should score 75-90):
            - Question: "Use a for loop to print numbers 1-5"
            - Correct: "for i in range(1, 6): print(i)"
            - Similar: "for num in range(1, 6): print(num)"  # Different variable name
            - Similar: "for i in range(5): print(i+1)"    # Different approach, same result
            - Similar: "for i in [1,2,3,4,5]: print(i)"  # Using list instead of range

            QUESTION: {correct_answer}
            STUDENT ANSWER: {student_answer}

            Evaluate if the student's answer demonstrates the same understanding and achieves the same goal,
            even if implemented differently. Focus on correctness of approach, not exact syntax matching.

            Provide your evaluation in this exact JSON format:
            {{
                "score": <number 0-100>,
                "confidence": <high|medium|low>,
                "reasoning": "<brief explanation of why score was given>",
                "breakdown": {{
                    "conceptual_understanding": <0-40>,
                    "technical_accuracy": <0-30>,
                    "completeness": <0-20>,
                    "clarity": <0-10>
                }}
            }}

            IMPORTANT: Return ONLY the JSON object, no additional text.
            """

        response = ollama.chat(
            model=os.getenv('OLLAMA_MODEL', 'llama3.2:3b'),
            messages=[{"role": "user", "content": evaluation_prompt}],
            options={"temperature": 0.1, "num_predict": 200}
        )

        score_text = response['message']['content'].strip()

        try:
            import json
            result = json.loads(score_text)
            score = result.get('score', 50)

            if not isinstance(score, (int, float)) or score < 0 or score > 100:
                score = 50

            return min(int(score), 100)

        except json.JSONDecodeError:
            import re
            score_match = re.search(r'"score"\s*:\s*(\d+)', score_text)
            if score_match:
                score = int(score_match.group(1))
                return min(score, 100)
            else:
                numbers = re.findall(r'\d+', score_text)
                if numbers:
                    score = int(numbers[0])
                    return min(score, 100)
                else:
                    return 50

    except Exception as e:
        print(f"Error in similarity calculation: {e}")
        return 50

if __name__ == '__main__':
    test_random_answer_scoring()
