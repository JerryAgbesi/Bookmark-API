from flask import Flask,redirect,jsonify
import os
from src.bookmarks import bookmark
from src.database import db,Bookmark
from src.auth import auth
from flask_jwt_extended import JWTManager


def create_app(testing_config=None):
    app = Flask(__name__,instance_relative_config=True)

    if testing_config is None:
        app.config.from_mapping(
            SECRET_key = os.environ.get('SECRET_KEY'),
            SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DB_URI'),
            JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY'))
    else:
        app.config.from_mapping(testing_config)

    @app.get("/")
    def index():
        return "Welcome to the Bookmarks API" 

    
    db.app = app
    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(auth)
    app.register_blueprint(bookmark)


    @app.get("/<short_url>")
    def redirect_to(short_url):
        bookmark = Bookmark.query.filter_by(short_url= short_url).first_or_404()

        if bookmark:
            bookmark.visits += 1
            db.session.commit()
            return redirect(bookmark.url),302
        else:
            return jsonify({
                "Error":"URL not found"
            }),404 

    #Error handling  
    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({"Error":"Resource not found"}),404

    @app.errorhandler(500)
    def handle_error(e):
        return jsonify({"Error":"It's not your fault,it's ours"}),500  

    return app
