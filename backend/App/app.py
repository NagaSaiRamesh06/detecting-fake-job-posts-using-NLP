from flask import Flask
from flask_cors import CORS
from .config import Config
from .database import init_db
from .routes import bp as main_bp

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../Templates', static_folder='../Static', static_url_path='/static')
    CORS(app, supports_credentials=True)
    app.config.from_object(config_class)
    
    # Configure ProxyFix for reverse proxies (Render SSL termination)
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Initialize Database
    with app.app_context():
        init_db()

    # CSRF Protection
    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect()
    csrf.init_app(app)

    app.register_blueprint(main_bp)

    from flask_jwt_extended import JWTManager
    jwt = JWTManager(app)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
