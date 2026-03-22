from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from scraper import scrape_topic_summary
from mock_data import QUESTIONS
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here' # In a real app, use an environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gmail = db.Column(db.String(100), unique=True, nullable=False)
    user_class = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    history = db.relationship('AssessmentHistory', backref='user', lazy=True)

class AssessmentHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(100))
    topic = db.Column(db.String(100))
    score = db.Column(db.Integer)
    total_questions = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        gmail = request.form.get('gmail')
        user_class = request.form.get('class')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(gmail=gmail).first()
        if user_exists:
            flash('Email already exists.', 'error')
            return redirect(url_for('register'))
            
        new_user = User(
            name=name, 
            gmail=gmail, 
            user_class=user_class, 
            password_hash=generate_password_hash(password, method='pbkdf2:sha256')
        )
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('auth.html', mode='register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        gmail = request.form.get('gmail')
        password = request.form.get('password')
        
        user = User.query.filter_by(gmail=gmail).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials.', 'error')
            return redirect(url_for('login'))
    return render_template('auth.html', mode='login')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.user_class = request.form.get('class')
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', user=current_user)

@app.route('/api/scrape', methods=['POST'])
@login_required
def scrape():
    data = request.json
    topic = data.get('topic')
    summary = scrape_topic_summary(topic)
    return jsonify({'summary': summary})

@app.route('/api/validate_answer', methods=['POST'])
@login_required
def validate():
    from scraper import validate_answer_with_web
    data = request.json
    question = data.get('question')
    user_answer = data.get('user_answer')
    expected_answer = data.get('expected_answer')
    
    is_correct, feedback = validate_answer_with_web(question, user_answer, expected_answer)
    return jsonify({
        'is_correct': is_correct,
        'feedback': feedback
    })

@app.route('/assessment', methods=['GET', 'POST'])
@login_required
def assessment():
    if request.method == 'POST':
        # Store initial config in session or pass to chat
        subject = request.form.get('subject')
        topic = request.form.get('topic')
        num_questions = request.form.get('num_questions')
        marks = request.form.get('marks')
        return render_template('chat.html', subject=subject, topic=topic, num_questions=num_questions, marks=marks)
    return redirect(url_for('index'))

@app.route('/api/get_questions', methods=['POST'])
@login_required
def get_questions():
    data = request.json
    topic = data.get('topic', '').lower()
    num = int(data.get('num_questions', 5))
    
    # Try to find the topic in our mock data
    topic_key = None
    for key in QUESTIONS.keys():
        if key in topic or topic in key:
            topic_key = key
            break
    
    if topic_key:
        sample = random.sample(QUESTIONS[topic_key], min(num, len(QUESTIONS[topic_key])))
        return jsonify({'questions': sample})
    else:
        # Fallback if topic not found
        fallback = random.sample(QUESTIONS['computer science'], min(num, len(QUESTIONS['computer science'])))
        return jsonify({'questions': fallback, 'note': 'Topic not found, providing general questions.'})

@app.route('/api/save_history', methods=['POST'])
@login_required
def save_history():
    data = request.json
    new_history = AssessmentHistory(
        user_id=current_user.id,
        subject=data.get('subject'),
        topic=data.get('topic'),
        score=data.get('score'),
        total_questions=data.get('total_questions')
    )
    db.session.add(new_history)
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/history')
@login_required
def history():
    user_history = AssessmentHistory.query.filter_by(user_id=current_user.id).order_by(AssessmentHistory.timestamp.desc()).all()
    return render_template('history.html', history=user_history)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
