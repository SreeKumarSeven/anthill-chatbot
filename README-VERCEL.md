# Anthill IQ Chatbot - Vercel Deployment Guide

This guide will help you deploy the Anthill IQ Chatbot to Vercel and integrate it with your Wix website.

## Project Structure

The project has been restructured for Vercel deployment:

```
anthill-chatbot/
├── api/                  # Serverless functions for Vercel
│   ├── index.py          # Main API endpoint
│   └── requirements.txt  # Python dependencies
│
├── public/               # Static assets and frontend files
│   ├── anthill-widget.js # Widget script for direct integration
│   ├── iframe.html       # For iframe embedding
│   └── index.html        # Landing page with instructions
│
├── backend/              # Backend logic
├── vercel.json           # Vercel configuration file
└── .gitignore            # Git ignore file
```

## Deployment Steps

### 1. Set Up Vercel

1. Sign up for a [Vercel account](https://vercel.com/signup) if you don't have one.
2. Install the Vercel CLI:
   ```
   npm install -g vercel
   ```

### 2. Configure Environment Variables

You'll need to set up environment variables for your Vercel deployment:

1. Create a `.env` file in the root of your project (this will not be committed to Git):
   ```
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_SHEET_ID=your_google_sheet_id
   ```

2. Use the Vercel CLI to add these as secrets:
   ```
   vercel secrets add openai_api_key your_openai_api_key
   vercel secrets add google_sheet_id your_google_sheet_id
   ```

### 3. Deploy to Vercel

1. Run the following command from your project root:
   ```
   vercel
   ```

2. Follow the prompts to configure your project:
   - Link to an existing project or create a new one
   - Confirm the project root directory
   - Accept the default settings

3. After deployment is complete, Vercel will provide you with a URL for your application.

### 4. Update Widget Configuration

After deployment, you need to update the URLs in the widget scripts:

1. Edit `public/anthill-widget.js` and update the CONFIG object with your Vercel URL:
   ```javascript
   const CONFIG = {
       API_URL: 'https://your-vercel-deployment-url.vercel.app/api/chat',
       REGISTRATION_API_URL: 'https://your-vercel-deployment-url.vercel.app/api/register-user',
       WIDGET_TITLE: 'Anthill IQ Assistant'
   };
   ```

2. Edit `public/iframe.html` and update the CONFIG object:
   ```javascript
   const CONFIG = {
       API_URL: 'https://your-vercel-deployment-url.vercel.app/api/chat',
       REGISTRATION_API_URL: 'https://your-vercel-deployment-url.vercel.app/api/register-user'
   };
   ```

3. Re-deploy your application:
   ```
   vercel --prod
   ```

## Wix Integration

### Method 1: Using Wix Custom Element (Recommended)

1. Log in to your Wix Studio account and open your website project.

2. Add a Custom Element:
   - Click on the "+" icon to add a new element
   - Search for "Custom Element" or "HTML iFrame" and add it to your page

3. Configure the Custom Element:
   - In the element settings panel, select "Embed Code" or "HTML"
   - Paste the following code snippet:

```html
<div id="anthill-chatbot-container"></div>
<script>
    (function() {
        var script = document.createElement('script');
        script.type = 'text/javascript';
        script.async = true;
        script.src = 'https://your-vercel-deployment-url.vercel.app/anthill-widget.js';
        
        var entry = document.getElementsByTagName('script')[0];
        entry.parentNode.insertBefore(script, entry);
    })();
</script>
```

4. Replace `your-vercel-deployment-url.vercel.app` with your actual Vercel deployment URL.

### Method 2: Using an iFrame

1. Add an HTML iFrame element to your Wix page.

2. Configure the iFrame with the following attributes:
   ```html
   <iframe 
     src="https://your-vercel-deployment-url.vercel.app/iframe.html" 
     width="400" 
     height="600" 
     frameborder="0"
     style="position: fixed; bottom: 20px; right: 20px; border: none; z-index: 9999;">
   </iframe>
   ```

3. Replace `your-vercel-deployment-url.vercel.app` with your actual Vercel deployment URL.

## Troubleshooting

- **CORS issues**: The API is configured to allow requests from any origin. If you're experiencing CORS issues, check your browser console for specific error messages.

- **API not responding**: Make sure your environment variables are correctly set in Vercel.

- **Widget not displaying**: Verify that the script URL is correct and that there are no JavaScript errors in the browser console.

## Customization

You can customize the appearance and behavior of the chatbot by modifying:

- `public/anthill-widget.js` - For the embedded script version
- `public/iframe.html` - For the iframe version

The main styling is included in these files as CSS. 