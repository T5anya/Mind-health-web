const { useState, useEffect, useRef } = React;

// Multilingual translations
const translations = {
  english: {
    title: "Mental Health Support 💙",
    placeholder: "Type your message here...",
    send: "Send",
    moodQuestion: "How are you feeling today?",
    languageLabel: "Language:",
    greeting: "Hello! I'm here to support you. How are you feeling today? 😊",
    moodLabels: {
      happy: "Happy",
      sad: "Sad", 
      anxious: "Anxious",
      angry: "Angry",
      calm: "Calm",
      confused: "Confused"
    }
  },
  hindi: {
    title: "मानसिक स्वास्थ्य सहायता 💙",
    placeholder: "यहाँ अपना संदेश लिखें...",
    send: "भेजें",
    moodQuestion: "आज आप कैसा महसूस कर रहे हैं?",
    languageLabel: "भाषा:",
    greeting: "नमस्ते! मैं आपकी सहायता के लिए यहाँ हूँ। आज आप कैसा महसूस कर रहे हैं? 😊",
    moodLabels: {
      happy: "खुश",
      sad: "उदास",
      anxious: "चिंतित",
      angry: "गुस्सा",
      calm: "शांत",
      confused: "भ्रमित"
    }
  },
  marathi: {
    title: "मानसिक आरोग्य सहाय्य 💙",
    placeholder: "तुमचा संदेश येथे टाइप करा...",
    send: "पाठवा",
    moodQuestion: "आज तुम्ही कसे वाटत आहात?",
    languageLabel: "भाषा:",
    greeting: "नमस्कार! मी तुमच्या मदतीसाठी येथे आहे। आज तुम्ही कसे वाटत आहात? 😊",
    moodLabels: {
      happy: "आनंदी",
      sad: "दुःखी",
      anxious: "चिंताग्रस्त",
      angry: "रागावलेला",
      calm: "शांत",
      confused: "गोंधळलेला"
    }
  },
  kannada: {
    title: "ಮಾನಸಿಕ ಆರೋಗ್ಯ ಬೆಂಬಲ 💙",
    placeholder: "ನಿಮ್ಮ ಸಂದೇಶವನ್ನು ಇಲ್ಲಿ ಟೈಪ್ ಮಾಡಿ...",
    send: "ಕಳುಹಿಸಿ",
    moodQuestion: "ಇಂದು ನೀವು ಹೇಗೆ ಅನಿಸುತ್ತಿದೆ?",
    languageLabel: "ಭಾಷೆ:",
    greeting: "ನಮಸ್ಕಾರ! ನಿಮ್ಮನ್ನು ಬೆಂಬಲಿಸಲು ನಾನು ಇಲ್ಲಿದ್ದೇನೆ। ಇಂದು ನೀವು ಹೇಗೆ ಅನಿಸುತ್ತಿದೆ? 😊",
    moodLabels: {
      happy: "ಸಂತೋಷ",
      sad: "ದುಃಖ",
      anxious: "ಆತಂಕ",
      angry: "ಕೋಪ",
      calm: "ಶಾಂತ",
      confused: "ಗೊಂದಲ"
    }
  }
};

