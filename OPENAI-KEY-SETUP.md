# Setting Up OpenAI API Key for Anthill Chatbot

The chatbot is currently showing "I'm sorry, the chatbot is not available at the moment" because the OpenAI API key is not properly configured in the Vercel environment.

## Steps to Fix This Issue:

1. Log in to the [Vercel Dashboard](https://vercel.com)

2. Select the "anthill-chatbot" project

3. Go to the "Settings" tab

4. Click on "Environment Variables" in the left sidebar

5. Add a new environment variable:
   - Name: `OPENAI_API_KEY`
   - Value: Your actual OpenAI API key (starts with "sk-")
   - Environments: Production, Preview, Development (check all)

6. Click "Save" to save the environment variable

7. Go to the "Deployments" tab

8. Find the latest deployment and click on the three dots (⋮)

9. Select "Redeploy" to deploy with the new environment variable

## Verifying the API Key is Working

Once deployed, you can verify that the OpenAI API key is properly set up by:

1. Visit https://anthill-chatbot.vercel.app/test.html
2. Click the "Test OpenAI Connection" button
3. You should see a success message if the key is properly configured

## Troubleshooting

If you're still seeing the "chatbot is not available" message:

1. Make sure the API key is valid and has not expired
2. Check that you've spelled the environment variable name correctly as `OPENAI_API_KEY`
3. Ensure the deployment completed successfully
4. Check the Vercel logs for any error messages

## Getting a New OpenAI API Key

If you need a new API key:

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Give it a name (e.g., "Anthill Chatbot")
4. Copy the key immediately (you won't be able to see it again)
5. Add it to your Vercel environment variables as described above 