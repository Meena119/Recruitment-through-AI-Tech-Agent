# Test scoring calculation for the scenario
print('=== SCORING SCENARIO TEST ===')
print('Student answered 2 MCQ + 2 Coding correctly, 2 random answers, out of 7 questions')
print()

# Question setup with realistic scores
questions = [
    {'type': 'coding', 'weight': 2.0, 'score': 95, 'answered': True, 'desc': 'Coding Q1 - Correct'},
    {'type': 'conceptual', 'weight': 1.5, 'score': 88, 'answered': True, 'desc': 'Conceptual Q2 - Correct'},
    {'type': 'mcq', 'weight': 1.0, 'score': 100, 'answered': True, 'desc': 'MCQ Q3 - Correct'},
    {'type': 'coding', 'weight': 2.0, 'score': 98, 'answered': True, 'desc': 'Coding Q4 - Correct'},
    {'type': 'mcq', 'weight': 1.0, 'score': 5, 'answered': True, 'desc': 'MCQ Q5 - Random Answer'},
    {'type': 'conceptual', 'weight': 1.5, 'score': 8, 'answered': True, 'desc': 'Conceptual Q6 - Random Answer'},
    {'type': 'mcq', 'weight': 1.0, 'score': 0, 'answered': False, 'desc': 'MCQ Q7 - Unanswered'}
]

print('QUESTION BREAKDOWN:')
total_weighted_score = 0
total_max_weighted_score = 0

for i, q in enumerate(questions, 1):
    if q['answered']:
        weighted_score = q['score'] * q['weight']
        max_weighted = 100 * q['weight']
        total_weighted_score += weighted_score
        total_max_weighted_score += max_weighted
        print(f'Q{i}: {q["desc"]} | Score: {q["score"]}% | Weight: {q["weight"]}x | Weighted: {weighted_score:.0f}/{max_weighted:.0f}')
    else:
        print(f'Q{i}: {q["desc"]} | Score: 0% | Weight: {q["weight"]}x | Not counted in total')

print()
final_score = (total_weighted_score / total_max_weighted_score) * 100 if total_max_weighted_score > 0 else 0
print(f'TOTAL WEIGHTED SCORE: {total_weighted_score:.0f} / {total_max_weighted_score:.0f}')
print(f'FINAL PERCENTAGE: {final_score:.1f}%')
print()
print('REASONING:')
print('- Only answered questions count toward maximum score')
print('- Coding questions weighted 2.0x (most important)')
print('- Conceptual questions weighted 1.5x')
print('- MCQ questions weighted 1.0x')
print('- Random answers get very low AI evaluation scores')
print('- Unanswered question contributes 0 but doesn\'t reduce the maximum')
