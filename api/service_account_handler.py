import os
import json

def load_service_account():
    """
    Load service account from environment variable or file.
    
    This handles both deployment and local development scenarios.
    """
    # Check if service account JSON is provided as an environment variable
    service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT')
    
    if service_account_json:
        try:
            # If it's provided as a string, parse it and create a temporary file
            service_account_info = json.loads(service_account_json)
            
            # Create a temporary service account file
            with open('/tmp/service-account.json', 'w') as f:
                json.dump(service_account_info, f)
                
            # Set the environment variable to point to this file
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/tmp/service-account.json'
            return True
        except Exception as e:
            print(f"Error processing service account JSON: {str(e)}")
            return False
    
    # If environment variable not available, look for file
    elif os.path.exists('service-account.json'):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service-account.json'
        return True
    
    return False 