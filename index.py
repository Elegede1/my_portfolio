from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort, Response
import io
import datetime
from flask_bootstrap import Bootstrap4
from flask_wtf import CSRFProtect
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import LoginForm, ContactForm, ProjectForm, UserForm, MessageForm, ExperienceForm, EducationForm, SkillForm, ResumeUploadForm
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
from flask_admin.contrib.fileadmin import FileAdmin

load_dotenv()

# Updated paths for Vercel structure
# We use root_path to ensure relative paths work in both local and Vercel environments
app = Flask(__name__)
# --- Robust Environment Variable Retrieval ---
# Try both lowercase and uppercase as users often mix them in Vercel settings
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or os.getenv('secret_key')

mongo_uri = os.getenv('MONGO_URI') or os.getenv('mongo_uri')
if mongo_uri:
    # Safety: Remove trailing slashes that cause "Bad database name" errors
    mongo_uri = mongo_uri.strip().replace('/?', '?')
    if mongo_uri.endswith('/'):
        mongo_uri = mongo_uri[:-1]

# IMPORTANT: We deliberately do NOT raise if MONGO_URI is missing or unreachable.
# Raising at module-import time kills the entire serverless function before any
# request can be served — meaning the homepage (which uses NO Mongo data) would
# 500 silently whenever Atlas is paused, misconfigured, or DNS-failing.
# Instead, we configure it if present and lazy-init the connection on first use.
# Per-route handlers protect themselves with get_db_or_503() so only the
# Mongo-dependent routes degrade, not the whole app.
if not mongo_uri:
    print("WARNING: MONGO_URI is not set. The site will render but Mongo-backed routes (/projects, /resume, /contact, /admin) will return 503.")
    app.config['MONGO_URI'] = None
else:
    app.config['MONGO_URI'] = mongo_uri

# Lazy PyMongo — do NOT instantiate at import time. Avoids invoking DNS SRV
# resolution until the first request that actually needs Mongo.
_mongo = None

def get_db_or_503():
    """Return the mongo db handle, or None if Mongo is unavailable.
    Routes that depend on data should call this and either render a graceful
    fallback or return a 503 if it returns None."""
    global _mongo
    if _mongo is not None:
        try:
            # touch the connection to make sure it's actually alive
            _mongo.db.command('ping')
            return _mongo.db
        except Exception:
            # connection died (e.g. Atlas paused mid-flight); fall through and try to re-init
            _mongo = None
    if not app.config.get('MONGO_URI'):
        return None
    try:
        _mongo = PyMongo(app)
        _mongo.db.command('ping')
        return _mongo.db
    except Exception as e:
        # Could be DNS failure (Atlas paused), bad URI, network blip, etc.
        # Don't crash; just route-level degrade.
        print(f"Mongo unavailable: {e}")
        _mongo = None
        return None

# For legacy code that imports `mongo` directly (admin views, Flask-Login user_loader),
# expose a backward-compatible proxy that lazily initializes on attribute access.
class _MongoProxy:
    """Backward-compatible proxy so existing `mongo.db...` references keep working.
    Each attribute access goes through get_db_or_503, so we never hold a dead connection."""
    @property
    def db(self):
        return get_db_or_503()

    def __getattr__(self, name):
        # fall back to the underlying PyMongo instance for non-db attrs
        if _mongo is not None:
            return getattr(_mongo, name)
        raise RuntimeError("Mongo is not available")

mongo = _MongoProxy()

login_manager = LoginManager()
login_manager.init_app(app)
# Redirect unauthenticated users to the secret login page instead of a bare 401.
login_manager.login_view = 'login'
csrf = CSRFProtect(app)
Bootstrap4(app)

# --- Define upload folder ---
try:
    UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create upload folder: {e}")

# --- Admin Security and Views ---
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

class SecureFileAdmin(FileAdmin):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

