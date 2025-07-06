from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort
import datetime
from flask_bootstrap import Bootstrap
from flask_wtf import CSRFProtect
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import LoginForm, RegisterForm, PostForm, ContactForm
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os

# New imports for MongoDB
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from pymongo.errors import ConnectionFailure

load_dotenv()

app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['CKEDITOR_CONFIG'] = {'toolbar': 'Full', 'height': 500}
app.config['SECRET_KEY'] = os.getenv('secret_key')
login_manager = LoginManager()
login_manager.init_app(app)
csrf = CSRFProtect(app)
Bootstrap(app)

# --- MongoDB Configuration ---
mongo_uri = os.getenv('MONGO_URI')
if not mongo_uri:
    # Fail fast with a clear error if the URI is missing
    raise ValueError("FATAL ERROR: MONGO_URI environment variable is not set.")

app.config['MONGO_URI'] = mongo_uri
mongo = PyMongo(app)

# --- Define upload folder ---
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Make sure UPLOAD_FOLDER exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- CLI Command for Database Initialization (Best Practice) ---
@app.cli.command("init-db")
def init_db_command():
    """
    Initializes the database, creates collections, indexes, and the admin user.
    This command should be run once during setup.
    """
    try:
        # 1. Test the connection
        mongo.db.command('ping')
        print("MongoDB connection successful!")

        # 2. Create collections and indexes
        users_collection = mongo.db.users
        users_collection.create_index([("email", 1)], unique=True)
        print("Indexes for 'users' collection created successfully.")

        # 3. Create initial admin user
        admin_email = os.getenv('ADMIN_EMAIL')
        admin_password = os.getenv('ADMIN_PASSWORD')

        if not admin_email or not admin_password:
            print("Warning: ADMIN_EMAIL or ADMIN_PASSWORD not set. Skipping admin creation.")
            return

        if users_collection.find_one({"email": admin_email}):
            print(f"Admin user with email '{admin_email}' already exists.")
        else:
            hashed_password = generate_password_hash(admin_password, method='pbkdf2:sha256', salt_length=8)
            users_collection.insert_one({
                "email": admin_email,
                "password": hashed_password,
                "name": 'Admin',
                "role": 'admin'
            })
            print(f"Admin user '{admin_email}' created successfully.")

    except ConnectionFailure as e:
        print(f"Database connection failed: {e}")
        print("Please check your MONGO_URI and Atlas IP Whitelist settings.")
    except Exception as e:
        print(f"An error occurred during database initialization: {e}")


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
        # This can happen if the DB is down during a request
        return None
    return None

# ... (The rest of your routes: admin_only, register, login, etc. remain the same) ...
# Make sure to remove the old init-admin command and the global-scope DB setup code.

# (Your routes go here)
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for role instead of a hardcoded ID
        if not current_user.is_authenticated or current_user.role != 'admin':
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user already exists by their email
        # FIX: Changed form.names.data to form.email.data
        existing_user = mongo.db.users.find_one({"email": form.email.data})
        if existing_user:
            flash('An account with that email already exists.')
            return redirect(url_for('login'))

        # Insert new user document into the 'users' collection
        mongo.db.users.insert_one({
            "email": form.email.data,
            "password": generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8),
            "name": form.name.data,
            "role": "user"  # Default role
        })
        flash('Account created successfully!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)




@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # World-Class Change: Find user by unique email, not by name.
        user_data = mongo.db.users.find_one({"email": form.email.data})

        if user_data and check_password_hash(user_data["password"], form.password.data):
            user = User(user_data)
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('add_project'))
            return redirect(url_for('projects'))
        else:
            # Update flash message for clarity
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
        # This will create a 'messages' collection on the first submission
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
    # Fetch all documents from the 'projects' collection
    # Sort by date, descending
    all_projects = mongo.db.projects.find().sort("date", -1)
    current_year = datetime.datetime.now().year
    return render_template('projects.html', projects=all_projects, year=current_year, user=current_user)


@app.route('/add_project', methods=['GET', 'POST'])
@login_required
@admin_only
def add_project():
    form = PostForm()
    if form.validate_on_submit():
        img_url = ''
        if form.img_url.data:
            file = form.img_url.data
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            img_url = f'uploads/{filename}'

        # Insert a new document into the 'projects' collection
        mongo.db.projects.insert_one({
            "title": form.title.data,
            "body": form.body.data,
            "img_url": img_url,
            "github_url": form.github_url.data,
            "date": datetime.datetime.utcnow(),
            "user_id": ObjectId(current_user.get_id())  # Store user's ObjectId
        })
        return redirect(url_for('projects'))
    return render_template('add_project.html', form=form)


@app.route('/edit_project/<project_id>', methods=['GET', 'POST'])
@login_required
@admin_only
def edit_project(project_id):
    # Find the project by its ObjectId
    project_data = mongo.db.projects.find_one_or_404({"_id": ObjectId(project_id)})

    # Pre-populate form with existing data
    form = PostForm()

    form.img_url.label.text = "Project Image (Optional: leave empty to keep current image)"

    if form.validate_on_submit():
        update_data = {
            "title": form.title.data,
            "body": form.body.data,
            "github_url": form.github_url.data,
        }
        # Handle optional image update
        if form.img_url.data:
            file = form.img_url.data
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            update_data["img_url"] = f'uploads/{filename}'

        # Update the document in the 'projects' collection
        mongo.db.projects.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": update_data}
        )
        flash('Project updated successfully.', 'success')
        return redirect(url_for('projects'))

    elif request.method == 'GET':
        form.title.data = project_data.get('title')
        form.body.data = project_data.get('body')
        form.github_url.data = project_data.get('github_url')

    # Pass the original image URL to the template for display
    current_img_url = project_data.get('img_url')
    return render_template('edit_project.html', form=form, project=project_data, current_img_url=current_img_url)


@app.route('/delete_project/<project_id>', methods=['POST'])
@login_required
@admin_only
def delete_project(project_id):
    # Delete the document from the 'projects' collection
    mongo.db.projects.delete_one({"_id": ObjectId(project_id)})
    flash('Project deleted successfully.', 'success')
    return redirect(url_for('projects'))


@app.route('/resume')
def resume():
    return render_template('resume.html')


@app.route('/download')
def download():
    return send_from_directory('static', path="files/Jekuthiel_Okafor's_resume.pdf")


if __name__ == '__main__':
    app.run(debug=True)
