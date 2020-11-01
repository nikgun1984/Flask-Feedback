from flask import Flask, render_template, redirect, flash, session, request, url_for
from flask_debugtoolbar import DebugToolbarExtension
from forms import RegisterForm, LoginForm, AddFeedBackForm,EmailVerificationForm, ResetPasswordForm
from sqlalchemy.exc import IntegrityError
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature

from models import db, connect_db, User, Feedback, bcrypt
from mail_settings import mail_settings

app = Flask(__name__)

# Application Configurations
app.config["SECRET_KEY"] = 'whatever'
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql:///feedbacks'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True #print all SQL statements to the terminal
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 #will update static content after any modifications
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config.update(mail_settings)

#Mail Object to send confirmation link
mail = Mail(app)

#Serializer obj for email token
s = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# Connect to database and create all tables
connect_db(app)
db.create_all()

# Debugger to the right side
toolbar = DebugToolbarExtension(app)
    
@app.route('/')
def go_register():
    return redirect('/register')

@app.route('/register', methods=["GET", "POST"])
def register_form():
    """Registration Form for a new user"""
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        token = s.dumps(email, salt="email-confirm")
        #register a new user
        new_user = User.register(username,password,email,first_name,last_name,token)

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
    """Login an existing user"""
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        # necessary to authenticate an existing user
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
    """Route for only an existing user"""
    return render_template('secret.html')

@app.route('/logout')
def logout():
    """Logout as a current user"""
    session.pop('user_id')
    flash("Goodbye!", "info")
    return redirect('/')

@app.route('/users/<int:user_id>')
def user_info(user_id):
    """Get info on user"""
    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    user = User.query.get_or_404(user_id)
    feedbacks = db.session.query(Feedback).filter_by(user_id=user_id).all()
    if user.is_admin:
        feedbacks = Feedback.query.all()
    return render_template('user_info.html', user=user, feedbacks=feedbacks)

@app.route('/users/<int:user_id>/delete', methods=["POST"])
def delete_user(user_id):
    """Delete User"""
    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    form = RegisterForm()
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    session.pop('user_id')
    flash('Account was deleted', 'warning')
    return redirect("/login")

@app.route('/users/<int:user_id>/feedback/add', methods=["GET","POST"])
def add_feedback(user_id):
    """Add feedback"""
    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    form = AddFeedBackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        feedback = Feedback(title=title,content=content,user_id=user_id)
        db.session.add(feedback)
        db.session.commit()
        flash("Feedback was added", "info")
        return redirect(f'/users/{user_id}')
    return render_template('add_feedback.html', form=form, btn="Submit")

@app.route('/feedback/<int:feedback_id>/update', methods=["GET","POST"])
def update_feedback(feedback_id):
    """Update feedback"""
    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    feedback = Feedback.query.get_or_404(feedback_id)
    form = AddFeedBackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        flash("Feedback updated successfully", "info")
        return redirect(f'/users/{session["user_id"]}')
    return render_template('update_feedback.html',btn='Update',form=form,feedback=feedback)

@app.route('/feedback/<int:feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    """Delete your feedback"""
    if session.get("user_id"):
        feedback = Feedback.query.get_or_404(feedback_id)
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedback deleted  successfully","info")
        return redirect(f'/users/{session["user_id"]}')
    else:
        flash("Please login first!", "danger")
        return redirect('/login')

@app.errorhandler(404)
def error(user_id):
    return render_template("404.html"), 404

@app.route('/users/<int:user_id>/mail', methods=["GET","POST"])
def send_email(user_id):
    """Send email with confirmation link"""
    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    form = EmailVerificationForm()
    user = User.query.get(user_id)
    if form.validate_on_submit():
        email = form.email.data
        token = user.token
        # Message consists of title, who to send email and body, can include sender(optional)
        msg = Message(subject='Password Change', recipients=[user.email])
        # get that external link with a valid token
        link = url_for('confirm_email', token=token, _external=True)
        msg.body = f"Your link is {link}"
        # send link
        mail.send(msg)
        flash("Your email sent successfully","info")
        return redirect(f'/users/{user_id}')
    return render_template('send_email.html', btn='Submit',form=form)
    # with app.open_resource('cat.png') as cat:
    #     msg.attach('cat.png','image/jpeg', cat.read())


@app.route('/confirm_email/<token>', methods=["GET","POST"])
def confirm_email(token):
    """Send a link to valid email with confirmation link/
       Change your password
    """
    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    form = ResetPasswordForm()
    user = User.query.get_or_404(session["user_id"])
    
    #Get that external link if successful get password reset form
    try:
        email = s.loads(token,salt="email-confirm", max_age=3600)
    except SignatureExpired:
        flash('The token has expired',"warning")
        return redirect(f'/users/{session["user_id"]}')
    except BadTimeSignature:
        flash('The wrong token',"warning")
        return redirect(f'/users/{session["user_id"]}')

    if form.validate_on_submit():
            hashed = bcrypt.generate_password_hash(form.password.data)
            # turn bytestring into normal unicode utf-8 string
            user.password = hashed.decode("utf8")
            db.session.commit()
            flash('Password reset successfully',"info")
            return redirect(f'/users/{session["user_id"]}')
    return render_template('reset_password.html', btn='Reset Password',form=form)
    







    