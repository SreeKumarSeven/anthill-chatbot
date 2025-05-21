"""
Simple script to start the Anthill IQ Chatbot API server
"""

import os
import subprocess
import sys
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup command line arguments
parser = argparse.ArgumentParser(description='Run the Anthill IQ Chatbot server')
parser.add_argument('--debug', action='store_true', help='Run in debug mode with verbose output')
args = parser.parse_args()

def run_server():
    """Run the FastAPI server using uvicorn"""
    try:
        # Get port from environment variable (for Heroku) or use default
        port = int(os.environ.get("PORT", 8080))
        
        # Run the uvicorn server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.app:app", 
            "--host", "0.0.0.0", 
            "--port", str(port),
            "--reload"
        ])
    except Exception as e:
        print(f"Error running server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    log_level = "debug" if args.debug else "info"
    # Get port from environment variable (for Heroku) or use default
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting Anthill IQ Chatbot server on port {port}...")
    print(f"Debug mode: {'ON' if args.debug else 'OFF'}")
    
    try:
        run_server()
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        print("Please check your dependencies and environment variables.")
        if args.debug:
            import traceback
            traceback.print_exc() 