from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import spacy
import paho.mqtt.client as mqtt
from threading import Thread
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models (unchanged)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    interests = db.Column(db.String(500))
    skills = db.Column(db.String(500))
    scores = db.Column(db.String(100))  # e.g., "Math:80,Science:90"
    parent_email = db.Column(db.String(100))

class MonitorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    focus_status = db.Column(db.String(50))
    footage_url = db.Column(db.String(200))  # Simulated or S3 link
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

# Synthetic Dataset for ML (unchanged)
data = {
    'Math': [80, 90, 60, 70, 85, 55, 95, 65, 75, 88],
    'Science': [85, 95, 65, 75, 90, 60, 90, 70, 80, 92],
    'Interests': ['coding', 'biology', 'art', 'business', 'coding', 'art', 'physics', 'business', 'engineering', 'medicine'],
    'Career': ['Software Engineer', 'Doctor', 'Designer', 'Manager', 'Data Scientist', 'Artist', 'Physicist', 'Entrepreneur', 'Engineer', 'Doctor']
}
df = pd.DataFrame(data)
le_interests = LabelEncoder()
df['Interests'] = le_interests.fit_transform(df['Interests'])
X = df[['Math', 'Science', 'Interests']]
y = df['Career']
model = DecisionTreeClassifier()
model.fit(X, y)

# NLP - Load spaCy model (unchanged)
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    print("spaCy model not found. Please run: python -m spacy download en_core_web_sm")
    nlp = None

# MQTT Configuration (unchanged)
broker = 'localhost'
port = 1883
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe('monitor/#')
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = msg.payload.decode()
        print(f"Received message: {topic} -> {payload}")
        
        if 'focus' in topic:
            topic_parts = topic.split('/')
            if len(topic_parts) >= 3:
                user_id = topic_parts[1]
                with app.app_context():
                    monitor = MonitorData(user_id=user_id, focus_status=payload)
                    db.session.add(monitor)
                    db.session.commit()
                    print(f"Saved focus data for user {user_id}: {payload}")
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

def on_disconnect(client, userdata, rc):
    print("Disconnected from MQTT Broker")

def mqtt_thread():
    try:
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        client.connect(broker, port, 60)
        client.loop_forever()
    except Exception as e:
        print(f"MQTT connection error: {e}")

# Start MQTT thread
mqtt_thread_instance = Thread(target=mqtt_thread, daemon=True)
mqtt_thread_instance.start()

