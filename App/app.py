from flask import Flask
from .config import Config
from .database import init_db
from .routes import bp as main_bp

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../Templates', static_folder='../Static', static_url_path='/static')
    app.config.from_object(config_class)

    # Initialize Database
    with app.app_context():
        init_db()

    # Register Blueprints
    from .routes import oauth
    oauth.init_app(app)
    
    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect()
    csrf.init_app(app)

    app.register_blueprint(main_bp)

    from flask_jwt_extended import JWTManager
    jwt = JWTManager(app)

    return app

if __name__ == "__main__":
    import os
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
