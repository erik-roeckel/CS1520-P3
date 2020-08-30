import os
import time
from datetime import datetime
import json
from flask import Flask, request, abort, url_for, redirect, session, render_template, flash, g, _app_ctx_stack, jsonify
from werkzeug import check_password_hash, generate_password_hash

from models import db, User, Chat, Message
app = Flask(__name__)

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'chat.db')
app.config.from_object(__name__)
app.config.from_envvar('CHAT_SETTINGS', silent = True)
app.secret_key = "development key"
DEBUG = True

db.init_app(app)

@app.cli.command('initdb')
def initdb_command():
	db.create_all()

def get_user_id(username):
	user = User.query.filter_by(username = username).first()
	if(user):
		return user.id
	else:
		return None
def get_chat_id(chatName):
	chat = Chat.query.filter_by(chat_name = chatName).first()
	if(chat):
		return chat.chat_id
	else:
		return None

def format_datetime(timestamp):
	return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')

@app.before_request
def before_request():
	g.user = None
	g.chat = None
	if 'id' in session:
		g.user = User.query.filter_by(id = session['id']).first()
	if 'chat_id' in session:
		g.chat = Chat.query.filter_by(chat_id = session['chat_id']).first()

@app.route("/")
def default():
	return redirect(url_for("login_controller"))
	
@app.route("/login/", methods=["GET", "POST"])
def login_controller():
    # first check if the user is already logged in
    if g.user:
        return redirect(url_for("profile", username = g.user.username))
    elif request.method == "POST":
        user = User.query.filter_by(username = request.form['username']).first()
        if user is None:
            flash('Invalid Username, try again')
            return redirect(url_for("login_controller"))
        elif not check_password_hash(user.hashedPass, request.form['password']):
            flash('Invalid Password, try again!')
        elif user:
            session['id'] = user.id
            return redirect(url_for("profile", username = user.username))
    # if not, and the incoming request is via POST try to log them in
    # if all else fails, offer to log them in
    return render_template("login.html")

@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
	all_chats = Chat.query.order_by(Chat.chat_id).all()
	if request.method == "GET":
		return render_template("profile.html", username = g.user.username, chats = all_chats)
	elif request.method == "POST":
		if not request.form['chatName']:
			flash("You must enter a chat name to create a new chat!")
		elif get_chat_id(request.form['chatName']) is not None:
			flash("This chat name has already been used, please try another!")
		else:
			db.session.add(Chat(g.user.id, request.form['chatName']))
			db.session.commit()
			flash("You have created a new chatroom, you can find this in the list of chatrooms to join")
			all_chats = Chat.query.order_by(Chat.chat_id).all()
	return render_template("profile.html", username = g.user.username, chats = all_chats)

@app.route("/profile/<username>/<chatName>/", methods=["GET", "POST"])
def join_chat(username, chatName):
	session['chat_id'] = get_chat_id(chatName)
	messages = Message.query.filter_by(chat_id = session['chat_id']).all()
	if request.method == "GET":
		return render_template("chat.html", chatName = chatName, username = username, messages = messages)
	elif request.method == "POST":
		return render_template("chat.html", chatName = chatName, username = username, messages = messages)

@app.route("/add_message", methods=["POST", "GET"])
def add_message():
	if not g.user.id:
		abort(401)
	if not request.form['text']:
		flash("You must enter something to post this message")
	else:
		db.session.add(Message(g.user.id, session['chat_id'], request.form['text'], int(time.time())))
		db.session.commit()
	return "OK!"

@app.route("/messages")
def get_messages():
	messages = Message.query.filter_by(chat_id = session['chat_id']).all()
	currentMessages = []
	mostRecentMessage = int((request.args.get('date')))
	if mostRecentMessage != 0:
		for message in messages:
			if message.pub_date >= mostRecentMessage:
				currentMessages.append(message)
		newMessages = [m.serialize() for m in currentMessages]
		return json.dumps(newMessages)
	else:
		return json.dumps(currentMessages)

@app.route("/author")
def get_author():
	d = {"author": g.user.username}
	return jsonify(d)


@app.route("/delete_chat/<chatName>/", methods =["GET", "POST"])
def delete_chat(chatName):
	if request.method == "GET":
		return render_template("deleteChat.html", chatName = chatName)
	else:
		deleteMessages = Message.query.filter_by(chat_id = get_chat_id(chatName)).all()
		for message in deleteMessages:
			db.session.delete(message)
		deleteChat = Chat.query.filter_by(chat_name = chatName).first()
		db.session.delete(deleteChat)
		db.session.commit()
		flash("You have successfully deleted this chat")
		return redirect(url_for('profile', username = g.user.username))

@app.route("/register" , methods = ["GET", "POST"])
def register_controller():
	if request.method == "GET":
		return render_template("register.html")
	elif request.method == "POST":
		if not request.form['user']:
			flash("You must enter a username to register", 'error')
		elif not request.form['password']:
			flash("You must enter a password to register", 'error')
		elif get_user_id(request.form['user']) is not None:
			flash("This username is already taken, try another", 'error')
		else:
			db.session.add(User(request.form['user'], generate_password_hash(request.form['password'])))
			db.session.commit()
			flash("You have registered for an account, please sign in")
			return redirect(url_for("login_controller"))
	return render_template("register.html")

@app.route("/logout")
def logout_controller():
	session.pop('id', None)
	flash("You have been successfully logged out")
	return redirect(url_for("login_controller"))

app.jinja_env.filters['datetimeformat'] = format_datetime

if __name__ == "__main__":
	app.run()