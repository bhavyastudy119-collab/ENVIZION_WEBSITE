from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from flask_cors import CORS
import json
import os
from datetime import datetime
import stripe
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'envizion-secret-key-2024')
CORS(app)

# Stripe configuration
stripe_keys = {
    'secret_key': os.environ.get('STRIPE_SECRET_KEY', 'sk_test_your_secret_key'),
    'publishable_key': os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_your_publishable_key')
}
stripe.api_key = stripe_keys['secret_key']

# Sample NGO data
SAMPLE_NGOS = [
    {
        'id': 1, 'name': 'Delhi Education Foundation', 'category': 'education',
        'services': 'Free Education, Mid-day Meals, School Supplies',
        'contact': '011-28765432, 9876543210', 'address': 'Karol Bagh, Delhi - 110005',
        'description': 'Provides free education with meals to underprivileged children'
    },
    {
        'id': 2, 'name': 'Food For All NGO', 'category': 'food',
        'services': 'Daily Meal Distribution, Nutrition Programs',
        'contact': '011-29876543, 9876543222', 'address': 'Lajpat Nagar, Delhi - 110024',
        'description': 'Distributes free meals to slum dwellers daily'
    },
    {
        'id': 3, 'name': 'Employment Generation Trust', 'category': 'employment',
        'services': 'Skill Training, Job Placement, Resume Building',
        'contact': '011-31234567, 9876543233', 'address': 'Paharganj, Delhi - 110055',
        'description': 'Vocational training and job placement services'
    },
    {
        'id': 4, 'name': 'Health Care Delhi', 'category': 'health',
        'services': 'Medical Camps, Medicines, Hygiene Kits',
        'contact': '011-29887766, 9876543244', 'address': 'Malviya Nagar, Delhi - 110017',
        'description': 'Organizes free health checkups and distributes medicines'
    }
]

# Team Members Data (for homepage)
TEAM_MEMBERS = [
    {'id': 1, 'name': 'Bhavya Jha', 'role': 'Team Leader & Concept Developer', 'image': '/static/assets/team/bhavya.png'},
    {'id': 2, 'name': 'Vritika', 'role': 'Web Designer & Prototype Developer', 'image': '/static/assets/team/vritika.png'},
    {'id': 3, 'name': 'Aayushi', 'role': 'Chatbot Developer & User Interaction', 'image': '/static/assets/team/aayushi.png'},
    {'id': 4, 'name': 'Ebbani', 'role': 'Documentation & Logbook Maintenance',  'image': '/static/assets/team/ebbani.png'},
    {'id': 5, 'name': 'Shruti', 'role': 'Data Research & Validation Support',  'image': '/static/assets/team/shruti.png'},
    {'id': 6, 'name': 'Avi', 'role': 'Survey & Field Data Collection', 'image': '/static/assets/team/avi.png'}
]

# Gallery Images
GALLERY_IMAGES = [
    {'id': 1, 'title': 'Community Education', 'desc': 'Children learning in slum schools'},
    {'id': 2, 'title': 'Food Distribution', 'desc': 'NGO distributing meals'},
    {'id': 3, 'title': 'Medical Camp', 'desc': 'Healthcare services in slums'},
    {'id': 4, 'title': 'Job Training', 'desc': 'Vocational skills workshop'},
    {'id': 5, 'title': 'Sanitation Project', 'desc': 'Clean water initiative'},
    {'id': 6, 'title': 'Community Meeting', 'desc': 'Planning development projects'}
]

# ========== ROUTES ==========

@app.route('/')
def home():
    """Homepage with team section included"""
    return render_template('index.html', 
                          title='ENVIZION - AI for Social Equity',
                          team_members=TEAM_MEMBERS,
                          ngos=SAMPLE_NGOS)

@app.route('/chatbot')
def chatbot():
    """Chatbot interface page"""
    return render_template('chatbot.html', title='AI Assistant - ENVIZION')

@app.route('/gallery')
def gallery():
    """Gallery page"""
    return render_template('gallery.html', 
                          title='Gallery - ENVIZION',
                          gallery_images=GALLERY_IMAGES)

@app.route('/donation')
def donation():
    """Donation page"""
    return render_template('donation.html', 
                          title='Donate - ENVIZION',
                          stripe_key=stripe_keys['publishable_key'])

@app.route('/presentation')
def presentation():
    """Presentation page (links to Canva)"""
    return render_template('presentation.html', title='Presentation - ENVIZION')

