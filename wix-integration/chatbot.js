/**
 * Anthill IQ Chatbot - Wix Integration Script
 * 
 * This script provides the client-side functionality for integrating
 * the Anthill IQ chatbot with a Wix website.
 * 
 * How to use:
 * 1. Add a custom HTML element to your Wix site
 * 2. Paste this script into the HTML/JavaScript section
 * 3. Update the API_BASE_URL to point to your deployed backend
 * 4. Customize styling as needed
 */

// Configuration
const API_BASE_URL = 'https://your-backend-api-url.com'; // Replace with your actual API URL
const USER_ID = generateUserId(); // Generate a random user ID or use Wix's member ID if available
let SESSION_ID = null; // Will be assigned by the server on first message

// Chatbot UI Elements
let chatContainer;
let chatMessages;
let chatInput;
let sendButton;
let chatToggle;
let chatWindow;

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Create the chatbot UI
    createChatbotUI();
    
    // Add event listeners
    chatInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
    
    sendButton.addEventListener('click', sendMessage);
    chatToggle.addEventListener('click', toggleChat);
    
    // Check if we need to restore a previous session
    restoreSession();
});

/**
 * Creates the chatbot UI and appends it to the document
 */
function createChatbotUI() {
    // Create main container
    chatContainer = document.createElement('div');
    chatContainer.className = 'anthill-chatbot';
    
    // Create chat window
    chatWindow = document.createElement('div');
    chatWindow.className = 'anthill-chat-window';
    chatWindow.style.display = 'none';
    
    // Create chat header
    const chatHeader = document.createElement('div');
    chatHeader.className = 'anthill-chat-header';
    chatHeader.innerHTML = '<h3>Anthill IQ Assistant</h3>';
    
    // Create chat messages container
    chatMessages = document.createElement('div');
    chatMessages.className = 'anthill-chat-messages';
    
    // Create chat input area
    const chatInputArea = document.createElement('div');
    chatInputArea.className = 'anthill-chat-input';
    
    // Create input field
    chatInput = document.createElement('input');
    chatInput.type = 'text';
    chatInput.placeholder = 'Type your message...';
    
    // Create send button
    sendButton = document.createElement('button');
    sendButton.innerHTML = 'Send';
    
    // Create chat toggle button
    chatToggle = document.createElement('div');
    chatToggle.className = 'anthill-chat-toggle';
    chatToggle.innerHTML = '<span>Chat with us</span>';
    
    // Assemble the UI
    chatInputArea.appendChild(chatInput);
    chatInputArea.appendChild(sendButton);
    
    chatWindow.appendChild(chatHeader);
    chatWindow.appendChild(chatMessages);
    chatWindow.appendChild(chatInputArea);
    
    chatContainer.appendChild(chatWindow);
    chatContainer.appendChild(chatToggle);
    
    // Add the UI to the document
    document.body.appendChild(chatContainer);
    
    // Add the initial bot message
    addMessage('Hello! I\'m the Anthill IQ assistant. How can I help you today?', 'bot');
    
    // Add the stylesheet
    addStylesheet();
}

/**
 * Adds the chatbot stylesheet to the document
 */
