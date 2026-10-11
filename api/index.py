import sys
import os

# Add parent directory to path so imports work cleanly in Vercel serverless environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
