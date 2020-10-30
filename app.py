from flask import Flask, render_template, redirect, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
from forms import RegisterForm
app = Flask(__name__)

app.config["SECRET_KEY"] = 'whatever'
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql:///feedbacks'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True #print all SQL statements to the terminal
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 #will update static content after any modifications

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

@app.route('/')
def go_register():
    return redirect('/register')

@app.route('/register', methods=["GET", "POST"])
def register_form():
    form = RegisterForm()
    return render_template('register.html', form=form, btn='Register')

@app.route('/login', methods=["GET","POST"])
def login_form():
    form = RegisterForm()
    return render_template('login.html', form=form, btn='Login')

@app.route('/secret')
def secret_place():
    return render_template('secret.html')