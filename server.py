import os
from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Use FLASK_SECRET_KEY from environment, or generate a random one for security
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))
app.permanent_session_lifetime = timedelta(hours=1)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE='Lax',
)
csrf = CSRFProtect(app)

@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

