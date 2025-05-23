# Wix Integration Guide for Anthill IQ Chatbot

This guide will help you add the Anthill IQ chatbot to your Wix website.

## Method 1: JavaScript Widget (Recommended)

This method adds a floating chat button in the corner of your website.

### Step 1: Access your Wix Editor

Log in to your Wix account and open the editor for your website.

### Step 2: Add an HTML Component

1. Click the **"+"** button on the left sidebar
2. Go to the **"Embed"** section
3. Select **"HTML iframe"** or **"Embed HTML Code"**
4. Drag it onto your page

### Step 3: Add the Chatbot Code

1. Click on the newly added HTML component
2. Click **"Enter Code"** in the settings panel
3. Copy and paste the following code:

```html
<div id="anthill-chatbot-container"></div>
<script>
    (function() {
        var script = document.createElement('script');
        script.type = 'text/javascript';
        script.async = true;
        
        // Replace with your preferred production URL
        script.src = 'https://anthill-chatbot-ghm916hgr-sreekumar-thorsigniaos-projects.vercel.app/anthill_chatbot_widget.js';
        
        var entry = document.getElementsByTagName('script')[0];
        entry.parentNode.insertBefore(script, entry);
    })();
</script>
```

4. Click **"Apply"** or **"Update"**

### Step 4: Publish Your Site

Click the **"Publish"** button in the top right corner to make the changes live.

## Method 2: iFrame Integration (Alternative)

If Method 1 doesn't work, you can try embedding the chatbot directly as an iframe.

### Step 1-2: Same as Method 1

Follow the same first two steps as in Method 1.

### Step 3: Add the iFrame Code

1. Click on the newly added HTML component
2. Click **"Enter Code"** in the settings panel
3. Copy and paste the following code:

```html
<iframe 
    src="https://anthill-chatbot-ghm916hgr-sreekumar-thorsigniaos-projects.vercel.app/iframe.html" 
    width="400" 
    height="600" 
    frameborder="0"
    style="position: fixed; bottom: 20px; right: 20px; border: none; z-index: 9999;">
</iframe>
```

4. Click **"Apply"** or **"Update"**

### Step 4: Publish Your Site

Click the **"Publish"** button in the top right corner to make the changes live.

## Troubleshooting

### The chatbot doesn't appear

- Make sure the HTML component is placed on all pages where you want the chatbot to appear (consider adding it to your site header or footer)
- Try using the alternative method (iFrame integration)
- Check your browser console for any JavaScript errors

### The chatbot appears but doesn't respond

- Ensure the Vercel deployment has a valid OpenAI API key set in its environment variables
- Try testing the API connection at /test.html on your deployed URL
- Check your browser console for any network errors

### The chatbot styling doesn't match my website

If you need to customize the appearance of the chatbot to match your website's design, contact us for custom styling options.

## Need Help?

If you encounter any issues with the integration, please contact us at connect@anthilliq.com for assistance. 