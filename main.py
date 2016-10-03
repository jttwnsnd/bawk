# Import flask stuff
from flask import Flask, render_template, redirect, request
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

# Create route for home page
@app.route('/')
def index():
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
	check_username_query = "SELECT * FROM users where username = '%s'" % request.form['username']
	cursor.execute(check_username_query)
	check_username_result = cursor.fetchone()
	# second, if it't not taken, then insert the username into mysql
	if (check_username_result is None):
		# no match. insert
		real_name = request.form['real_name']
		username = request.form['username']
		password = request.form['password'].encode('utf-8')
		hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
		email = request.form['email']
		username_insert_query = "INSERT INTO users VALUES (DEFAULT, %s, %s, %s, %s, NULL)"
		cursor.execute(username_insert_query, (real_name, username, hashed_password, email))
		conn.commit()
		return redirect('/')
	else:
		# second b, if it is taken, send them back to the register page with a message
		return redirect('/register?username=taken')
@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/login_submit', methods=['POST'])
def login_submit():
	password = request.form['password'].encode('utf-8')
	check_username_query = "SELECT password FROM users where username = '%s'" % request.form['username']
	cursor.execute(check_username_query)
	hashed_password_from_mysql = cursor.fetchone()
	print hashed_password_from_mysql[0]
	print hashed_password_from_mysql
	print bcrypt.hashpw(password, hashed_password_from_mysql[0])
	return 'testing'
	# to check a hash against english:
	if bcrypt.hashpw(password.encode('utf-8'), hashed_password_from_mysql) == hashed_password_from_mysql:
		#we have a match
		print 'yay'
		return 'I got it'
	else:
		return "it didnt work"

if __name__ == "__main__":
	app.run(debug=True)