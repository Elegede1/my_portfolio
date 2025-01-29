from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, URL
from wtforms import ValidationError
from flask_ckeditor import CKEditor, CKEditorField


class LoginForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    # def validate_email(self, field):
    #     if User.query.filter_by(email=field.data).first():
    #         raise ValidationError('Email already registered.')
    #
    # def validate_username(self, field):
    #     if User.query.filter_by(username=field.data).first():
    #         raise ValidationError('Username already in use.')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = CKEditorField('Content', validators=[DataRequired()])
    img_url = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    submit = SubmitField('Post')