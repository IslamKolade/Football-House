import os
from flask import Flask, redirect, render_template, flash, request, url_for
from werkzeug.utils import secure_filename
import uuid as uuid
import os

from datetime import datetime, time
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user


from forms import SignInForm, SignUpForm, UpdateForm, PostForm, SearchForm


#Create a flask instance
app = Flask(__name__)
#SQLite Database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///FootballHouse.db'

#POSTGRES DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = ('postgres://rvbrqpkdzzzcti:c85cfb0734f4559a2beb51ef17554bdbdb9278a6fb935cf8599548aedc245dba@ec2-54-86-106-48.compute-1.amazonaws.com:5432/ddl69nl7mmpcip').replace("://", "ql://", 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'nonsense'
UPLOAD_FOLDER = 'static/Uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#MYSQL Database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Kolade16@localhost/fh_users'
#Secret Key
#app.config['SECRET_KEY'] = 'gfgrytyujggfff'
#Initialize Database
db = SQLAlchemy(app)
migrate = Migrate(app,db)



#Flask Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'SignIn'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#Pass Form to Nav Bar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)



#Search function
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        #Get data from submitted form
        postsearched = form.searched.data
        #Query the database
        posts = posts.filter(Posts.content.like('%' + postsearched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template('search.html', form=form, searched = postsearched, posts = posts) 




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



#Profile
@app.route('/Profile', methods = ['GET', 'POST'])
@login_required
def Profile():
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
            about= form.about.data,
            password_hash = hashed_pw)
            db.session.add(user)
            db.session.commit()
        first_name = form.first_name.data
        form.email.data = ''
        form.first_name.data = ''
        form.last_name.data = ''
        form.username.data = ''
        form.about.data = ''
        form.password_hash.data = ''
        flash('User added successfully, now sign in to Football House.')
        return redirect (url_for('SignIn'))
    my_users = Users.query.order_by(Users.date_joined)
    return render_template('SignUp.html', first_name = first_name, form = form, my_users = my_users)






#Update Database Records
@app.route('/update/<int:id>', methods = ['GET', 'POST'])
@login_required
def update(id):
    form = UpdateForm()
    username_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        username_to_update.email = request.form['email']
        username_to_update.first_name = request.form['first_name']
        username_to_update.last_name = request.form['last_name']
        username_to_update.username = request.form['username']
        username_to_update.about = request.form['about']
        username_to_update.profile_pic = request.files['profile_pic']
        #Take Image
        pic_filename = secure_filename(username_to_update.profile_pic.filename)
        #Set UUID to change profile pic name to random to avoid duplication.
        pic_name = str(uuid.uuid1()) + '' + pic_filename
        #Save Image
        saver = request.files['profile_pic']

        #Convert Image to string to save to database
        username_to_update.profile_pic = pic_name


        try:
            db.session.commit()
            saver.save(os.path.join(app.config['UPLOAD_FOLDER']), pic_name)
            flash('User Updated Successfully')
            return redirect (url_for('Profile', form = form, username_to_update = username_to_update))
        except:
            flash('Error, looks like there was a problem. Try again!!')
            return redirect (url_for('Profile', form = form, username_to_update = username_to_update))
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

#Admin Page
@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 1:
        return render_template('admin.html')
    else:
        flash('Access Denied!')
        return redirect(url_for('Profile'))



#Delete Posts
@app.route('/post/delete/<int:id>')
@login_required
def delete_post(id):
    delete_post = Posts.query.get_or_404(id)
    id = current_user.id
    if id == delete_post.poster.id:
        try:
            db.session.delete(delete_post)
            db.session.commit()
            flash('Post Deleted Successfully')
            posts = Posts.query.order_by(Posts.date_posted)
            return redirect(url_for('home', posts = posts))
        except:
            flash('Oops, there was a problem deleting post. Try again')
            return redirect(url_for('home'))
    else:
        flash('You cant delete that post')
        posts = Posts.query.order_by(Posts.date_posted)
        return redirect(url_for('home', posts = posts))



#Edit Posts
@app.route('/post/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit_post(id):
    edit_post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        edit_post.title = form.title.data
        edit_post.content = form.content.data
        #Update Post in Database
        db.session.add(edit_post)
        db.session.commit()
        flash('Post Edited Successfully')
        return redirect(url_for('fullpost', id = edit_post.id))
    if current_user.id == edit_post.poster_id:
        form.title.data = edit_post.title
        form.content.data = edit_post.content
        return render_template('edit_post.html', form = form)
    else:
        flash("You aren't authorized to edit this post")
        posts = Posts.query.order_by(Posts.date_posted)
        return redirect(url_for('home', posts = posts))


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
        poster = current_user.id
        post = Posts(title=form.title.data, content=form.content.data, poster_id=poster)
        #Clear the Form
        title=form.title.data = ''
        content=form.content.data = ''
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


#Models
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, index=True)
    email = db.Column(db.String(500), unique=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(600), nullable=False, unique=True)
    about = db.Column(db.Text(), nullable=True)
    profile_pic = db.Column(db.String(), nullable=True)
    date_joined = db.Column(db.Date, default=datetime.now())
    #Password
    password_hash = db.Column(db.String(400))

    #A User can have many posts
    posts = db.relationship('Posts', backref = 'poster')

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
    date_posted = db.Column(db.DateTime, default= datetime.utcnow)
    # Foreign Key to Link Users (Going to refer to the primary key of the User)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))