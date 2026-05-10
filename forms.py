from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, URL, Optional


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')





class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Content', validators=[DataRequired()])

    # WORLD-CLASS CHANGE: Set a generic label in the form definition
    img_url = FileField('Project Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])

    github_url = StringField('GitHub URL', validators=[URL(), Optional()])  # Added Optional() here, see below
    submit = SubmitField('Save Changes')


class ProjectForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Description', validators=[DataRequired()])
    img_url = StringField('Image URL', validators=[DataRequired()])
    github_url = StringField('GitHub URL', validators=[Optional(), URL()])
    live_url = StringField('Live URL', validators=[Optional(), URL()])


class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = StringField('Role (admin/user)', validators=[DataRequired()])


class MessageForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')


class ExperienceForm(FlaskForm):
    company = StringField('Company', validators=[DataRequired()])
    title = StringField('Job Title', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    date_range = StringField('Date Range (e.g. 2019 - Present)', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])


class EducationForm(FlaskForm):
    institution = StringField('Institution', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    degree = StringField('Degree', validators=[DataRequired()])
    field = StringField('Field of Study', validators=[DataRequired()])
    date_range = StringField('Date Range (e.g. 2013 - 2017)', validators=[DataRequired()])


class SkillForm(FlaskForm):
    name = StringField('Skill Name', validators=[DataRequired()])
    skill_type = SelectField('Type', choices=[('Professional', 'Professional'), ('Language', 'Language')], validators=[DataRequired()])
