from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import ollama
import speech_recognition as sr
import base64
import json
import io
import random
from dataset_manager import DatasetManager
from enhanced_ai_scorer import EnhancedAIScorer

# Mixed questions for all domains
mixed_questions = {
    'python': [
        {'question': 'What is the output of: print(2 ** 3)?', 'type': 'mcq', 'options': ['8', '6', '9', '12'], 'answer': '8'},
        {'question': 'Write a Python function to calculate factorial.', 'type': 'coding', 'answer': 'def factorial(n): if n <= 1: return 1; return n * factorial(n-1)'},
        {'question': 'What is a Python list?', 'type': 'conceptual', 'answer': 'A list is an ordered collection of items in Python, defined with square brackets [].'},
        {'question': 'How do you create a dictionary in Python?', 'type': 'mcq', 'options': ['{}', '[]', '()', '<>'], 'answer': '{}'},
        {'question': 'Write a Python function to reverse a string.', 'type': 'coding', 'answer': 'def reverse_string(s): return s[::-1]'},
        {'question': 'What is the difference between list and tuple?', 'type': 'conceptual', 'answer': 'Lists are mutable, tuples are immutable. Lists use [], tuples use ().'},
        {'question': 'What is the output of: print([1,2,3] * 2)?', 'type': 'mcq', 'options': ['[1,2,3,1,2,3]', '[2,4,6]', '[1,2,3]', 'Error'], 'answer': '[1,2,3,1,2,3]'},
        {'question': 'Write a Python function to check if a number is prime.', 'type': 'coding', 'answer': 'def is_prime(n): if n < 2: return False; for i in range(2, int(n**0.5)+1): if n % i == 0: return False; return True'},
        {'question': 'What is list comprehension in Python?', 'type': 'conceptual', 'answer': 'List comprehension is a concise way to create lists using a single line of code with syntax [expression for item in iterable if condition].'},
        {'question': 'Which method is used to add an element to a list?', 'type': 'mcq', 'options': ['append()', 'add()', 'insert()', 'push()'], 'answer': 'append()'},
        {'question': 'Write a Python function to find the maximum element in a list.', 'type': 'coding', 'answer': 'def find_max(lst): return max(lst) if lst else None'},
        {'question': 'What is the purpose of the __init__ method?', 'type': 'conceptual', 'answer': '__init__ is a special method that initializes newly created objects and is called automatically when an object is instantiated.'},
        {'question': 'What is the output of: print(bool([]))?', 'type': 'mcq', 'options': ['False', 'True', 'None', 'Error'], 'answer': 'False'},
        {'question': 'Write a Python class representing a Car.', 'type': 'coding', 'answer': 'class Car: def __init__(self, brand, model): self.brand = brand; self.model = model; def display(self): return f"{self.brand} {self.model}"'},
        {'question': 'What is inheritance in Python?', 'type': 'conceptual', 'answer': 'Inheritance allows a class to inherit attributes and methods from another class, promoting code reuse and establishing a parent-child relationship.'},
        {'question': 'Which keyword is used to define a function?', 'type': 'mcq', 'options': ['def', 'function', 'func', 'define'], 'answer': 'def'},
        {'question': 'Write a Python function to calculate Fibonacci series.', 'type': 'coding', 'answer': 'def fibonacci(n): a, b = 0, 1; result = []; for _ in range(n): result.append(a); a, b = b, a + b; return result'},
        {'question': 'What is the difference between == and is in Python?', 'type': 'conceptual', 'answer': '== checks for value equality, while is checks for object identity (whether two variables refer to the same object in memory).'},
        {'question': 'What is the output of: print(3 // 2)?', 'type': 'mcq', 'options': ['1', '1.5', '2', '0'], 'answer': '1'},
        {'question': 'Write a Python function to remove duplicates from a list.', 'type': 'coding', 'answer': 'def remove_duplicates(lst): return list(dict.fromkeys(lst))'},
        {'question': 'What is a decorator in Python?', 'type': 'conceptual', 'answer': 'A decorator is a function that modifies or enhances another function without changing its source code, using the @ syntax.'},
        {'question': 'Which module is used for working with regular expressions?', 'type': 'mcq', 'options': ['re', 'regex', 'pattern', 'match'], 'answer': 're'},
        {'question': 'Write a Python function to read a file and count words.', 'type': 'coding', 'answer': 'def count_words(filename): with open(filename, \'r\') as f: return len(f.read().split())'},
        {'question': 'What is the Global Interpreter Lock (GIL)?', 'type': 'conceptual', 'answer': 'The GIL is a mutex that protects access to Python objects, preventing multiple native threads from executing Python bytecode simultaneously.'},
        {'question': 'What is the output of: print(set([1,2,2,3]))?', 'type': 'mcq', 'options': ['{1, 2, 3}', '[1,2,3]', '{1,2}', 'Error'], 'answer': '{1, 2, 3}'},
        {'question': 'Write a Python function to implement binary search.', 'type': 'coding', 'answer': 'def binary_search(arr, target): left, right = 0, len(arr)-1; while left <= right: mid = (left + right)//2; if arr[mid] == target: return mid; elif arr[mid] < target: left = mid + 1; else: right = mid - 1; return -1'},
        {'question': 'What is the difference between shallow copy and deep copy?', 'type': 'conceptual', 'answer': 'Shallow copy copies the references of nested objects, while deep copy creates independent copies of all objects found in the original.'},
        {'question': 'Which method is used to sort a list in place?', 'type': 'mcq', 'options': ['sort()', 'sorted()', 'order()', 'arrange()'], 'answer': 'sort()'},
        {'question': 'Write a Python function to check palindrome.', 'type': 'coding', 'answer': 'def is_palindrome(s): return s == s[::-1]'},
        {'question': 'What is the purpose of the __str__ method?', 'type': 'conceptual', 'answer': '__str__ returns a string representation of an object and is called by str() and print() functions.'},
        {'question': 'What is the output of: print(len("Python"))?', 'type': 'mcq', 'options': ['6', '5', '7', 'Error'], 'answer': '6'},
        {'question': 'Write a Python function to merge two dictionaries.', 'type': 'coding', 'answer': 'def merge_dicts(dict1, dict2): return {**dict1, **dict2}'},
        {'question': 'What is a generator in Python?', 'type': 'conceptual', 'answer': 'A generator is a special function that produces a sequence of values lazily using yield, allowing memory-efficient iteration.'},
        {'question': 'Which keyword is used for exception handling?', 'type': 'mcq', 'options': ['try', 'except', 'catch', 'handle'], 'answer': 'try'},
        {'question': 'Write a Python function to calculate GCD.', 'type': 'coding', 'answer': 'import math; def gcd(a, b): return math.gcd(a, b)'},
        {'question': 'What is the difference between local and global variables?', 'type': 'conceptual', 'answer': 'Local variables are accessible only within the function they are defined, while global variables are accessible throughout the program.'},
        {'question': 'What is the output of: print(type(lambda x: x))?', 'type': 'mcq', 'options': ['<class \'function\'>', '<class \'lambda\'>', '<class \'type\'>', 'Error'], 'answer': '<class \'function\'>'},
        {'question': 'Write a Python function to flatten a nested list.', 'type': 'coding', 'answer': 'def flatten(lst): result = []; for item in lst: if isinstance(item, list): result.extend(flatten(item)); else: result.append(item); return result'},
        {'question': 'What is the purpose of the __name__ variable?', 'type': 'conceptual', 'answer': '__name__ is a special variable that equals "__main__" when the script is run directly, allowing code to be executed only when run as a script.'},
        {'question': 'Which method removes the last element from a list?', 'type': 'mcq', 'options': ['pop()', 'remove()', 'delete()', 'del'], 'answer': 'pop()'},
        {'question': 'Write a Python function to implement bubble sort.', 'type': 'coding', 'answer': 'def bubble_sort(arr): n = len(arr); for i in range(n): for j in range(0, n-i-1): if arr[j] > arr[j+1]: arr[j], arr[j+1] = arr[j+1], arr[j]; return arr'},
        {'question': 'What is polymorphism in Python?', 'type': 'conceptual', 'answer': 'Polymorphism allows objects of different classes to be treated as objects of a common superclass, enabling method overriding and interface flexibility.'},
        {'question': 'What is the output of: print(0.1 + 0.2 == 0.3)?', 'type': 'mcq', 'options': ['False', 'True', 'None', 'Error'], 'answer': 'False'},
        {'question': 'Write a Python function to validate email format.', 'type': 'coding', 'answer': 'import re; def is_valid_email(email): pattern = r\'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$\'; return re.match(pattern, email) is not None'},
        {'question': 'What is the difference between append and extend?', 'type': 'conceptual', 'answer': 'append adds a single element to the end of a list, while extend adds all elements from an iterable to the end of the list.'},
        {'question': 'Which function returns the memory address of an object?', 'type': 'mcq', 'options': ['id()', 'memory()', 'address()', 'ref()'], 'answer': 'id()'},
        {'question': 'Write a Python function to implement a stack.', 'type': 'coding', 'answer': 'class Stack: def __init__(self): self.items = []; def push(self, item): self.items.append(item); def pop(self): return self.items.pop() if self.items else None; def is_empty(self): return len(self.items) == 0'},
        {'question': 'What is the purpose of the __iter__ method?', 'type': 'conceptual', 'answer': '__iter__ returns an iterator object, allowing an object to be used in for loops and other iteration contexts.'},
        {'question': 'What is the output of: print(dict.fromkeys([\'a\',\'b\',\'a\'], 1))?', 'type': 'mcq', 'options': ['{\'a\': 1, \'b\': 1}', '{\'a\': 1, \'b\': 1, \'a\': 1}', '{\'a\': 2, \'b\': 1}', 'Error'], 'answer': '{\'a\': 1, \'b\': 1}'},
        {'question': 'Write a Python function to find common elements in two lists.', 'type': 'coding', 'answer': 'def common_elements(list1, list2): return list(set(list1) & set(list2))'},
        {'question': 'What is the difference between static method and class method?', 'type': 'conceptual', 'answer': 'Static methods don\'t access class or instance data, while class methods receive the class as first argument and can access class-level data.'},
        {'question': 'Which operator is used for exponentiation?', 'type': 'mcq', 'options': ['**', '^', '*', 'pow()'], 'answer': '**'},
        {'question': 'Write a Python function to implement a queue.', 'type': 'coding', 'answer': 'from collections import deque; class Queue: def __init__(self): self.items = deque(); def enqueue(self, item): self.items.append(item); def dequeue(self): return self.items.popleft() if self.items else None'},
        {'question': 'What is the purpose of the __del__ method?', 'type': 'conceptual', 'answer': '__del__ is a destructor method called when an object is about to be destroyed, used for cleanup operations.'},
        {'question': 'What is the output of: print(chr(65))?', 'type': 'mcq', 'options': ['A', '65', 'a', 'Error'], 'answer': 'A'},
        {'question': 'Write a Python function to convert string to title case.', 'type': 'coding', 'answer': 'def to_title_case(s): return s.title()'},
        {'question': 'What is the difference between @staticmethod and @classmethod?', 'type': 'conceptual', 'answer': '@staticmethod doesn\'t receive any special first argument, while @classmethod receives the class as first argument (cls).'},
        {'question': 'Which built-in function returns the type of an object?', 'type': 'mcq', 'options': ['type()', 'typeof()', 'class()', 'obj_type()'], 'answer': 'type()'},
        {'question': 'Write a Python function to implement insertion sort.', 'type': 'coding', 'answer': 'def insertion_sort(arr): for i in range(1, len(arr)): key = arr[i]; j = i - 1; while j >= 0 and arr[j] > key: arr[j + 1] = arr[j]; j -= 1; arr[j + 1] = key; return arr'},
        {'question': 'What is the purpose of the __getitem__ method?', 'type': 'conceptual', 'answer': '__getitem__ allows objects to support indexing using square brackets notation, enabling custom behavior for obj[key] access.'},
        {'question': 'What is the output of: print(sum([1,2,3], 10))?', 'type': 'mcq', 'options': ['16', '6', '10', 'Error'], 'answer': '16'},
        {'question': 'Write a Python function to check if two strings are anagrams.', 'type': 'coding', 'answer': 'def are_anagrams(s1, s2): return sorted(s1.replace(\' \', \'\').lower()) == sorted(s2.replace(\' \', \'\').lower())'},
        {'question': 'What is the difference between abstract classes and interfaces?', 'type': 'conceptual', 'answer': 'Python uses abstract base classes (ABC) with abc module, which can have both abstract and concrete methods, unlike traditional interfaces.'},
        {'question': 'Which method is used to join list elements into a string?', 'type': 'mcq', 'options': ['join()', 'concat()', 'merge()', 'combine()'], 'answer': 'join()'},
        {'question': 'Write a Python function to implement quick sort.', 'type': 'coding', 'answer': 'def quick_sort(arr): if len(arr) <= 1: return arr; pivot = arr[len(arr)//2]; left = [x for x in arr if x < pivot]; middle = [x for x in arr if x == pivot]; right = [x for x in arr if x > pivot]; return quick_sort(left) + middle + quick_sort(right)'},
        {'question': 'What is the purpose of the __repr__ method?', 'type': 'conceptual', 'answer': '__repr__ returns an unambiguous string representation of an object, primarily used for debugging and development.'}
    ],
    'java': [
        {'question': 'What is the output of: System.out.println(5 + 3);', 'type': 'mcq', 'options': ['8', '5', '3', '53'], 'answer': '8'},
        {'question': 'Write a Java method to calculate factorial.', 'type': 'coding', 'answer': 'public static int factorial(int n) { if (n <= 1) return 1; return n * factorial(n-1); }'},
        {'question': 'What is a Java class?', 'type': 'conceptual', 'answer': 'A class is a blueprint for creating objects in Java'},
        {'question': 'How do you declare an array in Java?', 'type': 'mcq', 'options': ['int[] arr = new int[10];', 'int arr[] = new int[10];', 'array arr = new int[10];', 'int arr[10];'], 'answer': 'int[] arr = new int[10];'},
        {'question': 'Write a Java method to reverse a string.', 'type': 'coding', 'answer': 'public static String reverse(String s) { return new StringBuilder(s).reverse().toString(); }'},
        {'question': 'What is the difference between abstract class and interface?', 'type': 'conceptual', 'answer': 'Abstract class can have implementation, interface cannot have implementation (before Java 8)'},
        {'question': 'What is the output of: System.out.println(10 % 3);', 'type': 'mcq', 'options': ['1', '3', '0', '10'], 'answer': '1'},
        {'question': 'Write a Java method to check if a number is prime.', 'type': 'coding', 'answer': 'public static boolean isPrime(int n) { if (n < 2) return false; for (int i = 2; i <= Math.sqrt(n); i++) if (n % i == 0) return false; return true; }'},
        {'question': 'What is method overloading in Java?', 'type': 'conceptual', 'answer': 'Method overloading allows multiple methods with the same name but different parameters in the same class.'},
        {'question': 'Which keyword is used to inherit a class in Java?', 'type': 'mcq', 'options': ['extends', 'implements', 'inherits', 'super'], 'answer': 'extends'},
        {'question': 'Write a Java method to find the maximum element in an array.', 'type': 'coding', 'answer': 'public static int findMax(int[] arr) { int max = arr[0]; for (int num : arr) if (num > max) max = num; return max; }'},
        {'question': 'What is the purpose of the main method in Java?', 'type': 'conceptual', 'answer': 'The main method is the entry point of a Java application where program execution begins.'},
        {'question': 'What is the output of: System.out.println("Java".length());', 'type': 'mcq', 'options': ['4', '5', '3', 'Error'], 'answer': '4'},
        {'question': 'Write a Java class representing a Person.', 'type': 'coding', 'answer': 'public class Person { private String name; private int age; public Person(String name, int age) { this.name = name; this.age = age; } public String getName() { return name; } public int getAge() { return age; } }'},
        {'question': 'What is encapsulation in Java?', 'type': 'conceptual', 'answer': 'Encapsulation is the practice of hiding internal data and methods and providing access through public methods.'},
        {'question': 'Which access modifier makes a member accessible only within the same class?', 'type': 'mcq', 'options': ['private', 'public', 'protected', 'default'], 'answer': 'private'},
        {'question': 'Write a Java method to calculate Fibonacci series.', 'type': 'coding', 'answer': 'public static int[] fibonacci(int n) { int[] fib = new int[n]; fib[0] = 0; if (n > 1) fib[1] = 1; for (int i = 2; i < n; i++) fib[i] = fib[i-1] + fib[i-2]; return fib; }'},
        {'question': 'What is polymorphism in Java?', 'type': 'conceptual', 'answer': 'Polymorphism allows objects of different classes to be treated as objects of a common superclass, enabling method overriding.'},
        {'question': 'What is the output of: System.out.println(5 == 5.0);', 'type': 'mcq', 'options': ['true', 'false', 'error', '5.0'], 'answer': 'true'},
        {'question': 'Write a Java method to sort an array using bubble sort.', 'type': 'coding', 'answer': 'public static void bubbleSort(int[] arr) { int n = arr.length; for (int i = 0; i < n-1; i++) for (int j = 0; j < n-i-1; j++) if (arr[j] > arr[j+1]) { int temp = arr[j]; arr[j] = arr[j+1]; arr[j+1] = temp; } }'},
        {'question': 'What is the difference between == and equals() in Java?', 'type': 'conceptual', 'answer': '== compares object references, while equals() compares object content for value equality.'},
        {'question': 'Which keyword is used to create an object in Java?', 'type': 'mcq', 'options': ['new', 'create', 'object', 'instance'], 'answer': 'new'},
        {'question': 'Write a Java method to check if a string is a palindrome.', 'type': 'coding', 'answer': 'public static boolean isPalindrome(String s) { int left = 0, right = s.length() - 1; while (left < right) if (s.charAt(left++) != s.charAt(right--)) return false; return true; }'},
        {'question': 'What is the Java Virtual Machine (JVM)?', 'type': 'conceptual', 'answer': 'JVM is an abstract computing machine that enables Java bytecode to be executed on any platform, providing platform independence.'},
        {'question': 'What is the output of: System.out.println(Math.max(3, 7));', 'type': 'mcq', 'options': ['7', '3', '0', 'Error'], 'answer': '7'},
        {'question': 'Write a Java method to implement binary search.', 'type': 'coding', 'answer': 'public static int binarySearch(int[] arr, int target) { int left = 0, right = arr.length - 1; while (left <= right) { int mid = left + (right - left) / 2; if (arr[mid] == target) return mid; if (arr[mid] < target) left = mid + 1; else right = mid - 1; } return -1; }'},
        {'question': 'What is method overriding in Java?', 'type': 'conceptual', 'answer': 'Method overriding allows a subclass to provide a specific implementation of a method already defined in its superclass.'},
        {'question': 'Which interface is used to compare objects for sorting?', 'type': 'mcq', 'options': ['Comparable', 'Comparator', 'Sortable', 'Orderable'], 'answer': 'Comparable'},
        {'question': 'Write a Java method to remove duplicates from an ArrayList.', 'type': 'coding', 'answer': 'import java.util.*; public static <T> List<T> removeDuplicates(List<T> list) { return new ArrayList<>(new HashSet<>(list)); }'},
        {'question': 'What is the purpose of the static keyword in Java?', 'type': 'conceptual', 'answer': 'static indicates that a member belongs to the class rather than to instances of the class.'},
        {'question': 'What is the output of: System.out.println("Hello".charAt(1));', 'type': 'mcq', 'options': ['e', 'H', 'l', 'Error'], 'answer': 'e'},
        {'question': 'Write a Java method to calculate GCD of two numbers.', 'type': 'coding', 'answer': 'public static int gcd(int a, int b) { while (b != 0) { int temp = b; b = a % b; a = temp; } return a; }'},
        {'question': 'What is the difference between ArrayList and LinkedList?', 'type': 'conceptual', 'answer': 'ArrayList uses dynamic array for storage and provides fast random access, while LinkedList uses doubly-linked list and provides fast insertion/deletion.'},
        {'question': 'Which exception is thrown when dividing by zero?', 'type': 'mcq', 'options': ['ArithmeticException', 'NullPointerException', 'NumberFormatException', 'ArrayIndexOutOfBoundsException'], 'answer': 'ArithmeticException'},
        {'question': 'Write a Java method to implement a stack.', 'type': 'coding', 'answer': 'import java.util.*; public class Stack<T> { private List<T> items = new ArrayList<>(); public void push(T item) { items.add(item); } public T pop() { return items.isEmpty() ? null : items.remove(items.size() - 1); } public boolean isEmpty() { return items.isEmpty(); } }'},
        {'question': 'What is the final keyword used for in Java?', 'type': 'conceptual', 'answer': 'final can be used to make variables constant, prevent method overriding, or prevent class inheritance.'},
        {'question': 'What is the output of: System.out.println(Integer.parseInt("123"));', 'type': 'mcq', 'options': ['123', '123.0', 'Error', 'null'], 'answer': '123'},
        {'question': 'Write a Java method to find common elements in two arrays.', 'type': 'coding', 'answer': 'import java.util.*; public static List<Integer> findCommon(int[] arr1, int[] arr2) { Set<Integer> set = new HashSet<>(); for (int num : arr1) set.add(num); List<Integer> common = new ArrayList<>(); for (int num : arr2) if (set.contains(num)) common.add(num); return common; }'},
        {'question': 'What is the difference between HashMap and TreeMap?', 'type': 'conceptual', 'answer': 'HashMap provides O(1) average time complexity and doesn\'t maintain order, while TreeMap provides O(log n) time complexity and maintains sorted order.'},
        {'question': 'Which method is used to get the length of an array?', 'type': 'mcq', 'options': ['length', 'size()', 'len()', 'count()'], 'answer': 'length'},
        {'question': 'Write a Java method to implement a queue.', 'type': 'coding', 'answer': 'import java.util.*; public class Queue<T> { private LinkedList<T> items = new LinkedList<>(); public void enqueue(T item) { items.addLast(item); } public T dequeue() { return items.isEmpty() ? null : items.removeFirst(); } public boolean isEmpty() { return items.isEmpty(); } }'},
        {'question': 'What is the purpose of the super keyword?', 'type': 'conceptual', 'answer': 'super is used to refer to the immediate parent class, its methods, and constructors.'},
        {'question': 'What is the output of: System.out.println(String.valueOf(42));', 'type': 'mcq', 'options': ['42', '42.0', 'Error', 'null'], 'answer': '42'},
        {'question': 'Write a Java method to validate email format.', 'type': 'coding', 'answer': 'public static boolean isValidEmail(String email) { return email.matches("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\\\.[a-zA-Z]{2,}$"); }'},
        {'question': 'What is the difference between throw and throws?', 'type': 'conceptual', 'answer': 'throw is used to explicitly throw an exception, while throws is used to declare exceptions that a method might throw.'},
        {'question': 'Which collection class is synchronized by default?', 'type': 'mcq', 'options': ['Vector', 'ArrayList', 'LinkedList', 'HashSet'], 'answer': 'Vector'},
        {'question': 'Write a Java method to implement quick sort.', 'type': 'coding', 'answer': 'public static void quickSort(int[] arr, int low, int high) { if (low < high) { int pi = partition(arr, low, high); quickSort(arr, low, pi - 1); quickSort(arr, pi + 1, high); } } private static int partition(int[] arr, int low, int high) { int pivot = arr[high]; int i = low - 1; for (int j = low; j < high; j++) if (arr[j] < pivot) { i++; int temp = arr[i]; arr[i] = arr[j]; arr[j] = temp; } int temp = arr[i + 1]; arr[i + 1] = arr[high]; arr[high] = temp; return i + 1; }'},
        {'question': 'What is the purpose of the this keyword?', 'type': 'conceptual', 'answer': 'this refers to the current object instance and is used to distinguish instance variables from local variables.'},
        {'question': 'What is the output of: System.out.println("Java".substring(1, 3));', 'type': 'mcq', 'options': ['av', 'ava', 'Ja', 'Error'], 'answer': 'av'},
        {'question': 'Write a Java method to check if two strings are anagrams.', 'type': 'coding', 'answer': 'public static boolean areAnagrams(String s1, String s2) { char[] arr1 = s1.replaceAll("\\\\s", "").toLowerCase().toCharArray(); char[] arr2 = s2.replaceAll("\\\\s", "").toLowerCase().toCharArray(); Arrays.sort(arr1); Arrays.sort(arr2); return Arrays.equals(arr1, arr2); }'},
        {'question': 'What is the difference between interface and abstract class?', 'type': 'conceptual', 'answer': 'Interface can only have abstract methods (before Java 8) and supports multiple inheritance, while abstract class can have both abstract and concrete methods but single inheritance.'},
        {'question': 'Which method is used to convert string to integer?', 'type': 'mcq', 'options': ['Integer.parseInt()', 'String.toInt()', 'Integer.valueOf()', 'String.toInteger()'], 'answer': 'Integer.parseInt()'},
        {'question': 'Write a Java method to implement a linked list.', 'type': 'coding', 'answer': 'public class LinkedList<T> { class Node { T data; Node next; Node(T data) { this.data = data; this.next = null; } } private Node head; public void add(T data) { Node newNode = new Node(data); if (head == null) head = newNode; else { Node current = head; while (current.next != null) current = current.next; current.next = newNode; } } }'},
        {'question': 'What is the purpose of the toString() method?', 'type': 'conceptual', 'answer': 'toString() returns a string representation of an object and is automatically called when converting objects to strings.'}
    ],
    'cpp': [
        {'question': 'What is the output of: cout << (2 + 3);', 'type': 'mcq', 'options': ['5', '2', '3', '23'], 'answer': '5'},
        {'question': 'Write a C++ function to calculate factorial.', 'type': 'coding', 'answer': 'int factorial(int n) { if (n <= 1) return 1; return n * factorial(n-1); }'},
        {'question': 'What is a C++ class?', 'type': 'conceptual', 'answer': 'A class is a user-defined data type that contains data members and member functions'},
        {'question': 'How do you declare a pointer in C++?', 'type': 'mcq', 'options': ['int* ptr;', 'int &ptr;', 'int ptr[];', 'pointer ptr;'], 'answer': 'int* ptr;'},
        {'question': 'Write a C++ function to reverse a string.', 'type': 'coding', 'answer': 'string reverseString(string s) { reverse(s.begin(), s.end()); return s; }'},
        {'question': 'What is the difference between struct and class in C++?', 'type': 'conceptual', 'answer': 'struct members are public by default, class members are private by default'},
        {'question': 'What is the output of: cout << (10 % 3);', 'type': 'mcq', 'options': ['1', '3', '0', '10'], 'answer': '1'},
        {'question': 'Write a C++ function to check if a number is prime.', 'type': 'coding', 'answer': 'bool isPrime(int n) { if (n < 2) return false; for (int i = 2; i * i <= n; i++) if (n % i == 0) return false; return true; }'},
        {'question': 'What is function overloading in C++?', 'type': 'conceptual', 'answer': 'Function overloading allows multiple functions with the same name but different parameters in the same scope.'},
        {'question': 'Which keyword is used to allocate memory dynamically?', 'type': 'mcq', 'options': ['new', 'malloc', 'alloc', 'create'], 'answer': 'new'},
        {'question': 'Write a C++ function to find the maximum element in an array.', 'type': 'coding', 'answer': 'int findMax(int arr[], int size) { int max = arr[0]; for (int i = 1; i < size; i++) if (arr[i] > max) max = arr[i]; return max; }'},
        {'question': 'What is inheritance in C++?', 'type': 'conceptual', 'answer': 'Inheritance allows a class to inherit properties and methods from another class, promoting code reuse.'},
        {'question': 'What is the output of: cout << string("Hello").length();', 'type': 'mcq', 'options': ['5', '6', '4', 'Error'], 'answer': '5'},
        {'question': 'Write a C++ class representing a Person.', 'type': 'coding', 'answer': 'class Person { private: string name; int age; public: Person(string n, int a) : name(n), age(a) {} string getName() { return name; } int getAge() { return age; } };'},
        {'question': 'What is encapsulation in C++?', 'type': 'conceptual', 'answer': 'Encapsulation is the bundling of data and methods that operate on the data within one unit, hiding internal details.'},
        {'question': 'Which access specifier makes members accessible only within the class?', 'type': 'mcq', 'options': ['private', 'public', 'protected', 'internal'], 'answer': 'private'},
        {'question': 'Write a C++ function to calculate Fibonacci series.', 'type': 'coding', 'answer': 'vector<int> fibonacci(int n) { vector<int> fib; if (n >= 1) fib.push_back(0); if (n >= 2) fib.push_back(1); for (int i = 2; i < n; i++) fib.push_back(fib[i-1] + fib[i-2]); return fib; }'},
        {'question': 'What is polymorphism in C++?', 'type': 'conceptual', 'answer': 'Polymorphism allows objects of different classes to be treated as objects of a common base class, enabling virtual functions.'},
        {'question': 'What is the output of: cout << (5 == 5.0);', 'type': 'mcq', 'options': ['1', '0', 'error', '5.0'], 'answer': '1'},
        {'question': 'Write a C++ function to sort an array using bubble sort.', 'type': 'coding', 'answer': 'void bubbleSort(int arr[], int n) { for (int i = 0; i < n-1; i++) for (int j = 0; j < n-i-1; j++) if (arr[j] > arr[j+1]) swap(arr[j], arr[j+1]); }'},
        {'question': 'What is the difference between new and malloc?', 'type': 'conceptual', 'answer': 'new calls constructor and returns typed pointer, malloc allocates raw memory without initialization.'},
        {'question': 'Which operator is used to access members of a pointer to an object?', 'type': 'mcq', 'options': ['->', '.', '::', '*'], 'answer': '->'},
        {'question': 'Write a C++ function to check if a string is a palindrome.', 'type': 'coding', 'answer': 'bool isPalindrome(string s) { int left = 0, right = s.length() - 1; while (left < right) if (s[left++] != s[right--]) return false; return true; }'},
        {'question': 'What is a virtual function in C++?', 'type': 'conceptual', 'answer': 'A virtual function is a member function that can be overridden in derived classes, enabling runtime polymorphism.'},
        {'question': 'What is the output of: cout << max(3, 7);', 'type': 'mcq', 'options': ['7', '3', '0', 'Error'], 'answer': '7'},
        {'question': 'Write a C++ function to implement binary search.', 'type': 'coding', 'answer': 'int binarySearch(int arr[], int size, int target) { int left = 0, right = size - 1; while (left <= right) { int mid = left + (right - left) / 2; if (arr[mid] == target) return mid; if (arr[mid] < target) left = mid + 1; else right = mid - 1; } return -1; }'},
        {'question': 'What is function overriding in C++?', 'type': 'conceptual', 'answer': 'Function overriding allows a derived class to provide a specific implementation of a virtual function from base class.'},
        {'question': 'Which header file is needed for input/output operations?', 'type': 'mcq', 'options': ['<iostream>', '<stdio.h>', '<conio.h>', '<iostream.h>'], 'answer': '<iostream>'},
        {'question': 'Write a C++ function to remove duplicates from a vector.', 'type': 'coding', 'answer': '#include <algorithm>; vector<int> removeDuplicates(vector<int> vec) { sort(vec.begin(), vec.end()); vec.erase(unique(vec.begin(), vec.end()), vec.end()); return vec; }'},
        {'question': 'What is the purpose of the static keyword in C++?', 'type': 'conceptual', 'answer': 'static can be used for class members shared by all objects, or for variables with local scope but static storage duration.'},
        {'question': 'What is the output of: cout << string("Hello")[1];', 'type': 'mcq', 'options': ['e', 'H', 'l', 'Error'], 'answer': 'e'},
        {'question': 'Write a C++ function to calculate GCD of two numbers.', 'type': 'coding', 'answer': 'int gcd(int a, int b) { while (b != 0) { int temp = b; b = a % b; a = temp; } return a; }'},
        {'question': 'What is the difference between vector and array?', 'type': 'conceptual', 'answer': 'vector is dynamic and can grow/shrink, array has fixed size determined at compile time.'},
        {'question': 'Which exception is thrown when dividing by zero?', 'type': 'mcq', 'options': ['No exception (undefined behavior)', 'DivideByZeroException', 'ArithmeticException', 'RuntimeError'], 'answer': 'No exception (undefined behavior)'},
        {'question': 'Write a C++ class to implement a stack.', 'type': 'coding', 'answer': 'class Stack { private: vector<int> items; public: void push(int item) { items.push_back(item); } int pop() { if (items.empty()) return -1; int item = items.back(); items.pop_back(); return item; } bool isEmpty() { return items.empty(); } };'},
        {'question': 'What is the const keyword used for in C++?', 'type': 'conceptual', 'answer': 'const specifies that a variable cannot be modified, or that a member function doesn\'t modify the object.'},
        {'question': 'What is the output of: cout << to_string(42);', 'type': 'mcq', 'options': ['42', '42.0', 'Error', 'null'], 'answer': '42'},
        {'question': 'Write a C++ function to find common elements in two arrays.', 'type': 'coding', 'answer': '#include <unordered_set>; vector<int> findCommon(int arr1[], int size1, int arr2[], int size2) { unordered_set<int> set(arr1, arr1 + size1); vector<int> common; for (int i = 0; i < size2; i++) if (set.count(arr2[i])) common.push_back(arr2[i]); return common; }'},
        {'question': 'What is the difference between map and unordered_map?', 'type': 'conceptual', 'answer': 'map maintains sorted order with O(log n) operations, unordered_map uses hash table with O(1) average operations.'},
        {'question': 'Which method is used to get the size of a vector?', 'type': 'mcq', 'options': ['size()', 'length()', 'count()', 'capacity()'], 'answer': 'size()'},
        {'question': 'Write a C++ class to implement a queue.', 'type': 'coding', 'answer': 'class Queue { private: list<int> items; public: void enqueue(int item) { items.push_back(item); } int dequeue() { if (items.empty()) return -1; int item = items.front(); items.pop_front(); return item; } bool isEmpty() { return items.empty(); } };'},
        {'question': 'What is the purpose of the this pointer?', 'type': 'conceptual', 'answer': 'this pointer points to the current object instance and is used to access members of the object.'},
        {'question': 'What is the output of: cout << string("C++").substr(1, 2);', 'type': 'mcq', 'options': ['++', 'C+', '+', 'Error'], 'answer': '++'},
        {'question': 'Write a C++ function to check if two strings are anagrams.', 'type': 'coding', 'answer': '#include <algorithm>; bool areAnagrams(string s1, string s2) { s1.erase(remove(s1.begin(), s1.end(), \' \'), s1.end()); s2.erase(remove(s2.begin(), s2.end(), \' \'), s2.end()); sort(s1.begin(), s1.end()); sort(s2.begin(), s2.end()); return s1 == s2; }'},
        {'question': 'What is the difference between abstract class and interface?', 'type': 'conceptual', 'answer': 'C++ uses abstract classes with pure virtual functions; interfaces are typically implemented as abstract classes with only pure virtual functions.'},
        {'question': 'Which keyword is used to prevent inheritance?', 'type': 'mcq', 'options': ['final', 'sealed', 'sealed class', 'no_inherit'], 'answer': 'final'},
        {'question': 'Write a C++ function to implement a linked list.', 'type': 'coding', 'answer': 'struct Node { int data; Node* next; Node(int val) : data(val), next(nullptr) {} }; class LinkedList { private: Node* head; public: LinkedList() : head(nullptr) {} void add(int data) { Node* newNode = new Node(data); if (!head) head = newNode; else { Node* current = head; while (current->next) current = current->next; current->next = newNode; } } };'},
        {'question': 'What is the purpose of the destructor (~ClassName())?', 'type': 'conceptual', 'answer': 'Destructor is called when an object is destroyed and is used to clean up resources and deallocate memory.'},
        {'question': 'What is the output of: cout << (int*)nullptr;', 'type': 'mcq', 'options': ['0', 'nullptr', 'Error', 'null'], 'answer': '0'},
        {'question': 'Write a C++ function to implement quick sort.', 'type': 'coding', 'answer': 'int partition(int arr[], int low, int high) { int pivot = arr[high]; int i = low - 1; for (int j = low; j < high; j++) if (arr[j] < pivot) { i++; swap(arr[i], arr[j]); } swap(arr[i + 1], arr[high]); return i + 1; } void quickSort(int arr[], int low, int high) { if (low < high) { int pi = partition(arr, low, high); quickSort(arr, low, pi - 1); quickSort(arr, pi + 1, high); } }'},
        {'question': 'What is the difference between pass by value and pass by reference?', 'type': 'conceptual', 'answer': 'Pass by value creates a copy, pass by reference allows modification of the original variable using &.'},
        {'question': 'Which header is needed for vector container?', 'type': 'mcq', 'options': ['<vector>', '<array>', '<list>', '<container>'], 'answer': '<vector>'},
        {'question': 'Write a C++ template function to find maximum of two values.', 'type': 'coding', 'answer': 'template <typename T> T max(T a, T b) { return (a > b) ? a : b; }'},
        {'question': 'What is the purpose of the friend keyword?', 'type': 'conceptual', 'answer': 'friend allows a function or class to access private and protected members of another class.'}
    ],
    'javascript': [
        {'question': 'What is the output of: console.log(typeof null);', 'type': 'mcq', 'options': ['object', 'null', 'undefined', 'string'], 'answer': 'object'},
        {'question': 'Write a JavaScript function to calculate factorial.', 'type': 'coding', 'answer': 'function factorial(n) { if (n <= 1) return 1; return n * factorial(n-1); }'},
        {'question': 'What is a closure in JavaScript?', 'type': 'conceptual', 'answer': 'A closure is a function that has access to variables in its outer scope'},
        {'question': 'How do you declare a constant in JavaScript?', 'type': 'mcq', 'options': ['const PI = 3.14;', 'var PI = 3.14;', 'let PI = 3.14;', 'constant PI = 3.14;'], 'answer': 'const PI = 3.14;'},
        {'question': 'Write a JavaScript function to reverse a string.', 'type': 'coding', 'answer': 'function reverseString(s) { return s.split(\'\').reverse().join(\'\'); }'},
        {'question': 'What is the difference between let and const?', 'type': 'conceptual', 'answer': 'let allows reassignment, const does not'},
        {'question': 'What is the output of: console.log([] == false);', 'type': 'mcq', 'options': ['true', 'false', 'undefined', 'error'], 'answer': 'true'},
        {'question': 'Write a JavaScript function to check if a number is prime.', 'type': 'coding', 'answer': 'function isPrime(n) { if (n < 2) return false; for (let i = 2; i <= Math.sqrt(n); i++) if (n % i === 0) return false; return true; }'},
        {'question': 'What is hoisting in JavaScript?', 'type': 'conceptual', 'answer': 'Hoisting is JavaScript\'s behavior of moving declarations to the top of their scope before code execution.'},
        {'question': 'Which method is used to add elements to the end of an array?', 'type': 'mcq', 'options': ['push()', 'pop()', 'shift()', 'unshift()'], 'answer': 'push()'},
        {'question': 'Write a JavaScript function to find the maximum element in an array.', 'type': 'coding', 'answer': 'function findMax(arr) { return Math.max(...arr); }'},
        {'question': 'What is the difference between == and ===?', 'type': 'conceptual', 'answer': '== performs type coercion, === checks for strict equality without type conversion.'},
        {'question': 'What is the output of: console.log("5" + 3);', 'type': 'mcq', 'options': ['53', '8', 'error', 'undefined'], 'answer': '53'},
        {'question': 'Write a JavaScript class representing a Person.', 'type': 'coding', 'answer': 'class Person { constructor(name, age) { this.name = name; this.age = age; } getName() { return this.name; } getAge() { return this.age; } }'},
        {'question': 'What is the event loop in JavaScript?', 'type': 'conceptual', 'answer': 'The event loop is a mechanism that handles asynchronous operations by continuously checking the call stack and task queue.'},
        {'question': 'Which keyword is used to handle errors?', 'type': 'mcq', 'options': ['try', 'catch', 'throw', 'error'], 'answer': 'try'},
        {'question': 'Write a JavaScript function to calculate Fibonacci series.', 'type': 'coding', 'answer': 'function fibonacci(n) { const fib = [0, 1]; for (let i = 2; i < n; i++) fib[i] = fib[i-1] + fib[i-2]; return fib.slice(0, n); }'},
        {'question': 'What is a promise in JavaScript?', 'type': 'conceptual', 'answer': 'A promise is an object representing the eventual completion or failure of an asynchronous operation.'},
        {'question': 'What is the output of: console.log(null == undefined);', 'type': 'mcq', 'options': ['true', 'false', 'undefined', 'error'], 'answer': 'true'},
        {'question': 'Write a JavaScript function to sort an array.', 'type': 'coding', 'answer': 'function sortArray(arr) { return arr.slice().sort((a, b) => a - b); }'},
        {'question': 'What is the difference between var, let, and const?', 'type': 'conceptual', 'answer': 'var is function-scoped and can be redeclared, let and const are block-scoped, const cannot be reassigned.'},
        {'question': 'Which method removes the last element from an array?', 'type': 'mcq', 'options': ['pop()', 'shift()', 'splice()', 'remove()'], 'answer': 'pop()'},
        {'question': 'Write a JavaScript function to check if a string is a palindrome.', 'type': 'coding', 'answer': 'function isPalindrome(s) { return s === s.split(\'\').reverse().join(\'\'); }'},
        {'question': 'What is the DOM in JavaScript?', 'type': 'conceptual', 'answer': 'The Document Object Model (DOM) represents the structure of HTML documents as a tree of objects that can be manipulated with JavaScript.'},
        {'question': 'What is the output of: console.log(typeof []);', 'type': 'mcq', 'options': ['object', 'array', 'undefined', 'string'], 'answer': 'object'},
        {'question': 'Write a JavaScript function to implement binary search.', 'type': 'coding', 'answer': 'function binarySearch(arr, target) { let left = 0, right = arr.length - 1; while (left <= right) { const mid = Math.floor((left + right) / 2); if (arr[mid] === target) return mid; if (arr[mid] < target) left = mid + 1; else right = mid - 1; } return -1; }'},
        {'question': 'What is arrow function syntax?', 'type': 'conceptual', 'answer': 'Arrow functions provide a concise syntax using =>, don\'t have their own this, and cannot be used as constructors.'},
        {'question': 'Which method creates a new array by calling a function on every element?', 'type': 'mcq', 'options': ['map()', 'forEach()', 'filter()', 'reduce()'], 'answer': 'map()'},
        {'question': 'Write a JavaScript function to remove duplicates from an array.', 'type': 'coding', 'answer': 'function removeDuplicates(arr) { return [...new Set(arr)]; }'},
        {'question': 'What is the difference between synchronous and asynchronous code?', 'type': 'conceptual', 'answer': 'Synchronous code executes sequentially and blocks execution, asynchronous code doesn\'t block and uses callbacks/promises.'},
        {'question': 'What is the output of: console.log(0.1 + 0.2 === 0.3);', 'type': 'mcq', 'options': ['false', 'true', 'undefined', 'error'], 'answer': 'false'},
        {'question': 'Write a JavaScript function to calculate GCD.', 'type': 'coding', 'answer': 'function gcd(a, b) { while (b !== 0) { [a, b] = [b, a % b]; } return a; }'},
        {'question': 'What is the difference between setTimeout and setInterval?', 'type': 'conceptual', 'answer': 'setTimeout executes once after delay, setInterval repeatedly executes at specified intervals.'},
        {'question': 'Which method filters an array based on a condition?', 'type': 'mcq', 'options': ['filter()', 'map()', 'find()', 'some()'], 'answer': 'filter()'},
        {'question': 'Write a JavaScript function to implement a stack.', 'type': 'coding', 'answer': 'class Stack { constructor() { this.items = []; } push(item) { this.items.push(item); } pop() { return this.items.pop(); } isEmpty() { return this.items.length === 0; } }'},
        {'question': 'What is the spread operator in JavaScript?', 'type': 'conceptual', 'answer': 'The spread operator (...) expands iterables into individual elements and can be used for array/object manipulation.'},
        {'question': 'What is the output of: console.log([1,2,3] + [4,5,6]);', 'type': 'mcq', 'options': ['1,2,34,5,6', '[1,2,3,4,5,6]', 'error', 'undefined'], 'answer': '1,2,34,5,6'},
        {'question': 'Write a JavaScript function to find common elements in two arrays.', 'type': 'coding', 'answer': 'function findCommon(arr1, arr2) { return arr1.filter(item => arr2.includes(item)); }'},
        {'question': 'What is destructuring in JavaScript?', 'type': 'conceptual', 'answer': 'Destructuring extracts values from arrays or objects into distinct variables using concise syntax.'},
        {'question': 'Which method reduces an array to a single value?', 'type': 'mcq', 'options': ['reduce()', 'map()', 'filter()', 'forEach()'], 'answer': 'reduce()'},
        {'question': 'Write a JavaScript function to implement a queue.', 'type': 'coding', 'answer': 'class Queue { constructor() { this.items = []; } enqueue(item) { this.items.push(item); } dequeue() { return this.items.shift(); } isEmpty() { return this.items.length === 0; } }'},
        {'question': 'What is the purpose of the async/await syntax?', 'type': 'conceptual', 'answer': 'async/await provides syntactic sugar for working with promises, making asynchronous code look synchronous.'},
        {'question': 'What is the output of: console.log(typeof function(){});', 'type': 'mcq', 'options': ['function', 'object', 'undefined', 'string'], 'answer': 'function'},
        {'question': 'Write a JavaScript function to validate email format.', 'type': 'coding', 'answer': 'function isValidEmail(email) { const regex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/; return regex.test(email); }'},
        {'question': 'What is the difference between call, apply, and bind?', 'type': 'conceptual', 'answer': 'call and apply invoke functions immediately with specific this, bind returns a new function with bound this.'},
        {'question': 'Which method checks if an element passes a test?', 'type': 'mcq', 'options': ['some()', 'every()', 'find()', 'includes()'], 'answer': 'some()'},
        {'question': 'Write a JavaScript function to implement quick sort.', 'type': 'coding', 'answer': 'function quickSort(arr) { if (arr.length <= 1) return arr; const pivot = arr[Math.floor(arr.length / 2)]; const left = arr.filter(x => x < pivot); const middle = arr.filter(x => x === pivot); const right = arr.filter(x => x > pivot); return [...quickSort(left), ...middle, ...quickSort(right)]; }'},
        {'question': 'What is the prototype in JavaScript?', 'type': 'conceptual', 'answer': 'Prototype is a mechanism for sharing properties and methods between objects, enabling inheritance.'},
        {'question': 'What is the output of: console.log(parseInt("10px"));', 'type': 'mcq', 'options': ['10', 'NaN', 'error', 'undefined'], 'answer': '10'},
        {'question': 'Write a JavaScript function to check if two strings are anagrams.', 'type': 'coding', 'answer': 'function areAnagrams(s1, s2) { const normalize = str => str.replace(/\\s/g, \'\').toLowerCase().split(\'\').sort().join(\'\'); return normalize(s1) === normalize(s2); }'},
        {'question': 'What is the difference between null and undefined?', 'type': 'conceptual', 'answer': 'null is an intentional absence of value, undefined means a variable has been declared but not assigned a value.'},
        {'question': 'Which method converts JSON string to object?', 'type': 'mcq', 'options': ['JSON.parse()', 'JSON.stringify()', 'JSON.toObject()', 'JSON.from()'], 'answer': 'JSON.parse()'},
        {'question': 'Write a JavaScript function to implement a linked list.', 'type': 'coding', 'answer': 'class Node { constructor(data) { this.data = data; this.next = null; } } class LinkedList { constructor() { this.head = null; } add(data) { const newNode = new Node(data); if (!this.head) this.head = newNode; else { let current = this.head; while (current.next) current = current.next; current.next = newNode; } } }'},
        {'question': 'What is the purpose of the this keyword?', 'type': 'conceptual', 'answer': 'this refers to the context in which a function is executed, varying based on how the function is called.'}
    ],
    'sql': [
        {'question': 'What is the output of: SELECT 2 + 3;', 'type': 'mcq', 'options': ['5', '2', '3', '23'], 'answer': '5'},
        {'question': 'Write an SQL query to find all employees from the employees table.', 'type': 'coding', 'answer': 'SELECT * FROM employees;'},
        {'question': 'What is a primary key in SQL?', 'type': 'conceptual', 'answer': 'A primary key uniquely identifies each record in a table'},
        {'question': 'Which clause is used to filter results in SQL?', 'type': 'mcq', 'options': ['WHERE', 'FILTER', 'HAVING', 'GROUP BY'], 'answer': 'WHERE'},
        {'question': 'Write an SQL query to count employees in each department.', 'type': 'coding', 'answer': 'SELECT department, COUNT(*) FROM employees GROUP BY department;'},
        {'question': 'What is the difference between INNER JOIN and LEFT JOIN?', 'type': 'conceptual', 'answer': 'INNER JOIN returns matching rows, LEFT JOIN returns all rows from left table'},
        {'question': 'What is the output of: SELECT CONCAT(\'Hello\', \'World\');', 'type': 'mcq', 'options': ['HelloWorld', 'Hello World', 'Hello,World', 'Error'], 'answer': 'HelloWorld'},
        {'question': 'Write an SQL query to find employees with salary > 50000.', 'type': 'coding', 'answer': 'SELECT * FROM employees WHERE salary > 50000;'},
        {'question': 'What is a foreign key in SQL?', 'type': 'conceptual', 'answer': 'A foreign key is a field that links two tables together by referencing the primary key of another table.'},
        {'question': 'Which function is used to get the current date?', 'type': 'mcq', 'options': ['GETDATE()', 'CURRENT_DATE()', 'NOW()', 'DATE()'], 'answer': 'GETDATE()'},
        {'question': 'Write an SQL query to find the second highest salary.', 'type': 'coding', 'answer': 'SELECT MAX(salary) FROM employees WHERE salary < (SELECT MAX(salary) FROM employees);'},
        {'question': 'What is normalization in SQL?', 'type': 'conceptual', 'answer': 'Normalization is the process of organizing data in a database to reduce redundancy and improve data integrity.'},
        {'question': 'What is the output of: SELECT LENGTH(\'SQL\');', 'type': 'mcq', 'options': ['3', '4', '2', 'Error'], 'answer': '3'},
        {'question': 'Write an SQL query to update employee salary.', 'type': 'coding', 'answer': 'UPDATE employees SET salary = 60000 WHERE employee_id = 101;'},
        {'question': 'What is the difference between DELETE and TRUNCATE?', 'type': 'conceptual', 'answer': 'DELETE removes rows one by one and logs each deletion, TRUNCATE removes all rows at once and doesn\'t log individual row deletions.'},
        {'question': 'Which clause sorts the result set?', 'type': 'mcq', 'options': ['ORDER BY', 'SORT BY', 'GROUP BY', 'ARRANGE BY'], 'answer': 'ORDER BY'},
        {'question': 'Write an SQL query to find duplicate records.', 'type': 'coding', 'answer': 'SELECT column_name, COUNT(*) FROM table_name GROUP BY column_name HAVING COUNT(*) > 1;'},
        {'question': 'What is an index in SQL?', 'type': 'conceptual', 'answer': 'An index is a database object that improves the speed of data retrieval operations on a table.'},
        {'question': 'What is the output of: SELECT UPPER(\'sql\');', 'type': 'mcq', 'options': ['SQL', 'sql', 'Sql', 'Error'], 'answer': 'SQL'},
        {'question': 'Write an SQL query to create a table.', 'type': 'coding', 'answer': 'CREATE TABLE employees (id INT PRIMARY KEY, name VARCHAR(50), salary DECIMAL(10,2));'},
        {'question': 'What is the difference between CHAR and VARCHAR?', 'type': 'conceptual', 'answer': 'CHAR has fixed length, VARCHAR has variable length. CHAR pads with spaces, VARCHAR doesn\'t.'},
        {'question': 'Which operator is used for pattern matching?', 'type': 'mcq', 'options': ['LIKE', 'MATCH', 'PATTERN', 'REGEX'], 'answer': 'LIKE'},
        {'question': 'Write an SQL query to find employees hired in last 30 days.', 'type': 'coding', 'answer': 'SELECT * FROM employees WHERE hire_date >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY);'},
        {'question': 'What is a transaction in SQL?', 'type': 'conceptual', 'answer': 'A transaction is a sequence of operations performed as a single logical unit of work, following ACID properties.'},
        {'question': 'What is the output of: SELECT MOD(10, 3);', 'type': 'mcq', 'options': ['1', '3', '0', '10'], 'answer': '1'},
        {'question': 'Write an SQL query to find the average salary by department.', 'type': 'coding', 'answer': 'SELECT department, AVG(salary) FROM employees GROUP BY department;'},
        {'question': 'What is the difference between HAVING and WHERE?', 'type': 'conceptual', 'answer': 'WHERE filters rows before grouping, HAVING filters groups after aggregation.'},
        {'question': 'Which function counts all rows including NULL?', 'type': 'mcq', 'options': ['COUNT(*)', 'COUNT(column)', 'COUNT_ALL()', 'TOTAL()'], 'answer': 'COUNT(*)'},
        {'question': 'Write an SQL query to find employees without managers.', 'type': 'coding', 'answer': 'SELECT * FROM employees WHERE manager_id IS NULL;'},
        {'question': 'What is a view in SQL?', 'type': 'conceptual', 'answer': 'A view is a virtual table based on the result-set of an SQL statement, containing rows and columns like a real table.'},
        {'question': 'What is the output of: SELECT SUBSTRING(\'Database\', 1, 4);', 'type': 'mcq', 'options': ['Data', 'Base', 'Data', 'Error'], 'answer': 'Data'},
        {'question': 'Write an SQL query to delete a table.', 'type': 'coding', 'answer': 'DROP TABLE table_name;'},
        {'question': 'What is the difference between UNION and UNION ALL?', 'type': 'conceptual', 'answer': 'UNION removes duplicate rows, UNION ALL includes all rows including duplicates.'},
        {'question': 'Which constraint ensures unique values?', 'type': 'mcq', 'options': ['UNIQUE', 'PRIMARY KEY', 'DISTINCT', 'CHECK'], 'answer': 'UNIQUE'},
        {'question': 'Write an SQL query to find the third highest salary.', 'type': 'coding', 'answer': 'SELECT DISTINCT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 2;'},
        {'question': 'What is a stored procedure in SQL?', 'type': 'conceptual', 'answer': 'A stored procedure is a prepared SQL code that you can save and reuse multiple times.'},
        {'question': 'What is the output of: SELECT COALESCE(NULL, \'Default\', NULL, \'Value\');', 'type': 'mcq', 'options': ['Default', 'Value', 'NULL', 'Error'], 'answer': 'Default'},
        {'question': 'Write an SQL query to add a column to a table.', 'type': 'coding', 'answer': 'ALTER TABLE employees ADD COLUMN phone VARCHAR(20);'},
        {'question': 'What is the difference between clustered and non-clustered index?', 'type': 'conceptual', 'answer': 'Clustered index determines physical order of data, non-clustered index is separate structure pointing to data.'},
        {'question': 'Which function returns the first non-null value?', 'type': 'mcq', 'options': ['COALESCE()', 'ISNULL()', 'NULLIF()', 'FIRST_VALUE()'], 'answer': 'COALESCE()'},
        {'question': 'Write an SQL query to find employees with names starting with \'J\'.', 'type': 'coding', 'answer': 'SELECT * FROM employees WHERE name LIKE \'J%\';'},
        {'question': 'What is a trigger in SQL?', 'type': 'conceptual', 'answer': 'A trigger is a stored procedure that automatically executes when an event occurs in the database.'},
        {'question': 'What is the output of: SELECT ROUND(3.14159, 2);', 'type': 'mcq', 'options': ['3.14', '3.15', '3.1', 'Error'], 'answer': '3.14'},
        {'question': 'Write an SQL query to create an index.', 'type': 'coding', 'answer': 'CREATE INDEX idx_name ON employees(name);'},
        {'question': 'What is the difference between CROSS JOIN and INNER JOIN?', 'type': 'conceptual', 'answer': 'CROSS JOIN returns Cartesian product of tables, INNER JOIN returns only matching rows.'},
        {'question': 'Which clause limits the number of rows returned?', 'type': 'mcq', 'options': ['LIMIT', 'TOP', 'ROWNUM', 'FIRST'], 'answer': 'LIMIT'},
        {'question': 'Write an SQL query to find the Nth highest salary.', 'type': 'coding', 'answer': 'SELECT DISTINCT salary FROM employees e1 WHERE N-1 = (SELECT COUNT(DISTINCT salary) FROM employees e2 WHERE e2.salary > e1.salary);'},
        {'question': 'What is a cursor in SQL?', 'type': 'conceptual', 'answer': 'A cursor is a database object that allows row-by-row manipulation of result sets.'},
        {'question': 'What is the output of: SELECT REPLACE(\'Hello World\', \'World\', \'SQL\');', 'type': 'mcq', 'options': ['Hello SQL', 'Hello World', 'SQL', 'Error'], 'answer': 'Hello SQL'},
        {'question': 'Write an SQL query to backup a table.', 'type': 'coding', 'answer': 'CREATE TABLE employees_backup AS SELECT * FROM employees;'},
        {'question': 'What is the difference between RANK() and DENSE_RANK()?', 'type': 'conceptual', 'answer': 'RANK() leaves gaps in ranking after ties, DENSE_RANK() doesn\'t leave gaps.'},
        {'question': 'Which function returns the current user?', 'type': 'mcq', 'options': ['USER()', 'CURRENT_USER()', 'SESSION_USER()', 'GETUSER()'], 'answer': 'USER()'},
        {'question': 'Write an SQL query to pivot rows to columns.', 'type': 'coding', 'answer': 'SELECT * FROM (SELECT department, salary FROM employees) PIVOT (AVG(salary) FOR department IN ([\'Sales\'], [\'IT\'], [\'HR\'])) AS p;'},
        {'question': 'What is the difference between OLTP and OLAP?', 'type': 'conceptual', 'answer': 'OLTP handles transactional processing, OLAP handles analytical processing and reporting.'},
        {'question': 'Which aggregate function ignores NULL values?', 'type': 'mcq', 'options': ['COUNT(column)', 'COUNT(*)', 'SUM(ALL column)', 'AVG(ALL column)'], 'answer': 'COUNT(column)'},
        {'question': 'Write an SQL query to implement row-level security.', 'type': 'coding', 'answer': 'CREATE SECURITY POLICY policy_name ADD FILTER PREDICATE schema.function_name(column) ON table_name;'},
        {'question': 'What is a deadlock in SQL?', 'type': 'conceptual', 'answer': 'A deadlock occurs when two or more transactions are waiting for each other to release locks, preventing progress.'}
    ],
    'web': [
        {'question': 'What is the purpose of the <div> tag in HTML?', 'type': 'mcq', 'options': ['Division', 'Section', 'Container', 'Block'], 'answer': 'Division'},
        {'question': 'Write CSS to make text red and bold.', 'type': 'coding', 'answer': 'color: red; font-weight: bold;'},
        {'question': 'What is responsive web design?', 'type': 'conceptual', 'answer': 'Responsive design adapts layout to different screen sizes'},
        {'question': 'Which CSS property is used to change the background color?', 'type': 'mcq', 'options': ['background-color', 'color', 'background', 'background-image'], 'answer': 'background-color'},
        {'question': 'Write HTML to create a link.', 'type': 'coding', 'answer': '<a href=\'url\'>Link text</a>'},
        {'question': 'What is the difference between padding and margin in CSS?', 'type': 'conceptual', 'answer': 'Padding is inside the element, margin is outside'},
        {'question': 'What is the purpose of the <span> tag?', 'type': 'mcq', 'options': ['Inline container', 'Block element', 'Table row', 'List item'], 'answer': 'Inline container'},
        {'question': 'Write CSS to center text horizontally.', 'type': 'coding', 'answer': 'text-align: center;'},
        {'question': 'What is the DOM in web development?', 'type': 'conceptual', 'answer': 'Document Object Model represents the structure of HTML documents as a tree of objects.'},
        {'question': 'Which HTML5 element is used for navigation?', 'type': 'mcq', 'options': ['<nav>', '<navigation>', '<menu>', '<navbar>'], 'answer': '<nav>'},
        {'question': 'Write CSS to create a flex container.', 'type': 'coding', 'answer': 'display: flex;'},
        {'question': 'What is the difference between block and inline elements?', 'type': 'conceptual', 'answer': 'Block elements take full width and start on new lines, inline elements only take needed space and don\'t start new lines.'},
        {'question': 'Which CSS property controls text size?', 'type': 'mcq', 'options': ['font-size', 'text-size', 'size', 'font-scale'], 'answer': 'font-size'},
        {'question': 'Write HTML to create an image.', 'type': 'coding', 'answer': '<img src="image.jpg" alt="Description">'},
        {'question': 'What is CSS specificity?', 'type': 'conceptual', 'answer': 'CSS specificity determines which CSS rule is applied when multiple rules target the same element.'},
        {'question': 'What is the purpose of the <header> tag?', 'type': 'mcq', 'options': ['Page header', 'Document title', 'Meta data', 'Navigation'], 'answer': 'Page header'},
        {'question': 'Write CSS to add a border.', 'type': 'coding', 'answer': 'border: 1px solid black;'},
        {'question': 'What is the box model in CSS?', 'type': 'conceptual', 'answer': 'The box model consists of content, padding, border, and margin that surround every HTML element.'},
        {'question': 'Which CSS property changes text color?', 'type': 'mcq', 'options': ['color', 'text-color', 'font-color', 'foreground'], 'answer': 'color'},
        {'question': 'Write HTML to create a form.', 'type': 'coding', 'answer': '<form action="/submit" method="post"><input type="text" name="username"><input type="submit" value="Submit"></form>'},
        {'question': 'What is semantic HTML?', 'type': 'conceptual', 'answer': 'Semantic HTML uses HTML elements according to their intended purpose and meaning, improving accessibility and SEO.'},
        {'question': 'What is the purpose of the <footer> tag?', 'type': 'mcq', 'options': ['Page footer', 'Copyright', 'Links', 'End of document'], 'answer': 'Page footer'},
        {'question': 'Write CSS to create a grid layout.', 'type': 'coding', 'answer': 'display: grid; grid-template-columns: 1fr 1fr;'},
        {'question': 'What is the difference between relative and absolute positioning?', 'type': 'conceptual', 'answer': 'Relative positioning moves element relative to its normal position, absolute positioning moves element relative to its nearest positioned ancestor.'},
        {'question': 'Which CSS property adds shadow to text?', 'type': 'mcq', 'options': ['text-shadow', 'shadow', 'font-shadow', 'drop-shadow'], 'answer': 'text-shadow'},
        {'question': 'Write HTML to create a table.', 'type': 'coding', 'answer': '<table><tr><th>Header</th></tr><tr><td>Data</td></tr></table>'},
        {'question': 'What is CSS Grid?', 'type': 'conceptual', 'answer': 'CSS Grid is a two-dimensional layout system for creating complex web layouts with rows and columns.'},
        {'question': 'What is the purpose of the <main> tag?', 'type': 'mcq', 'options': ['Main content', 'Primary section', 'Container', 'Wrapper'], 'answer': 'Main content'},
        {'question': 'Write CSS to make an element round.', 'type': 'coding', 'answer': 'border-radius: 50%;'},
        {'question': 'What is the difference between em and rem units?', 'type': 'conceptual', 'answer': 'em is relative to parent element font size, rem is relative to root element font size.'},
        {'question': 'Which CSS property controls element transparency?', 'type': 'mcq', 'options': ['opacity', 'transparency', 'alpha', 'visible'], 'answer': 'opacity'},
        {'question': 'Write HTML to embed a video.', 'type': 'coding', 'answer': '<video controls><source src="video.mp4" type="video/mp4"></video>'},
        {'question': 'What are CSS pseudo-classes?', 'type': 'conceptual', 'answer': 'Pseudo-classes are keywords added to selectors that specify a special state of the element, like :hover or :active.'},
        {'question': 'What is the purpose of the <section> tag?', 'type': 'mcq', 'options': ['Content section', 'Division', 'Container', 'Article'], 'answer': 'Content section'},
        {'question': 'Write CSS to add transition effect.', 'type': 'coding', 'answer': 'transition: all 0.3s ease;'},
        {'question': 'What is the difference between display: none and visibility: hidden?', 'type': 'conceptual', 'answer': 'display: none removes element from layout, visibility: hidden hides element but maintains its space.'},
        {'question': 'Which CSS property creates rounded corners?', 'type': 'mcq', 'options': ['border-radius', 'corner-radius', 'round', 'border-corner'], 'answer': 'border-radius'},
        {'question': 'Write HTML to create a dropdown menu.', 'type': 'coding', 'answer': '<select><option value="1">Option 1</option><option value="2">Option 2</option></select>'},
        {'question': 'What is CSS Flexbox?', 'type': 'conceptual', 'answer': 'Flexbox is a one-dimensional layout method for arranging items in rows or columns, providing flexible alignment and distribution.'},
        {'question': 'What is the purpose of the <article> tag?', 'type': 'mcq', 'options': ['Independent content', 'Blog post', 'News', 'Story'], 'answer': 'Independent content'},
        {'question': 'Write CSS to create hover effect.', 'type': 'coding', 'answer': '.element:hover { transform: scale(1.1); }'},
        {'question': 'What is the difference between margin and padding?', 'type': 'conceptual', 'answer': 'Margin is outside the border, padding is inside the border between content and border.'},
        {'question': 'Which CSS property changes cursor style?', 'type': 'mcq', 'options': ['cursor', 'pointer', 'mouse', 'arrow'], 'answer': 'cursor'},
        {'question': 'Write HTML to create a button.', 'type': 'coding', 'answer': '<button type="button">Click me</button>'},
        {'question': 'What are CSS media queries?', 'type': 'conceptual', 'answer': 'Media queries allow applying different CSS styles based on device characteristics like screen size, orientation, or resolution.'},
        {'question': 'What is the purpose of the <aside> tag?', 'type': 'mcq', 'options': ['Sidebar content', 'Advertisement', 'Notes', 'Extra info'], 'answer': 'Sidebar content'},
        {'question': 'Write CSS to create gradient background.', 'type': 'coding', 'answer': 'background: linear-gradient(to right, #ff0000, #0000ff);'},
        {'question': 'What is the difference between inline and block CSS?', 'type': 'conceptual', 'answer': 'Inline CSS is applied directly to HTML elements, block CSS is defined in style blocks or external files.'},
        {'question': 'Which CSS property adds shadow to elements?', 'type': 'mcq', 'options': ['box-shadow', 'shadow', 'element-shadow', 'drop-shadow'], 'answer': 'box-shadow'},
        {'question': 'Write HTML to create an input field.', 'type': 'coding', 'answer': '<input type="text" placeholder="Enter text">'},
        {'question': 'What is CSS inheritance?', 'type': 'conceptual', 'answer': 'CSS inheritance is when child elements inherit property values from their parent elements.'},
        {'question': 'What is the purpose of the <figure> tag?', 'type': 'mcq', 'options': ['Figure with caption', 'Image', 'Diagram', 'Illustration'], 'answer': 'Figure with caption'},
        {'question': 'Write CSS to create animation.', 'type': 'coding', 'answer': '@keyframes slide { from { transform: translateX(0); } to { transform: translateX(100px); } } .element { animation: slide 2s infinite; }'},
        {'question': 'What is the difference between class and ID selectors?', 'type': 'conceptual', 'answer': 'Class selectors can be reused on multiple elements, ID selectors must be unique and can only be used once.'},
        {'question': 'Which CSS property controls element stacking?', 'type': 'mcq', 'options': ['z-index', 'stack', 'layer', 'order'], 'answer': 'z-index'},
        {'question': 'Write HTML to create a list.', 'type': 'coding', 'answer': '<ul><li>Item 1</li><li>Item 2</li></ul>'},
        {'question': 'What is responsive design?', 'type': 'conceptual', 'answer': 'Responsive design creates web layouts that adapt to different screen sizes and devices using flexible grids, images, and CSS media queries.'},
        {'question': 'What is the purpose of the <meta> tag?', 'type': 'mcq', 'options': ['Metadata', 'Media', 'Math', 'Method'], 'answer': 'Metadata'},
        {'question': 'Write CSS to create sticky positioning.', 'type': 'coding', 'answer': 'position: sticky; top: 0;'},
        {'question': 'What is the difference between px and em units?', 'type': 'conceptual', 'answer': 'px is absolute unit (pixels), em is relative unit based on parent element font size.'},
        {'question': 'Which CSS property transforms elements?', 'type': 'mcq', 'options': ['transform', 'transition', 'animation', 'modify'], 'answer': 'transform'},
        {'question': 'Write HTML to create a heading.', 'type': 'coding', 'answer': '<h1>Main Title</h1>'},
        {'question': 'What are CSS custom properties?', 'type': 'conceptual', 'answer': 'CSS custom properties (variables) allow storing values that can be reused throughout the stylesheet using --var-name syntax.'}
    ]
}

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# MongoDB setup
client = MongoClient(os.getenv('MONGO_URI'))
db = client.ai_interview

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'  # Redirect to index page instead of non-existent 'login' endpoint

