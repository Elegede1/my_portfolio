from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort
import datetime
from flask_bootstrap import Bootstrap
from flask_wtf import CSRFProtect
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import LoginForm, RegisterForm, PostForm, ContactForm
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os

# New imports for MongoDB and Flask-Admin
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from pymongo.errors import ConnectionFailure
from flask_admin import Admin
from flask_admin.contrib.pymongo import ModelView

load_dotenv()

# Updated paths for Vercel structure
# We use root_path to ensure relative paths work in both local and Vercel environments
app = Flask(__name__)
# --- Robust Environment Variable Retrieval ---
# Try both lowercase and uppercase as users often mix them in Vercel settings
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or os.getenv('secret_key')

mongo_uri = os.getenv('MONGO_URI') or os.getenv('mongo_uri')
if not mongo_uri:
    # On Vercel, we want to know exactly why it's failing
    print("CRITICAL: MONGO_URI is not set in environment variables.")
    raise ValueError("MONGO_URI environment variable is missing. Please add it to your Vercel Project Settings.")

app.config['MONGO_URI'] = mongo_uri
mongo = PyMongo(app)

login_manager = LoginManager()
login_manager.init_app(app)
csrf = CSRFProtect(app)
Bootstrap(app)

# --- Define upload folder ---
UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Admin Security and Views ---
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

class ProjectView(SecureModelView):
    column_list = ('title', 'date', 'github_url')
    # Flask-Admin PyMongo requires explicit form mapping if not using MongoEngine
    # However, since we want security and simplicity, we use the basic ModelView
    
    def on_model_change(self, form, model, is_created):
        if is_created:
            model['date'] = datetime.datetime.utcnow()
        return super().on_model_change(form, model, is_created)

class UserView(SecureModelView):
    column_list = ('name', 'email', 'role')

class MessageView(SecureModelView):
    column_list = ('name', 'email', 'subject', 'date_submitted')
    can_create = False # Messages come from contact form
    column_default_sort = ('date_submitted', True)

# Initialize Flask-Admin
admin = Admin(app, name='Portfolio Admin', template_mode='bootstrap4', url='/admin')
admin.add_view(ProjectView(mongo.db.projects, 'Projects'))
admin.add_view(UserView(mongo.db.users, 'Users'))
admin.add_view(MessageView(mongo.db.messages, 'Contact Messages'))

# --- User Model Wrapper for Flask-Login ---
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.email = user_data["email"]
        self.password = user_data["password"]
        self.name = user_data["name"]
        self.role = user_data.get("role")

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(user_data)
    except Exception:
        return None
    return None

# --- Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = mongo.db.users.find_one({"email": form.email.data})
        if existing_user:
            flash('An account with that email already exists.')
            return redirect(url_for('login'))

        mongo.db.users.insert_one({
            "email": form.email.data,
            "password": generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8),
            "name": form.name.data,
            "role": "user"
        })
        flash('Account created successfully!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_data = mongo.db.users.find_one({"email": form.email.data})

        if user_data and check_password_hash(user_data["password"], form.password.data):
            user = User(user_data)
            login_user(user)
            if user.role == 'admin':
                return redirect('/admin')
            return redirect(url_for('projects'))
        else:
            flash('Invalid email or password.')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
def index():
    current_year = datetime.datetime.now().year
    return render_template('index.html', year=current_year)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        mongo.db.messages.insert_one({
            "name": form.name.data,
            "email": form.email.data,
            "subject": form.subject.data,
            "message": form.message.data,
            "date_submitted": datetime.datetime.utcnow()
        })
        flash("Your message has been sent successfully! I'll get back to you soon.", "success")
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

@app.route('/projects', methods=['GET'])
def projects():
    all_projects = mongo.db.projects.find().sort("date", -1)
    current_year = datetime.datetime.now().year
    return render_template('projects.html', projects=all_projects, year=current_year, user=current_user)

@app.route('/resume')
def resume():
    return render_template('resume.html')

@app.route('/download')
def download():
    return send_from_directory('static', path="files/Jekuthiel_Okafor's_resume.pdf")

if __name__ == '__main__':
    app.run(debug=True)
