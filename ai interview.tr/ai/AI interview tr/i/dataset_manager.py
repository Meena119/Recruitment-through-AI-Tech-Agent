import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import groq
from datetime import datetime

load_dotenv()

class DatasetManager:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGO_URI'))
        self.db = self.client.ai_interview
        self.groq_client = None
        try:
            self.groq_client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))
        except Exception as e:
            print(f"Warning: Could not initialize Groq client: {e}")
    
    def upload_dataset(self, company_id, domain, dataset_data):
        """Upload and train a dataset for a specific company and domain"""
        try:
            # Validate dataset structure
            if not self._validate_dataset(dataset_data):
                return False, "Invalid dataset structure"
            
            # Remove existing dataset for this company/domain if exists
            self.db.datasets.delete_many({
                'company_id': company_id,
                'domain': domain
            })
            
            # Save new dataset
            dataset_doc = {
                'company_id': company_id,
                'domain': domain,
                'dataset': dataset_data,
                'created_at': datetime.now(),
                'is_active': True,
                'question_count': len(dataset_data.get('questions', []))
            }
            
            result = self.db.datasets.insert_one(dataset_doc)
            
            # Train the dataset with Groq (if available)
            if self.groq_client:
                self._train_dataset(str(result.inserted_id), dataset_data)
            
            return True, f"Dataset uploaded successfully with {dataset_doc['question_count']} questions"
            
        except Exception as e:
            return False, f"Error uploading dataset: {str(e)}"
    
    def _validate_dataset(self, dataset_data):
        """Validate dataset structure"""
        required_fields = ['questions']
        for field in required_fields:
            if field not in dataset_data:
                return False
        
        # Validate each question
        for i, question in enumerate(dataset_data['questions']):
            if 'question' not in question or 'answer' not in question:
                return False
        
        return True
    
    def _train_dataset(self, dataset_id, dataset_data):
        """Train dataset with Groq API for better evaluation"""
        if not self.groq_client:
            return
        
        try:
            # Create training prompt for better understanding
            training_prompt = f"""
            You are now trained as an expert technical interviewer for the following dataset:
            
            Domain: Technical Programming
            Questions and Answers:
            {json.dumps(dataset_data['questions'], indent=2)}
            
            Please learn these question-answer pairs. When evaluating student answers, compare them with the provided correct answers and score based on:
            1. Conceptual accuracy
            2. Code correctness
            3. Completeness
            4. Similarity to the provided answer
            
            Respond with "Training complete" to confirm.
            """
            
            response = self.groq_client.chat.completions.create(
                model="llama2-70b-4096",
                messages=[{"role": "system", "content": training_prompt}],
                max_tokens=10,
                temperature=0.1
            )
            
            print(f"Dataset {dataset_id} training completed")
            
        except Exception as e:
            print(f"Error training dataset: {e}")
    
    def get_dataset(self, company_id, domain):
        """Get active dataset for a company and domain"""
        dataset = self.db.datasets.find_one({
            'company_id': company_id,
            'domain': domain,
            'is_active': True
        })
        return dataset
    
    def evaluate_answer_with_dataset(self, student_answer, correct_answer, domain, dataset_context=None):
        """Evaluate student answer against dataset answer using Groq"""
        if not self.groq_client:
            # Fallback evaluation
            return self._basic_evaluation(student_answer, correct_answer)
        
        try:
            # Create context-aware evaluation prompt
            context = ""
            if dataset_context:
                context = f"""
Dataset Context:
{json.dumps(dataset_context[:3], indent=2)}  # Include first 3 Q&A pairs for context
"""
            
            evaluation_prompt = f"""
{context}

You are an expert technical interviewer evaluating a {domain} programming answer.

Correct/Expected Answer: {correct_answer}

Student's Answer: {student_answer}

Evaluate the student's answer based on:
1. Technical accuracy (40%)
2. Code correctness (30%)
3. Conceptual understanding (20%)
4. Similarity to expected answer (10%)

Provide a score from 0-100 and brief feedback.
Respond in JSON format: {{"score": number, "feedback": "text"}}
"""
            
            response = self.groq_client.chat.completions.create(
                model="llama2-70b-4096",
                messages=[{"role": "user", "content": evaluation_prompt}],
                max_tokens=150,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                result = json.loads(result_text)
                return result.get('score', 50), result.get('feedback', 'No feedback available')
            except json.JSONDecodeError:
                # Fallback: extract score from text
                import re
                score_match = re.search(r'\b(\d{1,3})\b', result_text)
                score = int(score_match.group(1)) if score_match else 50
                return min(score, 100), result_text
            
        except Exception as e:
            print(f"Error in evaluation: {e}")
            return self._basic_evaluation(student_answer, correct_answer)
    
    def _basic_evaluation(self, student_answer, correct_answer):
        """Basic evaluation without Groq"""
        if not student_answer or len(student_answer.strip()) < 10:
            return 20, "Answer too short or empty"
        
        # Simple similarity check
        student_words = set(student_answer.lower().split())
        correct_words = set(correct_answer.lower().split())
        
        if not correct_words:
            return 60, "Basic evaluation - no reference answer"
        
        common_words = student_words & correct_words
        similarity = len(common_words) / len(correct_words) * 100
        
        # Add length bonus
        length_bonus = min(len(student_answer) / 100, 20)
        
        final_score = min(similarity + length_bonus, 100)
        
        feedback = f"Basic evaluation - Similarity: {similarity:.1f}%"
        
        return final_score, feedback
    
    def get_all_datasets(self, company_id):
        """Get all datasets for a company"""
        datasets = list(self.db.datasets.find({'company_id': company_id}))
        return datasets
    
    def delete_dataset(self, dataset_id):
        """Delete a dataset"""
        result = self.db.datasets.delete_one({'_id': dataset_id})
        return result.deleted_count > 0

# Global instance
dataset_manager = DatasetManager()
