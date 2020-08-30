from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(24), nullable = False)
    hashedPass = db.Column(db.String(64), nullable = False)
    chats = db.relationship("Chat", backref= 'user', lazy = True)
    message = db.relationship("Message", backref = 'user', lazy = True)

    def __init__(self, username, hashedPass):
        self.username = username
        self.hashedPass = hashedPass
    def __repr__(self):
        return '<User {}>'.format(self.username)

class Chat(db.Model):
    chat_id = db.Column(db.Integer, primary_key =True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    chat_name = db.Column(db.Text, nullable = False)
    messages = db.relationship("Message", backref = 'chat', lazy = True)

    def __init__(self, creator_id, chat_name):
        self.creator_id = creator_id
        self.chat_name = chat_name

    def __repr__(self):
        return '{}'.format(self.chat_name)

class Message(db.Model):
    message_id = db.Column(db.Integer, primary_key = True)
    author_id = db.Column(db.String(24), db.ForeignKey('user.id'), nullable = False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.chat_id'), nullable = False)
    text = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.Integer)

    def __init__(self, author_id, chat_id, text, pub_date):
        self.author_id = author_id
        self.chat_id = chat_id
        self.text = text
        self.pub_date = pub_date
    
    def __repr__(self):
        return '<Message {}'.format(self.text)
    def serialize(self):
        toDict = {
            "author": self.author_id,
            "chat": self.chat_id,
            "text": self.text,
            "date": self.pub_date
        }
        return json.dumps(toDict)
    
    def convertTimestamp(self):
        return datetime.fromtimestamp(self.pub_date)
        

