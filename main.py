from app import app

# This enables running the Flask application
# with Gunicorn through the workflow configuration
# (gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app)

if __name__ == "__main__":
    # Running directly with Python
    app.run(host='0.0.0.0', port=5000, debug=True)
