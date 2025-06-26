import os
import logging
from datetime import datetime
from flask import Flask, send_from_directory, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define models after db initialization
class ContactSubmission(db.Model):
    """Model for storing contact form submissions"""
    __tablename__ = "contact_submissions"
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    form_type = db.Column(db.String(50), nullable=False)  # general, consultation, project
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    company = db.Column(db.String(255), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    company_size = db.Column(db.String(50), nullable=True)
    service = db.Column(db.String(100), nullable=True)
    budget = db.Column(db.String(50), nullable=True)
    timeline = db.Column(db.String(50), nullable=True)
    message = db.Column(db.Text, nullable=True)
    challenges = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    is_processed = db.Column(db.Boolean, default=False)

class NewsletterSubscription(db.Model):
    """Model for storing newsletter subscriptions"""
    __tablename__ = "newsletter_subscriptions"
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    industry = db.Column(db.String(100), nullable=True)
    subscribed_at = db.Column(db.DateTime, default=db.func.now())
    is_active = db.Column(db.Boolean, default=True)

with app.app_context():
    # Create all tables
    db.create_all()

# Serve static files (HTML, CSS, JS, images, etc.)
@app.route('/')
def index():
    """Serve the main index page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve all static files"""
    try:
        return send_from_directory('.', filename)
    except FileNotFoundError:
        # If file not found, redirect to index
        return redirect(url_for('index'))

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests"""
    return '', 204  # Return empty response with "No Content" status

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors by redirecting to index"""
    return redirect(url_for('index'))

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    """Handle contact form submissions"""
    try:
        data = request.get_json()
        
        # Create new contact submission
        submission = ContactSubmission(
            form_type=data.get('form_type', 'general'),
            first_name=data.get('firstName', ''),
            last_name=data.get('lastName', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            company=data.get('company', ''),
            industry=data.get('industry', ''),
            company_size=data.get('company-size', ''),
            service=data.get('service', ''),
            budget=data.get('budget', ''),
            timeline=data.get('timeline', ''),
            message=data.get('message', ''),
            challenges=data.get('challenges', ''),
            requirements=data.get('requirements', '')
        )
        
        db.session.add(submission)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Thank you for your submission!'})
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error submitting contact form: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred. Please try again.'}), 500

@app.route('/api/newsletter', methods=['POST'])
def subscribe_newsletter():
    """Handle newsletter subscriptions"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        industry = data.get('industry', '')
        
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400
        
        # Check if email already exists
        existing = NewsletterSubscription.query.filter_by(email=email).first()
        if existing:
            if existing.is_active:
                return jsonify({'success': False, 'message': 'This email is already subscribed'}), 400
            else:
                # Reactivate subscription
                existing.is_active = True
                existing.industry = industry
        else:
            # Create new subscription
            subscription = NewsletterSubscription(email=email, industry=industry)
            db.session.add(subscription)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Successfully subscribed to newsletter!'})
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error subscribing to newsletter: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred. Please try again.'}), 500

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False  # Set to False for production
    )
