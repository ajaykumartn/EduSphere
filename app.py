from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json
import random
import string
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

# Database configuration
DATABASE_NAME = 'edusphere.db'

# Security utility functions
def is_valid_api_key(api_key):
    """Validate API key format without exposing it"""
    if not api_key or api_key == 'your_gemini_api_key_here':
        return False
    # Basic validation - Gemini API keys typically start with 'AI' and are 39 characters
    return len(api_key) >= 30 and not api_key.isspace()

def mask_api_key(api_key):
    """Mask API key for logging purposes"""
    if not api_key or len(api_key) < 8:
        return "Not configured"
    return f"{api_key[:4]}...{api_key[-4:]}"

# Configure Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if is_valid_api_key(GEMINI_API_KEY):
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        print(f"✅ AI Assistant: Successfully configured with key {mask_api_key(GEMINI_API_KEY)}")
    except Exception as e:
        print(f"❌ AI Assistant: Configuration failed - Invalid API key or network error")
        model = None
else:
    model = None
    print("⚠️  AI Assistant: Not configured - Please set a valid GEMINI_API_KEY in .env file")

# Custom template filter for date formatting
@app.template_filter('dateformat')
def dateformat(value, format='%b %d, %Y'):
    if value:
        if isinstance(value, str):
            try:
                # Try to parse the string as datetime
                dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                return dt.strftime(format)
            except:
                # If parsing fails, just return the date part
                return value[:10]
        else:
            # If it's a datetime object, format it
            return value.strftime(format)
    return 'N/A'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, role, email=None, full_name=None):
        self.id = id
        self.username = username
        self.role = role
        self.email = email
        self.full_name = full_name

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role, email, full_name FROM users WHERE id = ?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return User(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4])
    return None

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student',
            email TEXT,
            full_name TEXT,
            phone TEXT,
            profile_image TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Courses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Enrollments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            course_id INTEGER,
            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (course_id) REFERENCES courses (id)
        )
    ''')
    
    # FLUX sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flux_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_code TEXT UNIQUE NOT NULL,
            teacher_id INTEGER,
            title TEXT DEFAULT 'FLUX Session',
            current_question_json TEXT,
            current_prompt TEXT,
            is_active BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users (id)
        )
    ''')
    
    # Session participants table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS session_participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            user_id INTEGER,
            username TEXT,
            score INTEGER DEFAULT 0,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES flux_sessions (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Quiz responses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            user_id INTEGER,
            question_id INTEGER,
            selected_answer TEXT,
            is_correct BOOLEAN,
            responded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES flux_sessions (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Test series table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_series (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            exam_type TEXT NOT NULL,
            subject TEXT NOT NULL,
            difficulty_level TEXT DEFAULT 'Medium',
            duration_minutes INTEGER DEFAULT 180,
            total_marks INTEGER DEFAULT 100,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Questions table for test series
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_series_id INTEGER,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            explanation TEXT,
            marks INTEGER DEFAULT 4,
            negative_marks INTEGER DEFAULT -1,
            question_type TEXT DEFAULT 'MCQ',
            FOREIGN KEY (test_series_id) REFERENCES test_series (id)
        )
    ''')
    
    # Test attempts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_series_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            score INTEGER DEFAULT 0,
            total_questions INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            wrong_answers INTEGER DEFAULT 0,
            unanswered INTEGER DEFAULT 0,
            time_taken INTEGER DEFAULT 0,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            is_completed BOOLEAN DEFAULT 0,
            FOREIGN KEY (test_series_id) REFERENCES test_series (id),
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    ''')
    
    # Test responses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attempt_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            selected_answer TEXT,
            is_correct BOOLEAN DEFAULT 0,
            marks_obtained INTEGER DEFAULT 0,
            time_spent INTEGER DEFAULT 0,
            answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (attempt_id) REFERENCES test_attempts (id),
            FOREIGN KEY (question_id) REFERENCES questions (id)
        )
    ''')
    
    # Quizzes table for faculty-created quizzes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            quiz_code TEXT UNIQUE NOT NULL,
            faculty_id INTEGER NOT NULL,
            time_limit INTEGER DEFAULT 30,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (faculty_id) REFERENCES users (id)
        )
    ''')
    
    # Quiz questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            points INTEGER DEFAULT 1,
            question_order INTEGER DEFAULT 1,
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
        )
    ''')
    
    # Quiz attempts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            score INTEGER DEFAULT 0,
            total_questions INTEGER DEFAULT 0,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            is_completed BOOLEAN DEFAULT 0,
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id),
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    ''')
    
    # Quiz answers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attempt_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            selected_answer TEXT,
            is_correct BOOLEAN DEFAULT 0,
            answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (attempt_id) REFERENCES quiz_attempts (id),
            FOREIGN KEY (question_id) REFERENCES quiz_questions (id)
        )
    ''')
    
    # Live classes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS live_classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            faculty_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            class_code TEXT UNIQUE NOT NULL,
            scheduled_at TIMESTAMP,
            started_at TIMESTAMP,
            ended_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 0,
            is_recording BOOLEAN DEFAULT 0,
            whiteboard_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses (id),
            FOREIGN KEY (faculty_id) REFERENCES users (id)
        )
    ''')
    
    # Live class participants table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS live_class_participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            left_at TIMESTAMP,
            is_present BOOLEAN DEFAULT 1,
            FOREIGN KEY (class_id) REFERENCES live_classes (id),
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    ''')
    
    # Whiteboard actions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS whiteboard_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            action_type TEXT NOT NULL,
            action_data TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (class_id) REFERENCES live_classes (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # AI Chat history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            user_role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Basic Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        email = request.form.get('email', '')
        full_name = request.form.get('full_name', '')
        phone = request.form.get('phone', '')
        
        if not username or not password or not role:
            flash('Please fill in all required fields')
            return render_template('register.html')
        
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
        if cursor.fetchone():
            flash('Username or email already exists')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, email, full_name, phone) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, password_hash, role, email, full_name, phone))
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password_hash, role, email, full_name FROM users WHERE email = ?', (email,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data[2], password):
            user = User(user_data[0], user_data[1], user_data[3], user_data[4], user_data[5])
            login_user(user)
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'faculty':
                return redirect(url_for('faculty_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Redirect to appropriate dashboard based on role
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif current_user.role == 'faculty':
        return redirect(url_for('faculty_dashboard'))
    else:
        return redirect(url_for('student_dashboard'))

@app.route('/student-dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get enrolled courses
    cursor.execute('''
        SELECT c.id, c.title, c.description, c.image_url 
        FROM courses c
        JOIN enrollments e ON c.id = e.course_id
        WHERE e.user_id = ?
    ''', (current_user.id,))
    enrolled_courses = cursor.fetchall()
    
    # Get test statistics
    cursor.execute('''
        SELECT COUNT(*) FROM quiz_responses 
        WHERE user_id = ?
    ''', (current_user.id,))
    tests_taken = cursor.fetchone()[0]
    
    # Get average score
    cursor.execute('''
        SELECT AVG(CASE WHEN is_correct THEN 1 ELSE 0 END) * 100 
        FROM quiz_responses 
        WHERE user_id = ?
    ''', (current_user.id,))
    avg_score = cursor.fetchone()[0] or 0
    
    # Get recent activity
    cursor.execute('''
        SELECT fs.title, qr.responded_at, qr.is_correct
        FROM quiz_responses qr
        JOIN flux_sessions fs ON qr.session_id = fs.id
        WHERE qr.user_id = ?
        ORDER BY qr.responded_at DESC
        LIMIT 5
    ''', (current_user.id,))
    recent_activity = cursor.fetchall()
    
    conn.close()
    
    return render_template('student_dashboard.html', 
                         courses=enrolled_courses,
                         tests_taken=tests_taken,
                         avg_score=round(avg_score, 1),
                         recent_activity=recent_activity)

@app.route('/faculty-dashboard')
@login_required
def faculty_dashboard():
    if current_user.role != 'faculty':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get faculty's sessions
    cursor.execute('''
        SELECT id, session_code, title, is_active, created_at
        FROM flux_sessions 
        WHERE teacher_id = ?
        ORDER BY created_at DESC
        LIMIT 10
    ''', (current_user.id,))
    sessions = cursor.fetchall()
    
    # Get total students taught
    cursor.execute('''
        SELECT COUNT(DISTINCT sp.user_id)
        FROM session_participants sp
        JOIN flux_sessions fs ON sp.session_id = fs.id
        WHERE fs.teacher_id = ?
    ''', (current_user.id,))
    total_students = cursor.fetchone()[0]
    
    # Get total sessions conducted
    cursor.execute('''
        SELECT COUNT(*) FROM flux_sessions 
        WHERE teacher_id = ?
    ''', (current_user.id,))
    total_sessions = cursor.fetchone()[0]
    
    # Get recent quiz responses
    cursor.execute('''
        SELECT fs.title, COUNT(qr.id) as responses, 
               AVG(CASE WHEN qr.is_correct THEN 1 ELSE 0 END) * 100 as avg_score
        FROM flux_sessions fs
        LEFT JOIN quiz_responses qr ON fs.id = qr.session_id
        WHERE fs.teacher_id = ?
        GROUP BY fs.id, fs.title
        ORDER BY fs.created_at DESC
        LIMIT 5
    ''', (current_user.id,))
    session_stats = cursor.fetchall()
    
    # Get faculty's quizzes
    cursor.execute('''
        SELECT id, title, quiz_code, is_active, created_at,
               (SELECT COUNT(*) FROM quiz_attempts WHERE quiz_id = quizzes.id) as attempts
        FROM quizzes 
        WHERE faculty_id = ?
        ORDER BY created_at DESC
        LIMIT 10
    ''', (current_user.id,))
    quizzes = cursor.fetchall()
    
    conn.close()
    
    return render_template('faculty_dashboard.html',
                         sessions=sessions,
                         total_students=total_students,
                         total_sessions=total_sessions,
                         session_stats=session_stats,
                         quizzes=quizzes)

@app.route('/create-quiz', methods=['GET', 'POST'])
@login_required
def create_quiz():
    if current_user.role != 'faculty':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description', '')
        time_limit = int(request.form.get('time_limit', 30))
        
        # Generate unique quiz code
        quiz_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        
        # Check if quiz code already exists
        while True:
            cursor.execute('SELECT id FROM quizzes WHERE quiz_code = ?', (quiz_code,))
            if not cursor.fetchone():
                break
            quiz_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Create quiz
        cursor.execute('''
            INSERT INTO quizzes (title, description, quiz_code, faculty_id, time_limit)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, quiz_code, current_user.id, time_limit))
        
        quiz_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        flash(f'Quiz created successfully! Quiz Code: {quiz_code}', 'success')
        return redirect(url_for('edit_quiz', quiz_id=quiz_id))
    
    return render_template('create_quiz.html')

