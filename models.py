from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """Connect to our database"""

    db.app = app
    db.init_app(app)

"""Models"""
class User(db.Model):

    ___tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)

    username = db.Column(db.String(20), nullable = False, unique = True)

    password = db.Column(db.Text, nullable = False)

    email = db.Column(db.String(50), nullable = False, unique = True)

    first_name = db.Column(db.String(30), nullable = False)

    last_name = db.Column(db.String(30), nullable = False)

    @classmethod
    def register(cls, username, pwd):
        """Register user w/hashed password & return user."""
        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal unicode utf-8 string
        hashed_utf8 = hashed.decode("utf8")

        #return instance of user w/username and hashed pwd
        return cls(username = username, password=hashed_utf8)

    @classmethod
    def authenticate(cls,username, pwd):
        """Validate that user exists and password is correct
           Return user if valid otherwise return false
        """

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, pwd):
            return user
        else:
            return False
