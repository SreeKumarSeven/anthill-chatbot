#!/usr/bin/env python3
"""
Test Google Sheets connection for Anthill IQ Chatbot
This script tests if your Google Sheets credentials and Sheet ID are properly configured.
"""

import os
import sys
import json
import dotenv
from pathlib import Path

# Try to load environment variables from .env file
dotenv.load_dotenv()

def test_sheets_connection():
    """Test connection to Google Sheets"""
    try:
        # Import required libraries
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        print("❌ Required libraries not installed. Please run:")
        print("   pip install -r requirements.txt")
        return False
    
    print("Testing Google Sheets connection...")
    
    # Check if Google Sheet ID is set
    google_sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not google_sheet_id:
        print("❌ GOOGLE_SHEET_ID environment variable not set")
        print("   Please set it in your .env file")
        return False
    
    print(f"✅ GOOGLE_SHEET_ID found: {google_sheet_id}")
    
    # Check Google Service Account credentials
    service_account_info = os.getenv("GOOGLE_SERVICE_ACCOUNT")
    service_account_file = Path("service_account.json")
    
    creds = None
    
    if service_account_info:
        print("✅ GOOGLE_SERVICE_ACCOUNT environment variable found")
        try:
            service_account_dict = json.loads(service_account_info)
            creds = Credentials.from_service_account_info(
                service_account_dict,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            print("✅ Google Service Account credentials from environment are valid")
        except Exception as e:
            print(f"❌ Error loading credentials from environment: {str(e)}")
    elif service_account_file.exists():
        print("✅ service_account.json file found")
        try:
            creds = Credentials.from_service_account_file(
                service_account_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            print("✅ Google Service Account credentials from file are valid")
        except Exception as e:
            print(f"❌ Error loading credentials from file: {str(e)}")
    else:
        print("❌ No Google Service Account credentials found")
        print("   Please either:")
        print("   1. Set GOOGLE_SERVICE_ACCOUNT environment variable in .env file")
        print("   2. Create a service_account.json file in the project root")
        return False
    
    # Test connection to Google Sheets
    if creds:
        try:
            client = gspread.authorize(creds)
            spreadsheet = client.open_by_key(google_sheet_id)
            print(f"✅ Successfully connected to Google Sheet: '{spreadsheet.title}'")
            
            # List worksheets
            worksheets = spreadsheet.worksheets()
            print(f"✅ Found {len(worksheets)} worksheets:")
            for sheet in worksheets:
                print(f"   - {sheet.title}")
            
            return True
        except Exception as e:
            print(f"❌ Error connecting to Google Sheets: {str(e)}")
            print("   Possible causes:")
            print("   1. Invalid Google Sheet ID")
            print("   2. Sheet not shared with service account email:")
            print("      anthill-chatbot-service@anthill-iq-chatot.iam.gserviceaccount.com")
            print("   3. API access issues")
            return False
    
    return False

def main():
    """Main function"""
    print("\n=== Anthill IQ Chatbot - Connection Test ===\n")
    
    # Test Google Sheets connection
    sheets_ok = test_sheets_connection()
    
    print("\n=== Test Results ===\n")
    
    if sheets_ok:
        print("✅ Google Sheets connection successful!")
        print("\nYou're all set to use the Anthill IQ Chatbot!")
    else:
        print("❌ Google Sheets connection failed.")
        print("   Please fix the issues mentioned above before running the chatbot.")
    
    print("\n===================================\n")

if __name__ == "__main__":
    main() 