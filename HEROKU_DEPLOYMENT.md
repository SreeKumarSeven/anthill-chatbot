# Heroku Deployment Guide for Anthill IQ Chatbot

This guide outlines the steps to deploy the Anthill IQ Chatbot to Heroku.

## Prerequisites

- A Heroku account
- Git installed on your computer
- Heroku CLI installed (recommended but optional)

## Step 1: Prepare Your Environment Variables

You'll need to set the following environment variables in Heroku:

1. `OPENAI_API_KEY` - Your OpenAI API key
2. `GOOGLE_SERVICE_ACCOUNT` - The entire content of your Google Service Account JSON file (as a single-line JSON string)
3. `GOOGLE_SHEET_ID` - The ID of your Google Sheet for conversation logging

## Step 2: Create a Heroku App

1. Log in to the [Heroku Dashboard](https://dashboard.heroku.com/)
2. Click "New" and then "Create new app"
3. Enter a unique app name and choose a region
4. Click "Create app"

## Step 3: Configure Environment Variables

1. In your app dashboard, go to the "Settings" tab
2. Click "Reveal Config Vars"
3. Add each of the environment variables mentioned in Step 1

## Step 4: Deploy Your Code

### Option A: Deploy with Heroku CLI (if installed)

```bash
# Login to Heroku
heroku login

# Add Heroku as a remote repository
heroku git:remote -a your-heroku-app-name

# Push to Heroku
git push heroku master
```

### Option B: Deploy with Heroku Git Integration

1. In your app dashboard, go to the "Deploy" tab
2. Under "Deployment method", choose "GitHub"
3. Connect your GitHub account and select the repository
4. Choose the branch to deploy and click "Deploy Branch"

## Step 5: Verify Deployment

1. Click "Open app" from your Heroku dashboard
2. You should see a message that the service is online
3. Test the API endpoint at `/api/test-config` to verify configuration

## Troubleshooting

If you encounter issues:

1. Check Heroku logs with `heroku logs --tail` or through the dashboard
2. Verify all environment variables are set correctly
3. Check that the service_account.json file is being generated correctly

## Additional Notes

- Heroku's free tier has been discontinued, so you'll need a paid plan
- The app will automatically handle the generation of service_account.json from the GOOGLE_SERVICE_ACCOUNT environment variable
- Heroku's dyno will sleep after 30 minutes of inactivity on eco plans, causing a slight delay on first access 