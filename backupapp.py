import email
from enum import unique
from turtle import title
from unicodedata import name
from flask import Flask, redirect, render_template, flash, request, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired,EqualTo, Length
from datetime import datetime
from wtforms.widgets import TextArea
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user


#Create a flask instance
app = Flask(__name__)
#SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///FootballHouse.db'
#MYSQL Database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Kolade16@localhost/fh_users'
#Secret Key
app.config['SECRET_KEY'] = 'gfgrytyujggfff'
#Initialize Database
db = SQLAlchemy(app)
migrate = Migrate(app,db)


#Models
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, index=True)
    email = db.Column(db.String(500), unique=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(600), nullable=False, unique=True)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    #Password
    password_hash = db.Column(db.String(400))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    #string
    def __repr__(self) -> str:
        return '< User: %r>'% self.first_name


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(800))
    content = db.Column(db.Text)
    author = db.Column(db.String(900))
    date_posted = db.Column(db.DateTime, default= datetime.utcnow)

#Flask Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'SignIn'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))



@app.route('/SignIn', methods = ['GET', 'POST'])
def SignIn():
    form = SignInForm()
    #Validate Form
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            #Check the hashed password
            if check_password_hash(user.password_hash, form.password_hash.data):
                login_user(user)
                flash('Login Successful')
                return redirect(url_for('Profile'))
            else:
                flash('Incorrect Password, try again.')
        else:
            flash('Email does not exist.')
    return render_template('SignIn.html', form = form)

#LogOut
@app.route('/LogOut', methods = ['GET', 'POST'])
@login_required
def LogOut():
    logout_user()
    flash('Log out successful')
    return redirect(url_for('SignIn'))




@app.route('/Profile', methods = ['GET', 'POST'])
@login_required
def Profile():
    id = current_user.id
    form = UpdateForm()
    username_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        username_to_update.email = request.form['email']
        username_to_update.first_name = request.form['first_name']
        username_to_update.last_name = request.form['last_name']
        username_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash('User Updated Successfully')
            return render_template('Profile.html', form = form, username_to_update = username_to_update)
        except:
            flash('Error, looks like there was a problem. Try again!!')
            return render_template('Profile.html', form = form, username_to_update = username_to_update)
    else:
        return render_template('Profile.html', form = form, username_to_update = username_to_update)
    return render_template('Profile.html')


@app.route('/SignUp', methods = ['GET', 'POST'])
def SignUp():
    first_name = None
    form = SignUpForm()
    #Validate Form
    if form.validate_on_submit():
        user = Users.query.filter_by(email = form.email.data).first()
        if user is None:
            #Hash Password
            hashed_pw = generate_password_hash(form.password_hash.data, 'sha256')
            user = Users(email = form.email.data, 
            first_name = form.first_name.data,
            last_name = form.last_name.data,
            username = form.username.data,
            password_hash = hashed_pw)
            db.session.add(user)
            db.session.commit()
        first_name = form.first_name.data
        form.email.data = ''
        form.first_name.data = ''
        form.last_name.data = ''
        form.username.data = ''
        form.password_hash.data = ''
        flash('User added successfully')
    my_users = Users.query.order_by(Users.date_joined)
    return render_template('SignUp.html', first_name = first_name, form = form, my_users = my_users)


#Form
class SignUpForm(FlaskForm):
    email = EmailField('Email Address: ', validators= [DataRequired()])
    first_name = StringField('First Name: ', validators= [DataRequired()])
    last_name = StringField('Last Name: ', validators= [DataRequired()])
    username = StringField('Username: ', validators= [DataRequired()])
    password_hash = PasswordField('Password: ', validators= [DataRequired(), EqualTo('confirm_password', message= 'Passwords Must Match!')])
    confirm_password = PasswordField('Confirm Password: ', validators= [DataRequired()])
    submit = SubmitField('Sign Up')

class UpdateForm(FlaskForm):
    email = EmailField('Email Address: ', validators= [DataRequired()])
    first_name = StringField('First Name: ', validators= [DataRequired()])
    last_name = StringField('Last Name: ', validators= [DataRequired()])
    username = StringField('Username: ', validators= [DataRequired()])
    submit = SubmitField('Update')

class SignInForm(FlaskForm):
    email = EmailField('Email Address: ', validators= [DataRequired()])
    password_hash = PasswordField('Password: ', validators= [DataRequired(), EqualTo('confirm_password', message= 'Passwords Must Match!')])
    confirm_password = PasswordField('Confirm Password: ', validators= [DataRequired()])
    submit = SubmitField('Sign In')

class PostForm(FlaskForm):
    title = StringField('Title: ', validators= [DataRequired()])
    content = StringField('Content: ', validators= [DataRequired()], widget=TextArea())
    author = StringField('Author: ', validators= [DataRequired()])
    submit = SubmitField('Post')




#Update Database Records
@app.route('/update/<int:id>', methods = ['GET', 'POST'])
def update(id):
    form = SignUpForm()
    username_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        username_to_update.email = request.form['email']
        username_to_update.first_name = request.form['first_name']
        username_to_update.last_name = request.form['last_name']
        username_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash('User Updated Successfully')
            return render_template('Profile.html', form = form, username_to_update = username_to_update)
        except:
            flash('Error, looks like there was a problem. Try again!!')
            return render_template('update.html', form = form, username_to_update = username_to_update)
    
    else:
        return render_template('update.html', form = form, username_to_update = username_to_update)

#Delete Database Records
@app.route('/delete/<int:id>')
def delete(id):
    form = SignUpForm()
    user_to_delete = Users.query.get_or_404(id)
    first_name = None
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User Deleted Successfully')
        my_users = Users.query.order_by(Users.date_joined)
        return render_template('SignUp.html', first_name = first_name, form = form, my_users = my_users)
    except:
        flash('Whoops! There was a problem deleting this user.')
        return render_template('SignUp.html', first_name = first_name, form = form, my_users = my_users)
#Routes
@app.route('/')
def home():
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('index.html', posts = posts)

#Delete Posts
@app.route('/post/delete/<int:id>')
@login_required
def delete_post(id):
    delete_post = Posts.query.get_or_404(id)
    try:
        db.session.delete(delete_post)
        db.session.commit()
        flash('Post Deleted Successfully')
        return redirect(url_for('home'))
    except:
        flash('Oops, there was a problem deleting post. Try again')
        return redirect(url_for('home'))


#Edit Posts
@app.route('/post/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit_post(id):
    edit_post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        edit_post.title = form.title.data
        edit_post.author = form.author.data
        edit_post.content = form.content.data
        #Update Post in Database
        db.session.add(edit_post)
        db.session.commit()
        flash('Post Edited Successfully')
        return redirect(url_for('fullpost', id = edit_post.id))
    form.title.data = edit_post.title
    form.author.data = edit_post.author
    form.content.data = edit_post.content
    return render_template('edit_post.html', form = form)


#Full Post
@app.route('/fullpost/<int:id>')
def fullpost(id):
    fullpost = Posts.query.get_or_404(id)
    return render_template('fullpost.html', fullpost = fullpost)

#Add Post Page
@app.route('/add-post', methods=['GET','POST'])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data, author=form.author.data)
        #Clear the Form
        title=form.title.data = ''
        content=form.content.data = ''
        author=form.author.data = ''
        #Add post data to database
        db.session.add(post)
        db.session.commit()
        flash('Posted Successfully')
        return redirect(url_for('home'))
    return render_template('add_post.html', form = form)

#All Posts
@app.route('/posts')
def posts():
    #To show all posts from the database.
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts = posts)


#Custom Error Message
#Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

#Internal error
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 404
