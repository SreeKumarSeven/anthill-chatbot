import requests
import json
import time

def test_hebbal_simple():
    """Simple test for Hebbal branch query"""
    
    # API endpoint
    api_url = "https://anthill-chatbot.vercel.app/api/chat"
    
    # Test message specifically asking about Hebbal
    test_message = "Is your Hebbal branch open yet?"
    
    # Send request with unique session ID to avoid caching
    response = requests.post(
        api_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "message": test_message,
            "user_id": "test_user",
            "session_id": f"test_session_{int(time.time())}"
        })
    )
    
    # Print results
    print("Status code:", response.status_code)
    
    if response.status_code == 200:
        data = response.json()
        print("\nAPI Response:")
        print(data.get("response", "No response"))
        print("\nSource:", data.get("source", "unknown"))
    else:
        print("Error:", response.text)

if __name__ == "__main__":
    test_hebbal_simple() 