# Initialize database
with app.app_context():
    db.create_all()

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        user = User(
            name=data.get('name', ''),
            email=data.get('email', ''),
            interests=data.get('interests', ''),
            skills=data.get('skills', ''),
            scores=data.get('scores', ''),
            parent_email=data.get('parent_email', '')
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'id': user.id, 'message': 'User registered successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        data = request.json
        goal = data.get('goal')  # Optional user-selected goal
        
        if goal:
            # Use user-selected goal
            prediction = goal
        else:
            # NLP extract interests
            interests_text = data.get('interests', '')
            if nlp and interests_text:
                doc = nlp(interests_text)
                extracted = ' '.join([token.text for token in doc if token.pos_ in ['NOUN', 'VERB']])
            else:
                extracted = interests_text
            
            # Simple interest mapping
            interest_mapping = {
                'coding': 'coding', 'programming': 'coding', 'software': 'coding',
                'biology': 'biology', 'medicine': 'biology', 'health': 'biology',
                'art': 'art', 'design': 'art', 'creative': 'art',
                'business': 'business', 'management': 'business', 'finance': 'business',
                'physics': 'physics', 'science': 'physics', 'engineering': 'physics'
            }
            
            best_match = 'coding'  # default
            for key, value in interest_mapping.items():
                if key in extracted.lower():
                    best_match = value
                    break
            
            try:
                interests_encoded = le_interests.transform([best_match])[0]
            except ValueError:
                interests_encoded = 0
            
            # Parse scores with error handling
            scores = {}
            try:
                if data.get('scores'):
                    for item in data['scores'].split(','):
                        if ':' in item:
                            key, value = item.split(':')
                            scores[key.strip()] = int(value.strip())
            except ValueError:
                return jsonify({'error': 'Invalid scores format'}), 400
            
            math_score = scores.get('Math', 70)
            science_score = scores.get('Science', 70)
            
            # Predict
            input_data = [[math_score, science_score, interests_encoded]]
            prediction = model.predict(input_data)[0]
        
        # Generate roadmap and timetable
        roadmap = generate_roadmap(prediction, scores.get('Math', 70), scores.get('Science', 70))
        return jsonify(roadmap)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def generate_roadmap(career, math_score, science_score):
    """Generate detailed roadmap and timetable based on career"""
    roadmaps = {
        'Software Engineer': {
            'career': career,
            'description': 'Design and develop software applications and systems',
            'skills': ['Python', 'JavaScript', 'SQL', 'Git', 'React', 'Node.js'],
            'courses': ['CS50 Introduction to Computer Science', 'Python for Everybody', 'Full Stack Web Development'],
            'internships': ['Software Development Intern at Tech Company', 'Web Development Intern', 'Data Science Intern'],
            'timeline': '6-12 months for basic skills, 2-3 years for proficiency',
            'salary_range': '$60,000 - $150,000+'
        },
        'Doctor': {
            'career': career,
            'description': 'Diagnose and treat medical conditions, provide patient care',
            'skills': ['Anatomy', 'Physiology', 'Medical Terminology', 'Patient Care', 'Diagnosis'],
            'courses': ['Pre-Medical Studies', 'MCAT Preparation', 'Medical School'],
            'internships': ['Hospital Volunteer', 'Medical Research Intern', 'Shadowing Program'],
            'timeline': '8+ years (4 years medical school + residency)',
            'salary_range': '$200,000 - $400,000+'
        },
        'Data Scientist': {
            'career': career,
            'description': 'Analyze complex data to help organizations make decisions',
            'skills': ['Python', 'R', 'Machine Learning', 'Statistics', 'SQL', 'Data Visualization'],
            'courses': ['Data Science Specialization', 'Machine Learning Course', 'Statistics and Probability'],
            'internships': ['Data Analysis Intern', 'Machine Learning Intern', 'Business Intelligence Intern'],
            'timeline': '6-18 months for entry level, 2-4 years for senior',
            'salary_range': '$70,000 - $180,000+'
        },
        'Designer': {
            'career': career,
            'description': 'Create visual concepts and designs for various media',
            'skills': ['Adobe Creative Suite', 'UI/UX Design', 'Typography', 'Color Theory', 'Figma'],
            'courses': ['Graphic Design Fundamentals', 'UI/UX Design Course', 'Digital Art'],
            'internships': ['Graphic Design Intern', 'UI/UX Intern', 'Creative Agency Intern'],
            'timeline': '3-12 months for basic skills, 1-3 years for portfolio',
            'salary_range': '$40,000 - $120,000+'
        },
        'Manager': {
            'career': career,
            'description': 'Lead teams and manage business operations',
            'skills': ['Leadership', 'Project Management', 'Communication', 'Strategic Planning', 'Team Building'],
            'courses': ['Business Administration', 'Project Management Certification', 'Leadership Development'],
            'internships': ['Management Trainee', 'Business Operations Intern', 'Team Lead Intern'],
            'timeline': '2-5 years for management roles',
            'salary_range': '$50,000 - $200,000+'
        },
        'Artist': {
            'career': career,
            'description': 'Create visual arts and designs',
            'skills': ['Drawing', 'Painting', 'Digital Art', 'Sculpting'],
            'courses': ['Art Fundamentals', 'Digital Illustration', 'Portfolio Building'],
            'internships': ['Gallery Intern', 'Design Studio Assistant', 'Freelance Artist'],
            'timeline': '1-3 years for professional portfolio',
            'salary_range': '$30,000 - $100,000+'
        },
        'Physicist': {
            'career': career,
            'description': 'Study physical phenomena and conduct research',
            'skills': ['Advanced Math', 'Physics Principles', 'Research Methods', 'Lab Skills'],
            'courses': ['Quantum Mechanics', 'Thermodynamics', 'Advanced Physics'],
            'internships': ['Research Lab Intern', 'NASA or Lab Placement', 'Academic Research'],
            'timeline': '4-8 years (degree + grad school)',
            'salary_range': '$80,000 - $150,000+'
        },
        'Entrepreneur': {
            'career': career,
            'description': 'Start and run businesses',
            'skills': ['Business Planning', 'Marketing', 'Finance Management', 'Networking'],
            'courses': ['Entrepreneurship 101', 'Business Strategy', 'Startup Fundamentals'],
            'internships': ['Startup Intern', 'Venture Capital Assistant', 'Business Development'],
            'timeline': 'Varies, 1-5 years to launch',
            'salary_range': 'Varies greatly'
        },
        'Engineer': {
            'career': career,
            'description': 'Design and build systems and structures',
            'skills': ['Engineering Principles', 'CAD Software', 'Problem Solving', 'Project Management'],
            'courses': ['Engineering Fundamentals', 'Specialization Courses (e.g., Mechanical)', 'CAD Training'],
            'internships': ['Engineering Intern', 'R&D Placement', 'Construction Site'],
            'timeline': '4 years degree + 2-4 years experience',
            'salary_range': '$70,000 - $140,000+'
        }
    }
    
    roadmap = roadmaps.get(career, {
        'career': career,
        'description': 'Professional career path',
        'skills': ['Core Skills', 'Industry Knowledge', 'Soft Skills'],
        'courses': ['Relevant Coursework', 'Professional Development'],
        'internships': ['Industry Internships', 'Professional Experience'],
        'timeline': 'Varies by field',
        'salary_range': 'Varies by location and experience'
    })
    
    # Add personalized timetable (simple hardcoded, adjusted by scores)
    weak_subject_time = 3 if math_score < 70 or science_score < 70 else 2  # Extra hour if weak
    roadmap['timetable'] = {
        'Monday': f'9AM-12PM: Study Core Subjects ({weak_subject_time}h Math/Science if needed)\n1PM-3PM: Skill Practice\n4PM-6PM: Courses',
        'Tuesday': '9AM-12PM: Internship Prep\n1PM-4PM: Project Work\n5PM-7PM: Review Interests',
        'Wednesday': f'9AM-1PM: Focused Study ({weak_subject_time}h on weak areas)\n2PM-5PM: Online Courses\n6PM-8PM: Rest/Reflection',
        'Thursday': '9AM-12PM: Skill Building\n1PM-3PM: Networking\n4PM-6PM: Goal Review',
        'Friday': '9AM-11AM: Weekly Assessment\n12PM-3PM: Free Time for Passions\n4PM-6PM: Update Progress',
        'Saturday': '10AM-2PM: Hands-on Projects\n3PM-5PM: Mentorship/Reading',
        'Sunday': 'Rest Day - Light Review'
    }
    
    return roadmap

@app.route('/api/parent/<int:user_id>', methods=['GET'])
def parent_view(user_id):
    try:
        monitors = MonitorData.query.filter_by(user_id=user_id).order_by(MonitorData.timestamp.desc()).limit(50).all()
        data = [{
            'id': m.id,
            'focus': m.focus_status, 
            'footage': m.footage_url or 'N/A',
            'timestamp': m.timestamp.isoformat() if m.timestamp else None
        } for m in monitors]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'interests': user.interests,
            'skills': user.skills,
            'scores': user.scores
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'mqtt_connected': client.is_connected()})

if __name__ == '__main__':
    print("Starting AI-Enhanced Career Guidance System...")
    print("Backend running on http://localhost:5000")
    print("Make sure MQTT broker is running on localhost:1883")
    app.run(debug=True, host='0.0.0.0', port=5000)