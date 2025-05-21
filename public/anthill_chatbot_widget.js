(function() {
    // Config variables
    const API_URL = 'https://anthill-chatbot-git-vercel-deploy-sreekumarseven.vercel.app/api';
    const WIDGET_URL = 'https://anthill-chatbot-git-vercel-deploy-sreekumarseven.vercel.app';
    const PRIMARY_COLOR = '#4a2c8f';
    const SECONDARY_COLOR = '#7e57c2';
    
    // Initial DOM setup
    function initializeWidget() {
        const widgetContainer = document.createElement('div');
        widgetContainer.id = 'anthill-chatbot-widget';
        widgetContainer.style.position = 'fixed';
        widgetContainer.style.bottom = '20px';
        widgetContainer.style.right = '20px';
        widgetContainer.style.zIndex = '9999';
        
        document.body.appendChild(widgetContainer);
        
        // Create the button
        const chatButton = document.createElement('div');
        chatButton.id = 'anthill-chat-button';
        chatButton.innerHTML = `
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2Z" fill="white"/>
            </svg>
        `;
        chatButton.style.width = '60px';
        chatButton.style.height = '60px';
        chatButton.style.borderRadius = '50%';
        chatButton.style.backgroundColor = PRIMARY_COLOR;
        chatButton.style.display = 'flex';
        chatButton.style.alignItems = 'center';
        chatButton.style.justifyContent = 'center';
        chatButton.style.cursor = 'pointer';
        chatButton.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
        chatButton.style.transition = 'all 0.3s ease';
        
        chatButton.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
        });
        
        chatButton.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
        
        // Chat window
        const chatWindow = document.createElement('div');
        chatWindow.id = 'anthill-chat-window';
        chatWindow.style.display = 'none';
        chatWindow.style.position = 'fixed';
        chatWindow.style.bottom = '90px';
        chatWindow.style.right = '20px';
        chatWindow.style.width = '350px';
        chatWindow.style.height = '500px';
        chatWindow.style.borderRadius = '10px';
        chatWindow.style.boxShadow = '0 5px 20px rgba(0,0,0,0.15)';
        chatWindow.style.overflow = 'hidden';
        chatWindow.style.transition = 'all 0.3s ease';
        chatWindow.style.zIndex = '9998';
        
        // Create iframe for the chat
        const chatIframe = document.createElement('iframe');
        chatIframe.src = `${WIDGET_URL}/iframe.html`;
        chatIframe.style.width = '100%';
        chatIframe.style.height = '100%';
        chatIframe.style.border = 'none';
        chatIframe.style.overflow = 'hidden';
        
        chatWindow.appendChild(chatIframe);
        
        // Toggle chat window
        chatButton.addEventListener('click', function() {
            if (chatWindow.style.display === 'none') {
                chatWindow.style.display = 'block';
                setTimeout(() => {
                    chatWindow.style.opacity = '1';
                }, 10);
            } else {
                chatWindow.style.opacity = '0';
                setTimeout(() => {
                    chatWindow.style.display = 'none';
                }, 300);
            }
        });
        
        // Add elements to container
        widgetContainer.appendChild(chatWindow);
        widgetContainer.appendChild(chatButton);
        
        // Add styles
        addStyles();
    }
    
    // Add global styles
    function addStyles() {
        const styleElement = document.createElement('style');
        styleElement.textContent = `
            #anthill-chat-button {
                transition: transform 0.2s ease;
            }
            #anthill-chat-button:hover {
                transform: scale(1.05);
            }
            #anthill-chat-window {
                opacity: 0;
                transition: opacity 0.3s ease;
            }
        `;
        document.head.appendChild(styleElement);
    }
    
    // Initialize when DOM is loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeWidget);
    } else {
        initializeWidget();
    }
})(); 