class ProjectView(SecureModelView):
    column_list = ('title', 'body', 'img_url', 'img_url_2', 'img_url_3', 'github_url', 'live_url')
    form = ProjectForm
    # Flask-Admin PyMongo requires explicit form mapping if not using MongoEngine
    # However, since we want security and simplicity, we use the basic ModelView
    
    def on_model_change(self, form, model, is_created):
        if is_created:
            model['date'] = datetime.datetime.utcnow()
        return super().on_model_change(form, model, is_created)

class UserView(SecureModelView):
    column_list = ('name', 'email', 'role')
    form = UserForm

class MessageView(SecureModelView):
    column_list = ('name', 'email', 'subject', 'date_submitted')
    form = MessageForm
    can_create = False # Messages come from contact form
    column_default_sort = ('date_submitted', True)

class ExperienceView(SecureModelView):
    column_list = ('company', 'title', 'date_range')
    form = ExperienceForm

class EducationView(SecureModelView):
    column_list = ('institution', 'degree', 'date_range')
    form = EducationForm

class SkillView(SecureModelView):
    column_list = ('name', 'skill_type')
    form = SkillForm


# Initialize Flask-Admin with secret URL and custom base template for Dark Mode
# Note: Admin views are registered lazily on first request to the admin area.
# This avoids requiring a live MongoDB connection at module import time, which
# would crash the serverless function if Atlas is paused/misconfigured.
admin = Admin(app, name='Portfolio Admin', template_mode='bootstrap4', url='/12812673-738234admin', base_template='admin/master.html')
_admin_views_registered = False

def _register_admin_views():
    """Register Flask-Admin views against the (possibly lazy) Mongo collections.
    Called on first request to /admin/* via a before_request hook. No-ops after
    the first successful registration."""
    global _admin_views_registered
    if _admin_views_registered:
        return
    db = get_db_or_503()
    if db is None:
        return  # Mongo not available; admin views stay unregistered this cycle
    try:
        admin.add_view(ProjectView(db.projects, 'Projects'))
        admin.add_view(UserView(db.users, 'Users'))
        admin.add_view(MessageView(db.messages, 'Contact Messages'))
        admin.add_view(ExperienceView(db.experience, 'Experience', category='Résumé'))
        admin.add_view(EducationView(db.education, 'Education', category='Résumé'))
        admin.add_view(SkillView(db.skills, 'Skills', category='Résumé'))
        _admin_views_registered = True
    except Exception as e:
        print(f"Admin views registration deferred (Mongo not ready): {e}")

@app.before_request
def _maybe_register_admin_views():
    # Only attempt registration on admin URLs to avoid hitting Mongo on every
    # public request. Triggers a lazy Mongo init only when admin is accessed.
    if request.path.startswith('/12812673-738234admin'):
        _register_admin_views()

# Allow editing the resume PDF
path = os.path.join(app.root_path, 'static', 'files')
admin.add_view(SecureFileAdmin(path, '/static/files/', name='Resume File', category='Résumé'))

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

