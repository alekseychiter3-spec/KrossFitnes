from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Конфигурация
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модели
class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    training_type = db.Column(db.String(50))
    preferred_date = db.Column(db.String(50))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'training_type': self.training_type,
            'preferred_date': self.preferred_date,
            'message': self.message,
            'created_at': self.created_at.isoformat()
        }

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# API для подписки
@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    try:
        from flask import request
        data = request.get_json()
        
        # Валидация
        if not data or not data.get('name') or not data.get('email'):
            return jsonify({'error': 'Name and email are required'}), 400
        
        # Проверка существующей подписки
        existing_subscription = Subscription.query.filter_by(email=data['email']).first()
        if existing_subscription:
            return jsonify({'error': 'Email already subscribed'}), 409
        
        # Создание новой подписки
        subscription = Subscription(
            name=data['name'],
            email=data['email']
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        return jsonify({
            'message': 'Successfully subscribed!',
            'subscription': subscription.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API для бронирования
@app.route('/api/book', methods=['POST'])
def book_training():
    try:
        from flask import request
        data = request.get_json()
        
        # Валидация
        required_fields = ['name', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Создание бронирования
        booking = Booking(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone', ''),
            training_type=data.get('training_type', ''),
            preferred_date=data.get('preferred_date', ''),
            message=data.get('message', '')
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'message': 'Training session booked successfully!',
            'booking': booking.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API для получения всех подписок (для админки)
@app.route('/api/subscriptions', methods=['GET'])
def get_subscriptions():
    try:
        subscriptions = Subscription.query.all()
        return jsonify({
            'subscriptions': [sub.to_dict() for sub in subscriptions]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API для получения всех бронирований (для админки)
@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    try:
        bookings = Booking.query.all()
        return jsonify({
            'bookings': [booking.to_dict() for booking in bookings]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Информация о тренировках
@app.route('/api/training-types', methods=['GET'])
def get_training_types():
    training_types = [
        {
            'id': 1,
            'name': 'Maxpump',
            'description': 'High-intensity muscle pumping workout',
            'image': '/static/images/training-types/1.svg'
        },
        {
            'id': 2,
            'name': 'Aron Gym',
            'description': 'Classic gym strength training',
            'image': '/static/images/training-types/2.svg'
        },
        {
            'id': 3,
            'name': 'Fit & Tone',
            'description': 'Body shaping and toning exercises',
            'image': '/static/images/training-types/3.svg'
        },
        {
            'id': 4,
            'name': 'Forza',
            'description': 'Power and strength focused training',
            'image': '/static/images/training-types/4.svg'
        },
        {
            'id': 5,
            'name': 'Balance Fitness',
            'description': 'Holistic approach to fitness and wellness',
            'image': '/static/images/training-types/5.svg'
        },
        {
            'id': 6,
            'name': 'Body Sculpt',
            'description': 'Sculpting and definition workout',
            'image': '/static/images/training-types/6.svg'
        }
    ]
    return jsonify({'training_types': training_types})

# События
@app.route('/api/events', methods=['GET'])
def get_events():
    events = [
        {
            'id': 1,
            'title': 'Crossfit',
            'date': '2024-06-07',
            'end_date': '2024-06-13',
            'description': 'New event coming up'
        }
    ]
    return jsonify({'events': events})

# Инициализация базы данных
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)