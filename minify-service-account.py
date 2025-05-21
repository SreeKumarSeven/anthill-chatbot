import json
import sys

def minify_json(json_str):
    """Minify a JSON string by parsing and re-serializing it without whitespace."""
    try:
        # Parse the JSON string
        parsed = json.loads(json_str)
        # Re-serialize without whitespace
        return json.dumps(parsed, separators=(',', ':'))
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

def main():
    print("Anthill IQ Chatbot - Service Account JSON Minifier")
    print("--------------------------------------------------")
    print("This script will help you prepare your service account JSON for Vercel.")
    
    # Check if JSON is provided via command line
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            json_str = f.read()
    else:
        # Ask user to paste JSON
        print("\nPaste your service account JSON below and press Enter twice when done:")
        lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)
        json_str = "\n".join(lines)
    
    # Minify the JSON
    minified = minify_json(json_str)
    
    if minified:
        print("\nMinified JSON (ready to copy to Vercel):")
        print("-----------------------------------------")
        print(minified)
        
        # Save to file
        with open("minified-service-account.txt", "w") as f:
            f.write(minified)
        print("\nThe minified JSON has also been saved to 'minified-service-account.txt'")
        
        print("\nVercel Setup Instructions:")
        print("1. Copy the entire minified JSON string above")
        print("2. In Vercel, add a new environment variable named GOOGLE_SERVICE_ACCOUNT")
        print("3. Paste the minified JSON as the value (with no additional quotes)")
        print("4. Select which environments should have access to this variable")
        print("5. Click Add and redeploy your application")
    else:
        print("Failed to minify JSON. Please check your input.")

if __name__ == "__main__":
    main() 