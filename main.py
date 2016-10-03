# Import flask stuff
from flask import Flask, render_template, redirect, request
from flaskext.mysql import MySQL

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
	return render_template('index.html')

@app.route('/register')
def register():
	return render_template('/register.html')

@app.route('/register_submit', methods=['POST'])
def register_submit():
	# first, check to see if the username already exists. SELECT statement.
	check_username_query = "SELECT * FROM users where username = '%s'" % request.form['username']
	
	#print check_username_query
	print check_username_query
	cursor.execute(check_username_query)
	check_username_result = cursor.fetchone()

	# second, if it is taken, send them back to the register page with a message
	# second b, if it't not taken, then insert the username into mysql
	return 'done'

if __name__ == "__main__":
	app.run(debug=True)