function addStylesheet() {
    const style = document.createElement('style');
    style.textContent = `
        .anthill-chatbot {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            font-family: Arial, sans-serif;
        }
        
        .anthill-chat-toggle {
            background-color: #4A90E2;
            color: white;
            padding: 12px 20px;
            border-radius: 30px;
            cursor: pointer;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            transition: background-color 0.3s;
        }
        
        .anthill-chat-toggle:hover {
            background-color: #3A80D2;
        }
        
        .anthill-chat-window {
            position: absolute;
            bottom: 70px;
            right: 0;
            width: 320px;
            height: 400px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 5px 25px rgba(0, 0, 0, 0.2);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .anthill-chat-header {
            background-color: #4A90E2;
            color: white;
            padding: 10px 15px;
        }
        
        .anthill-chat-header h3 {
            margin: 0;
            padding: 0;
            font-size: 16px;
        }
        
        .anthill-chat-messages {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
        }
        
        .anthill-message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 20px;
            max-width: 80%;
            word-wrap: break-word;
        }
        
        .anthill-bot-message {
            background-color: #F1F0F0;
            align-self: flex-start;
            margin-right: auto;
        }
        
        .anthill-user-message {
            background-color: #4A90E2;
            color: white;
            align-self: flex-end;
            margin-left: auto;
        }
        
        .anthill-chat-input {
            display: flex;
            padding: 10px;
            border-top: 1px solid #E0E0E0;
        }
        
        .anthill-chat-input input {
            flex: 1;
            padding: 10px;
            border: 1px solid #E0E0E0;
            border-radius: 20px;
            outline: none;
        }
        
        .anthill-chat-input button {
            background-color: #4A90E2;
            color: white;
            border: none;
            border-radius: 20px;
            padding: 10px 15px;
            margin-left: 10px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        .anthill-chat-input button:hover {
            background-color: #3A80D2;
        }
    `;
    document.head.appendChild(style);
}

/**
 * Sends a message to the API and handles the response
 */
function sendMessage() {
    const message = chatInput.value.trim();
    
    if (!message) return;
    
    // Add the user message to the chat
    addMessage(message, 'user');
    
    // Clear the input
    chatInput.value = '';
    
    // Show loading indicator
    const loadingMessage = addMessage('...', 'bot');
    
    // Send the message to the API
    fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            user_id: USER_ID,
            session_id: SESSION_ID
        }),
    })
    .then(response => response.json())
    .then(data => {
        // Remove loading indicator
        chatMessages.removeChild(loadingMessage);
        
        // Add the bot response to the chat
        addMessage(data.response, 'bot');
        
        // Save the session ID if it's the first message
        if (!SESSION_ID && data.session_id) {
            SESSION_ID = data.session_id;
            saveSession();
        }
    })
    .catch(error => {
        // Remove loading indicator
        chatMessages.removeChild(loadingMessage);
        
        // Add error message
        addMessage('Sorry, there was an error. Please try again later.', 'bot');
        console.error('Error:', error);
    });
}

/**
 * Adds a message to the chat window
 * 
 * @param {string} text - The message text
 * @param {string} sender - Either 'user' or 'bot'
 * @returns {HTMLElement} - The created message element
 */
function addMessage(text, sender) {
    const messageElement = document.createElement('div');
    messageElement.className = `anthill-message anthill-${sender}-message`;
    messageElement.textContent = text;
    
    chatMessages.appendChild(messageElement);
    
    // Scroll to the bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageElement;
}

/**
 * Toggles the chat window visibility
 */
function toggleChat() {
    const isVisible = chatWindow.style.display !== 'none';
    
    if (isVisible) {
        chatWindow.style.display = 'none';
        chatToggle.innerHTML = '<span>Chat with us</span>';
    } else {
        chatWindow.style.display = 'flex';
        chatToggle.innerHTML = '<span>Close chat</span>';
        chatInput.focus();
    }
}

/**
 * Generates a unique user ID
 * 
 * @returns {string} - A unique user ID
 */
function generateUserId() {
    // Use Wix member ID if available
    // If using Wix's API, you would retrieve the member ID here
    
    // For non-logged-in users, generate a random ID and store in localStorage
    let userId = localStorage.getItem('anthillChatUserId');
    
    if (!userId) {
        userId = 'visitor_' + Math.random().toString(36).substring(2, 15);
        localStorage.setItem('anthillChatUserId', userId);
    }
    
    return userId;
}

/**
 * Saves the current session to localStorage
 */
function saveSession() {
    if (SESSION_ID) {
        localStorage.setItem('anthillChatSessionId', SESSION_ID);
    }
}

/**
 * Restores a previous session from localStorage
 */
function restoreSession() {
    const savedSessionId = localStorage.getItem('anthillChatSessionId');
    
    if (savedSessionId) {
        SESSION_ID = savedSessionId;
    }
} 