# Dataset Manager setup
dataset_manager = DatasetManager()

# Groq client
# Initialize Groq client with user's API key
try:
    groq_client = groq.Groq(api_key=os.getenv('GROQ_API_KEY'))
    print("✅ Groq client initialized successfully")
    # Initialize enhanced AI scorer
    try:
        enhanced_scorer = EnhancedAIScorer(groq_client)
        print("✅ Enhanced AI Scorer initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize Enhanced AI Scorer: {e}")
        enhanced_scorer = None
except Exception as e:
    print(f"Warning: Could not initialize Groq client: {e}")
    groq_client = None
    enhanced_scorer = None

class User(UserMixin):
    def __init__(self, user_data, user_type):
        self.id = str(user_data['_id'])
        self.email = user_data['email']
        self.name = user_data['name']
        self.user_type = user_type
        self.data = user_data

@login_manager.user_loader
def load_user(user_id):
    # Check if user is company
    company_data = db.companies.find_one({'_id': ObjectId(user_id)})
    if company_data:
        return User(company_data, 'company')
    
    # Check if user is student
    student_data = db.students.find_one({'_id': ObjectId(user_id)})
    if student_data:
        return User(student_data, 'student')
    
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check-email')
def check_email():
    """Check if email already exists"""
    email = request.args.get('email')
    user_type = request.args.get('type')  # 'company' or 'student'
    
    if not email:
        return jsonify({'exists': False, 'message': 'Invalid email'})
    
    # Check in both collections
    existing_company = db.companies.find_one({'email': email})
    existing_student = db.students.find_one({'email': email})
    
    if existing_company and existing_student:
        return jsonify({'exists': True, 'message': 'Email already registered as both company and student'})
    elif existing_company:
        return jsonify({'exists': True, 'message': 'Email already registered as a company'})
    elif existing_student:
        return jsonify({'exists': True, 'message': 'Email already registered as a student'})
    else:
        return jsonify({'exists': False, 'message': 'Email available'})

