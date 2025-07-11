import sys
import os

# Add the parent directory to Python path to import app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import the Flask application
from app import app

# This is required for Vercel to recognize the app
app = app
