#run virtualenv on bin in b2 then go down into bawk and run python main.py

# Import flask stuff
from flask import Flask, render_template, redirect, request, session, jsonify
from flaskext.mysql import MySQL
import bcrypt

#create an instance of the mysql class
mysql = MySQL()
app = Flask(__name__)
#add to the app (Flask object) some config data for our connection
app.config['MYSQL_DATABASE_USER'] = 'x'
app.config['MYSQL_DATABASE_PASSWORD'] = 'x'
#The name of the database we want to connect to at the DB server
app.config['MYSQL_DATABASE_DB'] = 'bawk'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
# user the mysql object's method "init_app" and pass it the flask object
mysql.init_app(app)
conn = mysql.connect()
#set up a cursor object, which is what the sql uses to connect and run queries
cursor = conn.cursor()
#session secret key
app.secret_key = 'asdf&&^(*ahasfljhas'

# Create route for home page
@app.route('/')
def index():
	get_bawks_query = "SELECT b.id, b.post_content, b.current_vote, u.username FROM bawks AS b INNER JOIN user AS u ON b.uid = u.id WHERE 1"
	cursor.execute(get_bawks_query)
	get_bawks_result = cursor.fetchall()
	if get_bawks_result is not None:
		return render_template('index.html', bawks = get_bawks_result)
	else:
		return render_template('index.html', message = "No bawks yet!")
	if request.args.get('username'):
		#the username variable is set in the query string
		return render_template('register.html', message="That username is already taken")
	else:
		return render_template('index.html')

@app.route('/register')
def register():
	return render_template('/register.html')

@app.route('/register_submit', methods=['POST'])
def register_submit():
	# first, check to see if the username already exists. SELECT statement.
	check_username_query = "SELECT * FROM user where username = '%s'" % request.form['username']
	cursor.execute(check_username_query)
	check_username_result = cursor.fetchone()
	# second, if it't not taken, then insert the username into mysql
	if (check_username_result is None):
		# no match. insert
		session['username'] = request.form['username']
		real_name = request.form['real_name']
		username = request.form['username']
		password = request.form['password'].encode('utf-8')
		hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
		email = request.form['email']
		username_insert_query = "INSERT INTO user VALUES (DEFAULT, %s, %s, %s, %s, NULL)"
		cursor.execute(username_insert_query, (real_name, username, hashed_password, email))
		conn.commit()
		return render_template('index.html')
	else:
		# second b, if it is taken, send them back to the register page with a message
		return redirect('/register?username=taken')
@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/login_submit', methods=['POST'])
def login_submit():
	password = request.form['password']
	username = request.form['username']
	check_password_query = "SELECT password, id FROM user where username = '%s'" % request.form['username']
	cursor.execute(check_password_query)
	hashed_password_from_mysql = cursor.fetchone()
	# to check a hash against english:
	if bcrypt.hashpw(password.encode('utf-8'), hashed_password_from_mysql[0].encode('utf-8')) == hashed_password_from_mysql[0].encode('utf-8'):
		#we have a match
		session['username'] = request.form['username']
		session['id'] = check_password_query[1]
		return redirect('/')
	else:
		return redirect('/login?message=incorrect_password')

@app.route('/logout')
def logout():
	session.clear()
	return redirect('/?message=logged_out')

@app.route('/<username>')
def user_page(username):
	return render_template('user_landing.html')

@app.route('/post_submit', methods=["POST"])
def post_submit():
	# pull the post from the form
	post_content = request.form['post_content']
	# get the id of the user to keep track of who posted what
	get_user_id = "SELECT id FROM user WHERE username = '%s'" % session['username']
	cursor.execute(get_user_id)
	get_user_id_result = cursor.fetchone()
	user_id = get_user_id_result[0]
	# insert post into the MySQL
	post_content_query = "INSERT INTO bawks (post_content, uid, current_vote) VALUES ('"+post_content+"', "+str(user_id)+", 0)"
	cursor.execute(post_content_query)
	conn.commit()
	return request.form['post_content']

@app.route('/home')
def home():
	return 'home.html'
@app.route('/process_vote', methods=['POST'])
def process_vote():
	pid = request.form['vid'] # this came from jquery $.ajax
	voteType = request.form['voteType']
	username = session['username']
	check_user_votes = "SELECT * FROM votes INNER JOIN user ON user.id = votes.id WHERE user.username = '%s' AND votes.pid = '%s'" % (username, pid)
	cursor.execute(check_user_votes)
	votes = cursor.fetchone()
	# it's possible we get none back because the user hasn't voted on this post
	if votes is None:
		#user hasn't voted, insert
		insert_user_vote_query = "INSERT INTO votes (pid, uid, vote_type) VALUES ('%s', '%s', '%s')" % (pid, session['id'], voteType)
		cursor.execute(insert_user_vote_query)
		conn.commit()
	return jsonify('voteCounted')
	# return 'good'

if __name__ == "__main__":
	app.run(debug=True)