@app.route('/edit-quiz/<int:quiz_id>')
@login_required
def edit_quiz(quiz_id):
    if current_user.role != 'faculty':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get quiz details
    cursor.execute('''
        SELECT id, title, description, quiz_code, time_limit, is_active
        FROM quizzes 
        WHERE id = ? AND faculty_id = ?
    ''', (quiz_id, current_user.id))
    quiz = cursor.fetchone()
    
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('faculty_dashboard'))
    
    # Get quiz questions
    cursor.execute('''
        SELECT id, question_text, option_a, option_b, option_c, option_d, 
               correct_answer, points, question_order
        FROM quiz_questions 
        WHERE quiz_id = ?
        ORDER BY question_order
    ''', (quiz_id,))
    questions = cursor.fetchall()
    
    conn.close()
    
    return render_template('edit_quiz.html', quiz=quiz, questions=questions)

@app.route('/add-question/<int:quiz_id>', methods=['POST'])
@login_required
def add_question(quiz_id):
    if current_user.role != 'faculty':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    data = request.get_json()
    question_text = data.get('question_text')
    option_a = data.get('option_a')
    option_b = data.get('option_b')
    option_c = data.get('option_c')
    option_d = data.get('option_d')
    correct_answer = data.get('correct_answer')
    points = int(data.get('points', 1))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Verify quiz belongs to faculty
    cursor.execute('SELECT id FROM quizzes WHERE id = ? AND faculty_id = ?', (quiz_id, current_user.id))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'error': 'Quiz not found'})
    
    # Get next question order
    cursor.execute('SELECT MAX(question_order) FROM quiz_questions WHERE quiz_id = ?', (quiz_id,))
    max_order = cursor.fetchone()[0] or 0
    
    # Add question
    cursor.execute('''
        INSERT INTO quiz_questions 
        (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_answer, points, question_order)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_answer, points, max_order + 1))
    
    question_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'question_id': question_id})

@app.route('/delete-question/<int:question_id>', methods=['DELETE'])
@login_required
def delete_question(question_id):
    if current_user.role != 'faculty':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Verify question belongs to faculty's quiz
    cursor.execute('''
        SELECT qq.id FROM quiz_questions qq
        JOIN quizzes q ON qq.quiz_id = q.id
        WHERE qq.id = ? AND q.faculty_id = ?
    ''', (question_id, current_user.id))
    
    if not cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'error': 'Question not found'})
    
    # Delete question
    cursor.execute('DELETE FROM quiz_questions WHERE id = ?', (question_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/toggle-quiz/<int:quiz_id>', methods=['POST'])
@login_required
def toggle_quiz(quiz_id):
    if current_user.role != 'faculty':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Verify quiz belongs to faculty
    cursor.execute('SELECT is_active FROM quizzes WHERE id = ? AND faculty_id = ?', (quiz_id, current_user.id))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'success': False, 'error': 'Quiz not found'})
    
    # Toggle active status
    new_status = not result[0]
    cursor.execute('UPDATE quizzes SET is_active = ? WHERE id = ?', (new_status, quiz_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'is_active': new_status})

# Session Management Routes
@app.route('/session-details/<int:session_id>')
@login_required
def session_details(session_id):
    if current_user.role != 'faculty':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get session details
    cursor.execute('''
        SELECT id, session_code, title, is_active, created_at, current_prompt
        FROM flux_sessions 
        WHERE id = ? AND teacher_id = ?
    ''', (session_id, current_user.id))
    session = cursor.fetchone()
    
    if not session:
        conn.close()
        flash('Session not found', 'error')
        return redirect(url_for('faculty_dashboard'))
    
    # Get participants
    cursor.execute('''
        SELECT sp.username, sp.score, sp.joined_at,
               COUNT(qr.id) as responses,
               AVG(CASE WHEN qr.is_correct THEN 1 ELSE 0 END) * 100 as avg_score
        FROM session_participants sp
        LEFT JOIN quiz_responses qr ON sp.session_id = qr.session_id AND sp.username = qr.user_id
        WHERE sp.session_id = ?
        GROUP BY sp.id, sp.username, sp.score, sp.joined_at
        ORDER BY sp.score DESC, sp.joined_at ASC
    ''', (session_id,))
    participants = cursor.fetchall()
    
    # Get quiz responses for this session
    cursor.execute('''
        SELECT qr.responded_at, qr.is_correct, sp.username
        FROM quiz_responses qr
        JOIN session_participants sp ON qr.session_id = sp.session_id
        WHERE qr.session_id = ?
        ORDER BY qr.responded_at DESC
        LIMIT 20
    ''', (session_id,))
    recent_responses = cursor.fetchall()
    
    conn.close()
    
    return render_template('session_details.html', 
                         session=session, 
                         participants=participants,
                         recent_responses=recent_responses)

@app.route('/session-analytics/<int:session_id>')
@login_required
def session_analytics(session_id):
    if current_user.role != 'faculty':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get session details
    cursor.execute('''
        SELECT id, session_code, title, is_active, created_at
        FROM flux_sessions 
        WHERE id = ? AND teacher_id = ?
    ''', (session_id, current_user.id))
    session = cursor.fetchone()
    
    if not session:
        conn.close()
        flash('Session not found', 'error')
        return redirect(url_for('faculty_dashboard'))
    
    # Get participation stats
    cursor.execute('''
        SELECT COUNT(*) as total_participants,
               AVG(score) as avg_score,
               MAX(score) as max_score,
               MIN(score) as min_score
        FROM session_participants 
        WHERE session_id = ?
    ''', (session_id,))
    participation_stats = cursor.fetchone()
    
    # Get response accuracy over time
    cursor.execute('''
        SELECT DATE(qr.responded_at) as date,
               COUNT(*) as total_responses,
               SUM(CASE WHEN qr.is_correct THEN 1 ELSE 0 END) as correct_responses
        FROM quiz_responses qr
        WHERE qr.session_id = ?
        GROUP BY DATE(qr.responded_at)
        ORDER BY date
    ''', (session_id,))
    daily_stats = cursor.fetchall()
    
    # Get top performers
    cursor.execute('''
        SELECT sp.username, sp.score,
               COUNT(qr.id) as total_responses,
               AVG(CASE WHEN qr.is_correct THEN 1 ELSE 0 END) * 100 as accuracy
        FROM session_participants sp
        LEFT JOIN quiz_responses qr ON sp.session_id = qr.session_id
        WHERE sp.session_id = ?
        GROUP BY sp.id, sp.username, sp.score
        ORDER BY sp.score DESC, accuracy DESC
        LIMIT 10
    ''', (session_id,))
    top_performers = cursor.fetchall()
    
    conn.close()
    
    return render_template('session_analytics.html',
                         session=session,
                         participation_stats=participation_stats,
                         daily_stats=daily_stats,
                         top_performers=top_performers)

@app.route('/end-session/<int:session_id>', methods=['POST'])
@login_required
def end_session(session_id):
    if current_user.role != 'faculty':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Verify session belongs to faculty
    cursor.execute('SELECT id FROM flux_sessions WHERE id = ? AND teacher_id = ?', (session_id, current_user.id))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'error': 'Session not found'})
    
    # End session
    cursor.execute('UPDATE flux_sessions SET is_active = 0 WHERE id = ?', (session_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# Analytics and Student Management Routes
@app.route('/faculty-analytics')
@login_required
def faculty_analytics():
    if current_user.role != 'faculty':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Overall stats
    cursor.execute('''
        SELECT COUNT(DISTINCT fs.id) as total_sessions,
               COUNT(DISTINCT sp.username) as total_students,
               COUNT(qr.id) as total_responses,
               AVG(CASE WHEN qr.is_correct THEN 1 ELSE 0 END) * 100 as avg_accuracy
        FROM flux_sessions fs
        LEFT JOIN session_participants sp ON fs.id = sp.session_id
        LEFT JOIN quiz_responses qr ON fs.id = qr.session_id
        WHERE fs.teacher_id = ?
    ''', (current_user.id,))
    overall_stats = cursor.fetchone()
    
    # Quiz stats
    cursor.execute('''
        SELECT COUNT(*) as total_quizzes,
               COUNT(CASE WHEN is_active THEN 1 END) as active_quizzes,
               COUNT(DISTINCT qa.student_id) as students_attempted,
               AVG(qa.score) as avg_quiz_score
        FROM quizzes q
        LEFT JOIN quiz_attempts qa ON q.id = qa.quiz_id
        WHERE q.faculty_id = ?
    ''', (current_user.id,))
    quiz_stats = cursor.fetchone()
    
    # Monthly activity
    cursor.execute('''
        SELECT strftime('%Y-%m', fs.created_at) as month,
               COUNT(fs.id) as sessions_created,
               COUNT(DISTINCT sp.username) as unique_participants
        FROM flux_sessions fs
        LEFT JOIN session_participants sp ON fs.id = sp.session_id
        WHERE fs.teacher_id = ?
        GROUP BY strftime('%Y-%m', fs.created_at)
        ORDER BY month DESC
        LIMIT 12
    ''', (current_user.id,))
    monthly_activity = cursor.fetchall()
    
    # Top performing students
    cursor.execute('''
        SELECT sp.username,
               COUNT(DISTINCT sp.session_id) as sessions_joined,
               AVG(sp.score) as avg_session_score,
               COUNT(qr.id) as total_responses,
               AVG(CASE WHEN qr.is_correct THEN 1 ELSE 0 END) * 100 as accuracy
        FROM session_participants sp
        JOIN flux_sessions fs ON sp.session_id = fs.id
        LEFT JOIN quiz_responses qr ON sp.session_id = qr.session_id
        WHERE fs.teacher_id = ?
        GROUP BY sp.username
        HAVING sessions_joined > 0
        ORDER BY avg_session_score DESC, accuracy DESC
        LIMIT 15
    ''', (current_user.id,))
    top_students = cursor.fetchall()
    
    conn.close()
    
    return render_template('faculty_analytics.html',
                         overall_stats=overall_stats,
                         quiz_stats=quiz_stats,
                         monthly_activity=monthly_activity,
                         top_students=top_students)

@app.route('/manage-students')
@login_required
def manage_students():
    if current_user.role != 'faculty':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get all students who have participated in faculty's sessions
    cursor.execute('''
        SELECT DISTINCT sp.username,
               COUNT(DISTINCT sp.session_id) as sessions_joined,
               AVG(sp.score) as avg_score,
               MAX(sp.joined_at) as last_activity,
               COUNT(qr.id) as total_responses,
               AVG(CASE WHEN qr.is_correct THEN 1 ELSE 0 END) * 100 as accuracy
        FROM session_participants sp
        JOIN flux_sessions fs ON sp.session_id = fs.id
        LEFT JOIN quiz_responses qr ON sp.session_id = qr.session_id
        WHERE fs.teacher_id = ?
        GROUP BY sp.username
        ORDER BY last_activity DESC
    ''', (current_user.id,))
    students = cursor.fetchall()
    
    # Get students who have taken faculty's quizzes
    cursor.execute('''
        SELECT DISTINCT u.username, u.full_name, u.email,
               COUNT(qa.id) as quizzes_taken,
               AVG(qa.score) as avg_quiz_score,
               MAX(qa.completed_at) as last_quiz_date
        FROM users u
        JOIN quiz_attempts qa ON u.id = qa.student_id
        JOIN quizzes q ON qa.quiz_id = q.id
        WHERE q.faculty_id = ? AND u.role = 'student'
        GROUP BY u.id, u.username, u.full_name, u.email
        ORDER BY last_quiz_date DESC
    ''', (current_user.id,))
    quiz_students = cursor.fetchall()
    
    conn.close()
    
    return render_template('manage_students.html',
                         students=students,
                         quiz_students=quiz_students)

# Live Classes Routes
@app.route('/live-classes')
@login_required
def live_classes():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    if current_user.role == 'faculty':
        # Get faculty's live classes
        cursor.execute('''
            SELECT lc.id, lc.title, lc.class_code, lc.scheduled_at, lc.is_active,
                   c.title as course_title, COUNT(lcp.id) as participants
            FROM live_classes lc
            JOIN courses c ON lc.course_id = c.id
            LEFT JOIN live_class_participants lcp ON lc.id = lcp.class_id
            WHERE lc.faculty_id = ?
            GROUP BY lc.id
            ORDER BY lc.scheduled_at DESC
        ''', (current_user.id,))
        classes = cursor.fetchall()
        
        # Get courses taught by faculty
        cursor.execute('''
            SELECT DISTINCT c.id, c.title
            FROM courses c
            JOIN enrollments e ON c.id = e.course_id
            JOIN users u ON e.user_id = u.id
            WHERE u.role = 'student'
        ''')
        courses = cursor.fetchall()
        
    else:  # student
        # Get available live classes for enrolled courses
        cursor.execute('''
            SELECT lc.id, lc.title, lc.class_code, lc.scheduled_at, lc.is_active,
                   c.title as course_title, u.full_name as faculty_name,
                   COUNT(lcp.id) as participants
            FROM live_classes lc
            JOIN courses c ON lc.course_id = c.id
            JOIN users u ON lc.faculty_id = u.id
            JOIN enrollments e ON c.id = e.course_id
            LEFT JOIN live_class_participants lcp ON lc.id = lcp.class_id
            WHERE e.user_id = ?
            GROUP BY lc.id
            ORDER BY lc.scheduled_at DESC
        ''', (current_user.id,))
        classes = cursor.fetchall()
        courses = []
    
    conn.close()
    
    return render_template('live_classes.html', classes=classes, courses=courses)

@app.route('/create-live-class', methods=['POST'])
@login_required
def create_live_class():
    if current_user.role != 'faculty':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    data = request.get_json()
    course_id = data.get('course_id')
    title = data.get('title')
    description = data.get('description', '')
    scheduled_at = data.get('scheduled_at')
    
    # Generate unique class code
    class_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Check if class code already exists
    while True:
        cursor.execute('SELECT id FROM live_classes WHERE class_code = ?', (class_code,))
        if not cursor.fetchone():
            break
        class_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Create live class
    cursor.execute('''
        INSERT INTO live_classes (course_id, faculty_id, title, description, class_code, scheduled_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (course_id, current_user.id, title, description, class_code, scheduled_at))
    
    class_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'class_id': class_id,
        'class_code': class_code
    })