@app.route('/12812673-738234login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db = get_db_or_503()
        if db is None:
            flash('Login is temporarily unavailable. Please try again later.', 'danger')
            return render_template('login.html', form=form), 503
        user_data = db.users.find_one({"email": form.email.data})

        if user_data and check_password_hash(user_data["password"], form.password.data):
            user = User(user_data)
            login_user(user)
            if user.role == 'admin':
                return redirect('/12812673-738234admin')
            return redirect(url_for('projects'))
        else:
            flash('Invalid email or password.')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route('/test')
def test_route():
    return "App is running! If you see this, the serverless function is working, but the database connection might be the issue."

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
        db = get_db_or_503()
        if db is None:
            flash('Sorry, the contact form is temporarily unavailable. Please reach me via email or social media.', 'danger')
            return render_template('contact.html', form=form), 503
        db.messages.insert_one({
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
    db = get_db_or_503()
    if db is None:
        # Render with empty list rather than 500 — projects.html handles empty projects gracefully.
        all_projects = []
    else:
        all_projects = list(db.projects.find().sort("date", -1))
    current_year = datetime.datetime.now().year
    return render_template('projects.html', projects=all_projects, year=current_year, user=current_user)

@app.route('/resume')
def resume():
    db = get_db_or_503()
    if db is None:
        # Render with empty sections rather than 500 — resume.html should handle empty lists gracefully.
        return render_template('resume.html', experience=[], education=[], prof_skills=[], lang_skills=[])
    experience = list(db.experience.find())
    education = list(db.education.find())
    # Separate skills by type
    prof_skills = list(db.skills.find({"skill_type": "Professional"}))
    lang_skills = list(db.skills.find({"skill_type": "Language"}))
    
    return render_template('resume.html', 
                          experience=experience, 
                          education=education, 
                          prof_skills=prof_skills, 
                          lang_skills=lang_skills)


# --- Resume PDF management ---
# On Vercel the filesystem is read-only, so we CANNOT overwrite the bundled
# static PDF at runtime. Instead we store an uploaded resume in MongoDB (which
# is writable) and serve it from there, falling back to the bundled static file
# when no upload exists yet.
RESUME_STATIC_PATH = "files/Jekuthiel_Okafor's_resume.pdf"


@app.route('/12812673-738234admin/resume', methods=['GET', 'POST'])
@login_required
def upload_resume():
    """Secured page to replace the resume PDF. Stores the file in MongoDB so it
    persists on Vercel's read-only serverless filesystem."""
    if not (current_user.is_authenticated and getattr(current_user, 'role', None) == 'admin'):
        return redirect(url_for('login', next=request.url))

    form = ResumeUploadForm()
    db = get_db_or_503()

    # Info about the currently stored resume (if any) for display.
    current = None
    if db is not None:
        try:
            current = db.settings.find_one({"_id": "resume"})
        except Exception:
            current = None

    if form.validate_on_submit():
        if db is None:
            flash('Resume upload is temporarily unavailable (database offline). Please try again later.', 'danger')
            return render_template('admin/upload_resume.html', form=form, current=current), 503
        file = form.resume.data
        data = file.read()
        if not data:
            flash('The uploaded file was empty. Please choose a valid PDF.', 'danger')
            return redirect(url_for('upload_resume'))
        # Basic sanity check: PDFs start with "%PDF".
        if not data[:4] == b'%PDF':
            flash('That does not look like a valid PDF file.', 'danger')
            return redirect(url_for('upload_resume'))
        try:
            db.settings.update_one(
                {"_id": "resume"},
                {"$set": {
                    "data": data,
                    "filename": secure_filename(file.filename) or "resume.pdf",
                    "content_type": "application/pdf",
                    "size": len(data),
                    "updated_at": datetime.datetime.utcnow(),
                }},
                upsert=True,
            )
            flash('Resume replaced successfully! Visitors will now download the new PDF.', 'success')
            return redirect(url_for('upload_resume'))
        except Exception as e:
            print(f"Resume upload failed: {e}")
            flash('Sorry, saving the resume failed. Please try again.', 'danger')
            return redirect(url_for('upload_resume'))

    return render_template('admin/upload_resume.html', form=form, current=current)


@app.route('/download')
def download():
    """Serve the resume. Prefer the DB-stored upload; fall back to the bundled
    static PDF so the button always works even before the first upload."""
    db = get_db_or_503()
    if db is not None:
        try:
            doc = db.settings.find_one({"_id": "resume"})
            if doc and doc.get("data"):
                pdf_bytes = doc["data"]
                # PyMongo returns Binary; bytes() normalizes it for the Response.
                filename = doc.get("filename") or "Jekuthiel_Okafor_resume.pdf"
                return Response(
                    bytes(pdf_bytes),
                    mimetype="application/pdf",
                    headers={
                        "Content-Disposition": f'attachment; filename="{filename}"',
                        "Content-Length": str(len(pdf_bytes)),
                    },
                )
        except Exception as e:
            print(f"Serving resume from DB failed, falling back to static: {e}")
    # Fallback: bundled static file.
    return send_from_directory('static', path=RESUME_STATIC_PATH)


if __name__ == '__main__':
    app.run(debug=True)
