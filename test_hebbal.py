import requests
import json

def test_hebbal_reference():
    """Test if the API correctly states that Hebbal branch is now open"""
    
    # API endpoint
    api_url = "https://anthill-chatbot.vercel.app/api/chat"
    
    # Test message specifically asking about Hebbal
    test_message = "Tell me about your Hebbal branch. Is it open yet?"
    
    # Send request
    response = requests.post(
        api_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "message": test_message,
            "user_id": "test_user",
            "session_id": "test_session"
        })
    )
    
    # Print results
    print("Status code:", response.status_code)
    
    if response.status_code == 200:
        data = response.json()
        print("\nAPI Response:")
        print(data.get("response", "No response"))
    else:
        print("Error:", response.text)

if __name__ == "__main__":
    test_hebbal_reference() 