"""
Helper script to prepare Google Service Account JSON for Heroku.

This script takes a Google Service Account JSON file and converts it to a 
single-line JSON string that can be set as a Heroku environment variable.
"""

import os
import json
import sys
import argparse

def prepare_service_account(json_file_path):
    """Read a service account JSON file and format it for Heroku"""
    try:
        with open(json_file_path, 'r') as f:
            service_account_data = json.load(f)
        
        # Convert to a compact, single-line JSON string
        compact_json = json.dumps(service_account_data)
        
        print("\n=== Google Service Account JSON for Heroku ===")
        print("\nCopy the following value and set it as GOOGLE_SERVICE_ACCOUNT in Heroku config vars:\n")
        print(compact_json)
        print("\n=== End of JSON ===\n")
        
        # Additional instructions
        print("To set this in Heroku, you can either:")
        print("1. Use the Heroku Dashboard: Settings > Config Vars > Add")
        print("2. Use the Heroku CLI command:")
        print(f'   heroku config:set GOOGLE_SERVICE_ACCOUNT=\'{compact_json}\'')
        
        return True
    except FileNotFoundError:
        print(f"Error: The file {json_file_path} does not exist.")
        return False
    except json.JSONDecodeError:
        print(f"Error: The file {json_file_path} is not valid JSON.")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Prepare Google Service Account JSON for Heroku'
    )
    parser.add_argument(
        'json_file',
        help='Path to the service account JSON file'
    )
    
    args = parser.parse_args()
    
    if prepare_service_account(args.json_file):
        return 0
    else:
        return 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prepare_for_heroku.py path_to_service_account.json")
        sys.exit(1)
        
    sys.exit(main()) 