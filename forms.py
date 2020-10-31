from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, DataRequired, Email

class RegisterForm(FlaskForm):
    """Form for registering the user"""

    username = StringField("Username", validators=[InputRequired("Please enter your name")])
    password = PasswordField("Password", validators=[InputRequired("Please enter your password")])
    email = StringField("Email address", validators=[DataRequired("Please enter your email address."),Email("This field requires a valid email address")])
    first_name = StringField("First Name", validators=[InputRequired("Please enter your name")])
    last_name = StringField("Last Name", validators=[InputRequired("Please enter your last name")])

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired("Please enter your name")])
    password = PasswordField("Password", validators=[InputRequired("Please enter your password")])

class AddFeedBackForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired("Please enter the title of feedback")])
    content = TextAreaField("Content", validators=[InputRequired("Please enter missing comment")])