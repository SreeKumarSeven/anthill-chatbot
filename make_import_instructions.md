# Anthill IQ Chatbot Make.com Integration Guide

This guide explains how to import and configure the Anthill IQ chatbot workflow in make.com (formerly Integromat).

## Overview

The workflow handles:
1. Processing incoming chat messages
2. Detecting booking requests
3. Generating responses using your fine-tuned OpenAI model
4. Logging conversations to Google Sheets
5. Processing booking requests and sending notifications

## Step 1: Import the Workflow

1. Log in to your make.com account
2. Navigate to "Scenarios" in the left sidebar
3. Click "Create a new scenario"
4. Click on the three dots in the top right corner
5. Select "Import Blueprint"
6. Upload the `anthill_workflow.json` file
7. Click "Import"

## Step 2: Configure Connections

### OpenAI Connection
1. Click on the "Generate Chat Response" module
2. Create a new connection by clicking "Add"
3. Enter your OpenAI API key
4. Name the connection "Anthill OpenAI" and save

### Google Sheets Connection
1. Click on the "Log to Google Sheets" module
2. Create a new connection by clicking "Add"
3. Follow the Google authentication process
4. Name the connection "Anthill Google Sheets" and save
5. Repeat for the "Log Booking to Google Sheets" module

### Email Connection
1. Click on the "Send Email Notification" module
2. Create a new connection by clicking "Add"
3. Choose your email provider and follow the authentication steps
4. Name the connection "Anthill Notifications" and save

## Step 3: Configure Variables

Set up the following variables in make.com:
1. Go to "Scenarios" > "Variables" in the left sidebar
2. Add the following variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `FINE_TUNED_MODEL_ID`: Your fine-tuned model ID (ft:gpt-3.5-turbo-0125:thor-signia::BH7afRJw)
   - `GOOGLE_SHEET_ID`: Your Google Sheet ID
   - `GOOGLE_SERVICE_ACCOUNT`: Your Google service account email
   - `GOOGLE_PRIVATE_KEY`: Your Google service account private key

## Step 4: Google Sheets Setup

Ensure your Google Sheet has two worksheets:
1. "Conversations" with headers:
   - Timestamp
   - User ID
   - Message
   - Response
   - Source

2. "Bookings" with headers:
   - Timestamp
   - Name
   - Email
   - Phone
   - Service
   - Message

## Step 5: Testing the Workflow

1. Click "Run once" to test the workflow
2. Send a test request to the webhook URL
3. Monitor the workflow execution
4. Check that data is correctly logged to Google Sheets

## Step 6: Integration with Chatbot Frontend

Update your chatbot frontend to make API calls to the make.com webhook URL:

1. Get your webhook URL from the "Webhook" trigger module
2. Update your frontend API calls to point to this URL instead of your local server
3. Ensure your frontend sends requests in this format:

```javascript
// For chat messages
fetch('YOUR_WEBHOOK_URL', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    path: '/api/chat',
    message: 'User message here',
    user_id: 'unique_user_id',
    session_id: 'session_id'
  })
});

// For booking requests
fetch('YOUR_WEBHOOK_URL', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    path: '/api/booking',
    name: 'Customer Name',
    email: 'customer@example.com',
    phone: '1234567890',
    service: 'Day Pass',
    message: 'Additional details'
  })
});
```

## Step 7: Activate the Workflow

1. Click "Activate" to make your workflow live
2. The workflow will now automatically process incoming requests

## Troubleshooting

- **Webhook Issues**: Ensure your webhook URL is publicly accessible and correctly configured in your frontend.
- **Google Sheets Errors**: Verify that your service account has edit permissions for the Google Sheet.
- **OpenAI Errors**: Check your API key and model ID are correctly set up.
- **Email Notification Issues**: Verify your email connection settings.

For additional help, refer to the make.com documentation or contact support.

## Next Steps

- Enhance the workflow with additional error handling
- Add user feedback collection
- Implement follow-up sequences for bookings
- Set up analytics and reporting dashboards 