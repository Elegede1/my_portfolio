from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, abort
import datetime
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm, CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text
from forms import LoginForm, RegisterForm, PostForm
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

import os

load_dotenv()

app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['CKEDITOR_CONFIG'] = {'toolbar': 'Full', 'height': 500}
app.config['SECRET_KEY'] = os.getenv('secret_key')
login_manager = LoginManager()
login_manager.init_app(app)
csrf = CSRFProtect(app)
Bootstrap5(app)


class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('database_url')

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))

class Project(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[datetime.datetime] = mapped_column(db.DateTime, default=datetime.datetime.utcnow)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('user.id'))
    user: Mapped[User] = relationship('User', backref='projects')

with app.app_context():
    db.create_all() # create all tables in the database
    # Create default admin user if none exists
    if not User.query.first():
        admin_user = User(
            email=os.getenv('ADMIN_EMAIL', 'admin@example.com'),
            password=generate_password_hash(os.getenv('ADMIN_PASSWORD', os.getenv('admin_password')), method='pbkdf2:sha256', salt_length=8),
            name='Admin',
            id=1
        )
        db.session.add(admin_user)
        db.session.commit()

# Define upload folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # # Skip authentication check for index route
        # if request.endpoint == 'index':
        #     return f(*args, **kwargs)
        if current_user.id != 1 and not current_user.is_authenticated:
            return abort(403)
        else:
            return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(
            email=form.email.data,
            password=generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8),
            name=form.name.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.name == form.name.data)).scalar()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('add_project'))
            else:
                flash('Invalid password')
                return redirect(url_for('login'))
        else:
            flash('Invalid email')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)


@app.route('/')
def index():
    current_year = datetime.datetime.now().year
    return render_template('index.html', year=current_year)


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/projects', methods=['GET'])
def projects():
    projects = Project.query.all()
    # projects = db.get_or_404(Project)
    current_year = datetime.datetime.now().year
    return render_template('projects.html', projects=projects, year=current_year, user=current_user)




@app.route('/add_project', methods=['GET', 'POST'])
@login_required
@admin_only
def add_project():
    form = PostForm()
    if form.validate_on_submit():
        if form.img_url.data:
            file = form.img_url.data
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            img_url = f'uploads/{filename}' # save file to static/uploads folder
        new_project = Project(
            title=form.title.data,
            body=form.body.data,
            img_url=img_url,
            user_id=current_user.id
        )
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('projects'))
    return render_template('add_project.html', form=form)

@app.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
@login_required
@admin_only
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    form = PostForm(obj=project)
    if form.validate_on_submit():
        project.title = form.title.data
        project.body = form.body.data
        project.img_url = form.img_url.data
        db.session.commit()
        return redirect(url_for('projects'))
    return render_template('edit_project.html', form=form, project=project)

@app.route('/delete_project/<int:project_id>', methods=['GET', 'POST'])
@login_required
@admin_only
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('projects'))

@app.route('/resume')
def resume():
    return render_template('resume.html')

@app.route('/download')
def download():
    return send_from_directory('static', path="files/Jekuthiel_Okafor's_resume.pdf")

if __name__ == '__main__':
    app.run(debug=True)