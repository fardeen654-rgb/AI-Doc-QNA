from database import db
from flask_login import UserMixin
from datetime import datetime, date

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # 🟢 NEW: Email field for notifications
    email = db.Column(db.String(120), unique=True, nullable=False) 
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="user") 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    chats = db.relationship('ChatHistory', backref='author', lazy=True)
    analytics = db.relationship('UsageAnalytics', backref='user', lazy=True)


class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    sources = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class UsageAnalytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    action = db.Column(db.String(50))  # "upload_pdf" | "ask_question"
    count = db.Column(db.Integer, default=1)
    day = db.Column(db.Date, default=date.today)