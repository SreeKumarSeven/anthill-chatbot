/**
 * Anthill IQ Chatbot Widget
 * This script manages the chatbot interface for the Wix widget
 */

// Configuration
const CONFIG = {
    API_URL: 'http://localhost:8088/api/chat',
    BOOKING_API_URL: 'http://localhost:8088/api/booking',
    INITIAL_MESSAGE: 'Hello! I\'m the Anthill IQ Assistant. How can I help you today?',
    BOOKING_KEYWORDS: [
        'book', 'appointment', 'consultation', 'schedule', 'reserve', 'meeting',
        'day pass', 'talk to someone', 'speak with', 'meet'
    ]
};

// Get DOM elements
const chatToggle = document.getElementById('chat-toggle');
const chatWindow = document.getElementById('chat-window');
const closeChat = document.getElementById('close-chat');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendMessage = document.getElementById('send-message');
const bookingForm = document.getElementById('booking-form');
const consultationForm = document.getElementById('consultation-form');
const cancelBooking = document.getElementById('cancel-booking');

// State management
let sessionId = null;
let isTyping = false;

// Initialize the chat widget
function initChatWidget() {
    // Show initial message
    appendMessage(CONFIG.INITIAL_MESSAGE, 'bot', 'welcome');
    
    // Set up event listeners
    chatToggle.addEventListener('click', toggleChat);
    closeChat.addEventListener('click', closeWidget);
    sendMessage.addEventListener('click', handleSendMessage);
    chatInput.addEventListener('keypress', handleInputKeypress);
    consultationForm.addEventListener('submit', handleBookingSubmit);
    cancelBooking.addEventListener('click', hideBookingForm);
    
    // Auto-resize textarea as user types
    chatInput.addEventListener('input', autoResizeTextarea);
}

// Toggle chat window visibility
function toggleChat() {
    chatWindow.classList.toggle('hidden');
    if (!chatWindow.classList.contains('hidden')) {
        chatInput.focus();
    }
}

// Close the chat widget
function closeWidget() {
    chatWindow.classList.add('hidden');
}

// Show the booking form
function showBookingForm() {
    bookingForm.classList.remove('hidden');
    chatInput.disabled = true;
    sendMessage.disabled = true;
}

// Hide the booking form
function hideBookingForm() {
    bookingForm.classList.add('hidden');
    chatInput.disabled = false;
    sendMessage.disabled = false;
    chatInput.focus();
}

