from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, DataRequired, Email

class RegisterForm(FlaskForm):
    """Form for registering the user"""

    username = StringField("Username", validators=[InputRequired("Please enter your name")])
    password = PasswordField("Password", validators=[InputRequired("Please enter your password")])
    email = EmailField("Email address", validators=[DataRequired("Please enter your email address."),Email("This field requires a valid email address")])
    first_name = StringField("First Name", validators=[InputRequired("Please enter your name")])
    last_name = StringField("Last Name", validators=[InputRequired("Please enter your last name")])

