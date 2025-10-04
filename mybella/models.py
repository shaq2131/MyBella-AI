from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask import current_app
from sqlalchemy import text

# Create the database instance
db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Initialize the database with the app"""
    try:
        # Initialize database
        db.init_app(app)
        migrate.init_app(app, db)
        
        # Check if database needs to be created
        db.create_all()
        
        # Verify database connection
        try:
            db.session.execute('SELECT 1')
            db.session.commit()
            app.logger.info('Database initialized and connection verified successfully')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Database connection verification failed: {str(e)}')
            raise
    except Exception as e:
        app.logger.error(f'Database initialization error: {str(e)}')
        raise

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    chats = db.relationship('Chat', backref='user', lazy=True, cascade='all, delete-orphan')
    settings = db.relationship('UserSettings', backref='user', uselist=False, lazy=True, cascade='all, delete-orphan')

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    persona = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='chat', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    current_persona = db.Column(db.String(50), default='isabella')
    mode = db.Column(db.String(20), default='companion')  # 'wellness' or 'companion'
    tts_enabled = db.Column(db.Boolean, default=True)
    voice_override = db.Column(db.String(100))
    age_confirmed = db.Column(db.Boolean, default=False)
    show_ads = db.Column(db.Boolean, default=True)

def init_db(app):
    """Initialize database and migrations with the app"""
    try:
        # Initialize database and migrations
        db.init_app(app)
        migrate.init_app(app, db)

        # Create all tables within the app context
        with app.app_context():
            db.create_all()

            # Verify database connection and commit
            try:
                db.session.execute(text('SELECT 1'))
                db.session.commit()
                app.logger.info('Database initialized successfully - all tables created')

                # Log table creation
                inspector = db.inspect(db.engine)
                table_names = inspector.get_table_names()
                app.logger.info(f'Created tables: {", ".join(table_names)}')
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'Database connection verification failed: {str(e)}')
                raise
    except Exception as e:
        app.logger.error(f'Database initialization error: {str(e)}')
        raise