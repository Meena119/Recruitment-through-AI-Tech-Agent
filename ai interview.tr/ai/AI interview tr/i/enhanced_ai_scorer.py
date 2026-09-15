import re
import json
import hashlib
import difflib
import ast
import subprocess
import tempfile
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any
import ollama
from dotenv import load_dotenv

class EnhancedAIScorer:
    """Advanced AI scoring system with multi-dimensional evaluation"""
    
    def __init__(self, ollama_client=None):
        load_dotenv()
        self.ollama_client = ollama_client
        self.model_name = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
        self.plagiarism_threshold = 0.85
        
    def evaluate_answer(self, student_answer: str, correct_answer: str, 
                       question_data: Dict, domain: str, 
                       question_type: str = "coding") -> Dict[str, Any]:
        """
        Comprehensive evaluation with multiple scoring dimensions
        """
        try:
            # Initialize scoring components
            scores = {
                'technical_accuracy': 0,
                'conceptual_understanding': 0,
                'code_quality': 0,
                'completeness': 0,
                'originality': 0,
                'execution_result': 0
            }
            
            feedback_components = []
            
            # 1. Technical Accuracy Evaluation
            tech_score, tech_feedback = self._evaluate_technical_accuracy(
                student_answer, correct_answer, domain, question_type
            )
            scores['technical_accuracy'] = tech_score
            feedback_components.append(tech_feedback)
            
            # 2. Conceptual Understanding
            concept_score, concept_feedback = self._evaluate_conceptual_understanding(
                student_answer, question_data.get('question', ''), domain
            )
            scores['conceptual_understanding'] = concept_score
            feedback_components.append(concept_feedback)
            
            # 3. Code Quality (for coding questions)
            if question_type == 'coding':
                quality_score, quality_feedback = self._evaluate_code_quality(
                    student_answer, domain
                )
                scores['code_quality'] = quality_score
                feedback_components.append(quality_feedback)
                
                # 4. Code Execution
                exec_score, exec_feedback = self._execute_and_validate_code(
                    student_answer, question_data
                )
                scores['execution_result'] = exec_score
                feedback_components.append(exec_feedback)
            else:
                scores['code_quality'] = 0
                scores['execution_result'] = 0
            
            # 5. Completeness Evaluation
            completeness_score, completeness_feedback = self._evaluate_completeness(
                student_answer, correct_answer, question_type
            )
            scores['completeness'] = completeness_score
            feedback_components.append(completeness_feedback)
            
            # 6. Originality/Plagiarism Check
            originality_score, originality_feedback = self._check_originality(
                student_answer, correct_answer
            )
            scores['originality'] = originality_score
            feedback_components.append(originality_feedback)
            
            # Calculate weighted final score
            weights = self._get_question_weights(question_type)
            final_score = self._calculate_weighted_score(scores, weights)
            
            # Generate comprehensive feedback
            detailed_feedback = self._generate_comprehensive_feedback(
                scores, feedback_components, final_score, question_type
            )
            
            # Determine performance level
            performance_level = self._get_performance_level(final_score)
            
            return {
                'final_score': round(final_score, 2),
                'performance_level': performance_level,
                'dimension_scores': scores,
                'detailed_feedback': detailed_feedback,
                'improvement_suggestions': self._generate_improvement_suggestions(
                    scores, question_type, domain
                ),
                'evaluation_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error in enhanced evaluation: {e}")
            return self._fallback_evaluation(student_answer, correct_answer)
    
    def _evaluate_technical_accuracy(self, student_answer: str, correct_answer: str, 
                                   domain: str, question_type: str) -> Tuple[int, str]:
        """Evaluate technical accuracy using local evaluation"""
        try:
            if question_type == 'mcq':
                # Exact match for MCQ
                if student_answer.strip().upper() == correct_answer.strip().upper():
                    return 100, "Correct answer"
                else:
                    return 0, "Incorrect answer"
            else:
                # Similarity-based for coding/conceptual
                similarity = difflib.SequenceMatcher(None, student_answer.lower(), correct_answer.lower()).ratio()
                score = similarity * 100
                feedback = f"Answer similarity: {similarity:.1%} - {'Good match' if similarity > 0.7 else 'Poor match'}"
                
                return min(max(score, 0), 100), feedback
            
        except Exception as e:
            print(f"Technical accuracy evaluation error: {e}")
            return 50, "Technical evaluation failed"
    
    def _evaluate_conceptual_understanding(self, student_answer: str, 
                                        question: str, domain: str) -> Tuple[int, str]:
        """Evaluate conceptual understanding using Ollama LLM"""
        if not self.ollama_client:
            return 50, "AI evaluation unavailable"
        
        try:
            # Create prompt for conceptual evaluation
            prompt = f"""
You are an expert {domain} interviewer evaluating a candidate's answer.

Question: {question}

Candidate's Answer: {student_answer}

Please evaluate the conceptual understanding shown in this answer. Consider:
1. Does the answer demonstrate understanding of core concepts?
2. Is the explanation clear and accurate?
3. Does it address the question appropriately?
4. Are there any misconceptions or errors?

Provide a score from 0-100 and brief feedback explaining the evaluation.

Format your response as:
SCORE: [number]
FEEDBACK: [brief explanation]
"""
            
            # Call Ollama API
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.3, 'num_predict': 200}
            )
            
            result_text = response['message']['content'].strip()
            
            # Parse the response
            score = 50  # default
            feedback = "AI evaluation completed"
            
            lines = result_text.split('\n')
            for line in lines:
                if line.upper().startswith('SCORE:'):
                    try:
                        score_str = line.split(':', 1)[1].strip()
                        score = min(max(int(float(score_str)), 0), 100)
                    except:
                        pass
                elif line.upper().startswith('FEEDBACK:'):
                    feedback = line.split(':', 1)[1].strip()
            
            return score, feedback
            
        except Exception as e:
            print(f"Conceptual evaluation error: {e}")
            # Fallback to similarity-based evaluation
            similarity = difflib.SequenceMatcher(None, student_answer.lower(), 
                                               question.lower()).ratio()
            score = similarity * 100
            feedback = f"Conceptual similarity: {similarity:.1%} - {'Good understanding' if similarity > 0.7 else 'Poor understanding'}"
            
            return min(max(score, 0), 100), feedback
    
    def _evaluate_code_quality(self, code: str, domain: str) -> Tuple[int, str]:
        """Evaluate code quality metrics"""
        if not code.strip():
            return 0, "No code provided"
        
        try:
            # Parse code for syntax checking
            try:
                ast.parse(code)
                syntax_score = 100
                syntax_feedback = "Syntax is correct"
            except SyntaxError as e:
                syntax_score = 30
                syntax_feedback = f"Syntax error: {str(e)}"
            
            # Check code quality aspects
            quality_metrics = {
                'has_comments': bool(re.search(r'#.*|//.*|/\*.*\*/', code)),
                'proper_indentation': self._check_indentation(code),
                'meaningful_variables': self._check_variable_names(code),
                'function_structure': self._check_function_structure(code),
                'error_handling': self._check_error_handling(code, domain)
            }
            
            # Calculate quality score
            quality_score = syntax_score * 0.4 + sum([
                quality_metrics['has_comments'] * 10,
                quality_metrics['proper_indentation'] * 15,
                quality_metrics['meaningful_variables'] * 15,
                quality_metrics['function_structure'] * 10,
                quality_metrics['error_handling'] * 10
            ])
            
            feedback_parts = [syntax_feedback]
            if not quality_metrics['has_comments']:
                feedback_parts.append("Add comments for better readability")
            if not quality_metrics['proper_indentation']:
                feedback_parts.append("Improve code indentation")
            if not quality_metrics['meaningful_variables']:
                feedback_parts.append("Use more descriptive variable names")
            
            return min(quality_score, 100), "; ".join(feedback_parts)
            
        except Exception as e:
            print(f"Code quality evaluation error: {e}")
            return 50, "Code quality evaluation failed"
    
    def _execute_and_validate_code(self, code: str, question_data: Dict) -> Tuple[int, str]:
        """Execute code and validate output"""
        if not code.strip():
            return 0, "No code to execute"
        
        try:
            # Create temporary file for execution
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Execute code with timeout
                result = subprocess.run(
                    ['python', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    return 100, f"Code executed successfully. Output: {result.stdout[:200]}"
                else:
                    return 40, f"Runtime error: {result.stderr[:200]}"
                    
            except subprocess.TimeoutExpired:
                return 30, "Code execution timed out (possible infinite loop)"
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
        except Exception as e:
            print(f"Code execution error: {e}")
            return 50, "Code execution failed"
    
    def _evaluate_completeness(self, student_answer: str, correct_answer: str, 
                             question_type: str) -> Tuple[int, str]:
        """Evaluate answer completeness"""
        student_len = len(student_answer.strip())
        correct_len = len(correct_answer.strip())
        
        if student_len == 0:
            return 0, "No answer provided"
        
        # Calculate completeness based on length and content coverage
        length_ratio = min(student_len / max(correct_len, 1), 2.0)  # Cap at 2x expected length
        
        # Check for key components
        completeness_factors = {
            'has_main_content': student_len > 20,
            'addresses_question': bool(student_answer.strip()),
            'reasonably_complete': length_ratio >= 0.5
        }
        
        score = sum([
            completeness_factors['has_main_content'] * 30,
            completeness_factors['addresses_question'] * 40,
            completeness_factors['reasonably_complete'] * 30
        ])
        
        feedback = "Answer is complete" if score >= 70 else "Answer needs more detail"
        
        return score, feedback
    
    def _check_originality(self, student_answer: str, correct_answer: str) -> Tuple[int, str]:
        """Check for plagiarism using similarity analysis"""
        if not student_answer.strip():
            return 0, "No answer to check"
        
        try:
            # Calculate similarity ratio
            similarity = difflib.SequenceMatcher(None, student_answer.lower(), 
                                               correct_answer.lower()).ratio()
            
            if similarity > self.plagiarism_threshold:
                return 20, f"Answer appears to be copied (similarity: {similarity:.1%})"
            elif similarity > 0.6:
                return 60, f"Answer is similar to expected (similarity: {similarity:.1%})"
            else:
                return 100, f"Answer appears original (similarity: {similarity:.1%})"
                
        except Exception as e:
            print(f"Originality check error: {e}")
            return 70, "Originality check failed"
    
    def _get_question_weights(self, question_type: str) -> Dict[str, float]:
        """Get scoring weights based on question type"""
        base_weights = {
            'technical_accuracy': 0.35,
            'conceptual_understanding': 0.25,
            'code_quality': 0.15,
            'completeness': 0.15,
            'originality': 0.10
        }
        
        if question_type == 'coding':
            base_weights['execution_result'] = 0.15
            base_weights['code_quality'] = 0.20
            base_weights['technical_accuracy'] = 0.30
        elif question_type == 'conceptual':
            base_weights['conceptual_understanding'] = 0.40
            base_weights['technical_accuracy'] = 0.25
        elif question_type == 'mcq':
            base_weights['technical_accuracy'] = 0.60
            base_weights['conceptual_understanding'] = 0.20
        
        return base_weights
    
    def _calculate_weighted_score(self, scores: Dict[str, int], 
                                 weights: Dict[str, float]) -> float:
        """Calculate final weighted score"""
        total_score = 0
        total_weight = 0
        
        for dimension, score in scores.items():
            weight = weights.get(dimension, 0)
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 50
    
    def _generate_comprehensive_feedback(self, scores: Dict[str, int], 
                                       feedback_components: List[str], 
                                       final_score: float, 
                                       question_type: str) -> str:
        """Generate detailed feedback combining all evaluations"""
        performance_level = self._get_performance_level(final_score)
        
        feedback = f"Performance Level: {performance_level}\n\n"
        feedback += "Dimensional Analysis:\n"
        
        dimension_names = {
            'technical_accuracy': 'Technical Accuracy',
            'conceptual_understanding': 'Conceptual Understanding',
            'code_quality': 'Code Quality',
            'completeness': 'Completeness',
            'originality': 'Originality',
            'execution_result': 'Code Execution'
        }
        
        for dimension, score in scores.items():
            if score > 0:  # Only show relevant dimensions
                name = dimension_names.get(dimension, dimension)
                feedback += f"- {name}: {score}/100\n"
        
        feedback += "\nDetailed Feedback:\n"
        feedback += "\n".join(feedback_components)
        
        return feedback
    
    def _generate_improvement_suggestions(self, scores: Dict[str, int], 
                                        question_type: str, 
                                        domain: str) -> List[str]:
        """Generate specific improvement suggestions"""
        suggestions = []
        
        if scores.get('technical_accuracy', 0) < 70:
            suggestions.append(f"Review {domain} fundamentals and syntax")
        
        if scores.get('conceptual_understanding', 0) < 70:
            suggestions.append("Focus on understanding core concepts and principles")
        
        if scores.get('code_quality', 0) < 70 and question_type == 'coding':
            suggestions.extend([
                "Add meaningful comments to explain your code",
                "Use descriptive variable names",
                "Follow proper indentation and formatting"
            ])
        
        if scores.get('completeness', 0) < 70:
            suggestions.append("Provide more complete and detailed answers")
        
        if scores.get('originality', 0) < 60:
            suggestions.append("Try to formulate answers in your own words")
        
        if scores.get('execution_result', 0) < 70 and question_type == 'coding':
            suggestions.append("Test your code to ensure it runs without errors")
        
        return suggestions if suggestions else ["Great job! Keep practicing to maintain excellence"]
    
    def _get_performance_level(self, score: float) -> str:
        """Determine performance level based on score"""
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Very Good"
        elif score >= 70:
            return "Good"
        elif score >= 60:
            return "Satisfactory"
        else:
            return "Needs Improvement"
    
    def _fallback_evaluation(self, student_answer: str, correct_answer: str) -> Dict[str, Any]:
        """Fallback evaluation when AI scoring fails"""
        # Basic similarity-based scoring
        if not student_answer.strip():
            final_score = 0
        elif not correct_answer.strip():
            final_score = 50 if len(student_answer) > 20 else 30
        else:
            similarity = difflib.SequenceMatcher(None, student_answer.lower(), 
                                               correct_answer.lower()).ratio()
            final_score = similarity * 100
        
        return {
            'final_score': round(final_score, 2),
            'performance_level': self._get_performance_level(final_score),
            'dimension_scores': {'technical_accuracy': final_score},
            'detailed_feedback': "Basic evaluation - AI scoring unavailable",
            'improvement_suggestions': ["Provide more detailed answers"],
            'evaluation_timestamp': datetime.now().isoformat()
        }
    
    # Helper methods for code quality checks
    def _check_indentation(self, code: str) -> bool:
        """Check if code has proper indentation"""
        lines = code.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('#'):
                # Basic indentation check
                if line.startswith(' ') and not line.startswith('    '):
                    return False
        return True
    
    def _check_variable_names(self, code: str) -> bool:
        """Check if variable names are meaningful"""
        # Simple heuristic: avoid single-letter variables (except common ones)
        single_letter_vars = re.findall(r'\b([a-z])\s*=', code)
        common_single_letters = {'i', 'j', 'k', 'x', 'y', 'z', 'a', 'b', 'c'}
        
        for var in single_letter_vars:
            if var not in common_single_letters:
                return False
        return True
    
    def _check_function_structure(self, code: str) -> bool:
        """Check if code has proper function structure"""
        return bool(re.search(r'def\s+\w+\s*\(', code))
    
    def _check_error_handling(self, code: str, domain: str) -> bool:
        """Check if code includes error handling"""
        error_patterns = [
            r'try\s*:',
            r'except\s+\w+',
            r'if\s+.*error',
            r'if\s+.*fail'
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return True
        return False