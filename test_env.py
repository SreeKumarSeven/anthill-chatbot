import os
import json

def main():
    print("Testing environment variables...")
    
    # Check OpenAI API Key
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("✅ OPENAI_API_KEY is set")
    else:
        print("❌ OPENAI_API_KEY is NOT set")
    
    # Check Google Sheet ID
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if sheet_id:
        print("✅ GOOGLE_SHEET_ID is set:", sheet_id)
    else:
        print("❌ GOOGLE_SHEET_ID is NOT set")
    
    # Check Google Service Account
    google_sa = os.getenv("GOOGLE_SERVICE_ACCOUNT")
    if google_sa:
        try:
            json.loads(google_sa)
            print("✅ GOOGLE_SERVICE_ACCOUNT is set and is valid JSON")
        except json.JSONDecodeError:
            print("❌ GOOGLE_SERVICE_ACCOUNT is set but is NOT valid JSON")
    else:
        print("❌ GOOGLE_SERVICE_ACCOUNT is NOT set")
    
    # Check Fine-tuned Model ID
    model_id = os.getenv("FINE_TUNED_MODEL_ID")
    if model_id:
        print("✅ FINE_TUNED_MODEL_ID is set:", model_id)
    else:
        print("❌ FINE_TUNED_MODEL_ID is NOT set")

if __name__ == "__main__":
    main() 