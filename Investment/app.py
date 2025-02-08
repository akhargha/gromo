from flask import Flask
from flask_cors import CORS
from routes.index import index_bp
from routes.portfolios import portfolios_bp
from routes.investments import investments_bp
from routes.performance import performance_bp
from dotenv import load_dotenv

def create_app():
    load_dotenv()  # Load environment variables
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    # Register Blueprints with URL prefixes
    app.register_blueprint(index_bp, url_prefix='/')
    app.register_blueprint(portfolios_bp, url_prefix='/api')
    app.register_blueprint(investments_bp, url_prefix='/api')
    app.register_blueprint(performance_bp, url_prefix='/api')

    # Generic error handler
    @app.errorhandler(Exception)
    def handle_error(error):
        return {
            "message": str(error),
            "status": getattr(error, 'code', 500)
        }, getattr(error, 'code', 500)

    return app

if __name__ == "__main__":
    application = create_app()
    application.run(debug=True, host='0.0.0.0', port=5000)