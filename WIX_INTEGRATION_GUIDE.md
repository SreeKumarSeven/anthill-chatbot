# Anthill IQ Chatbot - Wix Studio Integration Guide

This guide will help you integrate the Anthill IQ Chatbot into your Wix Studio website.

## Prerequisites

- A Wix Studio premium account
- Access to your Anthill IQ Chatbot files
- Basic understanding of HTML/CSS/JavaScript and Wix Studio

## Integration Methods

There are two primary methods to integrate the chatbot into your Wix Studio website:

### Method 1: Using Wix Custom Elements (Recommended)

1. **Log in to your Wix Studio account** and open your website project.

2. **Add a Custom Element**:
   - Click on the "+" icon to add a new element
   - Search for "Custom Element" or "HTML iFrame" and add it to your page

3. **Configure the Custom Element**:
   - In the element settings panel, select "Embed Code" or "HTML"
   - Paste the following code snippet:

```html
<div id="anthill-chatbot-container"></div>
<script>
    (function() {
        // Create script element
        var script = document.createElement('script');
        script.type = 'text/javascript';
        script.async = true;
        script.src = 'YOUR_CHATBOT_SERVER_URL/anthill_chatbot_widget.js'; // Replace with your actual chatbot URL
        
        // Add script to document
        var entry = document.getElementsByTagName('script')[0];
        entry.parentNode.insertBefore(script, entry);
    })();
</script>
```

4. **Replace `YOUR_CHATBOT_SERVER_URL`** with the actual URL where your chatbot is hosted.

5. **Adjust Element Settings**:
   - Set the custom element to be "Fixed Position" so it appears on all pages
   - Position it in the corner of the page (typically bottom right)
   - Set z-index to a high value (e.g., 9999) to ensure it appears above other elements

### Method 2: Using Wix Velo (Code Panel)

1. **Enable Velo**:
   - Go to your Wix dashboard
   - Click on "Dev Mode" or "Velo by Wix" to enable development features

2. **Open the Code Panel**:
   - Click on "Site" in the top menu
   - Select "Code" from the dropdown menu

3. **Modify Master Page**:
   - In the Code Panel, navigate to "Public" > "Pages" > "masterPage.js"
   - Add the following code to the `$w.onReady` function:

```javascript
$w.onReady(function () {
    // Load external chatbot script
    const script = document.createElement('script');
    script.src = 'YOUR_CHATBOT_SERVER_URL/anthill_chatbot_widget.js'; // Replace with your actual URL
    script.async = true;
    document.head.appendChild(script);
    
    // Create container for the chatbot
    const chatContainer = document.createElement('div');
    chatContainer.id = 'anthill-chatbot-container';
    document.body.appendChild(chatContainer);
});
```

4. **Replace `YOUR_CHATBOT_SERVER_URL`** with the actual URL where your chatbot is hosted.

5. **Save and Publish** your changes.

## Creating a Deployable Widget Script

To make integration easier, create a standalone JavaScript file that can be deployed to your server:

1. Create a new file named `anthill_chatbot_widget.js` with the following content:

```javascript
// Anthill IQ Chatbot Widget Loader
(function() {
    // Create widget container
    var container = document.createElement('div');
    container.className = 'anthill-chatbot-widget';
    document.body.appendChild(container);
    
    // Inject widget styles
    var styles = document.createElement('style');
    styles.innerHTML = `
        /* Copy all CSS styles from your chatbot widget here */
        .chat-widget {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 10000;
            /* More styles here... */
        }
    `;
    document.head.appendChild(styles);
    
    // Create widget HTML
    container.innerHTML = `
        <!-- Copy the entire chat widget HTML here -->
        <div class="chat-widget">
            <!-- Chat toggle button -->
            <button id="chat-toggle" class="chat-toggle" aria-label="Toggle chat">
                <span class="chat-toggle-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
                    </svg>
                </span>
            </button>
            
            <!-- Chat window -->
            <!-- Rest of your chatbot HTML here -->
        </div>
    `;
    
    // Insert all your JavaScript code here
    var CONFIG = {
        API_URL: 'YOUR_CHATBOT_SERVER_URL/api/chat',
        BOOKING_API_URL: 'YOUR_CHATBOT_SERVER_URL/api/booking',
        USER_REGISTRATION_API_URL: 'YOUR_CHATBOT_SERVER_URL/api/register-user',
        // Rest of your configuration...
    };
    
    // Initialize widget
    // Copy all your JavaScript initialization code here
    
})();
```

2. Replace the placeholder HTML, CSS, and JavaScript with your actual widget code from the `anthill_chatbot_widget.html` file.

3. **Update the server URLs** in the CONFIG object to point to your actual server endpoints.

4. **Host this file** on your server along with your backend API.

## Hosting the Backend

To make your chatbot functional, you'll need to host the backend API:

1. **Set up a hosting service** for your Python backend (e.g., Heroku, AWS, GCP, etc.)

2. **Deploy your backend code** to the hosting service.

3. **Configure CORS** in your backend to allow requests from your Wix domain:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-wix-domain.com", "https://editor.wix.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

4. **Update the configuration** in the `anthill_chatbot_widget.js` file to point to your deployed backend API endpoints.

## Troubleshooting

- **Widget not displaying**: Check browser console for errors and ensure your script URL is correct.
- **CORS errors**: Make sure your backend CORS settings allow requests from your Wix domain.
- **Widget showing but not functioning**: Ensure your API endpoints are correctly configured and accessible.
- **Style conflicts**: Increase the specificity of your CSS selectors or use an iframe for complete isolation.

## Advanced Customization

- **Custom domain**: Consider using a custom domain for your backend API to match your brand.
- **SSL certificate**: Ensure your backend uses HTTPS for security.
- **Wix data integration**: Use Wix Velo APIs to integrate chatbot data with your Wix database collections.

## Need Help?

Contact Anthill IQ support at connect@anthilliq.com for assistance with integration. 