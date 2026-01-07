// // smart_school/static/js/ai_chat.js

// document.addEventListener('DOMContentLoaded', function () {
//     // Get all DOM elements safely
//     const chatButton     = document.getElementById('ai-chat-button');
//     const chatWindow     = document.getElementById('ai-chat-window');
//     const closeBtn       = document.getElementById('ai-chat-close');
//     const sendBtn        = document.getElementById('ai-chat-send');
//     const input          = document.getElementById('ai-chat-input');
//     const messages       = document.getElementById('ai-chat-messages');
//     const sidebarTrigger = document.getElementById('sidebar-ai-trigger');

//     // Safety check: if chat elements don't exist, stop early
//     if (!chatWindow || !messages || !input) {
//         console.warn('AI Chat widget elements not found on this page.');
//         return;
//     }

//     // === 1. Open chat via floating button ===
//     if (chatButton) {
//         chatButton.addEventListener('click', () => {
//             openChat();
//         });
//     }

//     // === 2. Open chat via sidebar menu ===
//     if (sidebarTrigger) {
//         sidebarTrigger.addEventListener('click', (e) => {
//             e.preventDefault();
//             openChat();
//         });
//     }

//     // === 3. Close chat ===
//     if (closeBtn) {
//         closeBtn.addEventListener('click', () => {
//             chatWindow.style.display = 'none';
//         });
//     }

//     // === Helper: Open chat function ===
//     function openChat() {
//         chatWindow.style.display = 'flex';
//         input.focus();
//         messages.scrollTop = messages.scrollHeight; // Scroll to bottom
//     }

//     // === 4. Welcome message on first open ===
//     let hasWelcomed = false;
//     const originalOpenChat = openChat;
//     openChat = function() {
//         originalOpenChat();
//         if (!hasWelcomed) {
//             addBotMessage("Hello! 👋 I'm your Elite International School AI Assistant. How can I help you today?");
//             hasWelcomed = true;
//         }
//     };

//     // === 5. Add bot message helper ===
//     function addBotMessage(text) {
//         const botMsg = document.createElement('div');
//         botMsg.className = 'message bot-message';
//         botMsg.textContent = text;
//         messages.appendChild(botMsg);
//         messages.scrollTop = messages.scrollHeight;
//     }

//     // === 6. Send message function ===
//     function sendMessage() {
//         const message = input.value.trim();
//         if (!message) return;

//         // Add user message
//         const userMsg = document.createElement('div');
//         userMsg.className = 'message user-message';
//         userMsg.textContent = message;
//         messages.appendChild(userMsg);

//         // Clear input
//         input.value = '';
//         messages.scrollTop = messages.scrollHeight;

//         // Show typing indicator
//         const typing = document.createElement('div');
//         typing.className = 'message bot-message';
//         typing.textContent = 'Typing...';
//         typing.id = 'typing-indicator';
//         messages.appendChild(typing);
//         messages.scrollTop = messages.scrollHeight;

//         // Send to backend
//         fetch('/ai/api/chat/', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//                 'X-CSRFToken': getCookie('csrftoken')
//             },
//             body: JSON.stringify({ message: message })
//         })
//         .then(response => {
//             if (!response.ok) throw new Error('Network error');
//             return response.json();
//         })
//         .then(data => {
//             // Remove typing
//             const typingEl = document.getElementById('typing-indicator');
//             if (typingEl) typingEl.remove();

//             // Add AI response
//             addBotMessage(data.response || "Sorry, I couldn't respond right now. Please try again.");
//         })
//         .catch(err => {
//             console.error('AI Chat Error:', err);
//             const typingEl = document.getElementById('typing-indicator');
//             if (typingEl) typingEl.remove();

//             addBotMessage("⚠️ Connection error. Please check your internet and try again.");
//         });
//     }

//     // === 7. Send triggers ===
//     if (sendBtn) {
//         sendBtn.addEventListener('click', sendMessage);
//     }

//     input.addEventListener('keypress', (e) => {
//         if (e.key === 'Enter' && !e.shiftKey) {
//             e.preventDefault();
//             sendMessage();
//         }
//     });

//     // === 8. Get CSRF token ===
//     function getCookie(name) {
//         let cookieValue = null;
//         if (document.cookie && document.cookie !== '') {
//             const cookies = document.cookie.split(';');
//             for (let i = 0; i < cookies.length; i++) {
//                 const cookie = cookies[i].trim();
//                 if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                     break;
//                 }
//             }
//         }
//         return cookieValue;
//     }

//     // Optional: Auto-open if URL has #ai-chat (for future links)
//     if (window.location.hash === '#ai-chat') {
//         openChat();
//     }
// });