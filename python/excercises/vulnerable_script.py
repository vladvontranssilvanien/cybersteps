import pickle
import sys

if len(sys.argv) != 2:
    print("Usage: python vulnerable_script.py <filename>")
    sys.exit(1)

filename = sys.argv[1]

try:
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    print("I unpickled your file!")
except Exception as e:
    print(f"Error loading pickle: {e}")
