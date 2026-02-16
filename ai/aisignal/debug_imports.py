import sys
import os

# Try to import intelligence as app.py does
try:
    from pages import intelligence
    print(f"Intelligence module file: {intelligence.__file__}")
except Exception as e:
    print(f"Error importing intelligence: {e}")

print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")
