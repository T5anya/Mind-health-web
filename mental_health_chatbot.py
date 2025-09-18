import os
import uuid
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import sqlite3
import pandas as pd
import numpy as np
from io import BytesIO
import streamlit as st
from enum import Enum
import asyncio
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =======================
# CONFIGURATION & CONSTANTS
# =======================

class Config:
    """Application configuration with updated settings"""
    # Database
    DATABASE_PATH = "mental_health_chatbot.db"
    
    # AI Model configurations
    EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"
    MENTAL_HEALTH_MODEL = "mental/mental-roberta-base"
    CONVERSATION_MODEL = "microsoft/DialoGPT-medium"
    CRISIS_MODEL = "unitary/toxic-bert"
    
    # API Keys (set via environment variables)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # App settings
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-here")
    CONVERSATION_MEMORY_LIMIT = 50
    SESSION_TIMEOUT_HOURS = 24
    
    # Supported languages
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'hi': 'हिन्दी',
        'ur': 'اردو',
        'pa': 'ਪੰਜਾਬੀ',
        'ks': 'कॉशुर',
        'do': 'डोगरी',
        'es': 'Español',
        'fr': 'Français',
        'de': 'Deutsch',
        'zh': '中文',
        'ja': '日本語',
        'ko': '한국어',
        'ar': 'العربية'
    }

# =======================
# DATA MODELS
# =======================

class EmotionState(Enum):
    JOY = "😊"
    SADNESS = "😢"
    ANGER = "😠"
    FEAR = "😨"
    SURPRISE = "😲"
    DISGUST = "🤢"
    LOVE = "❤️"
    OPTIMISM = "🌟"
    PESSIMISM = "😔"
    NEUTRAL = "😐"

class RiskLevel(Enum):
    MINIMAL = {"level": 1, "color": "#4CAF50", "emoji": "🟢"}
    MILD = {"level": 2, "color": "#8BC34A", "emoji": "🟡"}
    MODERATE = {"level": 3, "color": "#FF9800", "emoji": "🟠"}
    SEVERE = {"level": 4, "color": "#FF5722", "emoji": "🔴"}
    CRITICAL = {"level": 5, "color": "#D32F2F", "emoji": "🚨"}

class ResponseType(Enum):
    SUPPORTIVE = "💙"
    CRISIS = "🚨"
    INFORMATIONAL = "📚"
    THERAPEUTIC = "🩺"
    MOTIVATIONAL = "💪"
    CONVERSATIONAL = "💬"

@dataclass
class UserProfile:
    user_id: str
    name: str
    age: Optional[int]
    preferred_language: str
    location: str
    created_at: datetime
    last_active: datetime
    session_count: int = 0
    risk_history: List[Dict] = None
    preferences: Dict = None

@dataclass
class ConversationMessage:
    message_id: str
    user_id: str
    content: str
    timestamp: datetime
    is_user: bool
    emotion_detected: Optional[EmotionState]
    risk_level: Optional[RiskLevel]
    language: str
    confidence_score: float = 0.0

@dataclass
class AIResponse:
    text: str
    emotion_detected: EmotionState
    confidence_score: float
    risk_assessment: RiskLevel
    response_type: ResponseType
    suggested_actions: List[str]
    timestamp: datetime
    model_used: str
    processing_time: float

# =======================
# DATABASE MANAGEMENT
# =======================

