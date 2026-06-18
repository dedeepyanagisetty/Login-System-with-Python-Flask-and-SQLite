from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import re, hashlib

app = Flask(__name__)

# Secret key for session management (can be any random string) 
app.secret_key = 'your secret key'

# SQLite Database Configuration
# URI to the SQLite database file ('pythonlogin.db' will be created in your project folder)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pythonlogin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable Flask-SQLAlchemy modification tracking

# Initialize the SQLAlchemy object with Flask app
db = SQLAlchemy(app)

# Define the Account model (which will correspond to the 'accounts' table in the SQLite database)
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key field
    username = db.Column(db.String(50), nullable=False, unique=True)  # Username field (unique)
    password = db.Column(db.String(255), nullable=False)  # Password field
    email = db.Column(db.String(100), nullable=False, unique=True)  # Email field (unique)

    # Representation of Account object for debugging purposes
    def __repr__(self):
        return f"<Account {self.username}>"

# Create the 'accounts' table in the database (run once when app starts)
with app.app_context():
    db.create_all()

# localhost:5000/pythonlogin/ - Login page, supports both GET and POST methods
@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''  # Initialize message variable
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']  # Get the username from form
        password = request.form['password']  # Get the password from form
        
        # Check if account exists using SQLAlchemy (query the 'accounts' table)
        account = Account.query.filter_by(username=username).first()
        
        # If account exists, validate the password
        if account:
            # Hash the entered password and compare with the stored hash
            hash = password + app.secret_key  # Combine password with secret key for hashing
            hash = hashlib.sha1(hash.encode()).hexdigest()  # Hash the password
            if account.password == hash:
                # If login is successful, store session variables
                session['loggedin'] = True
                session['id'] = account.id
                session['username'] = account.username
                return redirect(url_for('home'))  # Redirect to the home page
            else:
                msg = 'Incorrect password!'  # Invalid password
        else:
            msg = 'Incorrect username/password!'  # Invalid username
    
    # Render the login page with any message (if exists)
    return render_template('index.html', msg=msg)

# localhost:5000/pythonlogin/register - Registration page, supports both GET and POST methods
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    msg = ''  # Initialize message variable
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']  # Get the username from form
        password = request.form['password']  # Get the password from form
        email = request.form['email']  # Get the email from form
        
        # Check if account with the same username already exists in the database
        account = Account.query.filter_by(username=username).first()
        
        if account:
            msg = 'Account already exists!'  # Account with the username already exists
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):  # Validate email format
            msg = 'Invalid email address!'  # Invalid email format
        elif not re.match(r'[A-Za-z0-9]+', username):  # Validate username (letters and numbers only)
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:  # Check if all fields are filled
            msg = 'Please fill out the form!'
        else:
            # Hash the password before storing it in the database
            hash = password + app.secret_key  # Combine password with secret key for hashing
            hash = hashlib.sha1(hash.encode()).hexdigest()  # Hash the password
            
            # Create a new account in the database
            new_account = Account(username=username, password=hash, email=email)
            db.session.add(new_account)  # Add the new account to the session
            db.session.commit()  # Commit the transaction to the database
            msg = 'You have successfully registered!'  # Success message
    
    # Render the registration page with any message (if exists)
    return render_template('register.html', msg=msg)

# localhost:5000/pythonlogin/home - Home page, accessible only after successful login
@app.route('/pythonlogin/home')
def home():
    if 'loggedin' in session:  # Check if user is logged in
        # Render the home page and pass the username to display on the page
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))  # Redirect to login page if not logged in

# localhost:5000/pythonlogin/profile - Profile page, accessible only after login
@app.route('/pythonlogin/profile')
def profile():
    if 'loggedin' in session:  # Check if user is logged in
        # Retrieve the account details from the database using the session's user ID
        account = Account.query.filter_by(id=session['id']).first()
        # Render the profile page with the account details
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))  # Redirect to login page if not logged in

# localhost:5000/pythonlogin/logout - Logout page to clear session and log out the user
@app.route('/pythonlogin/logout')
def logout():
    # Remove session variables to log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))  # Redirect to login page after logout

# Start the Flask app on localhost (default port is 5000)
if __name__ == '__main__':
    app.run(debug=True)
