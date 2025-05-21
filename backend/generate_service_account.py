"""
Generate service_account.json from environment variable.

On Heroku, we can't directly use a service_account.json file, so we store the
content in an environment variable and generate the file at runtime.
"""

import os
import json
import sys

def generate_service_account():
    """Generate service_account.json from GOOGLE_SERVICE_ACCOUNT environment variable"""
    service_account_env = os.getenv("GOOGLE_SERVICE_ACCOUNT")
    
    if not service_account_env:
        print("Warning: GOOGLE_SERVICE_ACCOUNT environment variable not found.")
        print("Google Sheets functionality will be limited.")
        return False
    
    try:
        # Parse the JSON from environment variable
        service_account_data = json.loads(service_account_env)
        
        # Write to service_account.json file
        with open("service_account.json", "w") as f:
            json.dump(service_account_data, f, indent=2)
            
        print("Successfully generated service_account.json")
        return True
    except json.JSONDecodeError:
        print("Error: GOOGLE_SERVICE_ACCOUNT is not valid JSON")
        return False
    except Exception as e:
        print(f"Error generating service_account.json: {str(e)}")
        return False

if __name__ == "__main__":
    generate_service_account() 