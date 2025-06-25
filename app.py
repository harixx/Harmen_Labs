from flask import Flask, send_from_directory, redirect, url_for
import os

app = Flask(__name__)

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