class DatabaseManager:
    """Handles all database operations with improved methods"""
    
    def __init__(self, db_path: str = Config.DATABASE_PATH):
        """Initialize the database manager with the given database path"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables if they do not exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER,
                    preferred_language TEXT DEFAULT 'en',
                    location TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_count INTEGER DEFAULT 0,
                    risk_history TEXT,
                    preferences TEXT
                )
            ''')
            
            # Conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    message_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_user BOOLEAN NOT NULL,
                    emotion_detected TEXT,
                    risk_level INTEGER,
                    language TEXT DEFAULT 'en',
                    confidence_score REAL DEFAULT 0.0,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    session_date DATE,
                    total_messages INTEGER,
                    dominant_emotion TEXT,
                    max_risk_level INTEGER,
                    session_duration INTEGER,
                    languages_used TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def create_user(self, user_profile: UserProfile):
        """Create a new user in the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, name, age, preferred_language, location, created_at, last_active, session_count, risk_history, preferences)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_profile.user_id,
                user_profile.name,
                user_profile.age,
                user_profile.preferred_language,
                user_profile.location,
                user_profile.created_at,
                user_profile.last_active,
                user_profile.session_count,
                json.dumps(user_profile.risk_history or []),
                json.dumps(user_profile.preferences or {})
            ))
            conn.commit()
    
    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve user profile from the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            
            if row:
                return UserProfile(
                    user_id=row[0],
                    name=row[1],
                    age=row[2],
                    preferred_language=row[3],
                    location=row[4],
                    created_at=datetime.fromisoformat(row[5]),
                    last_active=datetime.fromisoformat(row[6]),
                    session_count=row[7],
                    risk_history=json.loads(row[8]) if row[8] else [],
                    preferences=json.loads(row[9]) if row[9] else {}
                )
        return None
    
    def save_message(self, message: ConversationMessage):
        """Save conversation message to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO conversations 
                (message_id, user_id, content, timestamp, is_user, emotion_detected, risk_level, language, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                message.message_id,
                message.user_id,
                message.content,
                message.timestamp,
                message.is_user,
                message.emotion_detected.value if message.emotion_detected else None,
                message.risk_level.value["level"] if message.risk_level else None,
                message.language,
                message.confidence_score
            ))
            conn.commit()
    
    def get_conversation_history(self, user_id: str, limit: int = 50) -> List[ConversationMessage]:
        """Get conversation history for the specified user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM conversations 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            messages = []
            for row in cursor.fetchall():
                emotion = None
                if row[5]:
                    for e in EmotionState:
                        if e.value == row[5]:
                            emotion = e
                            break
                
                risk = None
                if row[6]:
                    for r in RiskLevel:
                        if r.value["level"] == row[6]:
                            risk = r
                            break
                
                messages.append(ConversationMessage(
                    message_id=row[0],
                    user_id=row[1],
                    content=row[2],
                    timestamp=datetime.fromisoformat(row[3]),
                    is_user=row[4],
                    emotion_detected=emotion,
                    risk_level=risk,
                    language=row[7],
                    confidence_score=row[8]
                ))
            
            return list(reversed(messages))

# =======================
# AI INTEGRATION ENGINE
# =======================

