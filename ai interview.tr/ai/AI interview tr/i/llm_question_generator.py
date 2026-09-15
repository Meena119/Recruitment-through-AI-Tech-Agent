import os
import json
import random
from typing import Dict, List, Any
from datetime import datetime
import ollama

class LLMQuestionGenerator:
    """Generate questions using LLM models"""
    
    def __init__(self, ollama_client=None):
        from dotenv import load_dotenv
        load_dotenv()
        self.ollama_client = ollama_client
        self.model_name = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
        self.question_templates = {
            'coding': [
                "Write a {language} function to {task}.",
                "Create a {language} program that {task}.",
                "Implement {task} in {language}.",
                "Develop a {language} solution for {task}."
            ],
            'mcq': [
                "What is the output of {code_snippet} in {language}?",
                "Which {language} keyword is used to {concept}?",
                "What is the difference between {option1} and {option2} in {language}?",
                "How do you {operation} in {language}?"
            ],
            'conceptual': [
                "Explain {concept} in {language}.",
                "What is the purpose of {feature} in {language}?",
                "Describe how {mechanism} works in {language}.",
                "What are the advantages of {concept} in {language}?"
            ]
        }
        
        self.topics = {
            'python': [
                'list comprehension', 'decorators', 'generators', 'lambda functions',
                'class inheritance', 'exception handling', 'file operations', 'modules',
                'virtual environments', 'data types', 'string manipulation', 'list operations',
                'dictionary methods', 'set operations', 'tuple operations', 'function parameters'
            ],
            'java': [
                'OOP concepts', 'inheritance', 'polymorphism', 'encapsulation',
                'exception handling', 'collections framework', 'multithreading', 'file I/O',
                'lambda expressions', 'streams API', 'generics', 'interfaces',
                'abstract classes', 'static methods', 'constructor chaining', 'package management'
            ],
            'cpp': [
                'classes and objects', 'inheritance', 'polymorphism', 'virtual functions',
                'templates', 'STL containers', 'memory management', 'pointers',
                'exception handling', 'file operations', 'operator overloading', 'friend functions',
                'constructors and destructors', 'static members', 'const correctness', 'smart pointers'
            ],
            'javascript': [
                'closures', 'promises', 'async/await', 'arrow functions',
                'array methods', 'object manipulation', 'DOM manipulation', 'event handling',
                'ES6 features', 'prototypes', 'hoisting', 'scope and closures',
                'callback functions', 'fetch API', 'localStorage', 'JSON handling'
            ],
            'sql': [
                'JOIN operations', 'aggregate functions', 'subqueries', 'window functions',
                'indexes', 'transactions', 'normalization', 'stored procedures',
                'triggers', 'views', 'CTE (Common Table Expressions)', 'pivot tables',
                'group by and having', 'case statements', 'foreign keys', 'primary keys'
            ],
            'web': [
                'responsive design', 'CSS flexbox', 'CSS grid', 'JavaScript frameworks',
                'HTML5 semantic elements', 'CSS animations', 'REST APIs', 'authentication',
                'session management', 'cookies vs localStorage', 'HTTP methods', 'CORS',
                'web accessibility', 'performance optimization', 'SEO basics', 'browser caching'
            ]
        }
    
    def generate_questions_with_llm(self, domain: str, count: int = 10) -> List[Dict]:
        """Generate questions using LLM"""
        if not self.groq_client:
            print("No LLM client available, using fallback questions")
            return self.generate_fallback_questions(domain, count)
        
        try:
            questions = []
            topics = self.topics.get(domain, self.topics['python'])
            
            # Generate mix of question types
            question_types = ['coding', 'mcq', 'conceptual']
            type_distribution = {
                'coding': count // 2,  # 50% coding
                'mcq': count // 3,     # 33% MCQ
                'conceptual': count - (count // 2) - (count // 3)  # Remaining conceptual
            }
            
            for q_type, q_count in type_distribution.items():
                for i in range(q_count):
                    question = self._generate_single_question(domain, q_type, topics)
                    if question:
                        questions.append(question)
            
            return questions
            
        except Exception as e:
            print(f"Error generating questions with LLM: {e}")
            return self.generate_fallback_questions(domain, count)
    
    def _generate_single_question(self, domain: str, q_type: str, topics: List[str]) -> Dict:
        """Generate a single question using LLM"""
        try:
            topic = random.choice(topics)
            template = random.choice(self.question_templates[q_type])
            
            prompt = self._create_generation_prompt(domain, q_type, topic, template)
            
            response = ollama.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.7, "num_predict": 300}
            )
            
            result_text = response['message']['content'].strip()
            
            # Parse the LLM response
            question_data = self._parse_llm_response(result_text, q_type)
            question_data['type'] = q_type
            
            return question_data
            
        except Exception as e:
            print(f"Error generating single question: {e}")
            return None
    
    def _create_generation_prompt(self, domain: str, q_type: str, topic: str, template: str) -> str:
        """Create prompt for LLM question generation"""
        base_prompt = f"""
You are an expert technical interviewer creating questions for {domain} programming interviews.

Generate a {q_type} question about "{topic}" in {domain}.

Requirements:
1. Question should be clear and specific
2. Difficulty level: Intermediate
3. Should test practical knowledge
4. Provide a complete, correct answer
"""
        
        if q_type == 'coding':
            base_prompt += f"""
5. Question template: {template}
6. Answer should be working code
7. Include proper syntax and best practices

Example format:
{{
    "question": "Write a Python function to reverse a string.",
    "answer": "def reverse_string(s): return s[::-1]"
}}
"""
        elif q_type == 'mcq':
            base_prompt += f"""
5. Question template: {template}
6. Provide 4 multiple choice options (A, B, C, D)
7. Indicate the correct answer

Example format:
{{
    "question": "What is the output of: print(2 ** 3)?",
    "options": ["8", "6", "9", "12"],
    "answer": "8"
}}
"""
        elif q_type == 'conceptual':
            base_prompt += f"""
5. Question template: {template}
6. Answer should be a clear explanation

Example format:
{{
    "question": "What is a Python list?",
    "answer": "A list is an ordered collection of items in Python, defined with square brackets []."
}}
"""
        
        base_prompt += "\n\nGenerate the question now in valid JSON format:"
        return base_prompt
    
    def _parse_llm_response(self, response: str, q_type: str) -> Dict:
        """Parse LLM response into question format"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                question_data = json.loads(json_str)
                return question_data
            else:
                # Fallback parsing
                return self._fallback_parse(response, q_type)
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return self._fallback_parse(response, q_type)
    
    def _fallback_parse(self, response: str, q_type: str) -> Dict:
        """Fallback parsing if JSON extraction fails"""
        lines = response.strip().split('\n')
        question_data = {}
        
        for line in lines:
            if 'question:' in line.lower():
                question_data['question'] = line.split(':', 1)[1].strip()
            elif 'answer:' in line.lower():
                question_data['answer'] = line.split(':', 1)[1].strip()
            elif 'options:' in line.lower() and q_type == 'mcq':
                options_str = line.split(':', 1)[1].strip()
                question_data['options'] = [opt.strip() for opt in options_str.split(',')]
        
        return question_data
    
    def generate_fallback_questions(self, domain: str, count: int) -> List[Dict]:
        """Generate fallback questions if LLM fails"""
        topics = self.topics.get(domain, self.topics['python'])
        questions = []
        
        for i in range(min(count, len(topics))):
            topic = topics[i]
            
            # Generate simple fallback questions
            if i % 3 == 0:  # Coding
                questions.append({
                    'question': f'Write a {domain} function to handle {topic}.',
                    'answer': f'// {domain} function for {topic}\nfunction example() {{ /* implementation */ }}',
                    'type': 'coding'
                })
            elif i % 3 == 1:  # MCQ
                questions.append({
                    'question': f'What is {topic} in {domain}?',
                    'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                    'answer': 'Option A',
                    'type': 'mcq'
                })
            else:  # Conceptual
                questions.append({
                    'question': f'Explain {topic} in {domain}.',
                    'answer': f'{topic} is an important concept in {domain} programming.',
                    'type': 'conceptual'
                })
        
        return questions

# Usage example
if __name__ == "__main__":
    # Initialize with Groq client
    try:
        from groq import Groq
        groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        generator = LLMQuestionGenerator(groq_client)
    except:
        generator = LLMQuestionGenerator()
    
    # Generate questions for Python
    python_questions = generator.generate_questions_with_llm('python', 10)
    print(f"Generated {len(python_questions)} Python questions")
    
    for i, q in enumerate(python_questions[:3]):
        print(f"\n{i+1}. {q.get('question', 'No question')}")
        print(f"   Type: {q.get('type', 'unknown')}")
        print(f"   Answer: {q.get('answer', 'No answer')}")
