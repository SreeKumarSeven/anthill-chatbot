"""
Test script to verify environment variables for Heroku deployment.
"""

import os
import json
import sys
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

def check_env_var(var_name, required=True, is_json=False):
    """Check if an environment variable is set and valid"""
    var_value = os.getenv(var_name)
    
    if var_value:
        if is_json:
            try:
                json.loads(var_value)
                return True, f"✅ {var_name} is set and is valid JSON"
            except json.JSONDecodeError:
                return False, f"❌ {var_name} is set but is NOT valid JSON"
        else:
            return True, f"✅ {var_name} is set"
    else:
        if required:
            return False, f"❌ {var_name} is NOT set (required)"
        else:
            return True, f"⚠️ {var_name} is NOT set (optional)"

def main():
    """Main test function"""
    print("Testing environment variables for Heroku deployment...\n")
    
    # Required variables
    openai_key_ok, openai_msg = check_env_var("OPENAI_API_KEY")
    google_sa_ok, google_sa_msg = check_env_var("GOOGLE_SERVICE_ACCOUNT", is_json=True)
    google_sheet_ok, google_sheet_msg = check_env_var("GOOGLE_SHEET_ID")
    
    # Optional variables
    port_ok, port_msg = check_env_var("PORT", required=False)
    
    # Print results
    print(openai_msg)
    print(google_sa_msg)
    print(google_sheet_msg)
    print(port_msg)
    print("")
    
    # Test service account generation
    if google_sa_ok:
        print("Testing service account generation...")
        try:
            from backend.generate_service_account import generate_service_account
            result = generate_service_account()
            if result:
                print("✅ Service account generated successfully")
                if os.path.exists("service_account.json"):
                    print("✅ service_account.json file exists")
                else:
                    print("❌ service_account.json file was NOT created")
            else:
                print("❌ Failed to generate service account")
        except Exception as e:
            print(f"❌ Error testing service account generation: {str(e)}")
    
    # Overall result
    if openai_key_ok and google_sa_ok and google_sheet_ok:
        print("\n✅ All required environment variables are set correctly!")
        print("You're ready to deploy to Heroku!")
        return 0
    else:
        print("\n❌ Some required environment variables are missing or invalid")
        print("Please check the messages above and set all required variables")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 