// Mental health responses
const mentalHealthResponses = {
  depression: {
    english: ["I understand you're going through a tough time. Remember, it's okay to feel this way, and you're not alone. 🤗 Try taking small steps like going for a walk or talking to someone you trust.",
              "Depression can feel overwhelming, but you're stronger than you know. 💪 Consider practicing deep breathing exercises or journaling your thoughts."],
    hindi: ["मैं समझ सकता हूँ कि आप कठिन समय से गुजर रहे हैं। याद रखें, ऐसा महसूस करना ठीक है, और आप अकेले नहीं हैं। 🤗 छोटे कदम उठाने की कोशिश करें जैसे टहलना या किसी विश्वसनीय व्यक्ति से बात करना।"],
    marathi: ["मला समजते की तुम्ही कठीण काळातून जात आहात। लक्षात ठेवा, असे वाटणे सामान्य आहे, आणि तुम्ही एकटे नाही आहात। 🤗 लहान पावले उचलण्याचा प्रयत्न करा जसे फिरायला जाणे किंवा तुमच्या विश्वासू व्यक्तीशी बोलणे।"],
    kannada: ["ನೀವು ಕಷ್ಟದ ಸಮಯದಲ್ಲಿದ್ದೀರಿ ಎಂದು ನನಗೆ ಅರ್ಥವಾಗುತ್ತದೆ। ನೆನಪಿಡಿ, ಹೀಗೆ ಅನಿಸುವುದು ಸಾಮಾನ್ಯ, ಮತ್ತು ನೀವು ಒಬ್ಬಂಟಿಗರಲ್ಲ। 🤗 ನಡೆಯಲು ಹೋಗುವುದು ಅಥವಾ ನಂಬಿಕೆಯ ವ್ಯಕ್ತಿಯೊಂದಿಗೆ ಮಾತನಾಡುವಂತಹ ಸಣ್ಣ ಹೆಜ್ಜೆಗಳನ್ನು ತೆಗೆದುಕೊಳ್ಳಲು ಪ್ರಯತ್ನಿಸಿ।"]
  },
  anxiety: {
    english: ["Anxiety can be really challenging. Try the 4-7-8 breathing technique: breathe in for 4, hold for 7, exhale for 8. 🌬️ You're going to get through this.",
              "I hear you're feeling anxious. Ground yourself by naming 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste. 🧘‍♀️"],
    hindi: ["चिंता वास्तव में चुनौतीपूर्ण हो सकती है। 4-7-8 सांस लेने की तकनीक आज़माएं: 4 के लिए सांस लें, 7 के लिए रोकें, 8 के लिए छोड़ें। 🌬️ आप इससे निकल जाएंगे।"],
    marathi: ["चिंता खरोखरच आव्हानात्मक असू शकते। 4-7-8 श्वास तंत्र वापरून पहा: 4 साठी श्वास घ्या, 7 साठी धरा, 8 साठी सोडा। 🌬️ तुम्ही यातून बाहेर पडाल।"],
    kannada: ["ಆತಂಕವು ನಿಜವಾಗಿಯೂ ಸವಾಲಿನದ್ದಾಗಿರಬಹುದು। 4-7-8 ಉಸಿರಾಟದ ತಂತ್ರವನ್ನು ಪ್ರಯತ್ನಿಸಿ: 4 ಕ್ಕೆ ಉಸಿರು ತೆಗೆದುಕೊಳ್ಳಿ, 7 ಕ್ಕೆ ಹಿಡಿದಿಟ್ಟುಕೊಳ್ಳಿ, 8 ಕ್ಕೆ ಬಿಡಿ। 🌬️ ನೀವು ಇದನ್ನು ಜಯಿಸುವಿರಿ।"]
  },
  stress: {
    english: ["Stress is your body's way of responding to challenges. Take a moment to pause and breathe deeply. 🌸 Consider breaking your tasks into smaller, manageable pieces.",
              "I can sense you're feeling stressed. Try progressive muscle relaxation or listen to calming music. 🎵 Remember to be kind to yourself."],
    hindi: ["तनाव आपके शरीर का चुनौतियों का जवाब देने का तरीका है। एक पल रुकें और गहरी सांस लें। 🌸 अपने कार्यों को छोटे, प्रबंधनीय टुकड़ों में बांटने पर विचार करें।"],
    marathi: ["तणाव हा तुमच्या शरीराचा आव्हानांना प्रतिसाद देण्याचा मार्ग आहे। एक क्षण थांबा आणि खोल श्वास घ्या। 🌸 तुमची कामे लहान, व्यवस्थापन करण्यायोग्य भागांमध्ये विभागण्याचा विचार करा।"],
    kannada: ["ಒತ್ತಡವು ಸವಾಲುಗಳಿಗೆ ಪ್ರತಿಕ್ರಿಯಿಸುವ ನಿಮ್ಮ ದೇಹದ ವಿಧಾನವಾಗಿದೆ। ಒಂದು ಕ್ಷಣ ವಿರಾಮ ತೆಗೆದುಕೊಂಡು ಆಳವಾಗಿ ಉಸಿರಾಡಿ। 🌸 ನಿಮ್ಮ ಕಾರ್ಯಗಳನ್ನು ಸಣ್ಣ, ನಿರ್ವಹಿಸಬಹುದಾದ ಭಾಗಗಳಾಗಿ ವಿಭಜಿಸುವುದನ್ನು ಪರಿಗಣಿಸಿ।"]
  }
};

