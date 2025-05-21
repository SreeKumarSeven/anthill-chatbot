# Vercel Environment Variables Guide

Below are the environment variables you need to set up in your Vercel project:

## Required Variables

| Name | Description |
|------|-------------|
| OPENAI_API_KEY | Your OpenAI API key |
| GOOGLE_SHEET_ID | Your Google Sheet ID |
| GOOGLE_SERVICE_ACCOUNT | Your entire Google Service Account JSON |
| FINE_TUNED_MODEL_ID | Your fine-tuned model ID (optional) |

## How to Set Up in Vercel

1. Go to your Vercel project dashboard
2. Click on "Settings" tab
3. Select "Environment Variables" from the left sidebar
4. Add each variable one by one:
   - Enter the variable name (e.g., `OPENAI_API_KEY`)
   - Enter the value (copy from your secure notes)
   - Select all environments (Production, Preview, Development)
   - Click "Add" button

## IMPORTANT: For GOOGLE_SERVICE_ACCOUNT

The Google Service Account JSON must be:
- Copied as a single line with no line breaks
- Include the entire JSON including the curly braces
- Contain no extra spaces or formatting

## After Setting Variables

1. Redeploy your application (Settings > Deployments > Redeploy)
2. Check that your API is working by visiting:
   - `https://your-vercel-url.vercel.app/api/chat`
   - You should see a JSON response with status "online"

## Need the Values?

For security reasons, we don't store credentials in Git repositories. 
Contact the project administrator for the actual values of these environment variables. 