@app.route('/start-live-class/<int:class_id>', methods=['POST'])
@login_required
def start_live_class(class_id):
    if current_user.role != 'faculty':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Verify class belongs to faculty
    cursor.execute('SELECT id FROM live_classes WHERE id = ? AND faculty_id = ?', (class_id, current_user.id))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'error': 'Class not found'})
    
    # Start the class
    cursor.execute('''
        UPDATE live_classes 
        SET is_active = 1, started_at = CURRENT_TIMESTAMP 
        WHERE id = ?
    ''', (class_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/end-live-class/<int:class_id>', methods=['POST'])
@login_required
def end_live_class(class_id):
    if current_user.role != 'faculty':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Verify class belongs to faculty
    cursor.execute('SELECT id FROM live_classes WHERE id = ? AND faculty_id = ?', (class_id, current_user.id))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'error': 'Class not found'})
    
    # End the class
    cursor.execute('''
        UPDATE live_classes 
        SET is_active = 0, ended_at = CURRENT_TIMESTAMP 
        WHERE id = ?
    ''', (class_id,))
    
    # Mark all participants as left
    cursor.execute('''
        UPDATE live_class_participants 
        SET left_at = CURRENT_TIMESTAMP, is_present = 0 
        WHERE class_id = ? AND left_at IS NULL
    ''', (class_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/join-live-class/<class_code>')
@login_required
def join_live_class(class_code):
    if current_user.role != 'student':
        flash('Only students can join live classes', 'error')
        return redirect(url_for('live_classes'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get class details
    cursor.execute('''
        SELECT lc.id, lc.title, lc.is_active, c.title as course_title,
               u.full_name as faculty_name
        FROM live_classes lc
        JOIN courses c ON lc.course_id = c.id
        JOIN users u ON lc.faculty_id = u.id
        WHERE lc.class_code = ?
    ''', (class_code,))
    class_info = cursor.fetchone()
    
    if not class_info:
        conn.close()
        flash('Class not found', 'error')
        return redirect(url_for('live_classes'))
    
    if not class_info[2]:  # is_active
        conn.close()
        flash('This class is not currently active', 'error')
        return redirect(url_for('live_classes'))
    
    # Check if student is enrolled in the course
    cursor.execute('''
        SELECT e.id FROM enrollments e
        JOIN live_classes lc ON e.course_id = lc.course_id
        WHERE lc.class_code = ? AND e.user_id = ?
    ''', (class_code, current_user.id))
    
    if not cursor.fetchone():
        conn.close()
        flash('You are not enrolled in this course', 'error')
        return redirect(url_for('live_classes'))
    
    # Add participant if not already joined
    cursor.execute('''
        INSERT OR IGNORE INTO live_class_participants (class_id, student_id)
        VALUES (?, ?)
    ''', (class_info[0], current_user.id))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('live_classroom', class_id=class_info[0]))

@app.route('/live-classroom/<int:class_id>')
@login_required
def live_classroom(class_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get class details
    cursor.execute('''
        SELECT lc.id, lc.title, lc.class_code, lc.is_active, lc.whiteboard_data,
               c.title as course_title, u.full_name as faculty_name, lc.faculty_id
        FROM live_classes lc
        JOIN courses c ON lc.course_id = c.id
        JOIN users u ON lc.faculty_id = u.id
        WHERE lc.id = ?
    ''', (class_id,))
    class_info = cursor.fetchone()
    
    if not class_info:
        conn.close()
        flash('Class not found', 'error')
        return redirect(url_for('live_classes'))
    
    # Check permissions
    if current_user.role == 'student':
        # Check if student is enrolled
        cursor.execute('''
            SELECT e.id FROM enrollments e
            JOIN live_classes lc ON e.course_id = lc.course_id
            WHERE lc.id = ? AND e.user_id = ?
        ''', (class_id, current_user.id))
        
        if not cursor.fetchone():
            conn.close()
            flash('You are not enrolled in this course', 'error')
            return redirect(url_for('live_classes'))
    
    elif current_user.role == 'faculty':
        # Check if faculty owns this class
        if class_info[7] != current_user.id:  # faculty_id
            conn.close()
            flash('Access denied', 'error')
            return redirect(url_for('live_classes'))
    
    # Get participants
    cursor.execute('''
        SELECT u.full_name, u.username, lcp.joined_at, lcp.is_present
        FROM live_class_participants lcp
        JOIN users u ON lcp.student_id = u.id
        WHERE lcp.class_id = ?
        ORDER BY lcp.joined_at
    ''', (class_id,))
    participants = cursor.fetchall()
    
    conn.close()
    
    return render_template('live_classroom.html', 
                         class_info=class_info, 
                         participants=participants,
                         is_faculty=(current_user.role == 'faculty' and current_user.id == class_info[7]))

@app.route('/api/whiteboard-action', methods=['POST'])
@login_required
def whiteboard_action():
    data = request.get_json()
    class_id = data.get('class_id')
    action_type = data.get('action_type')
    action_data = data.get('action_data')
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Verify user has access to this class
    if current_user.role == 'faculty':
        cursor.execute('SELECT id FROM live_classes WHERE id = ? AND faculty_id = ?', (class_id, current_user.id))
    else:
        cursor.execute('''
            SELECT lc.id FROM live_classes lc
            JOIN enrollments e ON lc.course_id = e.course_id
            WHERE lc.id = ? AND e.user_id = ?
        ''', (class_id, current_user.id))
    
    if not cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'error': 'Access denied'})
    
    # Save whiteboard action
    cursor.execute('''
        INSERT INTO whiteboard_actions (class_id, user_id, action_type, action_data)
        VALUES (?, ?, ?, ?)
    ''', (class_id, current_user.id, action_type, json.dumps(action_data)))
    
    # Update class whiteboard data if it's a faculty action
    if current_user.role == 'faculty':
        cursor.execute('''
            UPDATE live_classes 
            SET whiteboard_data = ? 
            WHERE id = ?
        ''', (json.dumps(action_data), class_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/get-whiteboard-data/<int:class_id>')
@login_required
def get_whiteboard_data(class_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get latest whiteboard data
    cursor.execute('''
        SELECT whiteboard_data FROM live_classes 
        WHERE id = ?
    ''', (class_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result and result[0]:
        return jsonify({'success': True, 'data': json.loads(result[0])})
    else:
        return jsonify({'success': True, 'data': None})

# Test Series Routes
@app.route('/test-series')
@login_required
def test_series():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get all test series grouped by exam type
    cursor.execute('''
        SELECT ts.id, ts.title, ts.description, ts.exam_type, ts.subject, 
               ts.difficulty_level, ts.duration_minutes, ts.total_marks,
               COUNT(q.id) as question_count,
               COUNT(ta.id) as attempt_count
        FROM test_series ts
        LEFT JOIN questions q ON ts.id = q.test_series_id
        LEFT JOIN test_attempts ta ON ts.id = ta.test_series_id AND ta.student_id = ?
        WHERE ts.is_active = 1
        GROUP BY ts.id
        ORDER BY ts.exam_type, ts.subject
    ''', (current_user.id,))
    
    all_tests = cursor.fetchall()
    
    # Group tests by exam type
    tests_by_exam = {}
    for test in all_tests:
        exam_type = test[3]
        if exam_type not in tests_by_exam:
            tests_by_exam[exam_type] = []
        tests_by_exam[exam_type].append(test)
    
    # Get user's recent attempts
    cursor.execute('''
        SELECT ta.id, ts.title, ts.exam_type, ta.score, ta.total_questions, 
               ta.completed_at, ta.is_completed
        FROM test_attempts ta
        JOIN test_series ts ON ta.test_series_id = ts.id
        WHERE ta.student_id = ?
        ORDER BY ta.started_at DESC
        LIMIT 5
    ''', (current_user.id,))
    recent_attempts = cursor.fetchall()
    
    conn.close()
    
    return render_template('test_series.html', 
                         tests_by_exam=tests_by_exam, 
                         recent_attempts=recent_attempts)

@app.route('/start-test/<int:test_id>')
@login_required
def start_test(test_id):
    if current_user.role != 'student':
        flash('Only students can take tests', 'error')
        return redirect(url_for('test_series'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get test details
    cursor.execute('''
        SELECT id, title, description, exam_type, subject, duration_minutes, total_marks
        FROM test_series 
        WHERE id = ? AND is_active = 1
    ''', (test_id,))
    test = cursor.fetchone()
    
    if not test:
        conn.close()
        flash('Test not found', 'error')
        return redirect(url_for('test_series'))
    
    # Check if student has already completed this test
    cursor.execute('''
        SELECT id, is_completed FROM test_attempts 
        WHERE test_series_id = ? AND student_id = ? AND is_completed = 1
    ''', (test_id, current_user.id))
    completed_attempt = cursor.fetchone()
    
    if completed_attempt:
        conn.close()
        flash('You have already completed this test', 'info')
        return redirect(url_for('test_result', attempt_id=completed_attempt[0]))
    
    # Get test questions
    cursor.execute('''
        SELECT id, question_text, option_a, option_b, option_c, option_d, marks
        FROM questions 
        WHERE test_series_id = ?
        ORDER BY id
    ''', (test_id,))
    questions = cursor.fetchall()
    
    if not questions:
        conn.close()
        flash('This test has no questions yet', 'error')
        return redirect(url_for('test_series'))
    
    # Create new attempt
    cursor.execute('''
        INSERT INTO test_attempts (test_series_id, student_id, total_questions)
        VALUES (?, ?, ?)
    ''', (test_id, current_user.id, len(questions)))
    attempt_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return render_template('take_test.html', 
                         test=test, 
                         questions=questions, 
                         attempt_id=attempt_id)

@app.route('/submit-test-answer', methods=['POST'])
@login_required
def submit_test_answer():
    if current_user.role != 'student':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    data = request.get_json()
    attempt_id = data.get('attempt_id')
    question_id = data.get('question_id')
    selected_answer = data.get('selected_answer')
    time_spent = data.get('time_spent', 0)
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Verify attempt belongs to student
    cursor.execute('''
        SELECT ta.test_series_id FROM test_attempts ta
        WHERE ta.id = ? AND ta.student_id = ? AND ta.is_completed = 0
    ''', (attempt_id, current_user.id))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'success': False, 'error': 'Invalid attempt'})
    
    # Get question details
    cursor.execute('''
        SELECT correct_answer, marks, negative_marks FROM questions 
        WHERE id = ? AND test_series_id = ?
    ''', (question_id, result[0]))
    question = cursor.fetchone()
    
    if not question:
        conn.close()
        return jsonify({'success': False, 'error': 'Question not found'})
    
    is_correct = selected_answer == question[0]
    marks_obtained = question[1] if is_correct else question[2]
    
    # Save or update response
    cursor.execute('''
        INSERT OR REPLACE INTO test_responses 
        (attempt_id, question_id, selected_answer, is_correct, marks_obtained, time_spent)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (attempt_id, question_id, selected_answer, is_correct, marks_obtained, time_spent))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'is_correct': is_correct, 'marks': marks_obtained})

@app.route('/complete-test/<int:attempt_id>', methods=['POST'])
@login_required
def complete_test(attempt_id):
    if current_user.role != 'student':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Verify attempt belongs to student
    cursor.execute('''
        SELECT id, total_questions FROM test_attempts 
        WHERE id = ? AND student_id = ? AND is_completed = 0
    ''', (attempt_id, current_user.id))
    attempt = cursor.fetchone()
    
    if not attempt:
        conn.close()
        return jsonify({'success': False, 'error': 'Invalid attempt'})
    
    # Calculate final score
    cursor.execute('''
        SELECT 
            COUNT(*) as total_answered,
            SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_answers,
            SUM(CASE WHEN is_correct = 0 AND selected_answer IS NOT NULL THEN 1 ELSE 0 END) as wrong_answers,
            SUM(marks_obtained) as total_score
        FROM test_responses 
        WHERE attempt_id = ?
    ''', (attempt_id,))
    result = cursor.fetchone()
    
    total_answered = result[0] or 0
    correct_answers = result[1] or 0
    wrong_answers = result[2] or 0
    total_score = result[3] or 0
    unanswered = attempt[1] - total_answered
    
    # Update attempt
    cursor.execute('''
        UPDATE test_attempts 
        SET score = ?, correct_answers = ?, wrong_answers = ?, unanswered = ?,
            is_completed = 1, completed_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (total_score, correct_answers, wrong_answers, unanswered, attempt_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True, 
        'score': total_score,
        'correct': correct_answers,
        'wrong': wrong_answers,
        'unanswered': unanswered
    })

@app.route('/test-result/<int:attempt_id>')
@login_required
def test_result(attempt_id):
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get attempt details
    cursor.execute('''
        SELECT ta.score, ta.total_questions, ta.correct_answers, ta.wrong_answers, 
               ta.unanswered, ta.completed_at, ts.title, ts.exam_type, ts.subject, ts.total_marks
        FROM test_attempts ta
        JOIN test_series ts ON ta.test_series_id = ts.id
        WHERE ta.id = ? AND ta.student_id = ?
    ''', (attempt_id, current_user.id))
    attempt = cursor.fetchone()
    
    if not attempt:
        conn.close()
        flash('Test result not found', 'error')
        return redirect(url_for('test_series'))
    
    # Get detailed answers
    cursor.execute('''
        SELECT q.question_text, q.option_a, q.option_b, q.option_c, q.option_d,
               q.correct_answer, tr.selected_answer, tr.is_correct, q.explanation, q.marks
        FROM test_responses tr
        JOIN questions q ON tr.question_id = q.id
        WHERE tr.attempt_id = ?
        ORDER BY q.id
    ''', (attempt_id,))
    answers = cursor.fetchall()
    
    # Get rank/percentile (simplified calculation)
    cursor.execute('''
        SELECT COUNT(*) as better_scores
        FROM test_attempts ta2
        JOIN test_attempts ta1 ON ta2.test_series_id = ta1.test_series_id
        WHERE ta1.id = ? AND ta2.score > ta1.score AND ta2.is_completed = 1
    ''', (attempt_id,))
    better_scores = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) as total_attempts
        FROM test_attempts ta2
        JOIN test_attempts ta1 ON ta2.test_series_id = ta1.test_series_id
        WHERE ta1.id = ? AND ta2.is_completed = 1
    ''', (attempt_id,))
    total_attempts = cursor.fetchone()[0]
    
    rank = better_scores + 1
    percentile = ((total_attempts - better_scores) / total_attempts * 100) if total_attempts > 0 else 0
    
    conn.close()
    
    return render_template('test_result.html', 
                         attempt=attempt, 
                         answers=answers,
                         rank=rank,
                         percentile=round(percentile, 2))

@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get user statistics
    cursor.execute('SELECT COUNT(*) FROM users WHERE role = "student"')
    total_students = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE role = "faculty"')
    total_faculty = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM courses')
    total_courses = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM flux_sessions')
    total_sessions = cursor.fetchone()[0]
    
    # Get recent registrations
    cursor.execute('''
        SELECT username, role, created_at 
        FROM users 
        ORDER BY created_at DESC 
        LIMIT 10
    ''')
    recent_users = cursor.fetchall()
    
    # Get active sessions
    cursor.execute('''
        SELECT fs.session_code, fs.title, u.username as teacher, 
               COUNT(sp.id) as participants
        FROM flux_sessions fs
        JOIN users u ON fs.teacher_id = u.id
        LEFT JOIN session_participants sp ON fs.id = sp.session_id
        WHERE fs.is_active = 1
        GROUP BY fs.id
    ''')
    active_sessions = cursor.fetchall()
    
    # Get course enrollment stats
    cursor.execute('''
        SELECT c.title, COUNT(e.id) as enrollments
        FROM courses c
        LEFT JOIN enrollments e ON c.id = e.course_id
        GROUP BY c.id, c.title
        ORDER BY enrollments DESC
        LIMIT 5
    ''')
    course_stats = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html',
                         total_students=total_students,
                         total_faculty=total_faculty,
                         total_courses=total_courses,
                         total_sessions=total_sessions,
                         recent_users=recent_users,
                         active_sessions=active_sessions,
                         course_stats=course_stats)

@app.route('/courses')
def courses():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM courses')
    all_courses = cursor.fetchall()
    
    # Get enrolled course IDs for current user
    enrolled_course_ids = []
    if current_user.is_authenticated:
        cursor.execute('SELECT course_id FROM enrollments WHERE user_id = ?', (current_user.id,))
        enrolled_course_ids = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return render_template('courses.html', courses=all_courses, enrolled_course_ids=enrolled_course_ids)

@app.route('/enroll/<int:course_id>')
@login_required
def enroll(course_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Check if already enrolled
    cursor.execute('SELECT id FROM enrollments WHERE user_id = ? AND course_id = ?', 
                  (current_user.id, course_id))
    if cursor.fetchone():
        flash('You are already enrolled in this course!')
    else:
        cursor.execute('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', 
                      (current_user.id, course_id))
        conn.commit()
        flash('Successfully enrolled in the course!')
    
    conn.close()
    return redirect(url_for('courses'))

# FLUX Classroom Routes
@app.route('/flux-classroom')
@login_required
def flux_classroom():
    # If user is a student, redirect directly to student join page
    if current_user.role == 'student':
        return render_template('flux_student_join.html')
    # If user is faculty/admin, show the choice page
    else:
        return render_template('flux_classroom_choice.html')

@app.route('/flux-teacher')
@login_required
def flux_teacher():
    return render_template('flux_teacher.html')

@app.route('/flux-teacher/create-session', methods=['POST'])
@login_required
def create_flux_session():
    # Generate unique session code
    session_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    title = request.form.get('title', 'FLUX Session')
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Deactivate any existing sessions for this teacher
    cursor.execute('UPDATE flux_sessions SET is_active = 0 WHERE teacher_id = ?', (current_user.id,))
    
    # Create new session
    cursor.execute('''
        INSERT INTO flux_sessions (session_code, teacher_id, title, is_active) 
        VALUES (?, ?, ?, 1)
    ''', (session_code, current_user.id, title))
    
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'session_code': session_code,
        'session_id': session_id,
        'join_link': f'/flux-student/{session_code}'
    })

@app.route('/api/flux/send-prompt', methods=['POST'])
@login_required
def send_prompt():
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Update current prompt for teacher's active session
    cursor.execute('''
        UPDATE flux_sessions 
        SET current_prompt = ?, current_question_json = NULL 
        WHERE teacher_id = ? AND is_active = 1
    ''', (prompt, current_user.id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/flux/send-quiz', methods=['POST'])
@login_required
def send_quiz():
    data = request.get_json()
    
    quiz_data = {
        'question': data.get('question'),
        'options': data.get('options'),
        'correct_answer': data.get('correct_answer'),
        'timer': data.get('timer', 30),
        'quiz_id': data.get('quiz_id', 1)
    }
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Clear previous responses for this quiz
    cursor.execute('DELETE FROM quiz_responses WHERE session_id = (SELECT id FROM flux_sessions WHERE teacher_id = ? AND is_active = 1)', (current_user.id,))
    
    # Update session with new quiz
    cursor.execute('''
        UPDATE flux_sessions 
        SET current_question_json = ?, current_prompt = NULL 
        WHERE teacher_id = ? AND is_active = 1
    ''', (json.dumps(quiz_data), current_user.id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/flux/teacher-poll')
@login_required
def teacher_poll():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get teacher's active session
    cursor.execute('SELECT id FROM flux_sessions WHERE teacher_id = ? AND is_active = 1', (current_user.id,))
    session = cursor.fetchone()
    
    if not session:
        conn.close()
        return jsonify({'active': False})
    
    session_id = session[0]
    
    # Get quiz responses
    cursor.execute('''
        SELECT selected_answer, COUNT(*) as count, is_correct
        FROM quiz_responses 
        WHERE session_id = ? 
        GROUP BY selected_answer, is_correct
    ''', (session_id,))
    responses = cursor.fetchall()
    
    # Get leaderboard
    cursor.execute('''
        SELECT sp.username, sp.score
        FROM session_participants sp
        WHERE sp.session_id = ?
        ORDER BY sp.score DESC
        LIMIT 10
    ''', (session_id,))
    leaderboard = cursor.fetchall()
    
    # Get participant count
    cursor.execute('SELECT COUNT(*) FROM session_participants WHERE session_id = ?', (session_id,))
    participant_count = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'active': True,
        'responses': responses,
        'leaderboard': leaderboard,
        'participant_count': participant_count
    })

# Student Routes
@app.route('/flux-student/<session_code>')
def flux_student(session_code):
    return render_template('flux_student.html', session_code=session_code)

@app.route('/join-quiz', methods=['POST'])
@login_required
def join_quiz():
    if current_user.role != 'student':
        flash('Only students can take quizzes', 'error')
        return redirect(url_for('dashboard'))
    
    quiz_code = request.form.get('quiz_code', '').upper().strip()
    
    if not quiz_code:
        flash('Please enter a quiz code', 'error')
        return redirect(url_for('student_dashboard'))
    
    return redirect(url_for('take_quiz', quiz_code=quiz_code))

@app.route('/take-quiz/<quiz_code>')
@login_required
def take_quiz(quiz_code):
    if current_user.role != 'student':
        flash('Only students can take quizzes', 'error')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get quiz details
    cursor.execute('''
        SELECT id, title, description, time_limit, is_active
        FROM quizzes 
        WHERE quiz_code = ?
    ''', (quiz_code,))
    quiz = cursor.fetchone()
    
    if not quiz:
        conn.close()
        flash('Quiz not found', 'error')
        return redirect(url_for('student_dashboard'))
    
    if not quiz[4]:  # is_active
        conn.close()
        flash('This quiz is not currently active', 'error')
        return redirect(url_for('student_dashboard'))
    
    # Check if student has already completed this quiz
    cursor.execute('''
        SELECT id, is_completed FROM quiz_attempts 
        WHERE quiz_id = ? AND student_id = ?
        ORDER BY started_at DESC LIMIT 1
    ''', (quiz[0], current_user.id))
    attempt = cursor.fetchone()
    
    if attempt and attempt[1]:  # is_completed
        conn.close()
        flash('You have already completed this quiz', 'info')
        return redirect(url_for('quiz_result', attempt_id=attempt[0]))
    
    # Get quiz questions
    cursor.execute('''
        SELECT id, question_text, option_a, option_b, option_c, option_d, points
        FROM quiz_questions 
        WHERE quiz_id = ?
        ORDER BY question_order
    ''', (quiz[0],))
    questions = cursor.fetchall()
    
    if not questions:
        conn.close()
        flash('This quiz has no questions yet', 'error')
        return redirect(url_for('student_dashboard'))
    
    # Create or get existing attempt
    if not attempt:
        cursor.execute('''
            INSERT INTO quiz_attempts (quiz_id, student_id, total_questions)
            VALUES (?, ?, ?)
        ''', (quiz[0], current_user.id, len(questions)))
        attempt_id = cursor.lastrowid
        conn.commit()
    else:
        attempt_id = attempt[0]
    
    conn.close()
    
    return render_template('take_quiz.html', quiz=quiz, questions=questions, attempt_id=attempt_id)

@app.route('/submit-quiz-answer', methods=['POST'])
@login_required
def submit_quiz_answer():
    if current_user.role != 'student':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    data = request.get_json()
    attempt_id = data.get('attempt_id')
    question_id = data.get('question_id')
    selected_answer = data.get('selected_answer')
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Verify attempt belongs to student
    cursor.execute('''
        SELECT qa.quiz_id FROM quiz_attempts qa
        WHERE qa.id = ? AND qa.student_id = ? AND qa.is_completed = 0
    ''', (attempt_id, current_user.id))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'success': False, 'error': 'Invalid attempt'})
    
    # Get correct answer
    cursor.execute('''
        SELECT correct_answer FROM quiz_questions 
        WHERE id = ? AND quiz_id = ?
    ''', (question_id, result[0]))
    correct_answer = cursor.fetchone()
    
    if not correct_answer:
        conn.close()
        return jsonify({'success': False, 'error': 'Question not found'})
    
    is_correct = selected_answer == correct_answer[0]
    
    # Save or update answer
    cursor.execute('''
        INSERT OR REPLACE INTO quiz_answers 
        (attempt_id, question_id, selected_answer, is_correct)
        VALUES (?, ?, ?, ?)
    ''', (attempt_id, question_id, selected_answer, is_correct))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'is_correct': is_correct})

@app.route('/complete-quiz/<int:attempt_id>', methods=['POST'])
@login_required
def complete_quiz(attempt_id):
    if current_user.role != 'student':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Verify attempt belongs to student
    cursor.execute('''
        SELECT id FROM quiz_attempts 
        WHERE id = ? AND student_id = ? AND is_completed = 0
    ''', (attempt_id, current_user.id))
    
    if not cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'error': 'Invalid attempt'})
    
    # Calculate score
    cursor.execute('''
        SELECT COUNT(*) as total, 
               SUM(CASE WHEN qa.is_correct THEN qq.points ELSE 0 END) as score
        FROM quiz_answers qa
        JOIN quiz_questions qq ON qa.question_id = qq.id
        WHERE qa.attempt_id = ?
    ''', (attempt_id,))
    result = cursor.fetchone()
    
    total_questions = result[0]
    score = result[1] or 0
    
    # Update attempt
    cursor.execute('''
        UPDATE quiz_attempts 
        SET score = ?, is_completed = 1, completed_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (score, attempt_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'score': score, 'total': total_questions})

@app.route('/quiz-result/<int:attempt_id>')
@login_required
def quiz_result(attempt_id):
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get attempt details
    cursor.execute('''
        SELECT qa.score, qa.total_questions, qa.completed_at, q.title, q.quiz_code
        FROM quiz_attempts qa
        JOIN quizzes q ON qa.quiz_id = q.id
        WHERE qa.id = ? AND qa.student_id = ?
    ''', (attempt_id, current_user.id))
    attempt = cursor.fetchone()
    
    if not attempt:
        conn.close()
        flash('Quiz result not found', 'error')
        return redirect(url_for('student_dashboard'))
    
    # Get detailed answers
    cursor.execute('''
        SELECT qq.question_text, qq.option_a, qq.option_b, qq.option_c, qq.option_d,
               qq.correct_answer, qa.selected_answer, qa.is_correct, qq.points
        FROM quiz_answers qa
        JOIN quiz_questions qq ON qa.question_id = qq.id
        WHERE qa.attempt_id = ?
        ORDER BY qq.question_order
    ''', (attempt_id,))
    answers = cursor.fetchall()
    
    conn.close()
    
    return render_template('quiz_result.html', attempt=attempt, answers=answers)

@app.route('/flux-join-session', methods=['POST'])
@login_required
def join_flux_session():
    session_code = request.form.get('session_code', '').upper()
    username = request.form.get('username', '')
    
    if not session_code or not username:
        flash('Please provide both session code and username', 'error')
        return redirect(url_for('flux_classroom'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Check if session exists and is active
    cursor.execute('SELECT id FROM flux_sessions WHERE session_code = ? AND is_active = 1', (session_code,))
    session = cursor.fetchone()
    
    if not session:
        conn.close()
        flash('Session not found or inactive. Please check the session code.', 'error')
        return redirect(url_for('flux_classroom'))
    
    session_id = session[0]
    
    # Check if username already exists in this session
    cursor.execute('SELECT id FROM session_participants WHERE session_id = ? AND username = ?', (session_id, username))
    if cursor.fetchone():
        conn.close()
        flash('Username already taken in this session. Please choose a different name.', 'error')
        return redirect(url_for('flux_classroom'))
    
    # Add participant
    cursor.execute('''
        INSERT INTO session_participants (session_id, username, score) 
        VALUES (?, ?, 0)
    ''', (session_id, username))
    
    participant_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Redirect to the student session page
    return redirect(url_for('flux_student', session_code=session_code))

@app.route('/api/flux/join-session', methods=['POST'])
def join_session():
    data = request.get_json()
    session_code = data.get('session_code')
    username = data.get('username')
    
    if not session_code or not username:
        return jsonify({'success': False, 'error': 'Missing session code or username'})
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Check if session exists and is active
    cursor.execute('SELECT id FROM flux_sessions WHERE session_code = ? AND is_active = 1', (session_code,))
    session = cursor.fetchone()
    
    if not session:
        conn.close()
        return jsonify({'success': False, 'error': 'Session not found or inactive'})
    
    session_id = session[0]
    
    # Check if username already exists in this session
    cursor.execute('SELECT id FROM session_participants WHERE session_id = ? AND username = ?', (session_id, username))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'error': 'Username already taken'})
    
    # Add participant
    cursor.execute('''
        INSERT INTO session_participants (session_id, username, score) 
        VALUES (?, ?, 0)
    ''', (session_id, username))
    
    participant_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'participant_id': participant_id,
        'session_id': session_id
    })

@app.route('/api/flux/student-poll/<session_code>')
def student_poll(session_code):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get session data
    cursor.execute('''
        SELECT id, current_question_json, current_prompt, is_active 
        FROM flux_sessions 
        WHERE session_code = ?
    ''', (session_code,))
    session_data = cursor.fetchone()
    
    if not session_data or not session_data[3]:  # not active
        conn.close()
        return jsonify({'active': False})
    
    session_id, question_json, prompt, is_active = session_data
    
    # Get leaderboard
    cursor.execute('''
        SELECT username, score
        FROM session_participants
        WHERE session_id = ?
        ORDER BY score DESC
        LIMIT 10
    ''', (session_id,))
    leaderboard = cursor.fetchall()
    
    conn.close()
    
    response_data = {
        'active': True,
        'leaderboard': leaderboard
    }
    
    if question_json:
        response_data['quiz'] = json.loads(question_json)
    elif prompt:
        response_data['prompt'] = prompt
    
    return jsonify(response_data)

@app.route('/api/flux/submit-answer', methods=['POST'])
def submit_answer():
    data = request.get_json()
    session_code = data.get('session_code')
    username = data.get('username')
    answer = data.get('answer')
    quiz_id = data.get('quiz_id', 1)
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get session and participant
    cursor.execute('''
        SELECT fs.id, fs.current_question_json, sp.id as participant_id
        FROM flux_sessions fs
        JOIN session_participants sp ON fs.id = sp.session_id
        WHERE fs.session_code = ? AND sp.username = ? AND fs.is_active = 1
    ''', (session_code, username))
    
    result = cursor.fetchone()
    if not result:
        conn.close()
        return jsonify({'success': False, 'error': 'Session or participant not found'})
    
    session_id, question_json, participant_id = result
    
    if not question_json:
        conn.close()
        return jsonify({'success': False, 'error': 'No active quiz'})
    
    quiz_data = json.loads(question_json)
    correct_answer = quiz_data.get('correct_answer')
    is_correct = str(answer) == str(correct_answer)
    
    # Check if already answered
    cursor.execute('''
        SELECT id FROM quiz_responses 
        WHERE session_id = ? AND user_id = ? AND question_id = ?
    ''', (session_id, participant_id, quiz_id))
    
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'error': 'Already answered'})
    
    # Store response
    cursor.execute('''
        INSERT INTO quiz_responses (session_id, user_id, question_id, selected_answer, is_correct) 
        VALUES (?, ?, ?, ?, ?)
    ''', (session_id, participant_id, quiz_id, answer, is_correct))
    
    # Update score if correct
    if is_correct:
        cursor.execute('''
            UPDATE session_participants 
            SET score = score + 10 
            WHERE id = ?
        ''', (participant_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'correct': is_correct,
        'correct_answer': correct_answer
    })




# Admin Routes
@app.route('/admin/add-user', methods=['POST'])
@login_required
def admin_add_user():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    email = data.get('email')
    full_name = data.get('full_name')
    phone = data.get('phone', '')
    
    if not all([username, password, role, email, full_name]):
        return jsonify({'success': False, 'error': 'All fields are required'})
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'error': 'Username or email already exists'})
    
    # Create user
    password_hash = generate_password_hash(password)
    cursor.execute('''
        INSERT INTO users (username, password_hash, role, email, full_name, phone) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, password_hash, role, email, full_name, phone))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get all users with statistics
    cursor.execute('''
        SELECT u.id, u.username, u.email, u.full_name, u.role, u.is_active, u.created_at,
               COUNT(DISTINCT e.id) as course_enrollments,
               COUNT(DISTINCT qa.id) as quiz_attempts,
               COUNT(DISTINCT ta.id) as test_attempts
        FROM users u
        LEFT JOIN enrollments e ON u.id = e.user_id
        LEFT JOIN quiz_attempts qa ON u.id = qa.student_id
        LEFT JOIN test_attempts ta ON u.id = ta.student_id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    ''')
    users = cursor.fetchall()
    
    conn.close()
    return render_template('admin_users.html', users=users)

@app.route('/admin/user/<int:user_id>/toggle-status', methods=['POST'])
@login_required
def admin_toggle_user_status(user_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get current status
    cursor.execute('SELECT is_active FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'success': False, 'error': 'User not found'})
    
    # Toggle status
    new_status = not result[0]
    cursor.execute('UPDATE users SET is_active = ? WHERE id = ?', (new_status, user_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'is_active': new_status})

@app.route('/admin/user/<int:user_id>/delete', methods=['DELETE'])
@login_required
def admin_delete_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    if user_id == current_user.id:
        return jsonify({'success': False, 'error': 'Cannot delete your own account'})
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Check if user has data
    cursor.execute('''
        SELECT 
            (SELECT COUNT(*) FROM enrollments WHERE user_id = ?) +
            (SELECT COUNT(*) FROM quiz_attempts WHERE student_id = ?) +
            (SELECT COUNT(*) FROM test_attempts WHERE student_id = ?) as total_data
    ''', (user_id, user_id, user_id))
    
    total_data = cursor.fetchone()[0]
    
    if total_data > 0:
        conn.close()
        return jsonify({'success': False, 'error': f'Cannot delete user with {total_data} associated records'})
    
    # Delete user
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/admin/analytics')
@login_required
def admin_analytics():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Platform statistics
    cursor.execute('''
        SELECT 
            (SELECT COUNT(*) FROM users WHERE role = 'student') as students,
            (SELECT COUNT(*) FROM users WHERE role = 'faculty') as faculty,
            (SELECT COUNT(*) FROM courses) as courses,
            (SELECT COUNT(*) FROM enrollments) as enrollments,
            (SELECT COUNT(*) FROM flux_sessions) as sessions,
            (SELECT COUNT(*) FROM quiz_attempts) as quiz_attempts,
            (SELECT COUNT(*) FROM test_attempts) as test_attempts
    ''')
    stats = cursor.fetchone()
    
    # Monthly registrations
    cursor.execute('''
        SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as registrations
        FROM users 
        WHERE created_at >= date('now', '-12 months')
        GROUP BY strftime('%Y-%m', created_at)
        ORDER BY month
    ''')
    monthly_registrations = cursor.fetchall()
    
    # Course popularity
    cursor.execute('''
        SELECT c.title, COUNT(e.id) as enrollments
        FROM courses c
        LEFT JOIN enrollments e ON c.id = e.course_id
        GROUP BY c.id, c.title
        ORDER BY enrollments DESC
        LIMIT 10
    ''')
    course_popularity = cursor.fetchall()
    
    # Active sessions by day
    cursor.execute('''
        SELECT DATE(created_at) as date, COUNT(*) as sessions
        FROM flux_sessions 
        WHERE created_at >= date('now', '-30 days')
        GROUP BY DATE(created_at)
        ORDER BY date
    ''')
    daily_sessions = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_analytics.html', 
                         stats=stats,
                         monthly_registrations=monthly_registrations,
                         course_popularity=course_popularity,
                         daily_sessions=daily_sessions)

@app.route('/admin/system-settings')
@login_required
def admin_system_settings():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    return render_template('admin_system_settings.html')

@app.route('/admin/backup-database', methods=['POST'])
@login_required
def admin_backup_database():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    try:
        import shutil
        from datetime import datetime
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'edusphere_backup_{timestamp}.db'
        
        # Copy database file
        shutil.copy2(DATABASE_NAME, f'backups/{backup_filename}')
        
        return jsonify({'success': True, 'filename': backup_filename})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/system-info')
@login_required
def admin_system_info():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    import os
    import psutil
    from datetime import datetime
    
    # Get system information
    system_info = {
        'database_size': os.path.getsize(DATABASE_NAME) / (1024 * 1024),  # MB
        'cpu_usage': psutil.cpu_percent(),
        'memory_usage': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('.').percent,
        'uptime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return jsonify(system_info)

@app.route('/admin/add-course', methods=['POST'])
@login_required
def admin_add_course():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    image_url = data.get('image_url', '')
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO courses (title, description, image_url) 
        VALUES (?, ?, ?)
    ''', (title, description, image_url))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/admin/manage-courses')
