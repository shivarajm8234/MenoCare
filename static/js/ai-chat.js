document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const quickTopicButtons = document.querySelectorAll('.quick-topic-btn');
    const voiceButton = document.getElementById('voice-input');
    let isProcessing = false;
    let selectedLanguage = 'en-US'; // Default language

    // Available languages with their codes and names
    const languages = [
        { code: 'en-US', name: 'English (US)', flag: '🇺🇸' },
        { code: 'hi-IN', name: 'Hindi', flag: '🇮🇳' },
        { code: 'ta-IN', name: 'Tamil', flag: '🇮🇳' },
        { code: 'te-IN', name: 'Telugu', flag: '🇮🇳' },
        { code: 'kn-IN', name: 'Kannada', flag: '🇮🇳' },
        { code: 'ml-IN', name: 'Malayalam', flag: '🇮🇳' },
        { code: 'mr-IN', name: 'Marathi', flag: '🇮🇳' },
        { code: 'gu-IN', name: 'Gujarati', flag: '🇮🇳' },
        { code: 'bn-IN', name: 'Bengali', flag: '🇮🇳' }
    ];

    // Create language selector
    function createLanguageSelector() {
        const languageContainer = document.createElement('div');
        languageContainer.className = 'language-selector flex flex-wrap gap-2 mb-4';
        
        languages.forEach(lang => {
            const button = document.createElement('button');
            button.className = `lang-btn px-3 py-1.5 rounded-full text-sm flex items-center gap-1.5 ${
                selectedLanguage === lang.code ? 'bg-primary text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`;
            button.innerHTML = `${lang.flag} ${lang.name}`;
            button.onclick = () => {
                selectedLanguage = lang.code;
                document.querySelectorAll('.lang-btn').forEach(btn => {
                    btn.className = `lang-btn px-3 py-1.5 rounded-full text-sm flex items-center gap-1.5 ${
                        selectedLanguage === btn.dataset.code ? 'bg-primary text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`;
                });
                // Show welcome message in selected language
                appendMessage('assistant', welcomeMessages[selectedLanguage]);
            };
            button.dataset.code = lang.code;
            languageContainer.appendChild(button);
        });
        
        chatMessages.insertBefore(languageContainer, chatMessages.firstChild);
    }

    // Initialize language selector
    createLanguageSelector();

    // Function to send message to server
    async function sendMessage(message) {
        if (!message || isProcessing) return;
        
        isProcessing = true;
        appendMessage('user', message);
        appendTypingIndicator();
        
        try {
            const response = await fetch('/analyze_concerns', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    concerns: message,
                    language: selectedLanguage
                })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            removeTypingIndicator();
            
            if (data.success) {
                // Add AI response
                appendMessage('assistant', data.analysis);
                
                // Add follow-up questions if available
                if (data.follow_up_questions && data.follow_up_questions.length > 0) {
                    appendFollowUpQuestions(data.follow_up_questions);
                }
            } else {
                throw new Error(data.error || 'Failed to get response');
            }
        } catch (error) {
            console.error('Error:', error);
            appendMessage('system', 'Sorry, I encountered an error. Please try again.');
        } finally {
            isProcessing = false;
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    // Function to append message to chat
    function appendMessage(type, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type} flex items-start space-x-3 mb-4 ${type === 'user' ? 'justify-end' : ''}`;
        
        const textContainer = document.createElement('div');
        textContainer.className = `flex-grow max-w-[80%] p-3 rounded-lg ${
            type === 'user' ? 'bg-primary text-white' : 
            type === 'system' ? 'bg-red-100 text-red-700' : 
            'bg-gray-100 text-gray-800'
        }`;
        
        const formattedText = text.replace(/\n/g, '<br>');
        textContainer.innerHTML = formattedText;
        
        if (type === 'user') {
            messageDiv.appendChild(textContainer);
        } else {
            const iconContainer = document.createElement('div');
            iconContainer.className = 'flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center';
            iconContainer.innerHTML = '<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>';
            
            messageDiv.appendChild(iconContainer);
            messageDiv.appendChild(textContainer);
        }
        
        chatMessages.appendChild(messageDiv);
    }

    // Function to append typing indicator
    function appendTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator flex items-start space-x-3 mb-4';
        typingDiv.innerHTML = `
            <div class="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
                </svg>
            </div>
            <div class="flex-grow max-w-[80%] p-3 rounded-lg bg-gray-100">
                <div class="flex space-x-2">
                    <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                    <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                    <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                </div>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
    }

    // Function to remove typing indicator
    function removeTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    // Function to append follow-up questions
    function appendFollowUpQuestions(questions) {
        const followUpContainer = document.createElement('div');
        followUpContainer.className = 'follow-up-questions mt-4 space-y-2';
        
        const followUpTitle = document.createElement('p');
        followUpTitle.className = 'text-sm text-gray-600 mb-2';
        followUpTitle.textContent = selectedLanguage.startsWith('hi-') ? 
            'आप यह भी पूछ सकते हैं:' : 'You might also want to ask:';
        followUpContainer.appendChild(followUpTitle);
        
        questions.forEach(question => {
            const button = document.createElement('button');
            button.className = 'follow-up-btn block w-full text-left px-4 py-2 text-sm text-primary bg-primary/5 rounded-lg hover:bg-primary hover:text-white transition-colors';
            button.textContent = question;
            button.onclick = () => {
                chatInput.value = question;
                sendMessage(question);
            };
            followUpContainer.appendChild(button);
        });
        
        chatMessages.appendChild(followUpContainer);
    }

    // Handle form submission
    chatForm.onsubmit = (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (message) {
            sendMessage(message);
            chatInput.value = '';
        }
    };

    // Handle quick topic buttons
    quickTopicButtons.forEach(button => {
        button.onclick = () => {
            const topic = button.textContent.trim();
            chatInput.value = topic;
            sendMessage(topic);
        };
    });

    // Welcome messages
    const welcomeMessages = {
        'en-US': 'Welcome to MenoCare! I can help you with menstrual health, pregnancy, and menopause concerns.',
        'hi-IN': 'मेनोकेयर में आपका स्वागत है! मैं मासिक धर्म स्वास्थ्य, गर्भावस्था और रजोनिवृत्ति संबंधी चिंताओं में आपकी मदद कर सकती हूं।',
        'ta-IN': 'மெனோகேர்க்கு வரவேற்கிறோம்! மாதவிடாய் சுகாதாரம், கர்ப்பம் மற்றும் மாதவிடாய் நிறுத்தம் தொடர்பான கவலைகளில் நான் உங்களுக்கு உதவ முடியும்.',
        'te-IN': 'మెనోకేర్‌కి స్వాగతం! రుతు ఆరోగ్యం, గర్భధారణ మరియు రజస్వల సమస్యలలో నేను మీకు సహాయం చేయగలను.',
        'kn-IN': 'ಮೆನೋಕೇರ್‌ಗೆ ಸುಸ್ವಾಗತ! ಮುಟ್ಟಿನ ಆರೋಗ್ಯ, ಗರ್ಭಾವಸ್ಥೆ ಮತ್ತು ರಜೋನಿವೃತ್ತಿ ಕಾಳಜಿಗಳಲ್ಲಿ ನಾನು ನಿಮಗೆ ಸಹಾಯ ಮಾಡಬಲ್ಲೆ.',
        'ml-IN': 'മെനോകെയറിലേക്ക് സ്വാഗതം! ആർത്തവ ആരോഗ്യം, ഗർഭധാരണം, ആർത്തവവിരാമം എന്നിവയുമായി ബന്ധപ്പെട്ട ആശങ്കകളിൽ എനിക്ക് നിങ്ങളെ സഹായിക്കാൻ കഴിയും.',
        'mr-IN': 'मेनोकेअर मध्ये आपले स्वागत आहे! मी मासिक पाळी आरोग्य, गर्भधारणा आणि रजोनिवृत्ती संबंधित चिंतांमध्ये आपली मदत करू शकते.',
        'gu-IN': 'મેનોકેર માં આપનું સ્વાગત છે! હું માસિક ધર્મ આરોગ્ય, ગર્ભાવસ્થા અને રજોનિવૃત્તિ સંબંધિત ચિંતાઓમાં આપની મદદ કરી શકું છું.',
        'bn-IN': 'মেনোকেয়ারে স্বাগতম! আমি মাসিক স্বাস্থ্য, গর্ভাবস্থা এবং রজঃনিবৃত্তি সংক্রান্ত উদ্বেগে আপনাকে সাহায্য করতে পারি।'
    };

    // Health topics
    const healthTopics = {
        'en-US': ['Menstrual Health', 'Pregnancy Care', 'Menopause', 'Reproductive Health'],
        'hi-IN': ['मासिक धर्म स्वास्थ्य', 'गर्भावस्था देखभाल', 'रजोनिवृत्ति', 'प्रजनन स्वास्थ्य'],
        'ta-IN': ['மாதவிடாய் சுகாதாரம்', 'கர்ப்பகால பராமரிப்பு', 'மாதவிடாய் நிறுத்தம்', 'இனப்பெருக்க ஆரோக்கியம்'],
        'te-IN': ['రుతు ఆరోగ్యం', 'గర్భధారణ సంరక్షణ', 'రజస్వల', 'ప్రజనన ఆరోగ్యం'],
        'kn-IN': ['ಮುಟ್ಟಿನ ಆರೋಗ್ಯ', 'ಗರ್ಭಾವಸ್ಥೆ ಆರೈಕೆ', 'ರಜೋನಿವೃತ್ತಿ', 'ಸಂತಾನೋತ್ಪತ್ತಿ ಆರೋಗ್ಯ'],
        'ml-IN': ['ആർത്തവ ആരോഗ്യം', 'ഗർഭകാല പരിചരണം', 'ആർത്തവവിരാമം', 'പ്രത്യുൽപ്പാദന ആരോഗ്യം'],
        'mr-IN': ['मासिक पाळी आरोग्य', 'गर्भधारणा काळजी', 'रजोनिवृत्ती', 'प्रजनन आरोग्य'],
        'gu-IN': ['માસિક ધર્મ આરોગ્ય', 'સગર્ભાવસ્થા સંભાળ', 'રજોનિવૃત્તિ', 'પ્રજનન આરોગ્ય'],
        'bn-IN': ['মাসিক স্বাস্থ্য', 'গর্ভাবস্থার যত্ন', 'রজঃনিবৃত্তি', 'প্রজনন স্বাস্থ্য']
    };

    // Function to update health topics
    function updateHealthTopics(language) {
        const healthTopicContainer = document.getElementById('health-topics');
        if (healthTopicContainer) {
            healthTopicContainer.remove();
        }

        const healthTopicList = document.createElement('ul');
        healthTopicList.id = 'health-topics';
        healthTopicList.className = 'health-topics list-none m-0 p-0';

        healthTopics[language].forEach(topic => {
            const topicItem = document.createElement('li');
            topicItem.className = 'health-topic inline-block mr-4';
            topicItem.textContent = topic;
            healthTopicList.appendChild(topicItem);
        });

        chatMessages.appendChild(healthTopicList);
    }

    // Function to update quick topic buttons
    function updateQuickTopicButtons(isDisabled) {
        quickTopicButtons.forEach(button => {
            if (isDisabled) {
                button.disabled = true;
                button.className = 'quick-topic-btn disabled:opacity-50 disabled:cursor-not-allowed';
            } else {
                button.disabled = false;
                button.className = 'quick-topic-btn';
            }
        });
    }
});
