from flask import Flask, send_from_directory, redirect, url_for, request, jsonify
import os
from database import create_tables, SessionLocal, ContactSubmission, NewsletterSubscription

app = Flask(__name__)

# Initialize database tables
create_tables()

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
        db = SessionLocal()
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
        
        db.add(submission)
        db.commit()
        db.close()
        
        return jsonify({'success': True, 'message': 'Thank you for your submission!'})
        
    except Exception as e:
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
        
        db = SessionLocal()
        
        # Check if email already exists
        existing = db.query(NewsletterSubscription).filter_by(email=email).first()
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
            db.add(subscription)
        
        db.commit()
        db.close()
        
        return jsonify({'success': True, 'message': 'Successfully subscribed to newsletter!'})
        
    except Exception as e:
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
