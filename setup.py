#!/usr/bin/env python3
"""
Anthill IQ Chatbot Setup Script
This script helps set up the initial configuration for the chatbot.
"""

import os
import sys
import shutil
from pathlib import Path

def create_env_file():
    """Create .env file from template"""
    template_path = Path('.env.template')
    env_path = Path('.env')
    
    if not template_path.exists():
        print("❌ .env.template file not found!")
        return False
    
    if env_path.exists():
        overwrite = input("⚠️ .env file already exists. Overwrite? (y/n): ")
        if overwrite.lower() != 'y':
            print("✅ Keeping existing .env file.")
            return True
    
    # Copy the template
    shutil.copy(template_path, env_path)
    
    # Get user input for OpenAI API key
    openai_key = input("Enter your OpenAI API Key (press Enter to skip for now): ")
    
    # Get user input for Google Sheet ID
    sheet_id = input("Enter your Google Sheet ID (press Enter to skip for now): ")
    
    # Read the env file
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    # Replace values if provided
    if openai_key:
        env_content = env_content.replace('OPENAI_API_KEY=your_openai_api_key_here', f'OPENAI_API_KEY={openai_key}')
    
    if sheet_id:
        env_content = env_content.replace('GOOGLE_SHEET_ID=your_google_spreadsheet_id_here', f'GOOGLE_SHEET_ID={sheet_id}')
    
    # Write back the updated content
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created successfully!")
    
    if not openai_key or not sheet_id:
        print("⚠️ Remember to update any missing values in the .env file before running the chatbot.")
    
    return True

def main():
    """Main function to run setup tasks"""
    print("\n=== Anthill IQ Chatbot Setup ===\n")
    
    # Create .env file
    if create_env_file():
        print("\n✅ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Make sure you've created a Google Sheet and shared it with:")
        print("   anthill-chatbot-service@anthill-iq-chatot.iam.gserviceaccount.com")
        print("2. Update your .env file with any missing values")
        print("3. Run the chatbot with: python backend/app.py")
    else:
        print("\n❌ Setup failed. Please check the error messages and try again.")
    
    print("\n===================================\n")

if __name__ == "__main__":
    main() 