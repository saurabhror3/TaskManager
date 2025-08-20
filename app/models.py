from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(60), nullable=False)
  tasks = db.relationship('Task', backref='owner', lazy=True)

class Category(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(30), unique=True, nullable=False)
  tasks = db.relationship('Task', backref='category', lazy=True)

class Task(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), nullable=False)
  description = db.Column(db.Text)
  due_date = db.Column(db.DateTime, nullable=True)
  priority = db.Column(db.String(10), default='Medium')
  is_completed = db.Column(db.Boolean, default=False)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
  date_created = db.Column(db.DateTime, default=datetime.utcnow)
