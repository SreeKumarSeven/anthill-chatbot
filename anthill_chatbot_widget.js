/**
 * Anthill IQ Chatbot Widget for Wix integration
 * Version: 1.0.3
 */

(function() {
  // Configuration
  const CONFIG = {
    API_URL: 'https://abcd.herokuapp.com/api/chat',
    BOOKING_API_URL: 'https://abcd.herokuapp.com/api/booking',
    BOOKING_FORM_URL: 'https://abcd.herokuapp.com/booking_form.html',
    USER_REGISTRATION_API_URL: 'https://abcd.herokuapp.com/api/register-user',
    WIDGET_TITLE: 'Anthill IQ Assistant',
    PRIMARY_COLOR: '#6c63ff',
    SECONDARY_COLOR: '#4a44b9',
    CHAT_BUBBLE_USER: '#e6f2ff',
    CHAT_BUBBLE_BOT: '#f0f0f0',
    CHAT_TEXT_USER: '#333333',
    CHAT_TEXT_BOT: '#333333',
    BUTTON_TEXT_COLOR: '#ffffff',
    WIDGET_WIDTH: '350px',
    WIDGET_HEIGHT: '500px',
    WIDGET_POSITION: 'right', // 'right' or 'left'
    WIDGET_DISTANCE: '20px',
    WIDGET_BORDER_RADIUS: '10px',
    WIDGET_SHADOW: '0 5px 15px rgba(0, 0, 0, 0.1)',
    TYPING_INDICATOR_DELAY: 1000, // milliseconds
    BOOKING_KEYWORDS: ['book', 'booking', 'reserve', 'reservation', 'schedule', 'appointment']
  };

  // Variables to store state
  let sessionId = generateSessionId();
  let isTyping = false;
  let userData = { name: '', phone: '' };
  
  // DOM elements
  let chatWidget, chatToggle, chatWindow, chatMessages, closeButton;
  let userRegistrationForm, userNameInput, userPhoneInput, registrationSubmit;
  let chatInputArea, chatInput, sendButton, typingIndicator;
  let bookingForm;

  // Initialize the widget
  function init() {
    injectStyles();
    createChatWidget();
    addEventListeners();
    console.log('Anthill IQ Chatbot initialized with session ID:', sessionId);
  }

  // Create and inject necessary styles
  function injectStyles() {
    const styleEl = document.createElement('style');
    styleEl.textContent = `
      /* Modern Reset and Base Styles */
      .chat-widget * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }
      
      /* Main widget container */
      .chat-widget {
        position: fixed;
        bottom: ${CONFIG.WIDGET_DISTANCE};
        ${CONFIG.WIDGET_POSITION}: ${CONFIG.WIDGET_DISTANCE};
        z-index: 10000;
      }
      
      @keyframes pulse {
        0% {
          box-shadow: 0 4px 15px var(--shadow-light);
          transform: scale(1);
        }
        70% {
          box-shadow: 0 0 0 10px rgba(42, 154, 22, 0);
        }
        100% {
          box-shadow: 0 4px 15px var(--shadow-light);
          transform: scale(1);
        }
      }
      
      .chat-toggle {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background-color: ${CONFIG.PRIMARY_COLOR};
        color: ${CONFIG.BUTTON_TEXT_COLOR};
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: ${CONFIG.WIDGET_SHADOW};
        transition: all 0.3s ease;
        position: relative;
      }
      
      .chat-toggle:hover {
        background-color: ${CONFIG.SECONDARY_COLOR};
        transform: scale(1.05);
      }
      
      .chat-toggle:active {
        transform: scale(0.95);
        animation: none;
      }
      
      .chat-window {
        position: absolute;
        bottom: 70px;
        ${CONFIG.WIDGET_POSITION}: 0;
        width: ${CONFIG.WIDGET_WIDTH};
        height: ${CONFIG.WIDGET_HEIGHT};
        background: white;
        border-radius: ${CONFIG.WIDGET_BORDER_RADIUS};
        box-shadow: ${CONFIG.WIDGET_SHADOW};
        overflow: hidden;
        display: flex;
        flex-direction: column;
        transition: all 0.3s ease;
        opacity: 0;
        transform: translateY(20px);
        pointer-events: none;
      }
      
      .hidden {
        opacity: 0;
        visibility: hidden;
        pointer-events: none;
      }
      
      .chat-header {
        padding: 15px;
        background-color: ${CONFIG.PRIMARY_COLOR};
        color: ${CONFIG.BUTTON_TEXT_COLOR};
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
      }
      
      .chat-header h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        letter-spacing: 0.2px;
      }
      
      .close-button {
        background: none;
        border: none;
        color: ${CONFIG.BUTTON_TEXT_COLOR};
        cursor: pointer;
        font-size: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        transition: background-color 0.3s;
      }
      
      .close-button:hover {
        background-color: rgba(255, 255, 255, 0.1);
      }
      
      .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 15px;
        display: flex;
        flex-direction: column;
        gap: 10px;
      }
      
      .message {
        padding: 10px 15px;
        border-radius: 18px;
        margin-bottom: 10px;
        max-width: 80%;
        position: relative;
        line-height: 1.4;
        word-wrap: break-word;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
      }
      
      .bot-message {
        background-color: ${CONFIG.CHAT_BUBBLE_BOT};
        color: ${CONFIG.CHAT_TEXT_BOT};
        align-self: flex-start;
        margin-right: auto;
        border-bottom-left-radius: 5px;
      }
      
      .user-message {
        background-color: ${CONFIG.CHAT_BUBBLE_USER};
        color: ${CONFIG.CHAT_TEXT_USER};
        align-self: flex-end;
        margin-left: auto;
        border-bottom-right-radius: 5px;
      }
      
      .message-wrapper {
        display: flex;
        flex-direction: column;
        width: 100%;
      }
      
      .message-wrapper .bot-message {
        margin-right: auto;
        margin-left: 0;
      }
      
      .message-wrapper .user-message {
        margin-left: auto;
        margin-right: 0;
      }
      
      .typing-indicator {
        display: flex;
        align-items: center;
        gap: 5px;
        padding: 10px 15px;
        background-color: ${CONFIG.CHAT_BUBBLE_BOT};
        border-radius: 18px;
        border-bottom-left-radius: 5px;
        align-self: flex-start;
        max-width: 60px;
      }
      
      .user-registration-form {
        padding: 25px;
        display: flex;
        flex-direction: column;
        height: 100%;
        background-color: var(--bg-light);
      }
      
      .user-registration-form h4 {
        color: var(--primary-color);
        font-size: 20px;
        text-align: center;
        margin-bottom: 10px;
        position: relative;
        padding-bottom: 15px;
      }
      
      .user-registration-form h4:after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 50px;
        height: 3px;
        background-color: var(--primary-color);
        border-radius: 3px;
      }
      
      .user-registration-form p {
        text-align: center;
        margin-bottom: 20px;
        color: var(--text-light);
      }
      
      .user-registration-form input {
        width: 100%;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        font-size: 14px;
        transition: border-color 0.3s, box-shadow 0.3s;
      }
      
      .user-registration-form input:focus {
        outline: none;
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px var(--shadow-light);
      }
      
      .user-registration-form button {
        width: 100%;
        padding: 15px;
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: 10px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.3s, transform 0.2s;
      }
      
      .user-registration-form button:hover {
        background-color: var(--primary-dark);
        transform: translateY(-2px);
      }
      
      .chat-input-area {
        padding: 15px;
        background-color: white;
        border-top: 1px solid #e2e8f0;
        display: flex;
        align-items: center;
      }
      
      .chat-input {
        flex: 1;
        padding: 12px 15px;
        border: 1px solid #e2e8f0;
        border-radius: 24px;
        font-size: 14px;
        resize: none;
        outline: none;
        overflow-y: auto;
        max-height: 100px;
        transition: border-color 0.3s;
      }
      
      .chat-input:focus {
        border-color: var(--primary-color);
      }
      
      .send-button {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: var(--primary-color);
        color: white;
        border: none;
        margin-left: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: background-color 0.3s;
      }
      
      .send-button:hover {
        background-color: var(--primary-dark);
      }
      
      @media (max-width: 480px) {
        .chat-window {
          width: 90%;
          height: 80vh;
          bottom: 90px;
          right: 5%;
        }
      }
    `;
    document.head.appendChild(styleEl);
  }

  // Create chat widget DOM structure
  function createChatWidget() {
    // Main container
    chatWidget = document.createElement('div');
    chatWidget.className = 'chat-widget';
    
    // Chat toggle button
    chatToggle = document.createElement('button');
    chatToggle.className = 'chat-toggle';
    chatToggle.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
      </svg>
    `;
    
    // Chat window
    chatWindow = document.createElement('div');
    chatWindow.className = 'chat-window hidden';
    
    // Chat header
    const chatHeader = document.createElement('div');
    chatHeader.className = 'chat-header';
    chatHeader.innerHTML = `
      <h3>${CONFIG.WIDGET_TITLE}</h3>
      <button class="close-button">×</button>
    `;
    
    // User registration form
    userRegistrationForm = document.createElement('div');
    userRegistrationForm.className = 'user-registration-form';
    userRegistrationForm.innerHTML = `
      <h4>Welcome to Anthill IQ</h4>
      <p>Please provide your details to continue</p>
      <form id="user-registration">
        <input type="text" id="user-name" placeholder="Your Name *" required>
        <input type="tel" id="user-phone" placeholder="Your Phone Number (10 digits) *" pattern="[0-9]{10}" title="Please enter exactly 10 digits" required>
        <button type="submit">Start Chat</button>
      </form>
    `;
    
    // Chat messages area
    chatMessages = document.createElement('div');
    chatMessages.className = 'chat-messages hidden';
    
    // Typing indicator
    typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.textContent = 'Anthill IQ Assistant is typing';
    chatMessages.appendChild(typingIndicator);
    
    // Chat input area
    chatInputArea = document.createElement('div');
    chatInputArea.className = 'chat-input-area hidden';
    
    chatInput = document.createElement('textarea');
    chatInput.className = 'chat-input';
    chatInput.placeholder = 'Type your message...';
    chatInput.rows = 1;
    
    sendButton = document.createElement('button');
    sendButton.className = 'send-button';
    sendButton.innerHTML = `
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M22 2L11 13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `;
    
    // Assemble the widget
    chatInputArea.appendChild(chatInput);
    chatInputArea.appendChild(sendButton);
    
    chatWindow.appendChild(chatHeader);
    chatWindow.appendChild(userRegistrationForm);
    chatWindow.appendChild(chatMessages);
    chatWindow.appendChild(chatInputArea);
    
    chatWidget.appendChild(chatToggle);
    chatWidget.appendChild(chatWindow);
    
    // Add to document
    document.body.appendChild(chatWidget);
    
    // Cache DOM elements
    closeButton = chatHeader.querySelector('.close-button');
    userNameInput = document.getElementById('user-name');
    userPhoneInput = document.getElementById('user-phone');
    registrationSubmit = document.getElementById('user-registration');
  }

  // Add event listeners
  function addEventListeners() {
    // Toggle chat window
    chatToggle.addEventListener('click', toggleChat);
    
    // Close chat window
    closeButton.addEventListener('click', closeChat);
    
    // Handle user registration
    registrationSubmit.addEventListener('submit', handleUserRegistration);
    
    // Send message on button click
    sendButton.addEventListener('click', sendMessage);
    
    // Send message on Enter key (but allow Shift+Enter for new line)
    chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
    
    // Auto-resize textarea
    chatInput.addEventListener('input', autoResizeTextarea);
  }

  // Toggle chat window visibility
  function toggleChat() {
    const isHidden = chatWindow.classList.contains('hidden');
    
    if (isHidden) {
      chatWindow.classList.remove('hidden');
    } else {
      chatWindow.classList.add('hidden');
    }
  }
  
  // Autoresize textarea
  function autoResizeTextarea() {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 100) + 'px';
  }

  // Close chat window
  function closeChat() {
    chatWindow.classList.add('hidden');
  }

  // Handle user registration
  function handleUserRegistration(e) {
    e.preventDefault();
    
    // Get user info
    const name = userNameInput.value.trim();
    const phone = userPhoneInput.value.trim();
    
    // Validate
    if (!name || !phone) {
      alert('Please fill out all required fields.');
      return;
    }
    
    if (phone.length !== 10 || !/^\d+$/.test(phone)) {
      alert('Please enter a valid 10-digit phone number.');
      return;
    }
    
    // Save user data
    userData = { name, phone };
    
    // Prepare data for API
    const requestData = {
      name: name,
      phone: phone,
      timestamp: new Date().toISOString(),
      session_id: sessionId
    };
    
    // Send registration to backend
    fetch(CONFIG.USER_REGISTRATION_API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
      console.log('Registration successful:', data);
    })
    .catch(error => {
      console.error('Error registering user:', error);
    });
    
    // Show chat interface
    userRegistrationForm.classList.add('hidden');
    chatMessages.classList.remove('hidden');
    chatInputArea.classList.remove('hidden');
    
    // Add welcome message
    addBotMessage(`Hello ${name}! ${CONFIG.WIDGET_TITLE} is ready to help you.`);
  }

  // Add a bot message
  function addBotMessage(text) {
    showTypingIndicator();
    
    // Simulate typing delay based on message length
    const delay = Math.min(1000, Math.max(800, text.length * 30));
    
    setTimeout(() => {
      hideTypingIndicator();
      
      const wrapper = document.createElement('div');
      wrapper.className = 'message-wrapper';
      
      const messageEl = document.createElement('div');
      messageEl.className = 'message bot-message';
      
      // Format text - convert URLs to links and replace newlines with <br>
      const formattedText = text
        .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" style="color: #2a9a16; text-decoration: underline;">$1</a>')
        .replace(/\n/g, '<br>');
      
      messageEl.innerHTML = formattedText;
      wrapper.appendChild(messageEl);
      
      chatMessages.appendChild(wrapper);
      scrollToBottom();
    }, delay);
  }

  // Add a user message
  function addUserMessage(text) {
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper';
    
    const messageEl = document.createElement('div');
    messageEl.className = 'message user-message';
    messageEl.textContent = text;
    
    wrapper.appendChild(messageEl);
    chatMessages.appendChild(wrapper);
    scrollToBottom();
  }

  // Show typing indicator
  function showTypingIndicator() {
    typingIndicator.style.display = 'block';
    scrollToBottom();
  }

  // Hide typing indicator
  function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
  }

  // Send message to backend
  function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addUserMessage(message);
    
    // Clear input
    chatInput.value = '';
    chatInput.style.height = 'auto';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Prepare data for API
    const requestData = {
      message: message,
      user_id: userData.name || 'Guest',
      session_id: sessionId
    };
    
    // Send to backend API
    fetch(CONFIG.API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestData)
    })
    .then(response => {
      if (!response.ok) throw new Error('Failed to get response');
      return response.json();
    })
    .then(data => {
      hideTypingIndicator();
      
      // Add response to chat
      if (data && data.response) {
        addBotMessage(data.response);
      } else {
        addBotMessage("I'm sorry, I couldn't process that request properly. Please try again.");
      }
    })
    .catch(error => {
      console.error('API error:', error);
      hideTypingIndicator();
      
      // Fallback response
      addBotMessage("I'm having trouble connecting to our services. Please try again later or contact us directly at connect@anthilliq.com.");
    });
  }

  // Scroll chat to bottom
  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // Generate session ID
  function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substring(2, 9);
  }

  // Check if we're in iframe mode
  function isIframeMode() {
    return window.ANTHILL_CONFIG && window.ANTHILL_CONFIG.iframeMode;
  }

  // Initialize when the DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
