from app import db


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