import sqlite3
import json

def populate_sample_data():
    conn = sqlite3.connect('edusphere.db')
    cursor = conn.cursor()
    
    # Sample users with different roles
    from werkzeug.security import generate_password_hash
    
    sample_users = [
        ('admin', 'admin123', 'admin', 'admin@edusphere.com', 'System Administrator'),
        ('teacher1', 'teacher123', 'faculty', 'teacher1@edusphere.com', 'Dr. John Smith'),
        ('teacher2', 'teacher123', 'faculty', 'teacher2@edusphere.com', 'Prof. Sarah Johnson'),
        ('student1', 'student123', 'student', 'student1@edusphere.com', 'Alice Brown'),
        ('student2', 'student123', 'student', 'student2@edusphere.com', 'Bob Wilson'),
        ('student3', 'student123', 'student', 'student3@edusphere.com', 'Carol Davis'),
    ]
    
    for username, password, role, email, full_name in sample_users:
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password_hash, role, email, full_name) 
            VALUES (?, ?, ?, ?, ?)
        ''', (username, password_hash, role, email, full_name))
    
    # Sample courses data
    courses = [
        # JEE Courses
        {
            'title': 'JEE Main Mathematics',
            'description': 'Complete mathematics preparation for JEE Main with advanced problem solving techniques',
            'image_url': 'https://via.placeholder.com/300x200/007bff/ffffff?text=JEE+Math'
        },
        {
            'title': 'JEE Advanced Physics',
            'description': 'Advanced physics concepts for JEE Advanced with detailed theory and numerical problems',
            'image_url': 'https://via.placeholder.com/300x200/6f42c1/ffffff?text=JEE+Physics'
        },
        {
            'title': 'JEE Chemistry Complete',
            'description': 'Organic, inorganic, and physical chemistry for JEE Main and Advanced preparation',
            'image_url': 'https://via.placeholder.com/300x200/fd7e14/ffffff?text=JEE+Chem'
        },
        
        # NEET Courses
        {
            'title': 'NEET Biology Masterclass',
            'description': 'Comprehensive biology course covering all NEET syllabus with detailed explanations',
            'image_url': 'https://via.placeholder.com/300x200/28a745/ffffff?text=NEET+Bio'
        },
        {
            'title': 'NEET Physics Foundation',
            'description': 'Physics fundamentals for NEET with focus on medical entrance exam patterns',
            'image_url': 'https://via.placeholder.com/300x200/20c997/ffffff?text=NEET+Phy'
        },
        {
            'title': 'NEET Chemistry Essentials',
            'description': 'Essential chemistry topics for NEET with practice questions and mock tests',
            'image_url': 'https://via.placeholder.com/300x200/e83e8c/ffffff?text=NEET+Chem'
        },
        
        # CAT & MBA Courses
        {
            'title': 'CAT Quantitative Aptitude',
            'description': 'Master quantitative aptitude for CAT with shortcuts and time-saving techniques',
            'image_url': 'https://via.placeholder.com/300x200/ffc107/000000?text=CAT+Quant'
        },
        {
            'title': 'CAT Verbal Ability & Reading',
            'description': 'Comprehensive verbal ability and reading comprehension for CAT preparation',
            'image_url': 'https://via.placeholder.com/300x200/6610f2/ffffff?text=CAT+Verbal'
        },
        {
            'title': 'CAT Data Interpretation & Logic',
            'description': 'Data interpretation and logical reasoning with advanced problem-solving strategies',
            'image_url': 'https://via.placeholder.com/300x200/d63384/ffffff?text=CAT+DI'
        },
        {
            'title': 'XAT & SNAP Preparation',
            'description': 'Complete preparation for XAT, SNAP, and other MBA entrance examinations',
            'image_url': 'https://via.placeholder.com/300x200/198754/ffffff?text=XAT+SNAP'
        },
        
        # UPSC & Civil Services
        {
            'title': 'UPSC General Studies',
            'description': 'Complete general studies preparation for UPSC prelims and mains examination',
            'image_url': 'https://via.placeholder.com/300x200/dc3545/ffffff?text=UPSC+GS'
        },
        {
            'title': 'UPSC History & Culture',
            'description': 'Indian history, art, and culture for UPSC civil services examination',
            'image_url': 'https://via.placeholder.com/300x200/795548/ffffff?text=UPSC+Hist'
        },
        {
            'title': 'UPSC Geography & Environment',
            'description': 'Physical and human geography with environmental studies for UPSC preparation',
            'image_url': 'https://via.placeholder.com/300x200/607d8b/ffffff?text=UPSC+Geo'
        },
        {
            'title': 'UPSC Polity & Governance',
            'description': 'Indian polity, constitution, and governance for UPSC civil services',
            'image_url': 'https://via.placeholder.com/300x200/ff5722/ffffff?text=UPSC+Pol'
        },
        {
            'title': 'UPSC Economics & Current Affairs',
            'description': 'Indian economy and current affairs analysis for UPSC preparation',
            'image_url': 'https://via.placeholder.com/300x200/9c27b0/ffffff?text=UPSC+Eco'
        },
        
        # SSC & Government Jobs
        {
            'title': 'SSC English & Reasoning',
            'description': 'English language and logical reasoning for SSC CGL, CHSL, and other examinations',
            'image_url': 'https://via.placeholder.com/300x200/17a2b8/ffffff?text=SSC+Eng'
        },
        {
            'title': 'SSC Mathematics & Statistics',
            'description': 'Quantitative aptitude and basic statistics for SSC examinations',
            'image_url': 'https://via.placeholder.com/300x200/343a40/ffffff?text=SSC+Math'
        },
        {
            'title': 'SSC General Knowledge',
            'description': 'General awareness and current affairs for SSC and other government exams',
            'image_url': 'https://via.placeholder.com/300x200/6c757d/ffffff?text=SSC+GK'
        },
        {
            'title': 'Railway & Banking Exams',
            'description': 'Comprehensive preparation for railway recruitment and banking sector examinations',
            'image_url': 'https://via.placeholder.com/300x200/495057/ffffff?text=Rail+Bank'
        },
        
        # State Board & CBSE
        {
            'title': 'Class 12 Mathematics',
            'description': 'Complete Class 12 mathematics for CBSE and state boards with board exam focus',
            'image_url': 'https://via.placeholder.com/300x200/0d6efd/ffffff?text=12th+Math'
        },
        {
            'title': 'Class 12 Physics',
            'description': 'Physics for Class 12 students with practical applications and board exam preparation',
            'image_url': 'https://via.placeholder.com/300x200/6f42c1/ffffff?text=12th+Phy'
        },
        {
            'title': 'Class 12 Chemistry',
            'description': 'Comprehensive chemistry course for Class 12 with lab experiments and theory',
            'image_url': 'https://via.placeholder.com/300x200/fd7e14/ffffff?text=12th+Chem'
        },
        {
            'title': 'Class 12 Biology',
            'description': 'Biology for Class 12 with detailed diagrams and medical entrance preparation',
            'image_url': 'https://via.placeholder.com/300x200/198754/ffffff?text=12th+Bio'
        },
        
        # Professional & Competitive Exams
        {
            'title': 'GATE Computer Science',
            'description': 'Complete GATE preparation for computer science and information technology',
            'image_url': 'https://via.placeholder.com/300x200/0dcaf0/000000?text=GATE+CS'
        },
        {
            'title': 'GATE Mechanical Engineering',
            'description': 'Mechanical engineering concepts and problem solving for GATE examination',
            'image_url': 'https://via.placeholder.com/300x200/6c757d/ffffff?text=GATE+Mech'
        },
        {
            'title': 'CLAT Legal Reasoning',
            'description': 'Legal reasoning and general knowledge for CLAT and other law entrance exams',
            'image_url': 'https://via.placeholder.com/300x200/212529/ffffff?text=CLAT+Law'
        },
        {
            'title': 'NDA & CDS Preparation',
            'description': 'National Defence Academy and Combined Defence Services examination preparation',
            'image_url': 'https://via.placeholder.com/300x200/198754/ffffff?text=NDA+CDS'
        },
        
        # Language & Communication
        {
            'title': 'English Communication Skills',
            'description': 'Improve English speaking, writing, and comprehension skills for all competitive exams',
            'image_url': 'https://via.placeholder.com/300x200/0f5132/ffffff?text=English'
        },
        {
            'title': 'Hindi Literature & Grammar',
            'description': 'Hindi language and literature for various competitive examinations',
            'image_url': 'https://via.placeholder.com/300x200/842029/ffffff?text=Hindi'
        },
        
        # Skill Development
        {
            'title': 'Computer Fundamentals',
            'description': 'Basic computer knowledge for government jobs and competitive examinations',
            'image_url': 'https://via.placeholder.com/300x200/495057/ffffff?text=Computer'
        },
        {
            'title': 'Data Analysis & Statistics',
            'description': 'Statistical analysis and data interpretation for research and competitive exams',
            'image_url': 'https://via.placeholder.com/300x200/6610f2/ffffff?text=Statistics'
        },
        {
            'title': 'Aptitude & Mental Ability',
            'description': 'Logical reasoning, analytical ability, and mental aptitude for all competitive exams',
            'image_url': 'https://via.placeholder.com/300x200/d63384/ffffff?text=Aptitude'
        }
    ]
    
    # Insert courses
    for course in courses:
        cursor.execute('''
            INSERT OR IGNORE INTO courses (title, description, image_url) 
            VALUES (?, ?, ?)
        ''', (course['title'], course['description'], course['image_url']))
    
    # Sample questions for test series
    questions = [
        {
            'question_text': 'What is the derivative of x² + 3x + 2?',
            'option_a': '2x + 3',
            'option_b': 'x² + 3',
            'option_c': '2x + 2',
            'option_d': 'x + 3',
            'correct_answer': 'A',
            'explanation': 'The derivative of x² is 2x, derivative of 3x is 3, and derivative of constant 2 is 0. So the answer is 2x + 3.'
        },
        {
            'question_text': 'Which organelle is known as the powerhouse of the cell?',
            'option_a': 'Nucleus',
            'option_b': 'Mitochondria',
            'option_c': 'Ribosome',
            'option_d': 'Endoplasmic Reticulum',
            'correct_answer': 'B',
            'explanation': 'Mitochondria are called the powerhouse of the cell because they produce ATP, which is the energy currency of the cell.'
        },
        {
            'question_text': 'If a train travels 120 km in 2 hours, what is its average speed?',
            'option_a': '50 km/h',
            'option_b': '60 km/h',
            'option_c': '70 km/h',
            'option_d': '80 km/h',
            'correct_answer': 'B',
            'explanation': 'Average speed = Total distance / Total time = 120 km / 2 hours = 60 km/h'
        },
        {
            'question_text': 'Who was the first President of India?',
            'option_a': 'Jawaharlal Nehru',
            'option_b': 'Mahatma Gandhi',
            'option_c': 'Dr. Rajendra Prasad',
            'option_d': 'Sardar Vallabhbhai Patel',
            'correct_answer': 'C',
            'explanation': 'Dr. Rajendra Prasad was the first President of India, serving from 1950 to 1962.'
        },
        {
            'question_text': 'Choose the correct synonym for "Abundant":',
            'option_a': 'Scarce',
            'option_b': 'Plentiful',
            'option_c': 'Limited',
            'option_d': 'Rare',
            'correct_answer': 'B',
            'explanation': 'Abundant means existing in large quantities, so plentiful is the correct synonym.'
        }
    ]
    
    # Insert questions
    for question in questions:
        cursor.execute('''
            INSERT OR IGNORE INTO questions 
            (question_text, option_a, option_b, option_c, option_d, correct_answer, explanation) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            question['question_text'],
            question['option_a'],
            question['option_b'],
            question['option_c'],
            question['option_d'],
            question['correct_answer'],
            question['explanation']
        ))
    
    # Create a sample FLUX session
    cursor.execute('''
        INSERT OR IGNORE INTO flux_sessions (id, teacher_id, current_question_json, is_active) 
        VALUES (1, 1, ?, 0)
    ''', (json.dumps({
        'question': 'What is 2 + 2?',
        'options': ['3', '4', '5', '6'],
        'correct': 1,
        'time_limit': 30
    }),))
    
    conn.commit()
    conn.close()
    print("Sample data populated successfully!")

if __name__ == '__main__':
    populate_sample_data()
