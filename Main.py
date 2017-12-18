import requests
import json
import os
from flask import Flask, request, render_template, make_response, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, PasswordField, BooleanField, SelectMultipleField, ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from flask_script import Manager, Shell
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
from imdb import IMDb
from threading import Thread
ia = IMDb()

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user

app = Flask(__name__)
app.debug = True

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:12345678@localhost/matlefkofsky364Final1"
# app.config["SQLALCHEMY_DATABASE_URI"] = "DATABASE_URLS"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587 #default
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'matlefkofsky364@gmail.com'
app.config['MAIL_PASSWORD'] = "matlefkofsky"
app.config['MAIL_SUBJECT_PREFIX'] = '[Movie Results]'
app.config['MAIL_SENDER'] = 'matlefkofsky364@gmail.com' 
app.config['ADMIN'] = 'matlefkofsky364@gmail.com' 

app.config['SECRET_KEY'] = 'hardtoguessstring'

# Set up Flask debug stuff
manager = Manager(app)
db = SQLAlchemy(app) # For database use
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
mail = Mail(app)
google_key = "AIzaSyCRQKx-rs1IRg-mlG11KrY412tnyUvs8w8"

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.init_app(app)

def send_async_email(app, msg):
	with app.app_context():
		mail.send(msg)

def send_email(to, subject, template, **kwargs):
	msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject,
				  sender=app.config['MAIL_SENDER'], recipients=[to])
	msg.body = render_template(template + '.txt', **kwargs)
	msg.html = render_template(template + '.html', **kwargs)
	thr = Thread(target=send_async_email, args=[app, msg])
	thr.start()
	return thr

class User(UserMixin, db.Model):
	__tablename__ = "user"
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(64), unique=True)
	password_hash = db.Column(db.String(200), unique=True)    
	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

## DB load functions
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id)) # returns User object or None

class RegistrationForm(FlaskForm):
	email = StringField('Email:', validators=[Required(),Length(1,64),Email()])
	password = PasswordField('Password:',validators=[Required(),EqualTo('password2',message="Passwords must match")])
	password2 = PasswordField("Confirm Password:",validators=[Required()])
	submit = SubmitField('Register User')

	#Additional checking methods for the form
	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registered.')

def get_or_create_movie(db_session, Title, director):
	NewMovie = db_session.query(Movie).filter_by(title=Title) .first()
	if NewMovie:
		return NewMovie
	else:
		NewMovie = Movie(title=Title, director = director)
		db_session.add(NewMovie)
		db_session.commit()
		return NewMovie

def get_or_create_actor(db_session, actor):
	NewActor = db_session.query(Actor).filter_by(actors=actor) .first()
	if NewActor:
		return NewActor
	else:
		NewActor = Actor(actors=actor)
		db_session.add(NewActor)
		db_session.commit()
		return NewActor

def get_data(Title):
	movie = requests.get("http://omdbapi.com/?apikey=5f9181f1&t="+ Title).json()
	new_movie = get_or_create_movie(db.session, movie["Title"], movie["Director"])
	for each in movie["Actors"].split(", "):
		new_actor = get_or_create_actor(db.session, each)
		get_or_create_ActorMovie(db.session, new_movie.id, new_actor.id)
	return movie

def get_or_create_ActorMovie(db_session, movieid, actorid):
	newActorMovie = db_session.query(ActorMovies).filter_by(actor_id=actorid, movie_id = movieid) .first()
	if newActorMovie:
		return newActorMovie
	else:
		newActorMovie = ActorMovies(actor_id=actorid, movie_id = movieid)
		db_session.add(newActorMovie)
		db_session.commit()
		return newActorMovie

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

@app.route('/login',methods=["GET","POST"])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			return redirect(request.args.get('next') or url_for('index'))
		flash('Invalid username or password.')
	return render_template('login.html',form=form)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out')
	send_email("abhi98041@gmail.com", "Logout Notification", "html_test")
	return redirect(url_for('index'))

@app.route('/register',methods=["GET","POST"])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(email=form.email.data,password=form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('You can now log in!')
		return redirect(url_for('login'))
	return render_template('register.html',form=form)

@app.route('/top250',methods=["GET","POST"])
def top250():
	header_text="Top 250 best movies of all time"
	dystopia = ia.get_top250_movies()#top 250
	return render_template('topmovie.html',dys=dystopia,header_from_temp=header_text)


@app.route('/bottom100',methods=["GET","POST"])
def bottom100():
	header_text="Top 100 worst movie of all time"
	bottom100 = ia.get_bottom100_movies()#worst 100
	return render_template('topmovie.html',dys=bottom100,header_from_temp=header_text)


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
	form = MovieForm()
	if form.validate_on_submit():
		data = get_data(form.text.data)
		actorsList = data["Actors"].split(", ")
		return render_template("movieresults.html", movieData= data, Actors = actorsList)
	return render_template("index.html", form= form)

@app.route('/actor/<Actor>',methods=["GET","POST"])
@login_required
def actor_search(Actor):
	act=Actor.replace(" ","+")
	testing =requests.get("http://www.theimdbapi.org/api/find/person?name="+act)
	data=json.loads(testing.text)
	text_actor_list=[]
	for i in range(0, 50):
		# print(data[0]['filmography']['actor'][i]['title'])
		text_actor_list.append(data[0]['filmography']['actor'][i]['title'])
	return render_template('actorresults.html',text_actor=text_actor_list)


class Movie(db.Model):
	__tablename__ = "movies"
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(285))
	director = db.Column(db.String)

class Actor(db.Model):
	__tablename__ = "actors"
	id = db.Column(db.Integer, primary_key=True)
	actors = db.Column(db.String)

class ActorMovies(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	actor_id = db.Column(db.Integer, db.ForeignKey('actors.id'))
	movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))

class MovieForm(FlaskForm):
	text = StringField("Type in a title of a movie to find out more about it", validators=[Required()])
	submit = SubmitField('Submit')

@app.errorhandler(404)
def fouronefour(e):
	return render_template("404.html")

@app.errorhandler(405)
def fouronefive(e):
	return render_template("405.html") 

if __name__ == '__main__':
	db.create_all()
	manager.run()