@app.route('/app-redirect')
def app_redirect():
    """Redirect to ENVIZION web app"""
    return redirect('https://envizion-479663f5.base44.app/')

# Static file serving
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'assets', 'logo'),
                              'logo.jpg', mimetype='image/vnd.microsoft.icon')

# ========== API ENDPOINTS ==========

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Chatbot API endpoint"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            })
        
        # Simple intent recognition
        intent = get_intent_from_message(user_message)
        
        # Get relevant NGOs
        if intent == 'general':
            ngos = SAMPLE_NGOS[:3]
        else:
            ngos = [ngo for ngo in SAMPLE_NGOS if ngo['category'] == intent][:3]
        
        # Generate response
        responses = {
            'education': "I found educational NGOs that can help with schooling and mid-day meals.",
            'food': "Here are food aid organizations that provide meals.",
            'employment': "These organizations offer job training and placement services.",
            'health': "I found healthcare NGOs that provide medical services.",
            'housing': "These organizations can help with shelter and housing.",
            'sanitation': "Here are NGOs working on clean water and sanitation.",
            'general': "I can help you connect with NGOs for various services."
        }
        
        response_text = responses.get(intent, responses['general'])
        
        return jsonify({
            'success': True,
            'intent': intent,
            'response': response_text,
            'ngos': ngos,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'response': "Sorry, I encountered an error. Please try again."
        })

@app.route('/api/donate', methods=['POST'])
def create_donation():
    """Create donation payment intent"""
    try:
        data = request.json
        amount = data.get('amount', 2000)  # Amount in cents
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='inr',
            description='ENVIZION Donation',
            metadata={'project': 'ENVIZION Social Platform'}
        )
        
        return jsonify({
            'success': True,
            'clientSecret': intent.client_secret
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/contact', methods=['POST'])
def contact_submit():
    """Handle contact form submissions"""
    try:
        data = request.json
        # Here you would save to database or send email
        print(f"Contact form submission: {data}")
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your message! We will get back to you soon.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/stats', methods=['GET'])
def stats_api():
    """Get statistics for visualization"""
    stats = {
        'education': {
            'labels': ['Currently Attending', 'Never Attended', 'Dropped Out'],
            'data': [54.5, 21.3, 24.2],
            'colors': ['#4CAF50', '#FF9800', '#F44336']
        },
        'sanitation': {
            'labels': ['Private Toilet', 'Community Toilet', 'No Toilet'],
            'data': [18.02, 60.79, 21.61],
            'colors': ['#2196F3', '#9C27B0', '#FF5722']
        },
        'impact': {
            'families': 12500,
            'ngos': 243,
            'volunteers': 567,
            'success_rate': 98
        }
    }
    
    return jsonify({'success': True, 'stats': stats})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ENVIZION Web Interface',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

# ========== HELPER FUNCTIONS ==========

def get_intent_from_message(message):
    """Simple keyword-based intent detection"""
    message_lower = message.lower()
    
    intent_keywords = {
        'education': ['school', 'education', 'study', 'learn', 'student', 'teacher', 'book', 'class'],
        'food': ['food', 'hunger', 'meal', 'eat', 'hungry', 'starving', 'rice', 'bread'],
        'employment': ['job', 'work', 'employment', 'salary', 'wage', 'income', 'earn'],
        'health': ['health', 'doctor', 'medicine', 'sick', 'hospital', 'clinic', 'fever'],
        'housing': ['house', 'home', 'shelter', 'live', 'room', 'stay', 'rent'],
        'sanitation': ['toilet', 'bathroom', 'water', 'clean', 'sanitation', 'hygiene']
    }
    
    for intent, keywords in intent_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            return intent
    
    return 'general'

# ========== MAIN ==========

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/assets', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("=" * 60)
    print("ENVIZION Professional Website")
    print("=" * 60)
    print("Server running on: http://localhost:5000")
    print("\nAvailable Pages:")
    print("  • Home: http://localhost:5000")
    print("  • AI Assistant: http://localhost:5000/chatbot")
    print("  • Gallery: http://localhost:5000/gallery")
    print("  • Donation: http://localhost:5000/donation")
    print("  • Presentation: http://localhost:5000/presentation")
    print("  • ENVIZION App: https://envizion-479663f5.base44.app/")
    print("\nNavigation:")
    print("  - Team section is now on homepage (scrolling required)")
    print("  - Removed separate team and help pages")
    print("  - Resources dropdown links to Canva presentations")
    print("=" * 60)
    
    # Get port from environment variable (for Render)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
