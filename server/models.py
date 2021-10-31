from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model): # type: ignore
	id = db.Column(db.Integer, primary_key=True) # type: ignore # primary keys are required by SQLAlchemy
	email = db.Column(db.String(100), unique=True) # type: ignore
	password = db.Column(db.String(100)) # type: ignore
	name = db.Column(db.String(1000)) # type: ignore