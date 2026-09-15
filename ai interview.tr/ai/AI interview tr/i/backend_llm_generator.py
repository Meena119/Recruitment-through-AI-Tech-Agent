import os
import json
import random
from typing import Dict, List, Any
from datetime import datetime
import ollama

class BackendLLMGenerator:
    """Backend-only LLM question generation for automatic dataset population"""
    
    def __init__(self, ollama_client=None):
        from dotenv import load_dotenv
        load_dotenv()
        self.ollama_client = ollama_client
        self.model_name = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
        
        # Comprehensive question templates for different domains
        self.question_templates = {
            'coding': [
                "Write a {language} function to {task}.",
                "Create a {language} program that {task}.",
                "Implement {task} in {language}.",
                "Develop a {language} solution for {task}.",
                "Code a {language} function that {task}."
            ],
            'mcq': [
                "What is the output of {code_snippet} in {language}?",
                "Which {language} keyword is used to {concept}?",
                "What is the difference between {option1} and {option2} in {language}?",
                "How do you {operation} in {language}?",
                "What does the {concept} do in {language}?"
            ],
            'conceptual': [
                "Explain {concept} in {language}.",
                "What is the purpose of {feature} in {language}?",
                "Describe how {mechanism} works in {language}.",
                "What are the advantages of {concept} in {language}?",
                "When would you use {concept} in {language}?"
            ]
        }
        
        # Domain-specific topics for question generation
        self.topics = {
            'python': [
                'list comprehension', 'decorators', 'generators', 'lambda functions',
                'class inheritance', 'exception handling', 'file operations', 'modules',
                'virtual environments', 'data types', 'string manipulation', 'list operations',
                'dictionary methods', 'set operations', 'tuple operations', 'function parameters',
                'context managers', 'iterators', 'closures', 'metaclasses', 'property decorators'
            ],
            'java': [
                'OOP concepts', 'inheritance', 'polymorphism', 'encapsulation',
                'exception handling', 'collections framework', 'multithreading', 'file I/O',
                'lambda expressions', 'streams API', 'generics', 'interfaces',
                'abstract classes', 'static methods', 'constructor chaining', 'package management',
                'annotations', 'reflection', 'serialization', 'design patterns', 'JVM memory'
            ],
            'cpp': [
                'classes and objects', 'inheritance', 'polymorphism', 'virtual functions',
                'templates', 'STL containers', 'memory management', 'pointers',
                'exception handling', 'file operations', 'operator overloading', 'friend functions',
                'constructors and destructors', 'static members', 'const correctness', 'smart pointers',
                'move semantics', 'RAII', 'template metaprogramming', 'multiple inheritance'
            ],
            'javascript': [
                'closures', 'promises', 'async/await', 'arrow functions',
                'array methods', 'object manipulation', 'DOM manipulation', 'event handling',
                'ES6 features', 'prototypes', 'hoisting', 'scope and closures',
                'callback functions', 'fetch API', 'localStorage', 'JSON handling',
                'modules', 'destructuring', 'spread operator', 'template literals', 'classes'
            ],
            'sql': [
                'JOIN operations', 'aggregate functions', 'subqueries', 'window functions',
                'indexes', 'transactions', 'normalization', 'stored procedures',
                'triggers', 'views', 'CTE (Common Table Expressions)', 'pivot tables',
                'group by and having', 'case statements', 'foreign keys', 'primary keys',
                'constraints', 'union operations', 'stored functions', 'database optimization'
            ],
            'web': [
                'responsive design', 'CSS flexbox', 'CSS grid', 'JavaScript frameworks',
                'HTML5 semantic elements', 'CSS animations', 'REST APIs', 'authentication',
                'session management', 'cookies vs localStorage', 'HTTP methods', 'CORS',
                'web accessibility', 'performance optimization', 'SEO basics', 'browser caching',
                'progressive web apps', 'web components', 'service workers', 'websockets'
            ]
        }
    
    def generate_questions_for_domain(self, domain: str, count: int = 15) -> List[Dict]:
        """Generate questions for a specific domain"""
        if not self.groq_client:
            print("No LLM client available, using fallback questions")
            return self.generate_fallback_questions(domain, count)
        
        try:
            questions = []
            topics = self.topics.get(domain, self.topics['python'])
            
            # Generate balanced mix of question types
            question_types = ['coding', 'mcq', 'conceptual']
            type_distribution = {
                'coding': count // 2,      # 50% coding questions
                'mcq': count // 3,         # 33% MCQ questions  
                'conceptual': count - (count // 2) - (count // 3)  # Remaining conceptual
            }
            
            for q_type, q_count in type_distribution.items():
                for i in range(q_count):
                    question = self._generate_single_question(domain, q_type, topics)
                    if question:
                        questions.append(question)
            
            print(f"Generated {len(questions)} questions for {domain} domain")
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
                options={"temperature": 0.8, "num_predict": 400}
            )
            
            result_text = response['message']['content'].strip()
            
            # Parse the LLM response
            question_data = self._parse_llm_response(result_text, q_type)
            question_data['type'] = q_type
            question_data['difficulty'] = 'intermediate'
            question_data['weight'] = 1.0  # Default weight
            
            return question_data
            
        except Exception as e:
            print(f"Error generating single question: {e}")
            return None
    
    def _create_generation_prompt(self, domain: str, q_type: str, topic: str, template: str) -> str:
        """Create prompt for LLM question generation"""
        base_prompt = f"""
You are an expert technical interviewer creating questions for {domain} programming interviews.

Generate a {q_type} question about "{topic}" in {language if domain != 'cpp' else 'C++'}.

Requirements:
1. Question should be clear and specific
2. Difficulty level: Intermediate to Advanced
3. Should test practical knowledge and real-world scenarios
4. Provide a complete, correct answer
5. Follow industry best practices
"""
        
        if q_type == 'coding':
            base_prompt += f"""
6. Question template: {template}
7. Answer should be working, production-ready code
8. Include proper error handling and comments where needed
9. Use modern syntax and best practices

Example format:
{{
    "question": "Write a Python function to reverse a string using slicing.",
    "answer": "def reverse_string(s): return s[::-1]"
}}
"""
        elif q_type == 'mcq':
            base_prompt += f"""
6. Question template: {template}
7. Provide 4 multiple choice options (A, B, C, D)
8. Only one option should be correct
9. Options should be plausible but clearly distinguishable

Example format:
{{
    "question": "What is the output of: print(2 ** 3)?",
    "options": ["8", "6", "9", "12"],
    "answer": "8"
}}
"""
        elif q_type == 'conceptual':
            base_prompt += f"""
6. Question template: {template}
7. Answer should be a clear, comprehensive explanation
8. Include practical examples or use cases where relevant

Example format:
{{
    "question": "What is a Python list and how does it differ from a tuple?",
    "answer": "A list is an ordered, mutable collection in Python defined with square brackets []. A tuple is an ordered, immutable collection defined with parentheses (). Lists can be modified after creation, while tuples cannot."
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
                question_data['question'] = line.split(':', 1)[1].strip().strip('"')
            elif 'answer:' in line.lower():
                question_data['answer'] = line.split(':', 1)[1].strip().strip('"')
            elif 'options:' in line.lower() and q_type == 'mcq':
                options_str = line.split(':', 1)[1].strip().strip('"')
                question_data['options'] = [opt.strip().strip('"') for opt in options_str.split(',')]
        
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
                    'type': 'coding',
                    'difficulty': 'intermediate',
                    'weight': 1.0
                })
            elif i % 3 == 1:  # MCQ
                questions.append({
                    'question': f'What is {topic} in {domain}?',
                    'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                    'answer': 'Option A',
                    'type': 'mcq',
                    'difficulty': 'intermediate',
                    'weight': 1.0
                })
            else:  # Conceptual
                questions.append({
                    'question': f'Explain {topic} in {domain}.',
                    'answer': f'{topic} is an important concept in {domain} programming that helps developers write better code.',
                    'type': 'conceptual',
                    'difficulty': 'intermediate',
                    'weight': 1.0
                })
        
        return questions
    
    def auto_populate_datasets(self, db_connection):
        """Automatically populate datasets for all domains"""
        domains = ['python', 'java', 'cpp', 'javascript', 'sql', 'web']
        
        for domain in domains:
            try:
                # Check if dataset already exists
                existing = db_connection.datasets.find_one({'domain': domain, 'auto_generated': True})
                if existing:
                    print(f"Dataset for {domain} already exists, skipping...")
                    continue
                
                # Generate questions
                questions = self.generate_questions_for_domain(domain, 15)
                
                # Create dataset
                dataset = {
                    'domain': domain,
                    'dataset': {
                        'questions': questions
                    },
                    'is_active': True,
                    'auto_generated': True,
                    'created_at': datetime.now(),
                    'question_count': len(questions)
                }
                
                # Insert into database
                result = db_connection.datasets.insert_one(dataset)
                print(f"✅ Auto-generated dataset for {domain} with {len(questions)} questions (ID: {result.inserted_id})")
                
            except Exception as e:
                print(f"❌ Error generating dataset for {domain}: {e}")

# Usage function for backend initialization
def initialize_backend_llm():
    """Initialize backend LLM generator and auto-populate datasets"""
    try:
        import ollama
        from pymongo import MongoClient
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Check if Ollama model is available
        try:
            ollama.list()
        except Exception as e:
            print(f"Ollama not running or model not available: {e}")
            print("Please ensure Ollama is running and the model is pulled.")
            return
        
        # Initialize clients
        mongo_client = MongoClient(os.getenv('MONGO_URI'))
        db = mongo_client.ai_interview
        
        # Initialize generator
        generator = BackendLLMGenerator()
        
        # Auto-populate datasets
        generator.auto_populate_datasets(db)
        
        print("✅ Backend LLM initialization complete!")
        
    except Exception as e:
        print(f"❌ Backend LLM initialization failed: {e}")

if __name__ == "__main__":
    initialize_backend_llm()
