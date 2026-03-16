# from flask import Flask
# app = Flask(__name__)


# @app.route('/')
# def hello_mate():
#     return '<h1>Hello from Anurag, Mate!</h1>'


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=10000)
# 1. IMPORTS - All the tools we need
from flask import (
    Flask, render_template, request,
    redirect, url_for, flash
)
from flask_sqlalchemy import SQLAlchemy  # Database
from flask_login import (
    LoginManager,
    UserMixin, login_user,
    login_required, logout_user, current_user
)  # Sessions
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)  # Password security

# 2. FLASK APP SETUP
app = Flask(__name__)
app.config['SECRET_KEY'] = 'devops-learning-key-change-in-prod'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# 3. DATABASE + LOGIN MANAGER
db = SQLAlchemy(app)                    # Database engine
login_manager = LoginManager(app)       # Session manager
login_manager.login_view = 'login'      # Redirect unauth users here

# 4. USER MODEL (Database Table)
class User(UserMixin, db.Model):        # UserMixin = login/logout helpers


    id = db.Column(db.Integer, primary_key=True)           # Auto ID
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)   # Hashed!

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))    # Flask-Login needs this


# 5. HOME PAGE - Public landing
@app.route('/')
def home():
    return render_template('home.html')    # Shows login/register links


# 6. REGISTER - Create new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])  # HASH!
        
        if User.query.filter_by(username=username).first():  # Exists?
            flash('Username already exists')
            return redirect(url_for('register'))
            
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()  # Saves to users.db!
        flash('Registered! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')  # Show form


# 7. LOGIN - Authenticate user
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)  # Creates secure session!
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')


# 8. DASHBOARD - PROTECTED PAGE
@app.route('/dashboard')
@login_required  # BLOCKS unauth users!
def dashboard():
    return render_template('dashboard.html', username=current_user.username)


# 9. LOGOUT
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# 10. CREATE DATABASE (runs once)
with app.app_context():
    db.create_all()  # Makes users.db table


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))  # Render sets PORT env var
    app.run(host='0.0.0.0', port=port)
