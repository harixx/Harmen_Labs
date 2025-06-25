"""
Admin dashboard for viewing database entries
"""
from flask import Flask, render_template_string, request
from database import SessionLocal, ContactSubmission, NewsletterSubscription, create_tables
from datetime import datetime

app = Flask(__name__)

# Ensure tables exist
create_tables()

# Admin dashboard HTML template
ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agentic Solutions - Admin Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); }
        .glass { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); }
    </style>
</head>
<body class="min-h-screen text-white">
    <div class="container mx-auto px-6 py-8">
        <h1 class="text-4xl font-bold mb-8 text-center">Admin Dashboard</h1>
        
        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="glass rounded-xl p-6">
                <h3 class="text-lg font-semibold text-cyan-300 mb-2">Total Contacts</h3>
                <p class="text-3xl font-bold">{{ contact_count }}</p>
            </div>
            <div class="glass rounded-xl p-6">
                <h3 class="text-lg font-semibold text-green-300 mb-2">Newsletter Subscribers</h3>
                <p class="text-3xl font-bold">{{ newsletter_count }}</p>
            </div>
            <div class="glass rounded-xl p-6">
                <h3 class="text-lg font-semibold text-purple-300 mb-2">Unprocessed Contacts</h3>
                <p class="text-3xl font-bold">{{ unprocessed_count }}</p>
            </div>
        </div>

        <!-- Contact Submissions -->
        <div class="glass rounded-xl p-6 mb-8">
            <h2 class="text-2xl font-bold mb-6">Recent Contact Submissions</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="border-b border-slate-700">
                            <th class="text-left p-3">Date</th>
                            <th class="text-left p-3">Type</th>
                            <th class="text-left p-3">Name</th>
                            <th class="text-left p-3">Email</th>
                            <th class="text-left p-3">Company</th>
                            <th class="text-left p-3">Industry</th>
                            <th class="text-left p-3">Status</th>
                            <th class="text-left p-3">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for contact in contacts %}
                        <tr class="border-b border-slate-800 hover:bg-slate-800/30">
                            <td class="p-3">{{ contact.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                            <td class="p-3">
                                <span class="px-2 py-1 text-xs rounded 
                                    {% if contact.form_type == 'general' %}bg-blue-600
                                    {% elif contact.form_type == 'consultation' %}bg-green-600
                                    {% elif contact.form_type == 'project' %}bg-purple-600
                                    {% else %}bg-gray-600{% endif %}">
                                    {{ contact.form_type.title() }}
                                </span>
                            </td>
                            <td class="p-3">{{ contact.first_name }} {{ contact.last_name }}</td>
                            <td class="p-3">{{ contact.email }}</td>
                            <td class="p-3">{{ contact.company or '-' }}</td>
                            <td class="p-3">{{ contact.industry or '-' }}</td>
                            <td class="p-3">
                                {% if contact.is_processed %}
                                    <span class="text-green-400">Processed</span>
                                {% else %}
                                    <span class="text-yellow-400">Pending</span>
                                {% endif %}
                            </td>
                            <td class="p-3">
                                <a href="/admin/contact/{{ contact.id }}" class="text-cyan-400 hover:text-cyan-300">View</a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Newsletter Subscribers -->
        <div class="glass rounded-xl p-6">
            <h2 class="text-2xl font-bold mb-6">Newsletter Subscribers</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-sm">
                    <thead>
                        <tr class="border-b border-slate-700">
                            <th class="text-left p-3">Date</th>
                            <th class="text-left p-3">Email</th>
                            <th class="text-left p-3">Industry</th>
                            <th class="text-left p-3">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for subscriber in subscribers %}
                        <tr class="border-b border-slate-800 hover:bg-slate-800/30">
                            <td class="p-3">{{ subscriber.subscribed_at.strftime('%Y-%m-%d %H:%M') }}</td>
                            <td class="p-3">{{ subscriber.email }}</td>
                            <td class="p-3">{{ subscriber.industry or '-' }}</td>
                            <td class="p-3">
                                {% if subscriber.is_active %}
                                    <span class="text-green-400">Active</span>
                                {% else %}
                                    <span class="text-red-400">Inactive</span>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""

CONTACT_DETAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact Details - Admin Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); }
        .glass { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); }
    </style>
