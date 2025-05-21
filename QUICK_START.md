# Anthill IQ Chatbot - Quick Start Guide

This guide will help you quickly set up and run the Anthill IQ Chatbot with Google Sheets integration.

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Up Your Environment

Create a `.env` file in the root directory with the following content:
```
OPENAI_API_KEY=your_openai_api_key
GOOGLE_SHEETS_ID=your_google_sheet_id
GOOGLE_SERVICE_ACCOUNT={"type":"service_account","project_id":"...","private_key_id":"...","private_key":"...","client_email":"...","client_id":"...","auth_uri":"...","token_uri":"...","auth_provider_x509_cert_url":"...","client_x509_cert_url":"..."}
```

## Step 3: Set Up Google Sheets

1. Create a new Google Sheet at [sheets.google.com](https://sheets.google.com)
2. Share the sheet with the email in your service account JSON (client_email field)
3. Give it "Editor" access
4. Copy the Sheet ID from the URL:
   - Example URL: `https://docs.google.com/spreadsheets/d/1ABC123_YOUR_SHEET_ID_XYZ/edit`
   - The Sheet ID is: `1ABC123_YOUR_SHEET_ID_XYZ`

## Step 4: Start the Chatbot

Start the chatbot API server:
```bash
python run_server.py
```

The API will be available at http://localhost:8080

## Step 5: Integrate with Your Website

### For Wix:
1. In your Wix editor, add a new "Custom Element" or "HTML Embed" component
2. Copy the contents of the `anthill_chatbot_widget.html` file
3. Update the `API_URL` in the CONFIG section to point to your deployed backend
4. Publish your Wix site

### For Other Websites:
1. Host the `anthill_chatbot_widget.html` file on your web server
2. Include it in your page using an iframe or by copying the code directly

## Common Issues

1. **Google Sheets Connection Error**
   - Make sure the Sheet ID is correct
   - Make sure you've shared the sheet with the service account email

2. **OpenAI API Error**
   - Verify your API key is correct
   - Check your OpenAI account has sufficient credits
   - The chatbot will fall back to keyword matching if OpenAI quota is exceeded 