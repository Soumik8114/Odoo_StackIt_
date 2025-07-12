from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField,PasswordField,SubmitField,BooleanField,TextAreaField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError
from blog import db
from blog.models import user
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),Length(min=2,max=10)])
    email=StringField("Email",validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    confirm_password=PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('Sign Up')

    def validate_username(self,username):
        usr=user.query.filter_by(username=username.data).first()
        if usr:
            raise ValidationError('That username already exists. Please choose a different username.')
    def validate_email(self,email):
        em=user.query.filter_by(email=email.data).first()
        if em:
            raise ValidationError('That email already exists. Please choose a different email.')

class LoginForm(FlaskForm):
    email=StringField("Email",validators=[DataRequired(),Email()])
    password=PasswordField('Password',validators=[DataRequired()])
    remember=BooleanField('Remember Me')
    submit=SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),Length(min=2,max=10)])
    email=StringField("Email",validators=[DataRequired(),Email()])
    pic=FileField('Update Profile Picture',validators=[FileAllowed(['jpg','png'])])
    submit=SubmitField('Update')

    def validate_username(self,username):
        if username.data!= current_user.username:
            usr=user.query.filter_by(username=username.data).first()
            if usr:
                raise ValidationError('That username already exists. Please choose a different username.')
    def validate_email(self,email):
        if email.data!= current_user.email:
            em=user.query.filter_by(email=email.data).first()
            if em:
                raise ValidationError('That email already exists. Please choose a different email.')

class PostForm(FlaskForm):
    title=StringField('Title',validators=[DataRequired()])
    content=TextAreaField('Content',validators=[DataRequired()])
    submit=SubmitField('Post')

class RequestResetForm(FlaskForm):
    email=StringField("Email",validators=[DataRequired(),Email()])
    submit=SubmitField('Request Password Reset')
    def validate_email(self,email):
        em=user.query.filter_by(email=email.data).first()
        if em is None:
            raise ValidationError('That Email does not exist. You must be registered first.')

class ResetPasswordForm(FlaskForm):
    password=PasswordField('Password',validators=[DataRequired()])
    confirm_password=PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField('Reset Password')