</head>
<body class="min-h-screen text-white">
    <div class="container mx-auto px-6 py-8 max-w-4xl">
        <div class="mb-6">
            <a href="/admin" class="text-cyan-400 hover:text-cyan-300">&larr; Back to Dashboard</a>
        </div>
        
        <div class="glass rounded-xl p-8">
            <div class="flex justify-between items-start mb-6">
                <h1 class="text-3xl font-bold">Contact Details</h1>
                <form method="POST" class="inline">
                    <button type="submit" name="toggle_processed" 
                        class="px-4 py-2 rounded 
                        {% if contact.is_processed %}bg-yellow-600 hover:bg-yellow-700
                        {% else %}bg-green-600 hover:bg-green-700{% endif %}">
                        {% if contact.is_processed %}Mark as Pending{% else %}Mark as Processed{% endif %}
                    </button>
                </form>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h3 class="text-lg font-semibold text-cyan-300 mb-4">Contact Information</h3>
                    <div class="space-y-3">
                        <div><strong>Name:</strong> {{ contact.first_name }} {{ contact.last_name }}</div>
                        <div><strong>Email:</strong> {{ contact.email }}</div>
                        <div><strong>Phone:</strong> {{ contact.phone or 'Not provided' }}</div>
                        <div><strong>Company:</strong> {{ contact.company or 'Not provided' }}</div>
                        <div><strong>Industry:</strong> {{ contact.industry or 'Not provided' }}</div>
                        <div><strong>Company Size:</strong> {{ contact.company_size or 'Not provided' }}</div>
                    </div>
                </div>
                
                <div>
                    <h3 class="text-lg font-semibold text-cyan-300 mb-4">Project Details</h3>
                    <div class="space-y-3">
                        <div><strong>Form Type:</strong> 
                            <span class="px-2 py-1 text-xs rounded 
                                {% if contact.form_type == 'general' %}bg-blue-600
                                {% elif contact.form_type == 'consultation' %}bg-green-600
                                {% elif contact.form_type == 'project' %}bg-purple-600
                                {% else %}bg-gray-600{% endif %}">
                                {{ contact.form_type.title() }}
                            </span>
                        </div>
                        <div><strong>Service Interest:</strong> {{ contact.service or 'Not specified' }}</div>
                        <div><strong>Budget Range:</strong> {{ contact.budget or 'Not specified' }}</div>
                        <div><strong>Timeline:</strong> {{ contact.timeline or 'Not specified' }}</div>
                        <div><strong>Submitted:</strong> {{ contact.created_at.strftime('%Y-%m-%d %H:%M:%S') }}</div>
                        <div><strong>Status:</strong> 
                            {% if contact.is_processed %}
                                <span class="text-green-400">Processed</span>
                            {% else %}
                                <span class="text-yellow-400">Pending</span>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
            
            {% if contact.message %}
            <div class="mt-6">
                <h3 class="text-lg font-semibold text-cyan-300 mb-4">Message</h3>
                <div class="glass rounded-lg p-4">{{ contact.message }}</div>
            </div>
            {% endif %}
            
            {% if contact.challenges %}
            <div class="mt-6">
                <h3 class="text-lg font-semibold text-cyan-300 mb-4">Business Challenges</h3>
                <div class="glass rounded-lg p-4">{{ contact.challenges }}</div>
            </div>
            {% endif %}
            
            {% if contact.requirements %}
            <div class="mt-6">
                <h3 class="text-lg font-semibold text-cyan-300 mb-4">Project Requirements</h3>
                <div class="glass rounded-lg p-4">{{ contact.requirements }}</div>
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard showing all submissions"""
    db = SessionLocal()
    
    contacts = db.query(ContactSubmission).order_by(ContactSubmission.created_at.desc()).limit(50).all()
    subscribers = db.query(NewsletterSubscription).order_by(NewsletterSubscription.subscribed_at.desc()).limit(50).all()
    
    contact_count = db.query(ContactSubmission).count()
    newsletter_count = db.query(NewsletterSubscription).filter_by(is_active=True).count()
    unprocessed_count = db.query(ContactSubmission).filter_by(is_processed=False).count()
    
    db.close()
    
    return render_template_string(ADMIN_TEMPLATE, 
                                contacts=contacts, 
                                subscribers=subscribers,
                                contact_count=contact_count,
                                newsletter_count=newsletter_count,
                                unprocessed_count=unprocessed_count)

@app.route('/admin/contact/<int:contact_id>', methods=['GET', 'POST'])
def contact_detail(contact_id):
    """View and manage individual contact"""
    db = SessionLocal()
    contact = db.query(ContactSubmission).filter_by(id=contact_id).first()
    
    if not contact:
        db.close()
        return "Contact not found", 404
    
    if request.method == 'POST':
        if 'toggle_processed' in request.form:
            contact.is_processed = not contact.is_processed
            db.commit()
    
    db.close()
    
    return render_template_string(CONTACT_DETAIL_TEMPLATE, contact=contact)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)