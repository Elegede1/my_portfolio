from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import datetime
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import os

# load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    current_year = datetime.datetime.now().year
    return render_template('index.html', year=current_year)

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