class AIIntegrationEngine:
    """Advanced AI integration with multiple models for better responses"""
    
    def __init__(self):
        """Initialize the AI engine"""
        self.device = "cpu"  # Default to CPU for compatibility
        logger.info(f"Using device for AI models: {self.device}")
        
        # Initialize crisis patterns
        self._init_crisis_patterns()
        
        logger.info("AI Integration Engine initialized successfully")
    
    def _init_crisis_patterns(self):
        """Initialize crisis detection patterns"""
        self.crisis_patterns = {
            'en': [
                r'\b(suicide|kill\s+myself|end\s+it\s+all|want\s+to\s+die|better\s+off\s+dead)\b',
                r'\b(hurt\s+myself|self\s+harm|cut\s+myself|overdose|jump\s+off)\b',
                r'\b(hopeless|worthless|no\s+point\s+living|cant\s+go\s+on)\b'
            ],
            'hi': [
                r'\b(आत्महत्या|खुद\s*को\s*मार|मरना\s*चाहता|जीने\s*का\s*कोई\s*फायदा\s*नहीं)\b',
                r'\b(निराश|बेकार|कोई\s*उम्मीद\s*नहीं)\b'
            ]
        }
    
    def detect_emotion(self, text: str, language: str = 'en') -> Dict[str, Any]:
        """Detect emotions from the provided text using simple rule-based approach"""
        start_time = datetime.now()
        
        try:
            # Simple sentiment analysis based on keywords
            positive_words = ['happy', 'joy', 'excited', 'good', 'great', 'love', 'wonderful']
            negative_words = ['sad', 'depressed', 'angry', 'hate', 'terrible', 'awful', 'bad']
            fear_words = ['scared', 'afraid', 'worried', 'anxious', 'panic', 'fear']
            
            text_lower = text.lower()
            
            # Count emotional indicators
            positive_score = sum(1 for word in positive_words if word in text_lower)
            negative_score = sum(1 for word in negative_words if word in text_lower)
            fear_score = sum(1 for word in fear_words if word in text_lower)
            
            # Determine dominant emotion
            if fear_score > 0:
                detected_emotion = EmotionState.FEAR
                confidence = min(0.8, fear_score * 0.3)
            elif positive_score > negative_score:
                detected_emotion = EmotionState.JOY
                confidence = min(0.8, positive_score * 0.2)
            elif negative_score > 0:
                detected_emotion = EmotionState.SADNESS
                confidence = min(0.8, negative_score * 0.2)
            else:
                detected_emotion = EmotionState.NEUTRAL
                confidence = 0.5
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'emotion': detected_emotion,
                'confidence': confidence,
                'processing_time': processing_time,
                'details': {
                    'original_text': text,
                    'language': language
                }
            }
            
        except Exception as e:
            logger.error(f"Emotion detection error: {e}")
            return {
                'emotion': EmotionState.NEUTRAL,
                'confidence': 0.5,
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'details': {'error': str(e)}
            }
    
    def detect_crisis_risk(self, text: str, language: str = 'en') -> Dict[str, Any]:
        """Detect potential crisis risks based on user input"""
        start_time = datetime.now()
        risk_score = 0
        detected_patterns = []
        
        try:
            # Pattern-based detection
            patterns = self.crisis_patterns.get(language, self.crisis_patterns['en'])
            for pattern in patterns:
                matches = re.findall(pattern, text.lower(), re.IGNORECASE | re.UNICODE)
                if matches:
                    risk_score += len(matches) * 2
                    detected_patterns.extend(matches)
            
            # Contextual risk indicators
            high_risk_words = ['hopeless', 'worthless', 'meaningless', 'pointless', 'alone', 'trapped']
            for word in high_risk_words:
                if word in text.lower():
                    risk_score += 1
            
            # Determine risk level
            if risk_score >= 6:
                risk_level = RiskLevel.CRITICAL
            elif risk_score >= 4:
                risk_level = RiskLevel.SEVERE
            elif risk_score >= 2:
                risk_level = RiskLevel.MODERATE
            elif risk_score >= 1:
                risk_level = RiskLevel.MILD
            else:
                risk_level = RiskLevel.MINIMAL
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'risk_level': risk_level,
                'risk_score': risk_score,
                'detected_patterns': detected_patterns,
                'needs_intervention': risk_level.value["level"] >= 4,
                'processing_time': processing_time
            }
            
        except Exception as e:
            logger.error(f"Crisis detection error: {e}")
            return {
                'risk_level': RiskLevel.MINIMAL,
                'risk_score': 0,
                'detected_patterns': [],
                'needs_intervention': False,
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
    
    def generate_response(self, text: str, context: Dict, user_profile: UserProfile) -> AIResponse:
        """Generate a response based on user input and context"""
        start_time = datetime.now()
        
        try:
            # Detect emotion and crisis risk
            emotion_result = self.detect_emotion(text, user_profile.preferred_language)
            crisis_result = self.detect_crisis_risk(text, user_profile.preferred_language)
            
            # Choose response strategy based on risk level and emotion
            if crisis_result['needs_intervention']:
                response_text = self._generate_crisis_response(text, context, user_profile, crisis_result)
                response_type = ResponseType.CRISIS
                model_used = "crisis_protocol"
            elif emotion_result['emotion'] in [EmotionState.SADNESS, EmotionState.PESSIMISM]:
                response_text = self._generate_supportive_response(text, context, user_profile, emotion_result)
                response_type = ResponseType.SUPPORTIVE
                model_used = "supportive_protocol"
            elif emotion_result['emotion'] == EmotionState.ANGER:
                response_text = self._generate_calming_response(text, context, user_profile)
                response_type = ResponseType.THERAPEUTIC
                model_used = "therapeutic_protocol"
            else:
                response_text = self._generate_conversational_response(text, context, user_profile)
                response_type = ResponseType.CONVERSATIONAL
                model_used = "conversational_protocol"
            
            # Generate suggested actions
            suggested_actions = self._get_suggested_actions(
                emotion_result['emotion'],
                crisis_result['risk_level'],
                user_profile.preferred_language
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AIResponse(
                text=response_text,
                emotion_detected=emotion_result['emotion'],
                confidence_score=emotion_result['confidence'],
                risk_assessment=crisis_result['risk_level'],
                response_type=response_type,
                suggested_actions=suggested_actions,
                timestamp=datetime.now(),
                model_used=model_used,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return self._get_fallback_response(user_profile.preferred_language)
    
    def _generate_crisis_response(self, text: str, context: Dict, user_profile: UserProfile, crisis_result: Dict) -> str:
        """Generate immediate crisis intervention response"""
        crisis_templates = {
            'en': [
                f"I'm very concerned about what you're sharing, {user_profile.name}. Your life has value and there are people who want to help. Please contact emergency services immediately at 112 or reach out to a trusted person. You don't have to face this alone.",
                f"I can hear that you're in tremendous pain right now, {user_profile.name}. These feelings are overwhelming, but they can change. Please get immediate help - contact emergency services or go to your nearest emergency room.",
                f"What you're experiencing sounds incredibly difficult, {user_profile.name}. Please know that there are trained professionals ready to help you through this crisis. Contact emergency services or reach out to someone you trust right now."
            ],
            'hi': [
                f"{user_profile.name}, मैं आपकी बात से बहुत चिंतित हूँ। आपका जीवन मूल्यवान है। कृपया तुरंत 112 पर कॉल करें या किसी विश्वसनीय व्यक्ति से संपर्क करें।",
                f"{user_profile.name}, मैं समझ सकता हूँ कि आप बहुत कष्ट में हैं। कृपया तुरंत professional help लें। आप अकेले नहीं हैं।"
            ]
        }
        
        lang = user_profile.preferred_language
        templates = crisis_templates.get(lang, crisis_templates['en'])
        
        return np.random.choice(templates)
    
    def _generate_supportive_response(self, text: str, context: Dict, user_profile: UserProfile, emotion_result: Dict) -> str:
        """Generate empathetic supportive response"""
        supportive_templates = {
            'en': [
                f"I can hear that you're going through a really tough time, {user_profile.name}. It takes courage to share these feelings. What you're experiencing is valid.",
                f"Thank you for trusting me with your feelings, {user_profile.name}. It sounds like you're carrying a lot right now. Remember that difficult emotions are temporary.",
                f"{user_profile.name}, I want you to know that your feelings matter and so do you. It's completely normal to have ups and downs. You don't have to face this alone."
            ],
            'hi': [
                f"{user_profile.name}, मैं समझ सकता हूँ कि आप मुश्किल दौर से गुज़र रहे हैं। आपकी भावनाएं मायने रखती हैं।",
                f"{user_profile.name}, आपने मुझसे अपनी बात साझा की, इसके लिए धन्यवाद। आप अकेले नहीं हैं।"
            ]
        }
        
        lang = user_profile.preferred_language
        templates = supportive_templates.get(lang, supportive_templates['en'])
        
        return np.random.choice(templates)
    
    def _generate_calming_response(self, text: str, context: Dict, user_profile: UserProfile) -> str:
        """Generate calming response for anger/frustration"""
        calming_templates = {
            'en': [
                f"I can sense the frustration in your words, {user_profile.name}. Those feelings are completely understandable. Let's take a moment to breathe together.",
                f"{user_profile.name}, it sounds like you're dealing with some really challenging situations. Anger often comes from feeling unheard. I'm here to listen.",
                f"I hear you, {user_profile.name}. When we're frustrated, everything can feel intense. What would help you feel more in control right now?"
            ]
        }
        
        lang = user_profile.preferred_language
        templates = calming_templates.get(lang, calming_templates['en'])
        
        return np.random.choice(templates)
    
    def _generate_conversational_response(self, text: str, context: Dict, user_profile: UserProfile) -> str:
        """Generate natural conversational response"""
        conversational_templates = {
            'en': [
                f"Thank you for sharing that with me, {user_profile.name}. How are you feeling about everything right now?",
                f"I appreciate you opening up, {user_profile.name}. What's been on your mind lately?",
                f"It sounds like there's a lot going on for you, {user_profile.name}. Would you like to talk more about what's happening?"
            ]
        }
        
        lang = user_profile.preferred_language
        templates = conversational_templates.get(lang, conversational_templates['en'])
        
        return np.random.choice(templates)
    
    def _get_suggested_actions(self, emotion: EmotionState, risk: RiskLevel, language: str = 'en') -> List[str]:
        """Get personalized action suggestions"""
        action_suggestions = {
            'en': {
                EmotionState.SADNESS: [
                    "Try a 5-minute mindfulness exercise",
                    "Reach out to a trusted friend or family member",
                    "Take a gentle walk outside",
                    "Write down three things you're grateful for"
                ],
                EmotionState.ANGER: [
                    "Practice deep breathing for 2 minutes",
                    "Try some physical exercise to release tension",
                    "Write down your thoughts to process them",
                    "Listen to calming music"
                ],
                EmotionState.FEAR: [
                    "Focus on what you can control right now",
                    "Try the 5-4-3-2-1 grounding technique",
                    "Challenge negative thoughts with evidence",
                    "Connect with your support system"
                ],
                EmotionState.JOY: [
                    "Celebrate this positive moment!",
                    "Reflect on what contributed to these feelings",
                    "Share this positivity with someone you care about",
                    "Capture this moment in a journal"
                ]
            },
            'hi': {
                EmotionState.SADNESS: [
                    "5 मिनट का ध्यान करें",
                    "किसी विश्वसनीय व्यक्ति से बात करें",
                    "बाहर टहलने जाएं",
                    "तीन अच्छी बातें लिखें"
                ],
                EmotionState.ANGER: [
                    "गहरी सांस लें",
                    "थोड़ा व्यायाम करें",
                    "अपने विचार लिखें",
                    "शांत संगीत सुनें"
                ]
            }
        }
        
        emotion_actions = action_suggestions.get(language, action_suggestions['en'])
        base_actions = emotion_actions.get(emotion, emotion_actions.get(EmotionState.SADNESS, []))
        
        # Add crisis-specific actions for high risk levels
        if risk.value["level"] >= 4:
            crisis_actions = [
                "Contact emergency services (112) immediately",
                "Go to the nearest hospital emergency room",
                "Call a crisis helpline for immediate support",
                "Stay with trusted individuals - don't be alone"
            ]
            return crisis_actions
        elif risk.value["level"] >= 3:
            base_actions.insert(0, "Consider speaking with a mental health professional")
        
        return base_actions[:4]
    
    def _get_fallback_response(self, language: str = 'en') -> AIResponse:
        """Provide fallback response when AI processing fails"""
        fallback_messages = {
            'en': "I'm here to listen and support you. Sometimes I might not have the perfect response, but I want you to know that your feelings are valid and important. How can I best help you right now?",
            'hi': "मैं यहाँ आपकी सुनने और मदद करने के लिए हूँ। आपकी भावनाएं महत्वपूर्ण हैं। मैं आपकी कैसे मदद कर सकता हूँ?"
        }
        
        return AIResponse(
            text=fallback_messages.get(language, fallback_messages['en']),
            emotion_detected=EmotionState.NEUTRAL,
            confidence_score=0.5,
            risk_assessment=RiskLevel.MINIMAL,
            response_type=ResponseType.SUPPORTIVE,
            suggested_actions=["Take a deep breath", "You're not alone", "Reach out to someone you trust"],
            timestamp=datetime.now(),
            model_used="fallback",
            processing_time=0.1
        )

# =======================
# MAIN CHATBOT APPLICATION
# =======================

class MentalHealthChatbot:
    """Main chatbot application class"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.ai_engine = AIIntegrationEngine()
        
        # Session management
        self.active_sessions = {}
        
        logger.info("Mental Health Chatbot initialized successfully")
    
    def process_message(self, user_id: str, message: str, message_type: str = 'text') -> AIResponse:
        """Process user message and generate response"""
        
        # Get or create user profile
        user_profile = self.db_manager.get_user(user_id)
        if not user_profile:
            # Create default profile
            user_profile = UserProfile(
                user_id=user_id,
                name="User",
                age=None,
                preferred_language='en',
                location="Unknown",
                created_at=datetime.now(),
                last_active=datetime.now()
            )
            self.db_manager.create_user(user_profile)
        
        # Update last active
        user_profile.last_active = datetime.now()
        self.db_manager.create_user(user_profile)
        
        # Get conversation context
        conversation_history = self.db_manager.get_conversation_history(user_id, 10)
        context = {
            'history': [msg.content for msg in conversation_history],
            'recent_emotions': [msg.emotion_detected for msg in conversation_history if msg.emotion_detected],
            'session_start': datetime.now()
        }
        
        # Save user message
        user_message = ConversationMessage(
            message_id=str(uuid.uuid4()),
            user_id=user_id,
            content=message,
            timestamp=datetime.now(),
            is_user=True,
            emotion_detected=None,
            risk_level=None,
            language=user_profile.preferred_language
        )
        self.db_manager.save_message(user_message)
        
        # Generate AI response
        ai_response = self.ai_engine.generate_response(message, context, user_profile)
        
        # Save bot response
        bot_message = ConversationMessage(
            message_id=str(uuid.uuid4()),
            user_id=user_id,
            content=ai_response.text,
            timestamp=ai_response.timestamp,
            is_user=False,
            emotion_detected=ai_response.emotion_detected,
            risk_level=ai_response.risk_assessment,
            language=user_profile.preferred_language,
            confidence_score=ai_response.confidence_score
        )
        self.db_manager.save_message(bot_message)
        
        return ai_response

# =======================
# STREAMLIT UI APPLICATION
# =======================

def create_streamlit_app():
    """Create Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title="Mental Health AI Assistant",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .chat-message {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .user-message {
        background: rgba(118, 75, 162, 0.3);
        border-left: 4px solid #764ba2;
        margin-left: 20%;
    }
    
    .bot-message {
        background: rgba(102, 126, 234, 0.3);
        border-left: 4px solid #667eea;
        margin-right: 20%;
    }
    
    .crisis-alert {
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        color: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #ff3838;
        margin: 20px 0;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 107, 107, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = MentalHealthChatbot()
        st.session_state.messages = []
        st.session_state.user_id = str(uuid.uuid4())
        st.session_state.user_profile = None
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 3.5em; margin-bottom: 0.2em;">Mental Health AI Assistant</h1>
        <h3 style="color: rgba(255,255,255,0.8); font-weight: 300;">Advanced AI-Powered Mental Health Support</h3>
        <p style="color: rgba(255,255,255,0.6); margin-top: 1em;">
            Confidential • Multi-language • AI-Enhanced • Always Here for You
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for user profile
    with st.sidebar:
        st.markdown("## User Profile")
        
        if not st.session_state.user_profile:
            st.markdown("### Welcome! Let's get to know you better")
            
            name = st.text_input("Your Name", placeholder="How should I address you?")
            age = st.number_input("Age", min_value=13, max_value=100, value=20)
            language = st.selectbox("Preferred Language", 
                                   options=list(Config.SUPPORTED_LANGUAGES.keys()),
                                   format_func=lambda x: f"{Config.SUPPORTED_LANGUAGES[x]} ({x})")
            location = st.text_input("Location", placeholder="e.g., Mumbai, India")
            
            if st.button("Start Chatting"):
                user_profile = UserProfile(
                    user_id=st.session_state.user_id,
                    name=name or "User",
                    age=age,
                    preferred_language=language,
                    location=location or "Unknown",
                    created_at=datetime.now(),
                    last_active=datetime.now()
                )
                
                st.session_state.chatbot.db_manager.create_user(user_profile)
                st.session_state.user_profile = user_profile
                st.rerun()
        else:
            profile = st.session_state.user_profile
            st.markdown(f"**Name:** {profile.name}")
            st.markdown(f"**Language:** {Config.SUPPORTED_LANGUAGES[profile.preferred_language]}")
            st.markdown(f"**Location:** {profile.location}")
            
            if st.button("Reset Profile"):
                st.session_state.user_profile = None
                st.session_state.messages = []
                st.rerun()
        
        st.markdown("---")
        st.markdown("## Emergency Resources")
        st.markdown("""
        **India Emergency:**
        - Emergency: 112
        - Mental Health: 1800-599-0019
        
        **Crisis Resources:**
        - Campus Counseling Centers
        - Nearest Hospital Emergency Room
        """)
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("## Chat with Your AI Assistant")
        
        # Display messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                    <small style="float: right; opacity: 0.7;">{message.get("timestamp", "")}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                emotion_emoji = message.get("emotion", EmotionState.NEUTRAL).value
                risk_color = message.get("risk_level", RiskLevel.MINIMAL).value["color"]
                
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <span style="font-size: 1.5em; margin-right: 10px;">{emotion_emoji}</span>
                        <strong>AI Assistant:</strong>
                        <span style="background: {risk_color}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.8em; margin-left: 10px;">
                            {message.get("risk_level", RiskLevel.MINIMAL).name}
                        </span>
                    </div>
                    {message["content"]}
                    <small style="float: right; opacity: 0.7;">{message.get("timestamp", "")}</small>
                </div>
                """, unsafe_allow_html=True)
                
                if message.get("suggested_actions"):
                    st.markdown("**Helpful Suggestions:**")
                    for action in message["suggested_actions"][:3]:
                        st.markdown(f"• {action}")
                
                if message.get("risk_level") and message["risk_level"].value["level"] >= 4:
                    st.markdown("""
                    <div class="crisis-alert">
                        <h4>Crisis Support Needed</h4>
                        <p>I'm concerned about your wellbeing. Please reach out for immediate help:</p>
                        <ul>
                            <li>Emergency Services: 112</li>
                            <li>Go to nearest hospital emergency room</li>
                            <li>Contact a trusted person immediately</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Input area
        user_input = st.chat_input("Share what's on your mind... I'm here to listen")
        
        if user_input and st.session_state.user_profile:
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().strftime("%H:%M")
            })
            
            try:
                # Generate AI response
                ai_response = st.session_state.chatbot.process_message(
                    st.session_state.user_id, user_input
                )
                
                # Add bot response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_response.text,
                    "timestamp": datetime.now().strftime("%H:%M"),
                    "emotion": ai_response.emotion_detected,
                    "risk_level": ai_response.risk_assessment,
                    "suggested_actions": ai_response.suggested_actions
                })
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Sorry, I'm having trouble processing your message: {e}")
    
    # Analytics panel
    with col2:
        st.markdown("## Session Info")
        
        if st.session_state.user_profile:
            st.metric("Messages", len(st.session_state.messages))
            st.metric("Session Time", "Active")
            
            if st.session_state.messages:
                last_emotion = None
                last_risk = None
                
                for msg in reversed(st.session_state.messages):
                    if msg["role"] == "assistant":
                        last_emotion = msg.get("emotion", EmotionState.NEUTRAL)
                        last_risk = msg.get("risk_level", RiskLevel.MINIMAL)
                        break
                
                if last_emotion:
                    st.markdown(f"**Current Mood:** {last_emotion.value}")
                if last_risk:
                    st.markdown(f"**Risk Level:** {last_risk.name}")

if __name__ == "__main__":
    create_streamlit_app()