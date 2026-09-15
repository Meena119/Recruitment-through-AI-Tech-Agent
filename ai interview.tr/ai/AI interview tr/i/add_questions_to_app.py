# Simple script to add questions to app.py
# This will add your CSV questions as mixed questions in the app

# Read your app.py file
with open('app.py', 'r') as f:
    content = f.read()

# Define your questions for all domains
questions_code = '''
# Mixed questions for all domains - added from CSV files
mixed_questions = {
    'python': [
        {
            'question': 'What is the output of: print(2 ** 3)?',
            'type': 'mcq',
            'options': ['8', '6', '9', '12'],
            'answer': '8'
        },
        {
            'question': 'Write a Python function to calculate factorial.',
            'type': 'coding',
            'answer': 'def factorial(n): if n <= 1: return 1; return n * factorial(n-1)'
        },
        {
            'question': 'What is a Python list?',
            'type': 'conceptual',
            'answer': 'A list is an ordered collection of items in Python, defined with square brackets [].'
        },
        {
            'question': 'How do you create a dictionary in Python?',
            'type': 'mcq',
            'options': ['{}', '[]', '()', '<>'],
            'answer': '{}'
        },
        {
            'question': 'Write a Python function to reverse a string.',
            'type': 'coding',
            'answer': 'def reverse_string(s): return s[::-1]'
        },
        {
            'question': 'What is the difference between list and tuple?',
            'type': 'conceptual',
            'answer': 'Lists are mutable, tuples are immutable. Lists use [], tuples use ().'
        }
    ],
    'java': [
        {
            'question': 'What is the output of: System.out.println(5 + 3);',
            'type': 'mcq',
            'options': ['8', '5', '3', '53'],
            'answer': '8'
        },
        {
            'question': 'Write a Java method to calculate factorial.',
            'type': 'coding',
            'answer': 'public static int factorial(int n) { if (n <= 1) return 1; return n * factorial(n-1); }'
        },
        {
            'question': 'What is a Java class?',
            'type': 'conceptual',
            'answer': 'A class is a blueprint for creating objects in Java'
        },
        {
            'question': 'How do you declare an array in Java?',
            'type': 'mcq',
            'options': ['int[] arr = new int[10];', 'int arr[] = new int[10];', 'array arr = new int[10];', 'int arr[10];'],
            'answer': 'int[] arr = new int[10];'
        },
        {
            'question': 'Write a Java method to reverse a string.',
            'type': 'coding',
            'answer': 'public static String reverse(String s) { return new StringBuilder(s).reverse().toString(); }'
        },
        {
            'question': 'What is the difference between abstract class and interface?',
            'type': 'conceptual',
            'answer': 'Abstract class can have implementation, interface cannot have implementation (before Java 8)'
        }
    ],
    'cpp': [
        {
            'question': 'What is the output of: cout << (2 + 3);',
            'type': 'mcq',
            'options': ['5', '2', '3', '23'],
            'answer': '5'
        },
        {
            'question': 'Write a C++ function to calculate factorial.',
            'type': 'coding',
            'answer': 'int factorial(int n) { if (n <= 1) return 1; return n * factorial(n-1); }'
        },
        {
            'question': 'What is a C++ class?',
            'type': 'conceptual',
            'answer': 'A class is a user-defined data type that contains data members and member functions'
        },
        {
            'question': 'How do you declare a pointer in C++?',
            'type': 'mcq',
            'options': ['int* ptr;', 'int &ptr;', 'int ptr[];', 'pointer ptr;'],
            'answer': 'int* ptr;'
        },
        {
            'question': 'Write a C++ function to reverse a string.',
            'type': 'coding',
            'answer': 'string reverseString(string s) { reverse(s.begin(), s.end()); return s; }'
        },
        {
            'question': 'What is the difference between struct and class in C++?',
            'type': 'conceptual',
            'answer': 'struct members are public by default, class members are private by default'
        }
    ],
    'javascript': [
        {
            'question': 'What is the output of: console.log(typeof null);',
            'type': 'mcq',
            'options': ['object', 'null', 'undefined', 'string'],
            'answer': 'object'
        },
        {
            'question': 'Write a JavaScript function to calculate factorial.',
            'type': 'coding',
            'answer': 'function factorial(n) { if (n <= 1) return 1; return n * factorial(n-1); }'
        },
        {
            'question': 'What is a closure in JavaScript?',
            'type': 'conceptual',
            'answer': 'A closure is a function that has access to variables in its outer scope'
        },
        {
            'question': 'How do you declare a constant in JavaScript?',
            'type': 'mcq',
            'options': ['const PI = 3.14;', 'var PI = 3.14;', 'let PI = 3.14;', 'constant PI = 3.14;'],
            'answer': 'const PI = 3.14;'
        },
        {
            'question': 'Write a JavaScript function to reverse a string.',
            'type': 'coding',
            'answer': 'function reverseString(s) { return s.split(\'\').reverse().join(\'\'); }'
        },
        {
            'question': 'What is the difference between let and const?',
            'type': 'conceptual',
            'answer': 'let allows reassignment, const does not'
        }
    ],
    'sql': [
        {
            'question': 'What is the output of: SELECT 2 + 3;',
            'type': 'mcq',
            'options': ['5', '2', '3', '23'],
            'answer': '5'
        },
        {
            'question': 'Write an SQL query to find all employees from the employees table.',
            'type': 'coding',
            'answer': 'SELECT * FROM employees;'
        },
        {
            'question': 'What is a primary key in SQL?',
            'type': 'conceptual',
            'answer': 'A primary key uniquely identifies each record in a table'
        },
        {
            'question': 'Which clause is used to filter results in SQL?',
            'type': 'mcq',
            'options': ['WHERE', 'FILTER', 'HAVING', 'GROUP BY'],
            'answer': 'WHERE'
        },
        {
            'question': 'Write an SQL query to count employees in each department.',
            'type': 'coding',
            'answer': 'SELECT department, COUNT(*) FROM employees GROUP BY department;'
        },
        {
            'question': 'What is the difference between INNER JOIN and LEFT JOIN?',
            'type': 'conceptual',
            'answer': 'INNER JOIN returns matching rows, LEFT JOIN returns all rows from left table'
        }
    ],
    'web': [
        {
            'question': 'What is the purpose of the <div> tag in HTML?',
            'type': 'mcq',
            'options': ['Division', 'Section', 'Container', 'Block'],
            'answer': 'Division'
        },
        {
            'question': 'Write CSS to make text red and bold.',
            'type': 'coding',
            'answer': 'color: red; font-weight: bold;'
        },
        {
            'question': 'What is responsive web design?',
            'type': 'conceptual',
            'answer': 'Responsive design adapts layout to different screen sizes'
        },
        {
            'question': 'Which CSS property is used to change the background color?',
            'type': 'mcq',
            'options': ['background-color', 'color', 'background', 'background-image'],
            'answer': 'background-color'
        },
        {
            'question': 'Write HTML to create a link.',
            'type': 'coding',
            'answer': '<a href=\'url\'>Link text</a>'
        },
        {
            'question': 'What is the difference between padding and margin in CSS?',
            'type': 'conceptual',
            'answer': 'Padding is inside the element, margin is outside'
        }
    ]
}
'''

# Add the questions after the imports section
import_section = "from enhanced_ai_scorer import EnhancedAIScorer\n"
if import_section in content:
    # Insert questions after the imports
    insertion_point = content.find(import_section) + len(import_section)
    new_content = content[:insertion_point] + questions_code + '\n\n' + content[insertion_point:]
    
    # Write the updated content back to app.py
    with open('app.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Questions added to app.py successfully!")
    print("📚 Added questions for: python, java, cpp, javascript, sql, web")
    print("🚀 Now your app will use these questions for each domain!")
else:
    print("❌ Could not find import section in app.py")

print("\n🎯 Next steps:")
print("1. Start your Flask app: python app.py")
print("2. Create jobs with different domains")
print("3. Students will get domain-specific questions!")
