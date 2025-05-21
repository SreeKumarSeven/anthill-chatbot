// Anthill IQ Chatbot Widget Loader
(function() {
    // Configuration - Replace with your deployed Vercel URL
    const CONFIG = {
        API_URL: 'https://your-vercel-deployment-url.vercel.app/api/chat',
        REGISTRATION_API_URL: 'https://your-vercel-deployment-url.vercel.app/api/register-user',
        WIDGET_TITLE: 'Anthill IQ Assistant'
    };

    // Create widget container
    const container = document.createElement('div');
    container.id = 'anthill-chat-widget';
    container.className = 'anthill-chat-widget';
    document.body.appendChild(container);
    
    // Inject widget styles
    const styles = document.createElement('style');
    styles.innerHTML = `
        .anthill-chat-widget {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif;
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 10000;
        }
        
        .chat-toggle {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #2a9a16, #228512);
            color: white;
            border: none;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.3s;
        }
        
        .chat-toggle:hover {
            transform: scale(1.05);
        }
        
        .chat-toggle-icon {
            font-size: 24px;
        }
        
        .chat-window {
            position: absolute;
            bottom: 80px;
            right: 0;
            width: 350px;
            height: 500px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #2a9a16, #228512);
            color: white;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chat-header h3 {
            margin: 0;
            font-size: 18px;
            font-weight: 500;
        }
        
        .close-button {
            background: none;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
        }
        
        .message {
            padding: 10px 15px;
            border-radius: 18px;
            margin-bottom: 10px;
            max-width: 80%;
            word-wrap: break-word;
        }
        
        .user-message {
            background-color: #2a9a16;
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 5px;
        }
        
        .bot-message {
            background-color: #f0f0f0;
            color: #333;
            align-self: flex-start;
            border-bottom-left-radius: 5px;
        }
        
        .registration-form {
            display: flex;
            flex-direction: column;
            padding: 20px;
        }
        
        .registration-form h4 {
            margin-top: 0;
            color: #2a9a16;
        }
        
        .registration-form input {
            margin-bottom: 12px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
        }
        
        .registration-form button {
            background: #2a9a16;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 6px;
            cursor: pointer;
        }
        
        .chat-input-area {
            padding: 15px;
            display: flex;
            border-top: 1px solid #eee;
        }
        
        .chat-input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 20px;
            outline: none;
            resize: none;
            max-height: 100px;
            min-height: 20px;
        }
        
        .send-button {
            background: #2a9a16;
            color: white;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-left: 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .hidden {
            display: none;
        }
    `;
    document.head.appendChild(styles);
    
    // Create widget HTML
    container.innerHTML = `
        <!-- Chat toggle button -->
        <button id="chat-toggle" class="chat-toggle" aria-label="Toggle chat">
            <span class="chat-toggle-icon">💬</span>
        </button>
        
        <!-- Chat window -->
        <div id="chat-window" class="chat-window hidden">
            <!-- Header -->
            <div class="chat-header">
                <h3>${CONFIG.WIDGET_TITLE}</h3>
                <button id="close-chat" class="close-button">×</button>
            </div>
            
            <!-- Messages container -->
            <div id="chat-messages" class="chat-messages"></div>
            
            <!-- Registration form (initially hidden) -->
            <div id="registration-form" class="registration-form hidden">
                <h4>Quick Registration</h4>
                <input type="text" id="name" placeholder="Your Name" required>
                <input type="tel" id="phone" placeholder="Phone Number" required>
                <button id="register-button">Start Chat</button>
            </div>
            
            <!-- Input area -->
            <div id="chat-input-area" class="chat-input-area">
                <textarea id="chat-input" class="chat-input" placeholder="Type your message..." rows="1"></textarea>
                <button id="send-message" class="send-button">➤</button>
            </div>
        </div>
    `;
    
    // Initialize state
    let state = {
        isOpen: false,
        sessionId: null,
        userId: null,
        isRegistered: false
    };
    
    // Helper functions
    function sendMessage(message) {
        if (!message.trim()) return;
        
        // Add user message to chat
        addMessageToChat(message, 'user');
        
        // Clear input
        document.getElementById('chat-input').value = '';
        
        // Send to backend
        fetch(CONFIG.API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                user_id: state.userId,
                session_id: state.sessionId
            })
        })
        .then(response => response.json())
        .then(data => {
            // Add bot response to chat
            addMessageToChat(data.response, 'bot');
            
            // Save session ID if provided
            if (data.session_id) {
                state.sessionId = data.session_id;
            }
            
            // Handle booking action if needed
            if (data.should_start_booking) {
                // Implement booking logic here
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessageToChat("I'm sorry, I'm having trouble connecting. Please try again later.", 'bot');
        });
    }
    
    function registerUser(name, phone) {
        fetch(CONFIG.REGISTRATION_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                phone: phone,
                session_id: state.sessionId
            })
        })
        .then(response => response.json())
        .then(data => {
            // Save user ID and session ID
            state.userId = data.user_id;
            state.sessionId = data.session_id;
            state.isRegistered = true;
            
            // Hide registration form, show chat
            document.getElementById('registration-form').classList.add('hidden');
            document.getElementById('chat-input-area').classList.remove('hidden');
            
            // Add welcome message
            addMessageToChat(`Welcome, ${name}! How can I help you today?`, 'bot');
        })
        .catch(error => {
            console.error('Error:', error);
            addMessageToChat("I'm sorry, I couldn't register you. Please try again.", 'bot');
        });
    }
    
    function addMessageToChat(text, sender) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender === 'user' ? 'user-message' : 'bot-message');
        messageElement.textContent = text;
        messagesContainer.appendChild(messageElement);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Event listeners
    document.getElementById('chat-toggle').addEventListener('click', function() {
        const chatWindow = document.getElementById('chat-window');
        state.isOpen = !state.isOpen;
        
        if (state.isOpen) {
            chatWindow.classList.remove('hidden');
            
            // Show registration form if not registered yet
            if (!state.isRegistered) {
                document.getElementById('registration-form').classList.remove('hidden');
                document.getElementById('chat-input-area').classList.add('hidden');
            }
        } else {
            chatWindow.classList.add('hidden');
        }
    });
    
    document.getElementById('close-chat').addEventListener('click', function() {
        document.getElementById('chat-window').classList.add('hidden');
        state.isOpen = false;
    });
    
    document.getElementById('send-message').addEventListener('click', function() {
        const message = document.getElementById('chat-input').value;
        sendMessage(message);
    });
    
    document.getElementById('chat-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            const message = this.value;
            sendMessage(message);
        }
    });
    
    document.getElementById('register-button').addEventListener('click', function() {
        const name = document.getElementById('name').value;
        const phone = document.getElementById('phone').value;
        
        if (name && phone) {
            registerUser(name, phone);
        } else {
            alert('Please fill in all fields');
        }
    });
    
    // Auto-resize textarea
    document.getElementById('chat-input').addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
})(); 