import requests
import json
import time

def test_hebbal_simple():
    """Simple test for Hebbal branch query"""
    
    # API endpoint
    api_url = "https://anthill-chatbot.vercel.app/api/chat"
    print(f"Testing API at: {api_url}")
    
    # Test message specifically asking about Hebbal
    test_message = "Is your Hebbal branch open yet?"
    print(f"Query: {test_message}")
    
    # Generate a unique session ID with timestamp to avoid caching
    session_id = f"test_session_{int(time.time())}"
    print(f"Session ID: {session_id}")
    
    # Send request with unique session ID to avoid caching
    response = requests.post(
        api_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "message": test_message,
            "user_id": "test_user",
            "session_id": session_id
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
    print("Waiting 10 seconds to ensure deployment is complete...")
    time.sleep(10)
    test_hebbal_simple() 