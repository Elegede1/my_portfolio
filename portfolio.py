from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import datetime
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text
from forms import LoginForm, RegisterForm, PostForm
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['CKEDITOR_CONFIG'] = {'toolbar': 'Full', 'height': 500}
app.config['SECRET_KEY'] = os.getenv('secret_key')
login_manager = LoginManager()
login_manager.init_app(app)
Bootstrap5(app)

class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))


@app.route('/')
def index():
    current_year = datetime.datetime.now().year
    return render_template('index.html', year=current_year)

@app.route('/Jekuthiel', methods=['GET', 'POST'])
def Jekuthiel():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        if login_form.email.data == "admin@email.com" and login_form.password.data == "12345678":
            return render_template('Jekuthiel.html')
        else:
            return render_template('denied.html')
    return render_template('Jekuthiel.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/resume')
def resume():
    return render_template('resume.html')

@app.route('/download')
def download():
    return send_from_directory('static', path="files/Jekuthiel_Okafor's_resume.pdf")

if __name__ == '__main__':
    app.run(debug=True)