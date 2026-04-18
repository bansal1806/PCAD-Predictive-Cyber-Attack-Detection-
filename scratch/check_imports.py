import sys
import os

# Check if src is importable
try:
    from src.preprocessing import DataCleaner
    print("SUCCESS: src.preprocessing is importable")
except ImportError as e:
    print(f"FAILURE: {e}")
    print(f"sys.path: {sys.path}")
    print(f"Current Dir: {os.getcwd()}")
    print(f"Contents of current dir: {os.listdir('.')}")
