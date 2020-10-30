from flask import Flask, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
from forms import RegisterForm, LoginForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config["SECRET_KEY"] = 'whatever'
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql:///feedbacks'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True #print all SQL statements to the terminal
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 #will update static content after any modifications
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

@app.route('/')
def go_register():
    return redirect('/register')

@app.route('/register', methods=["GET", "POST"])
def register_form():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username,password,email,first_name,last_name)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken.  Please pick another')
            return render_template('register.html', form=form, btn='Register')
        session['user_id'] = new_user.id
        flash('Welcome! Successfully Created Your Account!', "success")
        return redirect(f'/users/{new_user.id}')
    return render_template('register.html', form=form, btn='Register')

@app.route('/login', methods=["GET","POST"])
def login_form():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            flash(f'Welcome back, {user.username.upper()}!', "info")
            session['user_id'] = user.id
            return redirect(f'/users/{user.id}')
        else:
            form.username.errors = ['Invalid username/password.']
    return render_template('login.html', form=form, btn='Login')

@app.route('/secret')
def secret_place():
    return render_template('secret.html')

@app.route('/logout')
def logout():
    session.pop('user_id')
    flash("Goodbye!", "info")
    return redirect('/')

@app.route('/users/<int:user_id>')
def user_info(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_info.html', user=user)

@app.route('/users/<int:user_id>/delete', methods=["POST"])
def delete_user(user_id):
    form = RegisterForm()
    user = User.query.get_or_404(user_id)
    if session["user_id"]:
        db.session.delete(user)
        db.session.commit()
        session.pop('user_id')
        flash('Account was deleted', 'warning')
        return render_template('register.html', form=form, btn="Register")
    else:
        flash('You do not have permissions to delete this account', "danger")
        return render_template('register.html', form=form, btn="Register")
    