# TODO: UPDATE THIS FILE FOR DEPLOYMENT
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager


app = Flask(__name__)
CORS(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ultraSecretAndSecure'	


db = SQLAlchemy(app)


# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


import routes


with app.app_context():
    db.create_all()


if (__name__ == '__main__'):
    app.run(debug=True)