@login_required
def admin_manage_courses():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get all courses with enrollment count
    cursor.execute('''
        SELECT c.id, c.title, c.description, c.image_url, c.created_at,
               COUNT(e.id) as enrollment_count
        FROM courses c
        LEFT JOIN enrollments e ON c.id = e.course_id
        GROUP BY c.id
        ORDER BY c.created_at DESC
    ''')
    courses = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_manage_courses.html', courses=courses)

@app.route('/admin/delete-course/<int:course_id>', methods=['DELETE'])
@login_required
def admin_delete_course(course_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Check if course has enrollments
    cursor.execute('SELECT COUNT(*) FROM enrollments WHERE course_id = ?', (course_id,))
    enrollment_count = cursor.fetchone()[0]
    
    if enrollment_count > 0:
        conn.close()
        return jsonify({'success': False, 'error': f'Cannot delete course with {enrollment_count} enrollments'})
    
    # Delete course
    cursor.execute('DELETE FROM courses WHERE id = ?', (course_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# Role-based access decorator
def role_required(role):
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                flash('Access denied')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator

# AI Chat Routes
@app.route('/ai-chat')
@login_required
def ai_chat_page():
    """AI Chat page for authenticated users"""
    current_time = datetime.now().strftime('%H:%M')
    return render_template('ai_chat.html', current_time=current_time)

@app.route('/api/ai-chat', methods=['POST'])
@login_required
def ai_chat():
    # Initialize model if not available
    current_model = model
    if not current_model:
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key and api_key != 'your_gemini_api_key_here':
                genai.configure(api_key=api_key)
                current_model = genai.GenerativeModel('gemini-2.0-flash')
        except Exception as e:
            pass
    
    if not current_model:
        return jsonify({
            'success': False, 
            'error': 'AI Assistant is currently unavailable. Please contact administrator.'
        })
    
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'success': False, 'error': 'Message cannot be empty'})
        
        # Get role-based context
        role_context = get_role_context(current_user.role)
        
        # Create role-specific prompt
        system_prompt = f"""
        You are an AI assistant for EduSphere, an educational platform. 
        
        User Role: {current_user.role.title()}
        User Name: {current_user.full_name or current_user.username}
        
        {role_context}
        
        Guidelines:
        - Be helpful, encouraging, and educational
        - Provide specific, actionable advice
        - Keep responses concise but informative
        - Use a friendly, professional tone
        - If asked about topics outside education, politely redirect to educational content
        
        Formatting Instructions:
        - Use **bold** for important points and section headers
        - Use *italics* for emphasis
        - Use bullet points (•) for lists
        - Use numbered lists (1., 2., 3.) for step-by-step instructions
        - Structure your response with clear sections
        - Keep paragraphs short and readable
        
        User Question: {user_message}
        """
        
        # Generate AI response
        response = current_model.generate_content(system_prompt)
        ai_response = response.text
        
        # Store chat history in database
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ai_chat_history (user_id, user_message, ai_response, user_role)
            VALUES (?, ?, ?, ?)
        ''', (current_user.id, user_message, ai_response, current_user.role))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        
    except Exception as e:
        # Log the actual error for debugging (in production, use proper logging)
        print(f"AI Chat Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Sorry, I\'m experiencing technical difficulties. Please try again later.'
        })

def get_role_context(role):
    """Get role-specific context for AI responses"""
    contexts = {
        'student': """
        You are helping a student on an exam preparation platform. Focus on:
        - Study tips and techniques
        - Exam strategies and time management
        - Subject-specific guidance for competitive exams (JEE, NEET, CAT, UPSC, etc.)
        - Motivation and stress management
        - Learning resources and practice recommendations
        - Course selection advice
        - Performance improvement suggestions
        
        Be encouraging and supportive. Help them achieve their academic goals.
        """,
        
        'faculty': """
        You are helping a faculty member on an educational platform. Focus on:
        - Teaching methodologies and best practices
        - Student engagement strategies
        - Curriculum design and lesson planning
        - Assessment and evaluation techniques
        - Technology integration in teaching
        - Classroom management tips
        - Student performance analysis
        - Educational content creation
        
        Provide professional insights to enhance their teaching effectiveness.
        """,
        
        'admin': """
        You are helping an administrator of an educational platform. Focus on:
        - Platform management and optimization
        - User engagement strategies
        - Educational technology trends
        - System administration best practices
        - Data analytics and reporting
        - User experience improvements
        - Educational policy and compliance
        - Platform growth strategies
        
        Provide strategic and operational guidance for platform management.
        """
    }
    
    return contexts.get(role, contexts['student'])

@app.route('/api/chat-history')
@login_required
def get_chat_history():
    """Get user's chat history from database"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_message, ai_response, created_at
        FROM ai_chat_history
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 20
    ''', (current_user.id,))
    
    history = cursor.fetchall()
    conn.close()
    
    # Format history for frontend
    formatted_history = []
    for msg in reversed(history):  # Reverse to show chronological order
        formatted_history.append({
            'user_message': msg[0],
            'ai_response': msg[1],
            'timestamp': msg[2]
        })
    
    return jsonify({
        'success': True,
        'history': formatted_history
    })

