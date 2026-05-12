import sys
import os

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")

try:
    import numpy
    print(f"NumPy version: {numpy.__version__}")
    print(f"NumPy path: {numpy.__file__}")
except ImportError:
    print("NumPy not found")
except Exception as e:
    print(f"Error importing NumPy: {e}")

try:
    import bcrypt
    print("bcrypt found")
except ImportError:
    print("bcrypt not found")

try:
    import jwt
    print("PyJWT found")
except ImportError:
    print("PyJWT not found")
