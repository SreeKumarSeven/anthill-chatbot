# Anthill IQ Chatbot

A conversational AI chatbot for Anthill IQ coworking spaces in Bangalore.

## Locations

Anthill IQ has four locations in Bangalore:
- Cunningham Road (Central Bangalore) 
- Arekere (South Bangalore)
- Hulimavu (South Bangalore)
- Hebbal (North Bangalore) - Now Open!

## Features

- Information about Anthill IQ services and locations
- Booking assistance for workspace services
- Responsive design that works on mobile and desktop devices
- Embedded widget that can be added to any website
- Integration with booking and contact systems
- User registration: Collects user information before starting the chat
- Interactive booking flow: Guides users through selecting location, service, and appointment time
- Customizable styling: Easily change colors, fonts, and other visual elements

## Installation on Wix

There are two methods to add the chatbot to your Wix website:

### Method 1: Using HTML Embed (Recommended)

1. **Go to your Wix Editor**
2. **Add an HTML iFrame**:
   - Click the "+" button to add a new element
   - Search for "HTML iFrame" and add it to your page
   - Size the element as needed (you can make it invisible for the floating widget)

3. **Add the Widget Code**:
   - In the HTML settings panel, paste the following code:

```html
<script src="https://SreeKumarSeven.github.io/anthill-chatbot/anthill_chatbot_widget.js"></script>
<link rel="stylesheet" href="https://SreeKumarSeven.github.io/anthill-chatbot/anthill_chatbot_widget.css">
```

4. **Save and Publish** your Wix site

### Method 2: Using an Embedded iFrame

This method is useful if you want the chatbot to appear in a specific location on your page rather than as a floating widget.

1. **Go to your Wix Editor**
2. **Add an HTML iFrame**:
   - Click the "+" button to add a new element
   - Search for "HTML iFrame" and add it to your page
   - Size the element as needed

3. **Set the iFrame Source**:
   - In the iFrame settings, set the source URL to:
   ```
   https://SreeKumarSeven.github.io/anthill-chatbot/chatbot_iframe.html
   ```

4. **Save and Publish** your Wix site

## Customization

### Changing Colors and Styling

Edit the CSS variables at the top of `anthill_chatbot_widget.css`:

```css
:root {
  --anthill-primary: #4a2c8f;    /* Main brand color */
  --anthill-secondary: #7e57c2;  /* Secondary brand color */
  /* ... other variables ... */
}
```

### Changing Configuration Settings

Edit the configuration options in `anthill_chatbot_widget.js`:

```javascript
const config = {
  apiBaseUrl: 'https://anthill-iq-chatbot-88cca9381320.herokuapp.com',
  companyName: 'Anthill IQ',
  companyLogoUrl: 'https://example.com/logo.png',
  initialMessage: 'Hello! Welcome to Anthill IQ...',
  // ... other options ...
};
```

## Backend Integration

The chatbot widget connects to a backend API deployed at:
```
https://anthill-iq-chatbot-88cca9381320.herokuapp.com
```

### Available Endpoints

- `/api/message` - Send and receive chat messages
- `/api/register` - Register new users
- `/api/booking` - Create and manage bookings

## Development

### Prerequisites

- Git
- A GitHub account (for hosting the files)

### Setup Local Development

1. Clone the repository:
```
git clone https://github.com/SreeKumarSeven/anthill-chatbot.git
```

2. Make your changes to the files

3. Test locally by opening `index.html` in a browser

4. Commit and push changes to GitHub:
```
git add .
git commit -m "Your commit message"
git push origin main
```

5. The changes will be available on GitHub Pages after a few minutes

## License

Copyright © 2023 Anthill IQ. All rights reserved.

## Vercel Deployment

This project has been optimized for deployment on Vercel's serverless platform. The optimization was necessary to overcome Vercel's 250MB deployment size limit.

> **Note**: This branch is specifically optimized for Vercel deployment.

Key optimizations include:
- Minimized dependencies (only using openai, python-dotenv, requests, psycopg2-binary)
- Simplified database connections using direct psycopg2 instead of SQLAlchemy
- Exclusion of unnecessary files and directories via .vercelignore
- Core functionality maintained while removing unused features

For detailed deployment instructions, see [VERCEL-DEPLOY-GUIDE.md](VERCEL-DEPLOY-GUIDE.md). 