from flask import Flask
from .routes.twinestory_routes import twine_story_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(twine_story_bp, url_prefix='/story')
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