function MentalHealthChatbox() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [currentLanguage, setCurrentLanguage] = useState('english');
  const [userMood, setUserMood] = useState(null);
  const [showMoodSelector, setShowMoodSelector] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    // Initial greeting
    setMessages([{
      text: translations[currentLanguage].greeting,
      sender: 'bot',
      timestamp: new Date().toLocaleTimeString()
    }]);
    setShowMoodSelector(true);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleMoodSelection = (mood) => {
    setUserMood(mood);
    setShowMoodSelector(false);
    
    const moodMessage = {
      text: `${translations[currentLanguage].moodLabels[mood]} ${getMoodEmoji(mood)}`,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };
    
    const botResponse = generateMoodResponse(mood);
    
    setMessages(prev => [...prev, moodMessage, botResponse]);
  };

  const getMoodEmoji = (mood) => {
    const emojiMap = {
      happy: '😊',
      sad: '😢',
      anxious: '😰',
      angry: '😠',
      calm: '😌',
      confused: '😕'
    };
    return emojiMap[mood] || '😐';
  };

  const generateMoodResponse = (mood) => {
    let responseText = '';
    
    if (mood === 'sad') {
      responseText = mentalHealthResponses.depression[currentLanguage][0];
    } else if (mood === 'anxious') {
      responseText = mentalHealthResponses.anxiety[currentLanguage][0];
    } else if (mood === 'angry') {
      responseText = mentalHealthResponses.stress[currentLanguage][0];
    } else if (mood === 'happy') {
      responseText = currentLanguage === 'english' ? "That's wonderful to hear! 🌟 Keep nurturing those positive feelings. What's bringing you joy today?" :
                   currentLanguage === 'hindi' ? "यह सुनकर बहुत अच्छा लगा! 🌟 इन सकारात्मक भावनाओं को बनाए रखें। आज आपको क्या खुशी दे रहा है?" :
                   currentLanguage === 'marathi' ? "हे ऐकून खूप आनंद झाला! 🌟 या सकारात्मक भावनांना वाढवत रहा। आज तुम्हाला काय आनंद देत आहे?" :
                   "ಇದನ್ನು ಕೇಳಿ ತುಂಬಾ ಸಂತೋಷವಾಯಿತು! 🌟 ಈ ಧನಾತ್ಮಕ ಭಾವನೆಗಳನ್ನು ಪೋಷಿಸುತ್ತಲೇ ಇರಿ। ಇಂದು ನಿಮಗೆ ಸಂತೋಷ ತರುತ್ತಿರುವುದು ಏನು?";
    } else if (mood === 'calm') {
      responseText = currentLanguage === 'english' ? "It's great that you're feeling calm! 🧘‍♀️ This is a perfect state for reflection and mindfulness. How can I support you today?" :
                   currentLanguage === 'hindi' ? "यह बहुत अच्छा है कि आप शांत महसूस कर रहे हैं! 🧘‍♀️ यह चिंतन और सचेतता के लिए एक आदर्श स्थिति है। आज मैं आपकी कैसे सहायता कर सकता हूँ?" :
                   currentLanguage === 'marathi' ? "तुम्ही शांत वाटत आहात हे खूप चांगले आहे! 🧘‍♀️ ही चिंतन आणि जागरूकतेसाठी एक आदर्श स्थिती आहे। आज मी तुमची कशी मदत करू शकतो?" :
                   "ನೀವು ಶಾಂತವಾಗಿ ಅನಿಸುತ್ತಿರುವುದು ಬಹಳ ಒಳ್ಳೆಯದು! 🧘‍♀️ ಇದು ಚಿಂತನೆ ಮತ್ತು ಸಾವಧಾನತೆಗೆ ಪರಿಪೂರ್ಣ ಸ್ಥಿತಿ. ಇಂದು ನಾನು ನಿಮ್ಮನ್ನು ಹೇಗೆ ಬೆಂಬಲಿಸಬಹುದು?";
    } else {
      responseText = currentLanguage === 'english' ? "Thank you for sharing how you're feeling. I'm here to listen and support you. 💙 What would you like to talk about?" :
                   currentLanguage === 'hindi' ? "आपने अपनी भावनाएं साझा करने के लिए धन्यवाद। मैं सुनने और आपका समर्थन करने के लिए यहाँ हूँ। 💙 आप किस बारे में बात करना चाहेंगे?" :
                   currentLanguage === 'marathi' ? "तुमच्या भावना सामायिक केल्याबद्दल धन्यवाद। मी ऐकण्यासाठी आणि तुमचे समर्थन करण्यासाठी येथे आहे। 💙 तुम्हाला कशाबद्दल बोलायचे आहे?" :
                   "ನಿಮ್ಮ ಭಾವನೆಗಳನ್ನು ಹಂಚಿಕೊಂಡಿದ್ದಕ್ಕಾಗಿ ಧನ್ಯವಾದಗಳು. ನಾನು ಕೇಳಲು ಮತ್ತು ನಿಮ್ಮನ್ನು ಬೆಂಬಲಿಸಲು ಇಲ್ಲಿದ್ದೇನೆ। 💙 ನೀವು ಯಾವುದರ ಬಗ್ಗೆ ಮಾತನಾಡಲು ಬಯಸುತ್ತೀರಿ?";
    }
    
    return {
      text: responseText,
      sender: 'bot',
      timestamp: new Date().toLocaleTimeString()
    };
  };

  const generateBotResponse = (userMessage) => {
    const lowerMessage = userMessage.toLowerCase();
    let response = '';
    
    if (lowerMessage.includes('sad') || lowerMessage.includes('depressed') || lowerMessage.includes('down') ||
        lowerMessage.includes('उदास') || lowerMessage.includes('दुखी') || lowerMessage.includes('ದುಃಖ')) {
      response = mentalHealthResponses.depression[currentLanguage][Math.floor(Math.random() * mentalHealthResponses.depression[currentLanguage].length)];
    } else if (lowerMessage.includes('anxious') || lowerMessage.includes('worried') || lowerMessage.includes('panic') ||
               lowerMessage.includes('चिंतित') || lowerMessage.includes('चिंताग्रस्त') || lowerMessage.includes('ಆತಂಕ')) {
      response = mentalHealthResponses.anxiety[currentLanguage][Math.floor(Math.random() * mentalHealthResponses.anxiety[currentLanguage].length)];
    } else if (lowerMessage.includes('stress') || lowerMessage.includes('overwhelmed') || lowerMessage.includes('pressure') ||
               lowerMessage.includes('तनाव') || lowerMessage.includes('तणाव') || lowerMessage.includes('ಒತ್ತಡ')) {
      response = mentalHealthResponses.stress[currentLanguage][Math.floor(Math.random() * mentalHealthResponses.stress[currentLanguage].length)];
    } else {
      const genericResponses = {
        english: ["I hear you. Can you tell me more about what you're experiencing? 🤗", "Thank you for sharing that with me. How long have you been feeling this way? 💙", "That sounds challenging. What do you think might help you feel better? 🌟"],
        hindi: ["मैं आपकी बात सुन रहा हूँ। क्या आप मुझे बता सकते हैं कि आप क्या अनुभव कर रहे हैं? 🤗", "मेरे साथ साझा करने के लिए धन्यवाद। आप कितने समय से ऐसा महसूस कर रहे हैं? 💙"],
        marathi: ["मी तुमचे ऐकत आहे। तुम्ही मला सांगू शकता का की तुम्ही काय अनुभवत आहात? 🤗", "माझ्याशी सामायिक केल्याबद्दल धन्यवाद। तुम्ही किती काळापासून असे वाटत आहे? 💙"],
        kannada: ["ನಾನು ನಿಮ್ಮ ಮಾತು ಕೇಳುತ್ತಿದ್ದೇನೆ. ನೀವು ಏನನ್ನು ಅನುಭವಿಸುತ್ತಿದ್ದೀರಿ ಎಂದು ನನಗೆ ಹೆಚ್ಚು ಹೇಳಬಹುದೇ? 🤗", "ನನ್ನೊಂದಿಗೆ ಹಂಚಿಕೊಂಡಿದ್ದಕ್ಕಾಗಿ ಧನ್ಯವಾದಗಳು. ನೀವು ಎಷ್ಟು ಕಾಲದಿಂದ ಹೀಗೆ ಅನಿಸುತ್ತಿದೆ? 💙"]
      };
      response = genericResponses[currentLanguage][Math.floor(Math.random() * genericResponses[currentLanguage].length)];
    }
    
    return {
      text: response,
      sender: 'bot',
      timestamp: new Date().toLocaleTimeString()
    };
  };

  const handleSendMessage = () => {
    if (inputValue.trim() === '') return;
    
    const userMessage = {
      text: inputValue,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };
    
    const botResponse = generateBotResponse(inputValue);
    
    setMessages(prev => [...prev, userMessage, botResponse]);
    setInputValue('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="chatbox-container">
      <div className="chatbox-header">
        <h2>{translations[currentLanguage].title}</h2>
        <div className="language-selector">
          <label>{translations[currentLanguage].languageLabel}</label>
          <select 
            value={currentLanguage} 
            onChange={(e) => setCurrentLanguage(e.target.value)}
          >
            <option value="english">English</option>
            <option value="hindi">हिंदी</option>
            <option value="marathi">मराठी</option>
            <option value="kannada">ಕನ್ನಡ</option>
          </select>
        </div>
      </div>
      
      {showMoodSelector && (
        <div className="mood-selector">
          <p>{translations[currentLanguage].moodQuestion}</p>
          <div className="mood-buttons">
            {Object.keys(translations[currentLanguage].moodLabels).map(mood => (
              <button 
                key={mood}
                className="mood-btn"
                onClick={() => handleMoodSelection(mood)}
              >
                {getMoodEmoji(mood)} {translations[currentLanguage].moodLabels[mood]}
              </button>
            ))}
          </div>
        </div>
      )}
      
      <div className="messages-container">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.sender}`}>
            <div className="message-content">
              <p>{message.text}</p>
              <span className="timestamp">{message.timestamp}</span>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="input-container">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={translations[currentLanguage].placeholder}
          className="message-input"
        />
        <button onClick={handleSendMessage} className="send-btn">
          {translations[currentLanguage].send} 📤
        </button>
      </div>
      
      <style jsx>{`
        .chatbox-container {
          background: rgba(0, 0, 0, 0.9);
          border-radius: 20px;
          height: 100%;
          display: flex;
          flex-direction: column;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .chatbox-header {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          padding: 20px;
          border-radius: 20px 20px 0 0;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .chatbox-header h2 {
          margin: 0;
          font-size: 1.2rem;
          font-weight: 600;
        }
        
        .language-selector {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        
        .language-selector label {
          font-size: 0.9rem;
          font-weight: 500;
        }
        
        .language-selector select {
          background: rgba(255, 255, 255, 0.2);
          border: none;
          color: white;
          padding: 5px 10px;
          border-radius: 8px;
          font-size: 0.9rem;
        }
        
        .mood-selector {
          background: rgba(255, 255, 255, 0.05);
          padding: 20px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .mood-selector p {
          color: #e0e0e0;
          margin-bottom: 15px;
          font-weight: 500;
        }
        
        .mood-buttons {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 10px;
        }
        
        .mood-btn {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border: none;
          color: white;
          padding: 10px 15px;
          border-radius: 12px;
          cursor: pointer;
          font-size: 0.9rem;
          font-weight: 500;
          transition: all 0.3s ease;
        }
        
        .mood-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .messages-container {
          flex: 1;
          overflow-y: auto;
          padding: 20px;
          display: flex;
          flex-direction: column;
          gap: 15px;
        }
        
        .message {
          display: flex;
          max-width: 80%;
        }
        
        .message.user {
          align-self: flex-end;
        }
        
        .message.bot {
          align-self: flex-start;
        }
        
        .message-content {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          padding: 12px 16px;
          border-radius: 18px;
          position: relative;
          animation: fadeIn 0.3s ease;
        }
        
        .message.user .message-content {
          background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
          border-radius: 18px 18px 5px 18px;
        }
        
        .message.bot .message-content {
          border-radius: 18px 18px 18px 5px;
        }
        
        .message-content p {
          margin: 0 0 5px 0;
          line-height: 1.4;
        }
        
        .timestamp {
          font-size: 0.7rem;
          opacity: 0.7;
        }
        
        .input-container {
          padding: 20px;
          display: flex;
          gap: 10px;
          border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .message-input {
          flex: 1;
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: white;
          padding: 12px 16px;
          border-radius: 25px;
          font-size: 1rem;
          outline: none;
          transition: all 0.3s ease;
        }
        
        .message-input:focus {
          border-color: #667eea;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
        }
        
        .message-input::placeholder {
          color: rgba(255, 255, 255, 0.6);
        }
        
        .send-btn {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border: none;
          color: white;
          padding: 12px 20px;
          border-radius: 25px;
          cursor: pointer;
          font-weight: 600;
          transition: all 0.3s ease;
        }
        
        .send-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .messages-container::-webkit-scrollbar {
          width: 6px;
        }
        
        .messages-container::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 3px;
        }
        
        .messages-container::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.3);
          border-radius: 3px;
        }
        
        .messages-container::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.5);
        }
      `}</style>
    </div>
  );
}

// Render the component
ReactDOM.render(<MentalHealthChatbox />, document.getElementById('root'));