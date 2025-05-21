# Anthill IQ Chatbot Project Summary

## What We've Created

1. **CSS File (`anthill_chatbot_widget.css`)**
   - Comprehensive styling for the chatbot interface
   - Responsive design for all device sizes
   - Customizable color scheme using CSS variables
   - Animations and visual effects for better UX

2. **JavaScript File (`anthill_chatbot_widget.js`)**
   - Core chatbot functionality
   - User registration form handling
   - Booking flow for appointments
   - Message handling and display
   - Integration with backend API

3. **HTML Files**
   - `chatbot_iframe.html`: HTML file designed to be embedded via iframe
   - `index.html`: Landing page with documentation and demo

4. **Documentation**
   - README.md with installation and customization instructions

## Backend Integration

The chatbot is configured to connect to a backend API at:
```
https://anthill-iq-chatbot-88cca9381320.herokuapp.com
```

With endpoints for:
- User registration
- Message handling
- Booking management

## Deployment Instructions

1. **Create GitHub Repository**
   - Create a new GitHub repository named "anthill-chatbot" at https://github.com/SreeKumarSeven/anthill-chatbot
   - Use GitHub Pages for hosting the widget files

2. **Push Code to GitHub**
   ```bash
   # Initialize git repository
   git init
   
   # Add all files
   git add .
   
   # Commit changes
   git commit -m "Initial commit of Anthill IQ chatbot widget"
   
   # Add remote repository
   git remote add origin https://github.com/SreeKumarSeven/anthill-chatbot.git
   
   # Push to GitHub
   git push -u origin main
   ```

3. **Enable GitHub Pages**
   - Go to repository settings at https://github.com/SreeKumarSeven/anthill-chatbot/settings/pages
   - Navigate to "Pages" section
   - Select "main" branch as source
   - Save to publish site

4. **Test the Widget**
   - Verify the widget works at https://SreeKumarSeven.github.io/anthill-chatbot/
   - Test embedding on a test Wix site

## Wix Integration Code

Once GitHub Pages is active, use this code in Wix:

```html
<!-- Method 1: Using HTML Embed -->
<script src="https://SreeKumarSeven.github.io/anthill-chatbot/anthill_chatbot_widget.js"></script>
<link rel="stylesheet" href="https://SreeKumarSeven.github.io/anthill-chatbot/anthill_chatbot_widget.css">

<!-- Method 2: Using iFrame -->
<!-- In Wix Editor, add an HTML iFrame element and set source to: -->
<!-- https://SreeKumarSeven.github.io/anthill-chatbot/chatbot_iframe.html -->
```

## Additional Customization Options

- **Colors**: Edit CSS variables in `anthill_chatbot_widget.css`
- **Content**: Modify messages and options in `anthill_chatbot_widget.js`
- **Services/Locations**: Update the config object in `anthill_chatbot_widget.js`
- **Behavior**: Adjust animations and timing in the JavaScript file

## Testing Notes

The current implementation has placeholder API endpoints and simulated backend responses. For production use:

1. Verify API endpoints are correctly configured
2. Test form submissions thoroughly
3. Ensure all dynamic content loads properly
4. Test responsiveness on various devices 