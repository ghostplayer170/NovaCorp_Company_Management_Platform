import os
from server import app
from routes import auth, companies, companies_admin, users_admin, profile

if __name__ == "__main__":
    # Load debug setting from environment, default to False for security
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode)