@app.route('/api/clear-chat', methods=['POST'])
@login_required
def clear_chat():
    """Clear user's chat history from database"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM ai_chat_history WHERE user_id = ?', (current_user.id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/ai-status')
def ai_status():
    """Check AI service status without exposing sensitive information"""
    # For now, return true since we know the AI is configured
    return jsonify({
        'available': True,
        'service': 'Gemini AI',
        'status': 'online'
    })

# Faculty Management Routes (removed duplicate gradebook route)



# Faculty Dashboard Features Routes

@app.route('/faculty/gradebook')
@login_required
def faculty_gradebook():
    """Faculty gradebook for managing student grades"""
    if current_user.role != 'faculty':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get faculty's students and their grades
    cursor.execute('''
        SELECT DISTINCT u.id, u.full_name, u.username, u.email
        FROM users u
        JOIN quiz_attempts qa ON u.id = qa.student_id
        JOIN quizzes q ON qa.quiz_id = q.id
        WHERE q.faculty_id = ? AND u.role = 'student'
        ORDER BY u.full_name
    ''', (current_user.id,))
    students = cursor.fetchall()
    
    # Get faculty's quizzes for grade entry
    cursor.execute('''
        SELECT id, title, quiz_code FROM quizzes 
        WHERE faculty_id = ? AND is_active = 1
        ORDER BY created_at DESC
    ''', (current_user.id,))
    quizzes = cursor.fetchall()
    
    conn.close()
    return render_template('faculty_gradebook.html', students=students, quizzes=quizzes)

@app.route('/faculty/attendance')
@login_required
def faculty_attendance():
    """Faculty attendance tracker"""
    if current_user.role != 'faculty':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get faculty's live classes
    cursor.execute('''
        SELECT lc.id, lc.title, lc.scheduled_at, lc.is_active,
               COUNT(lcp.id) as total_participants
        FROM live_classes lc
        LEFT JOIN live_class_participants lcp ON lc.id = lcp.class_id
        WHERE lc.faculty_id = ?
        GROUP BY lc.id
        ORDER BY lc.scheduled_at DESC
        LIMIT 20
    ''', (current_user.id,))
    classes = cursor.fetchall()
    
    conn.close()
    return render_template('faculty_attendance.html', classes=classes)

@app.route('/faculty/assignments')
@login_required
def faculty_assignments():
    """Faculty assignment manager"""
    if current_user.role != 'faculty':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Create assignments table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            faculty_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            due_date TIMESTAMP,
            max_marks INTEGER DEFAULT 100,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (faculty_id) REFERENCES users (id)
        )
    ''')
    
    # Get faculty's assignments
    cursor.execute('''
        SELECT id, title, description, due_date, max_marks, is_active, created_at
        FROM assignments 
        WHERE faculty_id = ?
        ORDER BY created_at DESC
    ''', (current_user.id,))
    assignments = cursor.fetchall()
    
    conn.commit()
    conn.close()
    return render_template('faculty_assignments.html', assignments=assignments)

@app.route('/faculty/announcements')
@login_required
def faculty_announcements():
    """Faculty announcement center"""
    if current_user.role != 'faculty':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Create announcements table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            faculty_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            priority TEXT DEFAULT 'medium',
            target_audience TEXT DEFAULT 'all',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (faculty_id) REFERENCES users (id)
        )
    ''')
    
    # Get faculty's announcements
    cursor.execute('''
        SELECT id, title, content, priority, target_audience, is_active, created_at
        FROM announcements 
        WHERE faculty_id = ?
        ORDER BY created_at DESC
    ''', (current_user.id,))
    announcements = cursor.fetchall()
    
    conn.commit()
    conn.close()
    return render_template('faculty_announcements.html', announcements=announcements)

@app.route('/faculty/resources')
@login_required
def faculty_resources():
    """Faculty resource library"""
    if current_user.role != 'faculty':
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Create resources table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            faculty_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            resource_type TEXT NOT NULL,
            file_url TEXT,
            subject TEXT,
            is_public BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (faculty_id) REFERENCES users (id)
        )
    ''')
    
    # Get faculty's resources
    cursor.execute('''
        SELECT id, title, description, resource_type, file_url, subject, is_public, created_at
        FROM resources 
        WHERE faculty_id = ?
        ORDER BY created_at DESC
    ''', (current_user.id,))
    resources = cursor.fetchall()
    
    conn.commit()
    conn.close()
    return render_template('faculty_resources.html', resources=resources)

# API Routes for Faculty Features

@app.route('/api/faculty/create-assignment', methods=['POST'])
@login_required
def create_assignment():
    """Create a new assignment"""
    if current_user.role != 'faculty':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    due_date = data.get('due_date')
    max_marks = int(data.get('max_marks', 100))
    
    if not title:
        return jsonify({'success': False, 'error': 'Title is required'})
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO assignments (faculty_id, title, description, due_date, max_marks)
        VALUES (?, ?, ?, ?, ?)
    ''', (current_user.id, title, description, due_date, max_marks))
    
    assignment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'assignment_id': assignment_id})

@app.route('/api/faculty/create-announcement', methods=['POST'])
@login_required
def create_announcement():
    """Create a new announcement"""
    if current_user.role != 'faculty':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    priority = data.get('priority', 'medium')
    target_audience = data.get('target_audience', 'all')
    
    if not title or not content:
        return jsonify({'success': False, 'error': 'Title and content are required'})
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO announcements (faculty_id, title, content, priority, target_audience)
        VALUES (?, ?, ?, ?, ?)
    ''', (current_user.id, title, content, priority, target_audience))
    
    announcement_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'announcement_id': announcement_id})

@app.route('/api/faculty/create-resource', methods=['POST'])
@login_required
def create_resource():
    """Create a new resource"""
    if current_user.role != 'faculty':
        return jsonify({'success': False, 'error': 'Access denied'})
    
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    resource_type = data.get('resource_type')
    file_url = data.get('file_url', '')
    subject = data.get('subject', '')
    is_public = data.get('is_public', False)
    
    if not title or not resource_type:
        return jsonify({'success': False, 'error': 'Title and resource type are required'})
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO resources (faculty_id, title, description, resource_type, file_url, subject, is_public)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (current_user.id, title, description, resource_type, file_url, subject, is_public))
    
    resource_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'resource_id': resource_id})

if __name__ == '__main__':
    init_db()
    
    # Auto-populate data if database is empty
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    conn.close()
    
    if user_count == 0:
        try:
            from populate_data import populate_sample_data
            populate_sample_data()
            print("✅ Sample data populated successfully!")
        except Exception as e:
            print(f"⚠️ Could not populate sample data: {e}")
        
        try:
            from populate_test_series import populate_test_series
            populate_test_series()
            print("✅ Test series data populated successfully!")
        except Exception as e:
            print(f"⚠️ Could not populate test series: {e}")
    
    # Get port from environment variable for deployment
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
