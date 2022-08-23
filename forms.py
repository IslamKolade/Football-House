from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, TextAreaField
from wtforms.validators import DataRequired,EqualTo, Length
from wtforms.widgets import TextArea
from flask_wtf.file import FileField


#Form
class SignUpForm(FlaskForm):
    email = EmailField('Email Address: ', validators= [DataRequired()])
    first_name = StringField('First Name: ', validators= [DataRequired()])
    last_name = StringField('Last Name: ', validators= [DataRequired()])
    username = StringField('Username: ', validators= [DataRequired()])
    about = TextAreaField('About: ', validators= [DataRequired()])
    profile_pic = FileField('Upload profile picture: ')
    password_hash = PasswordField('Password: ', validators= [DataRequired(), EqualTo('confirm_password', message= 'Passwords Must Match!')])
    confirm_password = PasswordField('Confirm Password: ', validators= [DataRequired()])
    submit = SubmitField('Sign Up')

class UpdateForm(FlaskForm):
    email = EmailField('Email Address: ', validators= [DataRequired()])
    first_name = StringField('First Name: ', validators= [DataRequired()])
    last_name = StringField('Last Name: ', validators= [DataRequired()])
    username = StringField('Username: ', validators= [DataRequired()])
    about = TextAreaField('About:', validators= [DataRequired()])
    profile_pic = FileField('Upload profile picture: ')
    submit = SubmitField('Update')

class SignInForm(FlaskForm):
    email = EmailField('Email Address: ', validators= [DataRequired()])
    password_hash = PasswordField('Password: ', validators= [DataRequired(), EqualTo('confirm_password', message= 'Passwords Must Match!')])
    confirm_password = PasswordField('Confirm Password: ', validators= [DataRequired()])
    submit = SubmitField('Sign In')

class PostForm(FlaskForm):
    title = StringField('Title: ', validators= [DataRequired()])
    content = StringField('Content: ', validators= [DataRequired()], widget=TextArea())
    submit = SubmitField('Post')

class SearchForm(FlaskForm):
    searched = StringField('Searched ', validators= [DataRequired()])
    submit = SubmitField('Search')