// Append a message to the chat
function appendMessage(text, sender, source = '') {
    const messageWrapper = document.createElement('div');
    messageWrapper.className = 'message-wrapper';
    
    const message = document.createElement('div');
    message.className = `message ${sender}-message`;
    message.textContent = text;
    
    // Add source indicator for bot messages
    if (sender === 'bot' && source) {
        const sourceSpan = document.createElement('span');
        sourceSpan.className = 'message-source';
        sourceSpan.textContent = source;
        message.appendChild(sourceSpan);
    }
    
    messageWrapper.appendChild(message);
    
    const clearfix = document.createElement('div');
    clearfix.className = 'clearfix';
    messageWrapper.appendChild(clearfix);
    
    chatMessages.appendChild(messageWrapper);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Add quick reply buttons
function addQuickReplies(options) {
    const container = document.createElement('div');
    container.className = 'message-wrapper';
    
    const message = document.createElement('div');
    message.className = 'message bot-message';
    message.textContent = 'What would you like to book?';
    
    const repliesDiv = document.createElement('div');
    repliesDiv.className = 'quick-replies';
    
    options.forEach(option => {
        const button = document.createElement('button');
        button.className = 'quick-reply-button';
        button.textContent = option;
        button.addEventListener('click', () => {
            // Set form field if it exists
            const typeField = document.getElementById('booking-type');
            if (typeField) {
                typeField.value = option;
            }
            
            // Show booking form
            showBookingForm();
            
            // Send a message as user
            appendMessage(`I'd like to book a ${option}`, 'user');
        });
        repliesDiv.appendChild(button);
    });
    
    message.appendChild(repliesDiv);
    container.appendChild(message);
    
    const clearfix = document.createElement('div');
    clearfix.className = 'clearfix';
    container.appendChild(clearfix);
    
    chatMessages.appendChild(container);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show typing indicator
function showTypingIndicator() {
    if (isTyping) return;
    
    isTyping = true;
    const indicator = document.createElement('div');
    indicator.id = 'typing-indicator';
    indicator.className = 'typing-indicator';
    indicator.textContent = 'Anthill IQ is typing...';
    chatMessages.appendChild(indicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Hide typing indicator
function hideTypingIndicator() {
    isTyping = false;
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Auto-resize textarea as user types
function autoResizeTextarea() {
    chatInput.style.height = 'auto';
    chatInput.style.height = (chatInput.scrollHeight) + 'px';
}

// Check if a message contains booking intent
function containsBookingIntent(message) {
    const lowerMessage = message.toLowerCase();
    return CONFIG.BOOKING_KEYWORDS.some(keyword => lowerMessage.includes(keyword.toLowerCase()));
}

// Handle sending a message
async function handleSendMessage() {
    const userMessage = chatInput.value.trim();
    if (!userMessage) return;
    
    // Clear input and reset height
    chatInput.value = '';
    chatInput.style.height = 'auto';
    
    // Add user message to chat
    appendMessage(userMessage, 'user');
    
    // If message contains booking intent, show booking options
    if (containsBookingIntent(userMessage)) {
        addQuickReplies(['Day Pass', 'Consultation', 'Service Appointment']);
        return;
    }
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Prepare request data
        const requestData = {
            message: userMessage
        };
        
        // Add session ID if available
        if (sessionId) {
            requestData.session_id = sessionId;
        }
        
        // Send request to API
        const response = await fetch(CONFIG.API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        // Parse response
        const result = await response.json();
        
        // Save session ID
        if (result.session_id) {
            sessionId = result.session_id;
        }
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Check if this is a booking response
        if (result.source === 'booking') {
            // Add bot response
            appendMessage(result.response, 'bot', result.source);
            
            // Show booking options after a short delay
            setTimeout(() => {
                addQuickReplies(['Day Pass', 'Consultation', 'Service Appointment']);
            }, 1000);
        } else {
            // Add bot response
            appendMessage(result.response, 'bot', result.source);
        }
    } catch (error) {
        console.error('Error sending message:', error);
        hideTypingIndicator();
        appendMessage('Sorry, there was an error processing your request. Please try again later.', 'bot', 'error');
    }
}

// Handle input keypress (send message on Enter)
function handleInputKeypress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        handleSendMessage();
    }
}

// Handle booking form submission
async function handleBookingSubmit(event) {
    event.preventDefault();
    
    // Get form values
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    const datetime = document.getElementById('datetime').value;
    
    // Validate form
    if (!name || !email || !phone || !datetime) {
        alert('Please fill out all required fields.');
        return;
    }
    
    // Extract date and time
    const date = datetime.split('T')[0];
    const time = datetime.split('T')[1];
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Prepare booking data
        const bookingData = {
            name: name,
            email: email,
            phone: phone,
            service: 'Consultation',
            message: `Date: ${date}, Time: ${time}`
        };
        
        // Send booking request
        const response = await fetch(CONFIG.BOOKING_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(bookingData)
        });
        
        // Parse response
        const result = await response.json();
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Hide booking form
        hideBookingForm();
        
        // Format date for display
        const formattedDate = new Date(date).toLocaleDateString();
        
        // Add confirmation message
        appendMessage(`Thank you for your booking request! We've scheduled a consultation for you on ${formattedDate} at ${time}. We'll contact you at ${email} or ${phone} to confirm the details.`, 'bot', 'booking');
        
        // Reset form
        consultationForm.reset();
        
    } catch (error) {
        console.error('Error submitting booking:', error);
        hideTypingIndicator();
        appendMessage('Sorry, there was an error processing your booking. Please try again later.', 'bot', 'error');
        hideBookingForm();
    }
}

// Initialize the widget when the DOM is loaded
document.addEventListener('DOMContentLoaded', initChatWidget); 