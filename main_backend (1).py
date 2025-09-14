from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
from functools import wraps
import os
from enum import Enum
import uuid

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///mental_health.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_EXPIRATION_DELTA'] = timedelta(hours=24)

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# Enums for better data integrity
class UserRole(Enum):
    STUDENT = "student"
    COUNSELOR = "counselor"
    ADMIN = "admin"

class MoodLevel(Enum):
    VERY_LOW = 1
    LOW = 2
    MODERATE = 3
    GOOD = 4
    EXCELLENT = 5

class SessionStatus(Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    institution = db.Column(db.String(100))
    course = db.Column(db.String(100))
    year_of_study = db.Column(db.Integer)
    phone = db.Column(db.String(15))
    emergency_contact = db.Column(db.String(15))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    mood_entries = db.relationship('MoodEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    chat_sessions = db.relationship('ChatSession', backref='user', lazy=True, cascade='all, delete-orphan')
    counseling_sessions_as_student = db.relationship('CounselingSession', 
                                                   foreign_keys='CounselingSession.student_id', 
                                                   backref='student', 
                                                   lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role.value,
            'institution': self.institution,
            'course': self.course,
            'year_of_study': self.year_of_study,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class MoodEntry(db.Model):
    __tablename__ = 'mood_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mood_level = db.Column(db.Enum(MoodLevel), nullable=False)
    notes = db.Column(db.Text)
    stress_factors = db.Column(db.Text)  # Store as JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'mood_level': self.mood_level.value,
            'notes': self.notes,
            'stress_factors': self.stress_factors,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'is_active': self.is_active
        }

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_user_message = db.Column(db.Boolean, nullable=False)
    sentiment_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'is_user_message': self.is_user_message,
            'sentiment_score': self.sentiment_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CounselingSession(db.Model):
    __tablename__ = 'counseling_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    counselor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    status = db.Column(db.Enum(SessionStatus), default=SessionStatus.SCHEDULED)
    notes = db.Column(db.Text)
    is_emergency = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'counselor_id': self.counselor_id,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'duration_minutes': self.duration_minutes,
            'status': self.status.value,
            'is_emergency': self.is_emergency,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Resource(db.Model):
    __tablename__ = 'resources'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    resource_type = db.Column(db.String(50))
    tags = db.Column(db.Text)  # Store as JSON string
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'resource_type': self.resource_type,
            'tags': self.tags,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# JWT Functions
def generate_token(user_id):
    try:
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA']
        }
        return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    except Exception as e:
        return None

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Authentication Decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        current_user = User.query.get(user_id)
        if not current_user:
            return jsonify({'error': 'User not found'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validation
        required_fields = ['email', 'password', 'first_name', 'last_name', 'institution']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create new user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            institution=data['institution'],
            course=data.get('course'),
            year_of_study=data.get('year_of_study'),
            phone=data.get('phone'),
            emergency_contact=data.get('emergency_contact')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        token = generate_token(user.id)
        if not token:
            return jsonify({'error': 'Failed to generate token'}), 500
        
        return jsonify({
            'message': 'User registered successfully',
            'token': token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        token = generate_token(user.id)
        if not token:
            return jsonify({'error': 'Failed to generate token'}), 500
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    try:
        return jsonify({'user': current_user.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500

@app.route('/api/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        updatable_fields = ['first_name', 'last_name', 'institution', 'course', 'year_of_study', 'phone', 'emergency_contact']
        for field in updatable_fields:
            if field in data:
                setattr(current_user, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500

@app.route('/api/mood', methods=['POST'])
@token_required
def log_mood(current_user):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        mood_level = data.get('mood_level')
        if not mood_level or mood_level not in [1, 2, 3, 4, 5]:
            return jsonify({'error': 'Valid mood level (1-5) is required'}), 400
        
        # Convert stress factors to string for storage
        stress_factors = data.get('stress_factors', [])
        if isinstance(stress_factors, list):
            import json
            stress_factors_str = json.dumps(stress_factors)
        else:
            stress_factors_str = str(stress_factors)
        
        mood_entry = MoodEntry(
            user_id=current_user.id,
            mood_level=MoodLevel(mood_level),
            notes=data.get('notes'),
            stress_factors=stress_factors_str
        )
        
        db.session.add(mood_entry)
        db.session.commit()
        
        return jsonify({
            'message': 'Mood logged successfully',
            'mood_entry': mood_entry.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to log mood: {str(e)}'}), 500

@app.route('/api/mood', methods=['GET'])
@token_required
def get_mood_history(current_user):
    try:
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        mood_entries = MoodEntry.query.filter(
            MoodEntry.user_id == current_user.id,
            MoodEntry.created_at >= start_date
        ).order_by(MoodEntry.created_at.desc()).all()
        
        return jsonify({
            'mood_entries': [entry.to_dict() for entry in mood_entries]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get mood history: {str(e)}'}), 500

@app.route('/api/chat/session', methods=['POST'])
@token_required
def create_chat_session(current_user):
    try:
        chat_session = ChatSession(user_id=current_user.id)
        db.session.add(chat_session)
        db.session.commit()
        
        return jsonify({
            'message': 'Chat session created',
            'session': chat_session.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create chat session: {str(e)}'}), 500

@app.route('/api/chat/message', methods=['POST'])
@token_required
def send_chat_message(current_user):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        session_id = data.get('session_id')
        message = data.get('message')
        
        if not session_id or not message:
            return jsonify({'error': 'Session ID and message are required'}), 400
        
        # Verify session belongs to user
        chat_session = ChatSession.query.filter_by(
            session_id=session_id,
            user_id=current_user.id
        ).first()
        
        if not chat_session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Save user message
        user_message = ChatMessage(
            session_id=chat_session.id,
            message=message,
            is_user_message=True
        )
        db.session.add(user_message)
        
        # Simple AI response (replace with your AI integration)
        ai_response = "Thank you for sharing. I'm here to listen and support you. How are you feeling about this situation?"
        
        ai_message = ChatMessage(
            session_id=chat_session.id,
            message=ai_response,
            is_user_message=False
        )
        db.session.add(ai_message)
        db.session.commit()
        
        return jsonify({
            'user_message': user_message.to_dict(),
            'ai_response': ai_message.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to send message: {str(e)}'}), 500

@app.route('/api/resources', methods=['GET'])
@token_required
def get_resources(current_user):
    try:
        resource_type = request.args.get('type')
        featured_only = request.args.get('featured', False, type=bool)
        
        query = Resource.query
        
        if resource_type:
            query = query.filter_by(resource_type=resource_type)
        
        if featured_only:
            query = query.filter_by(is_featured=True)
        
        resources = query.order_by(Resource.created_at.desc()).all()
        
        return jsonify({
            'resources': [resource.to_dict() for resource in resources]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get resources: {str(e)}'}), 500

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

# Database initialization
def init_db():
    """Initialize database and create sample data"""
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            
            # Create sample resources if they don't exist
            if Resource.query.count() == 0:
                sample_resources = [
                    Resource(
                        title="Managing Academic Stress",
                        description="Learn effective strategies to handle academic pressure",
                        content="Academic stress is common among students. Here are some effective strategies...",
                        resource_type="article",
                        tags='["stress", "academics", "coping"]',
                        is_featured=True
                    ),
                    Resource(
                        title="Breathing Exercises for Anxiety",
                        description="Simple breathing techniques to reduce anxiety",
                        content="Deep breathing exercises can help calm your mind and reduce anxiety...",
                        resource_type="exercise",
                        tags='["anxiety", "breathing", "mindfulness"]',
                        is_featured=True
                    )
                ]
                
                for resource in sample_resources:
                    db.session.add(resource)
                
                db.session.commit()
                print("Sample resources created successfully!")
            
            print("Database initialized successfully!")
            
    except Exception as e:
        print(f"Database initialization failed: {e}")
        if db.session:
            db.session.rollback()

if __name__ == '__main__':
    # Initialize database when running the app
    init_db()
    print("Starting Mental Health Support System...")
    print("API endpoints available at: http://localhost:5000/api/")
    app.run(debug=True, host='0.0.0.0', port=5000)