@app.route('/company/signup', methods=['GET', 'POST'])
def company_signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        company_size = request.form.get('company_size')
        industry = request.form.get('industry')
        description = request.form.get('description')
        
        # Check if email already exists in either companies or students collection
        existing_company = db.companies.find_one({'email': email})
        existing_student = db.students.find_one({'email': email})
        
        if existing_company:
            flash('This email is already registered as a company. Please use a different email or login.', 'error')
            return redirect(url_for('company_signup'))
        
        if existing_student:
            flash('This email is already registered as a student. Please use a different email or login.', 'error')
            return redirect(url_for('company_signup'))
        
        # Create new company
        company = {
            'name': name,
            'email': email,
            'password': generate_password_hash(password),
            'company_size': company_size,
            'industry': industry,
            'description': description,
            'created_at': datetime.now()
        }
        
        db.companies.insert_one(company)
        flash('Company registered successfully', 'success')
        return redirect(url_for('company_login'))
    
    return render_template('company/signup.html')

@app.route('/company/login', methods=['GET', 'POST'])
def company_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        company = db.companies.find_one({'email': email})
        if company and check_password_hash(company['password'], password):
            user = User(company, 'company')
            login_user(user)
            return redirect(url_for('company_dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('company/login.html')

@app.route('/student/signup', methods=['GET', 'POST'])
def student_signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        education = request.form.get('education')
        skills = request.form.get('skills')
        
        print(f"Student registration attempt: {name}, {email}")
        
        # Check if email already exists in either students or companies collection
        existing_student = db.students.find_one({'email': email})
        existing_company = db.companies.find_one({'email': email})
        
        print(f"Existing student: {existing_student is not None}")
        print(f"Existing company: {existing_company is not None}")
        
        if existing_student:
            flash('This email is already registered as a student. Please use a different email or login.', 'error')
            return redirect(url_for('student_signup'))
        
        if existing_company:
            flash('This email is already registered as a company. Please use a different email or login.', 'error')
            return redirect(url_for('student_signup'))
        
        # Create new student
        student = {
            'name': name,
            'email': email,
            'password': generate_password_hash(password),
            'phone': phone,
            'education': education,
            'skills': skills,
            'created_at': datetime.now()
        }
        
        print(f"Creating student: {student}")
        db.students.insert_one(student)
        print(f"Student created successfully, redirecting to login")
        flash('Student registered successfully', 'success')
        return redirect(url_for('student_login'))
    
    return render_template('student/signup.html')

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        print(f"Student login attempt: {email}")
        
        student = db.students.find_one({'email': email})
        print(f"Student found: {student is not None}")
        
        if student and check_password_hash(student['password'], password):
            print(f"Password correct, logging in student")
            user = User(student, 'student')
            login_user(user)
            print(f"Student logged in, redirecting to dashboard")
            return redirect(url_for('student_dashboard'))
        else:
            print(f"Invalid credentials")
            flash('Invalid email or password', 'error')
    
    return render_template('student/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/company/dashboard')
@login_required
def company_dashboard():
    if current_user.user_type != 'company':
        return redirect(url_for('index'))
    
    # Get company's posted jobs
    jobs = list(db.jobs.find({'company_id': current_user.id}))
    return render_template('company/dashboard.html', jobs=jobs)

@app.route('/company/upload_dataset', methods=['GET', 'POST'])
@login_required
def upload_dataset():
    if current_user.user_type != 'company':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        domain = request.form.get('domain')
        upload_format = request.form.get('upload_format', 'json')
        
        try:
            dataset = None
            
            if upload_format == 'json':
                # Handle JSON upload
                dataset_json = request.form.get('dataset')
                dataset = json.loads(dataset_json)
            elif upload_format == 'csv':
                # Handle CSV file upload
                if 'csv_file' not in request.files:
                    flash('No CSV file selected', 'error')
                    return redirect(url_for('upload_dataset'))
                
                file = request.files['csv_file']
                if file.filename == '':
                    flash('No file selected', 'error')
                    return redirect(url_for('upload_dataset'))
                
                if file and file.filename.endswith('.csv'):
                    # Read CSV file
                    stream = io.StringIO(file.stream.read().decode("utf8"))
                    df = pd.read_csv(stream)
                    
                    # Convert CSV to dataset format
                    dataset = convert_csv_to_dataset(df, request.form.get('csv_question_col', 'question'), 
                                                   request.form.get('csv_answer_col', 'answer'))
                else:
                    flash('Please upload a CSV file', 'error')
                    return redirect(url_for('upload_dataset'))
            
            # Use dataset manager to upload and train
            success, message = dataset_manager.upload_dataset(
                current_user.id, 
                domain, 
                dataset
            )
            
            if success:
                flash(message, 'success')
                return redirect(url_for('company_dashboard'))
            else:
                flash(message, 'error')
                
        except json.JSONDecodeError:
            flash('Invalid JSON format', 'error')
        except Exception as e:
            flash(f'Error uploading dataset: {str(e)}', 'error')
    
    return render_template('company/upload_dataset.html')

def convert_csv_to_dataset(df, question_col, answer_col):
    """Convert CSV DataFrame to dataset format"""
    questions = []
    
    for index, row in df.iterrows():
        if pd.notna(row.get(question_col)) and pd.notna(row.get(answer_col)):
            questions.append({
                'question': str(row[question_col]).strip(),
                'answer': str(row[answer_col]).strip()
            })
    
    return {'questions': questions}

@app.route('/company/post_job', methods=['GET', 'POST'])
@login_required
def post_job():
    if current_user.user_type != 'company':
        return redirect(url_for('index'))
    
    # Get all available datasets for showing in form (not just company-specific)
    all_datasets = list(db.datasets.find({'is_active': True}))
    company_datasets = list(db.datasets.find({'company_id': current_user.id}))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        requirements = request.form.get('requirements')
        domains = request.form.getlist('domains')
        duration = int(request.form.get('duration', 30))
        difficulty = request.form.get('difficulty')
        cutoff_score = int(request.form.get('cutoff_score', 70))
        
        # Automatically use datasets - no checkbox needed
        use_dataset = True  # Always use datasets now
        
        job = {
            'company_id': current_user.id,
            'company_name': current_user.name,
            'title': title,
            'description': description,
            'requirements': requirements,
            'domains': domains,
            'duration': duration,
            'difficulty': difficulty,
            'cutoff_score': cutoff_score,
            'use_dataset': use_dataset,
            'created_at': datetime.now(),
            'status': 'active'
        }
        
        db.jobs.insert_one(job)
        flash('Job posted successfully', 'success')
        return redirect(url_for('company_dashboard'))
    
    return render_template('company/post_job.html', datasets=all_datasets)

@app.route('/company/edit_job/<job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    if current_user.user_type != 'company':
        return redirect(url_for('index'))
    
    job = db.jobs.find_one({'_id': ObjectId(job_id)})
    if not job or job['company_id'] != current_user.id:
        flash('Job not found', 'error')
        return redirect(url_for('company_dashboard'))
    
    if request.method == 'POST':
        # Update job details
        title = request.form.get('title')
        description = request.form.get('description')
        requirements = request.form.get('requirements')
        domains = request.form.getlist('domains')
        duration = int(request.form.get('duration', 30))
        difficulty = request.form.get('difficulty')
        cutoff_score = int(request.form.get('cutoff_score', 70))
        
        # Update job
        db.jobs.update_one(
            {'_id': ObjectId(job_id)},
            {'$set': {
                'title': title,
                'description': description,
                'requirements': requirements,
                'domains': domains,
                'duration': duration,
                'difficulty': difficulty,
                'cutoff_score': cutoff_score,
                'updated_at': datetime.now()
            }}
        )
        
        flash('Job updated successfully', 'success')
        return redirect(url_for('company_dashboard'))
    
    # Get all available datasets for showing in form
    all_datasets = list(db.datasets.find({'is_active': True}))
    
    return render_template('company/edit_job.html', job=job, datasets=all_datasets)

@app.route('/company/delete_job/<job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    if current_user.user_type != 'company':
        return redirect(url_for('index'))
    
    job = db.jobs.find_one({'_id': ObjectId(job_id)})
    if not job or job['company_id'] != current_user.id:
        flash('Job not found', 'error')
        return redirect(url_for('company_dashboard'))
    
    # Check if there are any exam results for this job
    exam_results = db.exam_results.count_documents({'job_id': job_id})
    
  
    # Delete the job
    db.jobs.delete_one({'_id': ObjectId(job_id)})
    flash('Job deleted successfully', 'success')
    return redirect(url_for('company_dashboard'))

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    print(f"Student dashboard accessed by user: {current_user.id}, type: {current_user.user_type}")
    
    if current_user.user_type != 'student':
        print(f"User type mismatch: {current_user.user_type} != student")
        return redirect(url_for('index'))
    
    print(f"User type verified: student")
    
    # Get all available jobs
    try:
        jobs = list(db.jobs.find({'status': 'active'}))
        print(f"Student dashboard: Found {len(jobs)} active jobs")
        
        # Debug job IDs
        for job in jobs:
            print(f"Job ID: {str(job['_id'])}, Title: {job.get('title', 'No title')}")
        
        # Get student's exam results
        results = list(db.exam_results.find({'student_id': current_user.id}))
        print(f"Found {len(results)} exam results for student")
        
        print(f"Rendering student dashboard template")
        return render_template('student/dashboard.html', jobs=jobs, results=results)
        
    except Exception as e:
        print(f"Error in student dashboard: {e}")
        flash('Error loading dashboard', 'error')
        return redirect(url_for('index'))

@app.route('/student/exam/<job_id>')
@login_required
def take_exam(job_id):
    if current_user.user_type != 'student':
        return redirect(url_for('index'))
    
    print(f"Student {current_user.id} trying to take exam for job {job_id}")
    
    job = db.jobs.find_one({'_id': ObjectId(job_id)})
    if not job:
        print(f"Job {job_id} not found")
        flash('Job not found', 'error')
        return redirect(url_for('student_dashboard'))
    
    print(f"Job found: {job.get('title', 'No title')}")
    
    # Check if student already took this exam
    existing_result = db.exam_results.find_one({
        'student_id': current_user.id,
        'job_id': job_id
    })
    
    if existing_result:
        print(f"Student already took this exam on {existing_result.get('submitted_at')}")
        flash('You have already taken this exam', 'error')
        return redirect(url_for('student_dashboard'))
    
    print(f"Student has not taken this exam yet")
    
    # Always use mixed_questions for testing (comment out dataset logic)
    domain_for_exam = job['domains'][0] if job['domains'] else 'python'
    print(f"Using mixed questions for {domain_for_exam} domain")
    questions = get_mixed_questions(domain_for_exam)
    dataset = None  # Set dataset to None since we're not using it
    
    # OLD DATASET LOGIC (temporarily disabled for testing):
    # # Always prioritize uploaded datasets - check all available datasets
    # questions = []
    # domain_for_exam = job['domains'][0] if job['domains'] else 'python'
    # print(f"Using domain: {domain_for_exam}")
    # 
    # # Try to get company-specific dataset first
    # try:
    #     dataset = dataset_manager.get_dataset(job['company_id'], domain_for_exam)
    #     print(f"Company dataset result: {dataset is not None}")
    #     if dataset:
    #         print(f"Using company-specific dataset for {domain_for_exam}")
    #     else:
    #         print(f"No company-specific dataset found for {domain_for_exam}")
    # except Exception as e:
    #     print(f"Error getting company dataset: {e}")
    #     dataset = None
    # 
    # # If no company dataset, try to get any active dataset for this domain
    # if not dataset:
    #     try:
    #         any_dataset = db.datasets.find_one({
    #             'domain': domain_for_exam,
    #             'is_active': True
    #         })
    #         if any_dataset:
    #             dataset = any_dataset
    #             print(f"Using public dataset for {domain_for_exam}")
    #         else:
    #             print(f"No public dataset found for {domain_for_exam}")
    #     except Exception as e:
    #         print(f"Error finding public dataset: {e}")
    #         dataset = None
    # 
    # if dataset:
    #     # Get all available questions from dataset
    #     raw_questions = dataset.get('dataset', {}).get('questions', []) if isinstance(dataset, dict) else []
    #     
    #     print(f"Raw questions count from dataset: {len(raw_questions)}")
    #     
    #     if len(raw_questions) == 0:
    #         print("Dataset has no questions, falling back to mixed questions")
    #         questions = get_mixed_questions(domain_for_exam)
    #     else:
    #         # Filter out bad questions
    #         filtered_questions = []
    #         seen = set()
    #         for q in raw_questions:
    #             if 'question' in q and q['question'].strip() and q['question'].strip() not in seen:
    #                 filtered_questions.append(q)
    #                 seen.add(q['question'].strip())
    #         
    #         print(f"Filtered questions count: {len(filtered_questions)}")
    #         
    #         # Use 6-7 questions for exam
    #         num_questions = min(len(filtered_questions), random.randint(6, 7))
    #         questions = random.sample(filtered_questions, num_questions)
    #         
    #         print(f"Final questions count from dataset: {len(questions)}")
    # else:
    #     # Use mixed questions only if absolutely no datasets available
    #     print("No datasets found, using mixed questions as last resort")
    #     questions = get_mixed_questions(domain_for_exam)

    # Store exam questions server-side so submit evaluates against the exact same questions
    exam_session_doc = {
        'student_id': current_user.id,
        'job_id': str(job['_id']),
        'company_id': job.get('company_id'),
        'domain': domain_for_exam,
        'dataset_id': str(dataset.get('_id')) if isinstance(dataset, dict) and dataset.get('_id') else None,
        'questions': questions,  # Store the complete question objects
        'created_at': datetime.now(),
        'status': 'active'
    }
    exam_session_id = str(db.exam_sessions.insert_one(exam_session_doc).inserted_id)
    
    # Debug: Print questions being passed to template
    print(f"Passing {len(questions)} questions to template:")
    for i, q in enumerate(questions[:2]):  # Print first 2 questions
        print(f"  Template Question {i+1}: {q.get('question', 'No question text')}")
        print(f"  Type: {q.get('type', 'No type')}")
        print(f"  Options: {q.get('options', 'No options')}")
    
    return render_template('student/exam.html', job=job, questions=questions, dataset_info=dataset, exam_session_id=exam_session_id)

def get_mixed_questions(domain):
    """Get mixed questions for exam"""
    import random
    
    # Get questions for the domain and randomize them
    domain_questions = mixed_questions.get(domain, mixed_questions.get('python', []))
    
    print(f"Available questions for {domain}: {len(domain_questions)}")
    for i, q in enumerate(domain_questions[:2]):  # Print first 2 questions for debugging
        print(f"  Question {i+1}: {q.get('question', 'No question text')}")
        print(f"  Type: {q.get('type', 'No type')}")
        print(f"  Answer: {q.get('answer', 'No answer')}")
    
    # Return a random subset of 6-7 questions
    num_questions = min(len(domain_questions), random.randint(6, 7))
    selected_questions = random.sample(domain_questions, num_questions)
    
    print(f"Selected {num_questions} random questions for {domain} domain")
    for i, q in enumerate(selected_questions[:2]):  # Print first 2 selected questions
        print(f"  Selected {i+1}: {q.get('question', 'No question text')}")
    
    return selected_questions

def get_exam_pattern(domain):
    pattern_types = [
        # Pattern 1: Balanced Mix
        {
            'name': 'Balanced Mix',
            'mcq_count': 2,
            'coding_count': 2,
            'conceptual_count': 2,
            'order': ['mcq', 'coding', 'conceptual']
        },
        # Pattern 2: Coding Focus
        {
            'name': 'Coding Focus',
            'mcq_count': 1,
            'coding_count': 3,
            'conceptual_count': 2,
            'order': ['mcq', 'coding', 'conceptual']
        },
        # Pattern 3: Theory Focus
        {
            'name': 'Theory Focus',
            'mcq_count': 3,
            'coding_count': 1,
            'conceptual_count': 2,
            'order': ['mcq', 'conceptual', 'coding']
        },
        # Pattern 4: Quick Assessment
        {
            'name': 'Quick Assessment',
            'mcq_count': 2,
            'coding_count': 1,
            'conceptual_count': 3,
            'order': ['mcq', 'coding', 'conceptual']
        },
        # Pattern 5: Comprehensive Test
        {
            'name': 'Comprehensive Test',
            'mcq_count': 2,
            'coding_count': 2,
            'conceptual_count': 2,
            'order': ['mcq', 'coding', 'conceptual']
        },
        # Pattern 6: Practical Focus
        {
            'name': 'Practical Focus',
            'mcq_count': 1,
            'coding_count': 4,
            'conceptual_count': 1,
            'order': ['mcq', 'coding', 'conceptual']
        }
    ]
    
    selected_pattern = random.choice(pattern_types)
    print(f"Selected pattern: {selected_pattern['name']}")
    
    domain_mcqs = [q for q in mixed_questions.get(domain, []) if q['type'] == 'mcq']
    domain_coding = [q for q in mixed_questions.get(domain, []) if q['type'] == 'coding']
    domain_conceptual = [q for q in mixed_questions.get(domain, []) if q['type'] == 'conceptual']
    
    question_pool = {
        'mcq': random.sample(domain_mcqs, min(selected_pattern['mcq_count'], len(domain_mcqs))),
        'coding': random.sample(domain_coding, min(selected_pattern['coding_count'], len(domain_coding))),
        'conceptual': random.sample(domain_conceptual, min(selected_pattern['conceptual_count'], len(domain_conceptual)))
    }
    
    all_questions = []
    for q_type in selected_pattern['order']:
        if question_pool[q_type]:
            all_questions.append(question_pool[q_type].pop(0))
    
    remaining_questions = []
    for q_type in ['mcq', 'coding', 'conceptual']:
        remaining_questions.extend(question_pool[q_type])
    
    if remaining_questions:
        random.shuffle(remaining_questions)
        all_questions.extend(remaining_questions)
    
    return all_questions

@app.route('/student/log_tab_switch', methods=['POST'])
@login_required
def log_tab_switch():
    """Log tab switching during exam"""
    if current_user.user_type != 'student':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        data = request.get_json()
        exam_session_id = data.get('exam_session_id')
        switch_count = data.get('switch_count', 0)
        timestamp = data.get('timestamp')
        
        # Log the tab switch event
        log_entry = {
            'student_id': current_user.id,
            'exam_session_id': exam_session_id,
            'switch_count': switch_count,
            'timestamp': timestamp or datetime.now().isoformat(),
            'event_type': 'tab_switch'
        }
        
        # Store in exam_logs collection
        db.exam_logs.insert_one(log_entry)
        
        return jsonify({'success': True, 'message': 'Tab switch logged'})
        
    except Exception as e:
        print(f"Error logging tab switch: {e}")
        return jsonify({'success': False, 'message': 'Failed to log tab switch'}), 500

@app.route('/student/submit_exam', methods=['POST'])
@login_required
def submit_exam():
    if current_user.user_type != 'student':
        return redirect(url_for('index'))
    
    job_id = request.form.get('job_id')
    domain = request.form.get('domain')
    exam_session_id = request.form.get('exam_session_id')
    answers = request.form.to_dict()
    audio_transcripts_raw = request.form.get('audio_transcripts', '{}')

    try:
        audio_transcripts = json.loads(audio_transcripts_raw) if audio_transcripts_raw else {}
    except Exception:
        audio_transcripts = {}
    
    # Remove non-answer fields
    answers.pop('job_id', None)
    answers.pop('domain', None)
    answers.pop('audio_transcripts', None)
    answers.pop('exam_session_id', None)
    
    # Get job info
    job = db.jobs.find_one({'_id': ObjectId(job_id)})
    if not job:
        return jsonify({'success': False, 'message': 'Job not found'})

    # Load the exact questions shown to the student
    dataset_questions = []
    if exam_session_id:
        try:
            session_doc = db.exam_sessions.find_one({'_id': ObjectId(exam_session_id), 'student_id': current_user.id, 'job_id': str(job['_id']), 'status': 'active'})
        except Exception:
            session_doc = None
        if session_doc and isinstance(session_doc.get('questions'), list):
            dataset_questions = session_doc['questions']
            # Use the stored domain if available
            domain = session_doc.get('domain') or domain

    # Fallback: use dataset lookup with the same logic as take_exam
    if not dataset_questions:
        dataset = dataset_manager.get_dataset(job['company_id'], domain)
        if not dataset:
            dataset = db.datasets.find_one({'domain': domain, 'is_active': True})
        if not dataset:
            return jsonify({'success': False, 'message': 'Dataset not found'})
        dataset_questions = dataset.get('dataset', {}).get('questions', [])[:5]
    
    # Evaluate answers using Ollama-based similarity scoring
    answer_items = [(k, v) for k, v in answers.items() if k.startswith('q') and v.strip() not in ("", "0")]
    answer_items.sort(key=lambda kv: int(kv[0][1:]) if kv[0][1:].isdigit() else 0)

    # Check if no answers provided
    if not answer_items:
        # No answers provided, score = 0
        cutoff_score = job.get('cutoff_score', 70)
        result = {
            'student_id': current_user.id,
            'student_name': current_user.name,
            'student_email': current_user.email,
            'job_id': job_id,
            'company_id': job['company_id'],
            'company_name': job['company_name'],
            'job_title': job['title'],
            'domain': domain,
            'answers': answers,
            'audio_transcripts': audio_transcripts if isinstance(audio_transcripts, dict) else {},
            'evaluation_results': [],
            'score': 0,
            'cutoff_score': cutoff_score,
            'eligible_for_hr': False,
            'submitted_at': datetime.now()
        }
        
        # Save to exam results
        db.exam_results.insert_one(result)
        
        # Also save detailed answers to company portal for review
        company_submission = {
            'student_id': current_user.id,
            'student_name': current_user.name,
            'student_email': current_user.email,
            'job_id': job_id,
            'job_title': job['title'],
            'domain': domain,
            'answers': [],
            'audio_transcripts': audio_transcripts if isinstance(audio_transcripts, dict) else {},
            'score': 0,
            'eligible_for_hr': False,
            'submitted_at': datetime.now(),
            'reviewed': False
        }
        
        db.company_submissions.insert_one(company_submission)

        # Mark exam session as completed
        if exam_session_id:
            try:
                db.exam_sessions.update_one({'_id': ObjectId(exam_session_id), 'student_id': current_user.id}, {'$set': {'status': 'completed', 'completed_at': datetime.now()}})
            except Exception:
                pass
        
        return jsonify({
            'success': True,
            'score': 0,
            'eligible_for_hr': False,
            'evaluation_count': 0
        })

    final_score = evaluate_answers_with_similarity(answers, dataset_questions, domain, audio_transcripts)
    
    # Create detailed evaluation results for display
    evaluation_results = []
    for i, question_data in enumerate(dataset_questions):
        question_key = f"q{i+1}"
        student_answer = answers.get(question_key, "")
        
        # Combine written answer with audio transcript if available
        audio_answer = audio_transcripts.get(question_key, '') if isinstance(audio_transcripts, dict) else ''
        combined_answer = student_answer
        
        if audio_answer:
            combined_answer += f" [Spoken: {audio_answer}]"
        
        # Evaluate this specific question individually
        if combined_answer.strip():
            # Get question type for proper evaluation method
            question_type = question_data.get('type', 'conceptual')
            
            if question_type == 'mcq':
                # Exact matching for MCQ questions in feedback
                if combined_answer.strip().lower() == question_data.get('answer', '').strip().lower():
                    question_score = 100
                    feedback = "Correct answer! Well done."
                else:
                    question_score = 0
                    feedback = "Incorrect answer. Please review the correct solution."
            else:
                # Get individual question score and feedback using AI
                question_score = calculate_similarity_with_ollama(combined_answer, question_data.get('answer', ''), domain)
                
                # Generate specific feedback based on score
                if question_score >= 90:
                    feedback = f"Excellent answer (Score: {question_score}). Demonstrates strong understanding and correct implementation."
                elif question_score >= 80:
                    feedback = f"Very good answer (Score: {question_score}). Minor improvements needed but solid understanding shown."
                elif question_score >= 70:
                    feedback = f"Good answer (Score: {question_score}). Works correctly but has some issues or could be optimized."
                elif question_score >= 60:
                    feedback = f"Adequate answer (Score: {question_score}). Basic functionality present but significant problems exist."
                elif question_score >= 40:
                    feedback = f"Poor answer (Score: {question_score}). Major errors in logic or approach."
                else:
                    feedback = f"Very poor answer (Score: {question_score}). Incorrect solution or fundamental misunderstandings."
        else:
            # Unanswered question
            question_score = 0
            feedback = "Question not answered. No evaluation possible."
        
        evaluation_results.append({
            'question': question_data.get('question', ''),
            'student_answer': combined_answer,
            'correct_answer': question_data.get('answer', ''),
            'score': question_score,  # Individual question score
            'feedback': feedback,  # Specific AI feedback for this question
            'question_type': question_data.get('type', 'coding')
        })

    # Calculate final score (already done by evaluate_answers_with_similarity)
    # final_score is already calculated above
    
    # Determine eligibility for TRI round using job's cutoff score
    cutoff_score = job.get('cutoff_score', 70)
    eligible_for_hr = final_score >= cutoff_score
    
    # Save exam result with detailed evaluation
    result = {
        'student_id': current_user.id,
        'student_name': current_user.name,
        'student_email': current_user.email,
        'job_id': job_id,
        'company_id': job['company_id'],
        'company_name': job['company_name'],
        'job_title': job['title'],
        'domain': domain,
        'answers': answers,
        'audio_transcripts': audio_transcripts if isinstance(audio_transcripts, dict) else {},
        'evaluation_results': evaluation_results,
        'score': round(final_score, 2),
        'cutoff_score': cutoff_score,
        'eligible_for_hr': eligible_for_hr,
        'submitted_at': datetime.now(),
        'reviewed': False  # Add reviewed field for template compatibility
    }
    
    # Save to exam results
    db.exam_results.insert_one(result)
    
    # Also save detailed answers to company portal for review
    company_submission = {
        'student_id': current_user.id,
        'student_name': current_user.name,
        'student_email': current_user.email,
        'job_id': job_id,
        'job_title': job['title'],
        'domain': domain,
        'answers': answers,  # Original student answers (MCQ selections, text answers, etc.)
        'evaluation_results': evaluation_results,  # Detailed evaluation with feedback
        'audio_transcripts': audio_transcripts if isinstance(audio_transcripts, dict) else {},
        'score': round(final_score, 2),
        'eligible_for_hr': eligible_for_hr,
        'submitted_at': datetime.now(),
        'reviewed': False
    }
    
    db.company_submissions.insert_one(company_submission)

    # Mark exam session as completed
    if exam_session_id:
        try:
            db.exam_sessions.update_one({'_id': ObjectId(exam_session_id), 'student_id': current_user.id}, {'$set': {'status': 'completed', 'completed_at': datetime.now()}})
        except Exception:
            pass
    
    return jsonify({
        'success': True,
        'score': round(final_score, 2),
        'eligible_for_hr': eligible_for_hr,
        'evaluation_count': len(evaluation_results),  # Now shows all questions
        'answered_count': len(answer_items)  # Shows how many were actually answered
    })

@app.route('/company/submissions')
@login_required
def company_submissions():
    if current_user.user_type != 'company':
        return redirect(url_for('index'))
    
    # Get all student exam results for this company
    submissions = list(db.exam_results.find({'company_id': current_user.id}).sort('submitted_at', -1))
    
    return render_template('company/submissions.html', submissions=submissions)

@app.route('/company/submission/<submission_id>')
@login_required
def view_submission(submission_id):
    if current_user.user_type != 'company':
        return redirect(url_for('index'))
    
    # Get specific submission
    submission = db.exam_results.find_one({'_id': ObjectId(submission_id)})
    
    if not submission or submission['company_id'] != current_user.id:
        flash('Submission not found', 'error')
        return redirect(url_for('company_submissions'))
    
    # Mark as reviewed
    db.exam_results.update_one(
        {'_id': ObjectId(submission_id)},
        {'$set': {'reviewed': True}}
    )
    
    return render_template('company/view_submission.html', submission=submission)

@app.route('/company/tri_candidates')
@login_required
def tri_candidates():
    """View all candidates who passed exams for TRI round"""
    if current_user.user_type != 'company':
        return redirect(url_for('index'))
    
    # Get all candidates who passed exams (eligible for HR)
    candidates = list(db.exam_results.find({
        'eligible_for_hr': True,
        'company_id': current_user.id
    }).sort('submitted_at', -1))
    
    return render_template('company/tri_candidates.html', candidates=candidates)

@app.route('/company/schedule_tri/<candidate_id>', methods=['POST'])
@login_required
def schedule_tri(candidate_id):
    """Schedule TRI interview with candidate"""
    if current_user.user_type != 'company':
        return redirect(url_for('index'))
    
    candidate = db.exam_results.find_one({'_id': ObjectId(candidate_id)})
    if not candidate or candidate['company_id'] != current_user.id:
        flash('Candidate not found', 'error')
        return redirect(url_for('tri_candidates'))
    
    # Check if already scheduled
    existing_schedule = db.tri_schedules.find_one({
        'candidate_id': ObjectId(candidate_id),
        'company_id': current_user.id
    })
    
    if existing_schedule:
        flash('Interview already scheduled', 'warning')
        return redirect(url_for('tri_candidates'))
    
    # Schedule the interview
    schedule = {
        'candidate_id': ObjectId(candidate_id),
        'company_id': current_user.id,
        'scheduled_at': datetime.now(),
        'status': 'scheduled',
        'interview_date': request.form.get('interview_date'),
        'interview_time': request.form.get('interview_time'),
        'interview_type': request.form.get('interview_type', 'technical'),
        'interviewer_name': request.form.get('interviewer_name'),
        'interviewer_email': request.form.get('interviewer_email'),
        'notes': request.form.get('notes'),
        'created_at': datetime.now()
    }
    
    db.tri_schedules.insert_one(schedule)
    
    # Update candidate status
    db.exam_results.update_one(
        {'_id': ObjectId(candidate_id)},
        {'$set': {'tri_scheduled': True}}
    )
    
    flash('TRI interview scheduled successfully', 'success')
    return redirect(url_for('tri_candidates'))

@app.route('/company/tri_schedule/<schedule_id>')
@login_required
def view_tri_schedule(schedule_id):
    """View TRI interview schedule details"""
    if current_user.user_type != 'company':
        return redirect(url_for('index'))
    
    schedule = db.tri_schedules.find_one({
        '_id': ObjectId(schedule_id),
        'company_id': current_user.id
    })
    
    if not schedule:
        flash('Schedule not found', 'error')
        return redirect(url_for('tri_candidates'))
    
    candidate = db.exam_results.find_one({'_id': schedule['candidate_id']})
    
    return render_template('company/view_tri_schedule.html', schedule=schedule, candidate=candidate)

@app.route('/company/update_tri_status/<schedule_id>')
@login_required
def update_tri_status(schedule_id):
    """Update TRI interview status"""
    if current_user.user_type != 'company':
        return redirect(url_for('index'))
    
    schedule = db.tri_schedules.find_one({
        '_id': ObjectId(schedule_id),
        'company_id': current_user.id
    })
    
    if not schedule:
        flash('Schedule not found', 'error')
        return redirect(url_for('tri_candidates'))
    
    new_status = request.form.get('status')
    valid_statuses = ['scheduled', 'completed', 'cancelled', 'rescheduled']
    
    if new_status not in valid_statuses:
        flash('Invalid status', 'error')
        return redirect(url_for('view_tri_schedule', schedule_id=schedule_id))
    
    db.tri_schedules.update_one(
        {'_id': ObjectId(schedule_id)},
        {'$set': {'status': new_status, 'updated_at': datetime.now()}}
    )
    
    flash('Interview status updated successfully', 'success')
    return redirect(url_for('view_tri_schedule', schedule_id=schedule_id))

@app.route('/company/datasets')
@login_required
def manage_datasets():
    if current_user.user_type != 'company':
        return redirect(url_for('index'))
    
    # Get all datasets for this company
    datasets = dataset_manager.get_all_datasets(current_user.id)
    
    return render_template('company/datasets.html', datasets=datasets)

@app.route('/company/delete_dataset/<dataset_id>', methods=['POST'])
@login_required
def delete_dataset(dataset_id):
    if current_user.user_type != 'company':
        return redirect(url_for('index'))
    
    # Delete dataset
    success = dataset_manager.delete_dataset(ObjectId(dataset_id))
    
    if success:
        flash('Dataset deleted successfully', 'success')
    else:
        flash('Error deleting dataset', 'error')
    
    return redirect(url_for('manage_datasets'))

def evaluate_with_enhanced_api(student_answer, correct_answer, domain, question_context=None):
    """Enhanced evaluation using user's API key for accurate scoring"""
    if not groq_client:
        return 50, "API not available - using basic evaluation"
    
    try:
        # Create detailed evaluation prompt
        evaluation_prompt = f"""
        You are an expert technical interviewer evaluating a student's answer in {domain}.
        
        Question Context: {question_context or 'Technical programming question'}
        
        Correct/Expected Answer: {correct_answer}
        
        Student's Answer: {student_answer}
        
        Evaluate the student's answer based on:
        1. Technical Accuracy (40%) - Is the code/logic correct?
        2. Conceptual Understanding (30%) - Does the student understand the underlying concept?
        3. Code Quality (20%) - Is the answer well-structured and follows best practices?
        4. Completeness (10%) - Does the answer fully address the question?
        
        Provide:
        1. A score from 0-100
        2. Detailed feedback explaining the evaluation
        3. Specific suggestions for improvement
        4. A final assessment (Pass/Fail/Excellent/Good)
        
        Respond in JSON format with: {{"score": number, "feedback": "detailed feedback text", "suggestions": ["improvement1", "improvement2"]}}
        """
        
        response = groq_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": evaluation_prompt}],
            max_tokens=300,
            temperature=0.1
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            result = json.loads(result_text)
            score = min(max(result.get('score', 50), 0), 100)  # Ensure 0-100 range
            feedback = result.get('feedback', 'No detailed feedback available')
            suggestions = result.get('suggestions', [])
            
            # Enhanced scoring logic
            if 'correct' in feedback.lower():
                score += 10  # Bonus for correct answer
            if 'well-structured' in feedback.lower():
                score += 5   # Bonus for good code quality
            if 'complete' in feedback.lower():
                score += 5   # Bonus for complete answer
            
            # Determine final assessment
            if score >= 90:
                assessment = "Excellent"
            elif score >= 80:
                assessment = "Very Good"
            elif score >= 70:
                assessment = "Good"
            elif score >= 60:
                assessment = "Satisfactory"
            else:
                assessment = "Needs Improvement"
            
            return score, f"{assessment}: {feedback}. Suggestions: {', '.join(suggestions) if suggestions else 'None'}"
            
        except json.JSONDecodeError:
            # Fallback parsing
            import re
            score_match = re.search(r'\b(\d{1,3})\b', result_text)
            score = int(score_match.group(1)) if score_match else 50
            feedback = result_text
            suggestions = []
            
            return score, f"{feedback}. Suggestions: {', '.join(suggestions) if suggestions else 'None'}"
            
    except Exception as e:
        print(f"Error in enhanced evaluation: {e}")
        return 50, "Evaluation error - using basic scoring"

def evaluate_answers_with_similarity(answers, dataset_questions, domain, audio_transcripts):
    """Evaluate answers using similarity scoring with Ollama API"""
    try:
        total_weighted_score = 0
        total_max_weighted_score = 0

        # If we have dataset_questions, evaluate all questions (answered get their score, unanswered get 0)
        if dataset_questions:
            for i, question_data in enumerate(dataset_questions):
                question_key = f"q{i+1}"  # Assuming question keys are q1, q2, etc.
                student_answer = answers.get(question_key, "")  # Empty string if not answered
                correct_answer = question_data.get('answer', '')
                # Get weight from question data, or assign based on type
                question_weight = question_data.get('weight')
                if question_weight is None:
                    question_type = question_data.get('type', 'conceptual')
                    if question_type == 'coding':
                        question_weight = 2.0  # Highest weight for coding questions
                    else:
                        question_weight = 1.0  # Standard weight for conceptual and MCQ questions

                # Combine written answer with audio transcript if available
                audio_answer = audio_transcripts.get(question_key, '') if isinstance(audio_transcripts, dict) else ''
                combined_answer = student_answer

                if audio_answer:
                    combined_answer += f" [Spoken: {audio_answer}]"

                # Only evaluate if student provided an answer
                if combined_answer.strip():
                    # Check question type for evaluation method
                    if question_type == 'mcq':
                        # Exact matching for MCQ questions
                        if combined_answer.strip().lower() == correct_answer.strip().lower():
                            similarity_score = 100
                        else:
                            similarity_score = 0
                    else:
                        # Use AI evaluation for coding and conceptual questions
                        similarity_score = calculate_similarity_with_ollama(combined_answer, correct_answer, domain)
                else:
                    # Unanswered questions get 0 and don't count toward max score
                    similarity_score = 0

                # Apply question weight to score
                weighted_score = similarity_score * question_weight

                # Only count answered questions toward maximum score
                if combined_answer.strip():
                    max_weighted_score = 100 * question_weight
                    total_max_weighted_score += max_weighted_score

                total_weighted_score += weighted_score
        else:
            # Fallback: evaluate only answered questions (old behavior) - now with equal weights
            # CRITICAL FIX: Don't use empty correct_answer - this was causing 0 scores for correct answers
            print("WARNING: dataset_questions is empty, using fallback evaluation - this may cause incorrect scoring")
            for i, (question_key, student_answer) in enumerate(answers.items()):
                correct_answer = "Please evaluate this answer based on technical correctness and completeness"  # Generic fallback
                # Assign weights: coding questions highest, others equal
                if i == 0:
                    question_weight = 2.0  # First question: coding (highest weight)
                else:
                    question_weight = 1.0  # All other questions: equal weight (conceptual/MCQ)

                # Combine written answer with audio transcript if available
                audio_answer = audio_transcripts.get(question_key, '') if isinstance(audio_transcripts, dict) else ''
                combined_answer = student_answer

                if audio_answer:
                    combined_answer += f" [Spoken: {audio_answer}]"

                # Use Ollama API for similarity evaluation with generic correct answer
                similarity_score = calculate_similarity_with_ollama(combined_answer, correct_answer, domain)

                # Apply question weight to score
                weighted_score = similarity_score * question_weight

                # Only count answered questions toward maximum score
                if combined_answer.strip():
                    max_weighted_score = 100 * question_weight
                    total_max_weighted_score += max_weighted_score

                total_weighted_score += weighted_score

        # Calculate final score with completion scaling
        if total_max_weighted_score > 0:
            knowledge_score = (total_weighted_score / total_max_weighted_score) * 100
            
            # Apply completion rate scaling for fairness
            total_questions = len(dataset_questions) if dataset_questions else len(answers)
            answered_questions = sum(1 for key, answer in answers.items() if answer.strip())
            completion_rate = answered_questions / total_questions if total_questions > 0 else 1
            
            # Final score = knowledge_score × completion_rate
            final_score = knowledge_score * completion_rate
            final_score = round(final_score)  # Round to nearest integer for exact score
            final_score = min(final_score, 100)  # Cap at 100%
        else:
            final_score = 0

        return final_score

    except Exception as e:
        print(f"Error evaluating answers: {e}")
        return 50  # Default score if evaluation fails

def calculate_similarity_with_ollama(student_answer, correct_answer, domain):
    """Calculate similarity score using Ollama API"""
    if not correct_answer:
        # If no correct answer available, do basic evaluation
        return 70 if len(student_answer.strip()) > 10 else 40
    
    try:
        # Detect if this is a coding question based on domain
        is_coding = any(lang in domain.lower() for lang in ['python', 'javascript', 'java', 'cpp', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala', 'typescript', 'html', 'css', 'sql'])
        
        if is_coding:
            # STRICT coding evaluation - only correct solutions get high scores
            evaluation_prompt = f"""
            You are an expert technical interviewer evaluating a {domain} CODING answer.
            
            CRITICAL: Be EXTREMELY STRICT. Only give high scores to CORRECT, FUNCTIONAL code that actually solves the problem.
            Random, irrelevant, or wrong answers should get VERY LOW scores (0-20).
            
            CODING EVALUATION CRITERIA:
            1. Functional Correctness (40%) - Does the code CORRECTLY solve the exact problem?
            2. Logic Soundness (25%) - Is the algorithm/approach technically sound and correct?
            3. Syntax Validity (20%) - Is the code syntactically correct and runnable?
            4. Efficiency (15%) - Is the solution reasonably efficient?
            
            STRICT SCORING GUIDELINES (BE RUTHLESS):
            - 90-100: PERFECT solution - correct, efficient, handles all cases, matches requirements exactly
            - 80-89: Excellent - correct with only minor style/syntax differences
            - 70-79: Good - correct solution, minor issues but fundamentally works
            - 60-69: Adequate - works but has clear problems or inefficiencies
            - 40-59: Poor - partially works but has major issues
            - 20-39: Very poor - major logic errors, doesn't work properly
            - 10-19: Almost completely wrong - shows some understanding but mostly incorrect
            - 0-9: Completely wrong, irrelevant, or random - no relation to the question
            
            EXAMPLES OF LOW SCORES (0-20):
            - Random text: "I don't know, maybe use loops?"
            - Wrong approach: "Use machine learning to sort arrays"
            - Irrelevant: "The weather is nice today"
            - Gibberish: "asdkfjhasdkjfhasd"
            
            QUESTION: {correct_answer}
            STUDENT CODE: {student_answer}
            
            If the student's code has NO RELATION to the question or is completely wrong, give score 0-10.
            Only give scores above 60 if the code actually solves the problem correctly.
            
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
            # STRICT evaluation for non-coding questions - be ruthless with wrong answers
            evaluation_prompt = f"""
            You are an expert technical interviewer evaluating a {domain} programming answer.
            
            CRITICAL: Be EXTREMELY STRICT. Only give high scores to answers that demonstrate CORRECT technical understanding.
            Random, irrelevant, or wrong answers should get VERY LOW scores (0-20).
            
            EVALUATION CRITERIA (Weight in final score):
            1. Conceptual Understanding (40%) - Does the student demonstrate deep understanding of the core concept?
            2. Technical Accuracy (30%) - Is the solution technically correct and valid?
            3. Completeness (20%) - Does it fully and correctly address the problem requirements?
            4. Clarity (10%) - Is the answer clear and technically sound?
            
            STRICT SCORING GUIDELINES (BE RUTHLESS):
            - 90-100: PERFECT understanding - correct, complete, technically accurate, shows deep knowledge
            - 80-89: Excellent - correct with only minor differences in wording/approach
            - 70-79: Good - correct understanding, minor technical issues but fundamentally right
            - 60-69: Adequate - partially correct but missing key technical details
            - 40-59: Poor - shows some understanding but major technical errors
            - 20-39: Very poor - fundamental misunderstandings, mostly incorrect
            - 10-19: Almost completely wrong - shows minimal understanding
            - 0-9: Completely wrong, irrelevant, or random - no relation to the question
            
            EXAMPLES OF LOW SCORES (0-20):
            - Random text: "I don't know, maybe it's something with computers?"
            - Wrong concept: "Inheritance means copying code manually"
            - Irrelevant: "The answer is 42, the meaning of life"
            - Gibberish: "asdkfjhasdkjfhasd"
            
            QUESTION: {correct_answer}
            STUDENT ANSWER: {student_answer}
            
            If the student's answer has NO RELATION to the question or is completely wrong, give score 0-10.
            Only give scores above 60 if the answer demonstrates genuine technical understanding.
            
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
            options={"temperature": 0.1, "num_predict": 200}  # Increased for JSON output
        )
        
        score_text = response['message']['content'].strip()
        
        # Enhanced parsing for JSON response
        try:
            import json
            # Try to parse as JSON first
            result = json.loads(score_text)
            score = result.get('score', 50)
            
            # Validate score is reasonable
            if not isinstance(score, (int, float)) or score < 0 or score > 100:
                score = 50  # Fallback if invalid
            
            return min(int(score), 100)
            
        except json.JSONDecodeError:
            # Fallback to regex parsing if JSON fails
            import re
            score_match = re.search(r'"score"\s*:\s*(\d+)', score_text)
            if score_match:
                score = int(score_match.group(1))
                return min(score, 100)
            else:
                # Last resort: extract any number
                numbers = re.findall(r'\d+', score_text)
                if numbers:
                    score = int(numbers[0])
                    return min(score, 100)
                else:
                    return 50  # Default fallback
        
    except Exception as e:
        print(f"Error in similarity calculation: {e}")
        return 50

if __name__ == '__main__':
    app.run(debug=True)